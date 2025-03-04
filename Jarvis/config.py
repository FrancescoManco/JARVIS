from pathlib import Path
import os
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file if it exists
load_dotenv()

# Paths
PROJ_ROOT = Path(__file__).resolve().parents[1]
logger.info(f"PROJ_ROOT path is: {PROJ_ROOT}")

DATA_DIR = PROJ_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
INTERIM_DATA_DIR = DATA_DIR / "interim"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"

MODELS_DIR = PROJ_ROOT / "models"

REPORTS_DIR = PROJ_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
GROQ_KEY = os.getenv("GROQ_KEY")
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME")
CREDENTIAL_FILE_PATH = os.getenv("CREDENTIAL_FILE_PATH")
TOKEN_FILE_PATH = os.getenv("TOKEN_FILE_PATH")

