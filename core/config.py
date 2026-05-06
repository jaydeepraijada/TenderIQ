import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY: str | None = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"
MODEL_VERSION = f"{MODEL_NAME}@2026-05-07"

CONFIDENCE_HIGH = 0.80
CONFIDENCE_REVIEW = 0.55
OCR_TESSERACT_MIN_CONF = 0.65

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = str(BASE_DIR / ".chroma")
AUDIT_DB = str(BASE_DIR / "audit.db")
PRECOMPUTED_DIR = DATA_DIR / "precomputed"
OCR_CACHE_DIR = BASE_DIR / ".ocr_cache"
