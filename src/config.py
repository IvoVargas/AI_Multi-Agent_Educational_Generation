import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "outputs/presentations")
IMAGE_DIR = os.getenv("IMAGE_DIR", "outputs/images")