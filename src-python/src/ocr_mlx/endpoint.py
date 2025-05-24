import datetime
import logging
import os
import signal
import socket
import sys
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Annotated, Any, cast

import anyio
import mlx.core as mx
import pydantic
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.routing import APIRoute
from mlx.core import clear_cache
from PIL import ImageOps
from transformers.models.nougat.processing_nougat import NougatProcessor

from ocr_mlx.inference.generate import generate
from ocr_mlx.llm_endpoint import router as llm_router
from ocr_mlx.model.nougat import Nougat
from ocr_mlx.utils.image_utils import load_image

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Create a temp file for logs
log_tempfile = tempfile.NamedTemporaryFile(  # noqa: SIM115
    prefix="ocr_mlx_log_", suffix=".log", delete=False
)
log_file_path = log_tempfile.name
print(f"Log file is at: {log_file_path}")
log_tempfile.close()  # Close the file, logging will handle writing

# Add file handler to logger
file_handler = logging.FileHandler(log_file_path)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logger.addHandler(file_handler)

DEFAULT_PORT_API = 7771


def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def find_free_port(preferred_port=DEFAULT_PORT_API, max_tries=100):
    port = preferred_port
    for _ in range(max_tries):
        if is_port_available(port):
            return port
        port += 1  # Increment the port number to try the next one
    msg = f"No available port found after {max_tries} attempts."
    raise RuntimeError(msg)


@dataclass
class ModelCacheState:
    model: Nougat | None = None
    processor: NougatProcessor | None = None
    model_name: str | None = None
    reset_scheduler: BackgroundScheduler = field(init=False)

    def __post_init__(self):
        self.reset_scheduler = BackgroundScheduler()
        self.reset_scheduler.start()

    def reset(self) -> None:
        logger.info("Resetting model cache")
        self.model = None
        self.processor = None
        self.model_name = None
        clear_cache()

    @contextmanager
    def lifespan(
        self, model_name: str
    ) -> Generator[tuple[Nougat, NougatProcessor], None, None]:
        logger.info("API is starting up...")
        self.reset_scheduler.remove_all_jobs()

        if (
            self.model is None
            or self.processor is None
            or self.model_name != model_name
        ):
            self.reset()
            logger.info("Loading model: %s", model_name)
            self.model = Nougat.from_pretrained(model_name)
            self.processor = cast(
                "NougatProcessor", NougatProcessor.from_pretrained(model_name)
            )
            self.model_name = model_name
        try:
            yield self.model, self.processor

        finally:
            logger.info("API is shutting down...")
            reset_time = datetime.datetime.now(tz=datetime.UTC) + datetime.timedelta(
                seconds=MODEL_CACHE_TIMEOUT
            )
            self.reset_scheduler.add_job(
                self.reset,
                "date",
                run_date=reset_time,
            )
            logger.info(
                "Reset scheduler added job to reset model cache in %s seconds",
                MODEL_CACHE_TIMEOUT,
            )


MODEL_CACHE_TIMEOUT = 10  # Model cache timeout in seconds
STATE = ModelCacheState()


def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"


app = FastAPI(
    title="OCR MLX API",
    description="OCR tool using Nougat models and LLM vision capabilities",
    version="1.0.0",
    generate_unique_id_function=custom_generate_unique_id,
)

# Include LLM router
app.include_router(llm_router)

origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class OCRRequest(pydantic.BaseModel):
    filename: Annotated[str, pydantic.Field(default="", description="Filename")]
    model: Annotated[
        str,
        pydantic.Field(
            default="facebook/nougat-small",
            description="Model name or path",
            examples=["facebook/nougat-small", "facebook/nougat-large"],
        ),
    ]
    temperature: Annotated[
        float,
        pydantic.Field(
            default=0.0,
            description="Sampling temperature",
            ge=0.0,
            le=1.0,
        ),
    ]
    top_p: Annotated[
        float,
        pydantic.Field(
            default=0.0,
            description="Top-p sampling threshold",
            ge=0.0,
            le=1.0,
        ),
    ]
    repetition_penalty: Annotated[
        float | None,
        pydantic.Field(
            default=None,
            description="Repetition penalty",
            ge=1.0,
        ),
    ]
    padding: Annotated[
        int | None,
        pydantic.Field(
            default=None,
            description="Padding",
        ),
    ]


@app.post(
    "/ocr",
    response_class=PlainTextResponse,
    summary="Perform OCR on an image or PDF",
    tags=["ocr"],
)
async def ocr(request: OCRRequest) -> str | None:
    with STATE.lifespan(request.model) as (nougat_model, nougat_processor):
        try:
            # Load and preprocess image
            image = load_image(request.filename).convert("RGB")

            # If padding is not None add a white padding border to the image
            if request.padding is not None:
                image = ImageOps.expand(image, border=request.padding, fill="white")

            pixel_values = mx.array(
                nougat_processor(image, return_tensors="np").pixel_values
            ).transpose(0, 2, 3, 1)

            # If repetition penalty is 1.0, set it to None (no repetition penalty)
            # TODO: This not very clean because this is not the expected behavior
            # But I prefer this than having to change the frontend code
            if request.repetition_penalty == 1.0:
                request.repetition_penalty = None

            # Generate text from model
            outputs = generate(
                nougat_model,
                pixel_values,
                max_new_tokens=4096,
                eos_token_id=nougat_processor.tokenizer.eos_token_id,  # type: ignore
                temperature=request.temperature,
                top_p=request.top_p,
                repetition_penalty=request.repetition_penalty,
            )
            result_text = nougat_processor.tokenizer.decode(outputs)  # type: ignore
        except Exception as e:
            msg = f"Error during OCR: {e!s}"
            logger.exception(msg)
            return None
        else:
            return result_text


@app.get(
    "/health",
    response_class=PlainTextResponse,
    summary="Health check endpoint",
    tags=["health"],
)
async def health() -> str:
    return "OK!!!"


@app.get(
    "/shutdown",
    response_class=PlainTextResponse,
    summary="Shutdown endpoint",
    tags=["shutdown"],
)
async def shutdown():
    logger.info("Shutting down...")
    # Kill the process
    os.kill(os.getpid(), signal.SIGINT)
    return "Shutting down..."


@app.get(
    "/logs",
    response_class=PlainTextResponse,
    summary="Get current log file contents",
    tags=["logs"],
)
async def get_logs():
    try:
        async with await anyio.open_file(log_file_path, "r", encoding="utf-8") as f:
            log_content = await f.read()
    except Exception:
        logger.exception("Error reading log file")
        return "Could not read log file."
    return log_content


def main():
    print("Starting OCR MLX API !!!")

    def handler(signum: int, frame: Any):  # noqa: ARG001
        print("Caught shutdown signal.")
        # Clean up anything if needed here
        sys.exit(0)

    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)

    port = find_free_port()
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    main()
