from __future__ import annotations

import base64
from pathlib import Path
from typing import Optional

from openai import OpenAI

from src.config import (
    ENABLE_IMAGE_GENERATION,
    IMAGE_DIR,
    IMAGE_SIZE,
    OPENAI_API_KEY,
    OPENAI_IMAGE_MODEL,
)
from src.utils.logging_utils import get_logger

logger = get_logger(__name__)


class ImageService:
    def __init__(self) -> None:
        self.enabled = ENABLE_IMAGE_GENERATION
        self.client = OpenAI(api_key=OPENAI_API_KEY) if self.enabled else None

    def generate_image(self, prompt: str, filename_stem: str, size: str | None = None) -> Optional[str]:
        if not self.enabled:
            logger.info("Image generation disabled. Skipping image for %s", filename_stem)
            return None

        chosen_size = size or IMAGE_SIZE

        logger.info("Generating image for %s with size=%s", filename_stem, chosen_size)

        output_dir = Path(IMAGE_DIR)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{filename_stem}.png"

        try:
            response = self.client.images.generate(
                model=OPENAI_IMAGE_MODEL,
                prompt=prompt,
                size=chosen_size,
            )

            data_item = response.data[0]

            if getattr(data_item, "b64_json", None):
                output_path.write_bytes(base64.b64decode(data_item.b64_json))
                logger.info("Image saved to %s", output_path)
                return str(output_path)

            if getattr(data_item, "url", None):
                logger.warning("Image API returned URL instead of base64 for %s", filename_stem)
                return data_item.url

            logger.warning("Image API returned no usable image data for %s", filename_stem)
            return None

        except Exception:
            logger.exception("Image generation failed for %s", filename_stem)
            return None