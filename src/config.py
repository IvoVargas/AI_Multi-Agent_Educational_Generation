from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs/presentations")
IMAGE_DIR = os.getenv("IMAGE_DIR", "outputs/images")

ENABLE_IMAGE_GENERATION = os.getenv("ENABLE_IMAGE_GENERATION", "false").lower() == "true"
OPENAI_IMAGE_MODEL = os.getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1024")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")