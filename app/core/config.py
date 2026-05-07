import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Project root (two levels up from app/core/)
BASE_DIR = Path(__file__).resolve().parents[2]

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886")
LINKUP_API_KEY = os.getenv("LINKUP_API_KEY")

DATASET_PATH = str(BASE_DIR / "data" / "schemes.csv")
FAISS_INDEX_PATH = str(BASE_DIR / "vector_store" / "scheme_faiss_index")
EMBEDDING_MODEL = "text-embedding-3-large"
LLM_MODEL = "gpt-4o-mini"

TWILIO_MAX_BODY_LEN = 1600
