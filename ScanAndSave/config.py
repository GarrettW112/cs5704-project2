import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("VT_ARC_API_KEY")

if not API_KEY:
    raise ValueError("VT_ARC_API_KEY not found in .env")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://llm-api.arc.vt.edu/api/v1/"
)

# Your standard fast text model for Classification, Normalization, etc.
MODEL_NAME = "gpt-oss-120b"

# Your multimodal model specifically for Receipt Extraction
VISION_MODEL_NAME = "Kimi-K2.5"