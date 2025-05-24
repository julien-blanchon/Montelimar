import base64
import io
import logging

import requests
from PIL import Image as PILImage

logger = logging.getLogger(__name__)


def load_image(filename: str) -> PILImage.Image:
    """
    Load an image from various sources (file path, URL, or base64 data).

    Args:
        filename: Image source - can be a file path, URL, or base64 data URI

    Returns:
        PIL Image object

    Raises:
        ValueError: If the image source format is not supported

    """
    if filename.startswith("file://"):
        return PILImage.open(filename[7:])
    if filename.startswith(("http://", "https://")):
        response = requests.get(filename, timeout=10)
        response.raise_for_status()
        return PILImage.open(io.BytesIO(response.content))
    if filename.startswith("data:"):
        header = "data:image/png;base64,"
        base64_str = filename[len(header) :].replace("\n", "")
        image_data = base64.b64decode(base64_str)
        return PILImage.open(io.BytesIO(image_data))
    msg = f"Unsupported image source: {filename}"
    logger.error(msg)
    raise ValueError(msg)
