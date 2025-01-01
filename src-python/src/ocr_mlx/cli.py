#!/usr/bin/env python3

import argparse
import logging
import time
from pathlib import Path
from typing import cast

import mlx.core as mx
from transformers.models.nougat.processing_nougat import NougatProcessor

from ocr_mlx.inference.generate import generate
from ocr_mlx.model.nougat import Nougat
from ocr_mlx.utils import load_image

logger = logging.getLogger(__name__)


def main() -> str:
    parser = argparse.ArgumentParser(description="OCR tool using Nougat model")
    parser.add_argument(
        "--model", default="facebook/nougat-small", help="Model name or path"
    )
    parser.add_argument(
        "--input", required=True, help="Input image or PDF file path or URL"
    )
    parser.add_argument("--output", help="Output file path to save results")
    parser.add_argument(
        "--temperature", type=float, default=0.0, help="Sampling temperature"
    )
    parser.add_argument(
        "--top_p", type=float, default=0.0, help="Top-p sampling threshold"
    )
    parser.add_argument(
        "--repetition_penalty", type=float, default=None, help="Repetition penalty"
    )
    args = parser.parse_args()

    logger.info(f"Loading model: {args.model}")  # noqa: G004
    nougat_processor = NougatProcessor.from_pretrained(args.model)
    nougat_processor = cast(NougatProcessor, nougat_processor)
    model = Nougat.from_pretrained(args.model)

    images = [load_image(args.input)]

    results = []
    start_time = time.time()

    for i, img in enumerate(images):
        logger.info(f"Processing page {i + 1}/{len(images)}")  # noqa: G004
        pixel_values = mx.array(
            nougat_processor(img, return_tensors="np").pixel_values
        ).transpose(0, 2, 3, 1)
        outputs = generate(
            model,
            pixel_values,
            max_new_tokens=4096,
            eos_token_id=nougat_processor.tokenizer.eos_token_id,  # type: ignore
            temperature=args.temperature,
            top_p=args.top_p,
            repetition_penalty=args.repetition_penalty,
        )
        results.append(nougat_processor.tokenizer.decode(outputs))  # type: ignore

    end_time = time.time()
    elapsed_time = end_time - start_time

    output_text = "\n\n".join(results)
    logger.info(output_text)
    logger.info(f"\nGeneration time: {elapsed_time:.2f} seconds")  # noqa: G004

    if args.output:
        Path(args.output).write_text(output_text, encoding="utf-8")
        logger.info(f"Results saved to {args.output}")  # noqa: G004

    return output_text


if __name__ == "__main__":
    main()
