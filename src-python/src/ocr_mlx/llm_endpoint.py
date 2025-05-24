import logging
from typing import Annotated

import pydantic
from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse

from ocr_mlx.utils.image_utils import load_image
from ocr_mlx.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)

# Create router for LLM endpoints
router = APIRouter(prefix="/llm", tags=["llm"])


class LLMOCRRequest(pydantic.BaseModel):
    filename: Annotated[
        str, pydantic.Field(default="", description="Filename or image data")
    ]
    api_key: Annotated[
        str,
        pydantic.Field(
            description="API key for the LLM service",
            default="",
        ),
    ]
    model: Annotated[
        str,
        pydantic.Field(
            default="gpt-4.1-mini",
            description="Model name to use",
            examples=["gpt-4.1-mini", "gpt-4o", "gpt-4o-mini"],
        ),
    ]
    endpoint_url: Annotated[
        str,
        pydantic.Field(
            default="https://api.openai.com/v1/chat/completions",
            description="LLM API endpoint URL",
        ),
    ]
    max_tokens: Annotated[
        int,
        pydantic.Field(
            default=1000,
            description="Maximum tokens in response",
            ge=1,
            le=4096,
        ),
    ]
    temperature: Annotated[
        float,
        pydantic.Field(
            default=0.0,
            description="Sampling temperature",
            ge=0.0,
            le=2.0,
        ),
    ]
    prompt: Annotated[
        str,
        pydantic.Field(
            default="""You are an OCR model.
I will give you an image of a document, sign, or printed text.
Your task is to extract the visible text exactly as it appears in the image.
- Preserve line breaks and formatting where possible.
- Do not add or remove any words.
- Output text only — no explanations, no commentary.
Here is the image:
            """,
            description="Custom prompt for text extraction",
        ),
    ]


@router.post(
    "/ocr",
    response_class=PlainTextResponse,
    summary="Perform OCR on an image using LLM vision capabilities",
    description="Extract text from images using Large Language Models with vision capabilities like GPT-4 Vision",
)
async def llm_ocr(request: LLMOCRRequest) -> str:
    """
    Perform OCR using LLM vision capabilities.

    This endpoint uses Large Language Models (like GPT-4 Vision) to extract text from images.
    It supports various image formats and can handle complex layouts and handwritten text.
    """
    try:
        # Load and preprocess image
        logger.info(f"Loading image for LLM OCR: {request.filename[:50]}...")
        image = load_image(request.filename).convert("RGB")

        # Create LLM client
        llm_client = LLMClient(
            api_key=request.api_key or "",
            endpoint_url=request.endpoint_url,
        )

        # Extract text using LLM
        logger.info(f"Extracting text using LLM model: {request.model}")
        result_text = llm_client.extract_text_from_image(
            image=image,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            prompt=request.prompt,
        )

        logger.info("LLM OCR completed successfully")

        # Hot patch to avoid llm tokens in the result
        result_text_sanitized = (
            result_text.replace("<end_of_utterance>", "")
            .replace("<start_of_utterance>", "")
            .replace("</s>", "")
            .replace("<s>", "")
            .replace("<pad>", "")
            .replace("<unk>", "")
            .replace("<eot>", "")
        )
        return result_text_sanitized

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logger.exception("Error during LLM OCR")
        raise HTTPException(status_code=500, detail=f"LLM OCR failed: {e!s}")
