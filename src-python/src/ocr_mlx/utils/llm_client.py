import base64
import io
import logging

import requests
from PIL import Image as PILImage

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for making LLM API calls for OCR tasks."""

    def __init__(
        self,
        api_key: str,
        endpoint_url: str = "https://api.openai.com/v1/chat/completions",
    ):
        self.api_key = api_key
        self.endpoint_url = endpoint_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def image_to_base64(self, image: PILImage.Image) -> str:
        """Convert PIL Image to base64 string."""
        # Convert image to RGB if it's not already
        if image.mode != "RGB":
            image = image.convert("RGB")

        # Save image to bytes
        img_buffer = io.BytesIO()
        image.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # Encode to base64
        base64_image = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
        return base64_image

    def extract_text_from_image(
        self,
        image: PILImage.Image,
        model: str = "gpt-4.1-mini",
        max_tokens: int = 1000,
        temperature: float = 0.0,
        prompt: str = """You are an OCR model.
I will give you an image of a document, sign, or printed text.
Your task is to extract the visible text exactly as it appears in the image.
- Preserve line breaks and formatting where possible.
- Do not add or remove any words.
- Output text only — no explanations, no commentary.
Here is the image:
""",
    ) -> str:
        """
        Extract text from image using LLM vision capabilities.

        Args:
            image: PIL Image object
            model: Model name to use
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature
            prompt: Custom prompt for text extraction

        Returns:
            Extracted text as string

        Raises:
            Exception: If API call fails

        """
        try:
            # Convert image to base64
            base64_image = self.image_to_base64(image)

            # Prepare the API request payload
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                },
                            },
                        ],
                    }
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            }

            # Send the request
            logger.info(
                f"Making LLM API request to {self.endpoint_url} with model {model}"
            )
            response = requests.post(
                self.endpoint_url,
                headers=self.headers,
                json=payload,
                timeout=60,  # 60 second timeout
            )

            # Check if request was successful
            response.raise_for_status()

            # Parse response
            response_data = response.json()

            if "choices" not in response_data or len(response_data["choices"]) == 0:
                raise ValueError("No choices returned from LLM API")

            # Extract the text content
            content = response_data["choices"][0]["message"]["content"]

            logger.info("Successfully extracted text using LLM")
            return content

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error during LLM API call: {e}")
            raise Exception(f"LLM API request failed: {e}")
        except KeyError as e:
            logger.error(f"Unexpected response format from LLM API: {e}")
            raise Exception(f"Invalid response format from LLM API: {e}")
        except Exception as e:
            logger.error(f"Error during LLM text extraction: {e}")
            raise Exception(f"LLM text extraction failed: {e}")
