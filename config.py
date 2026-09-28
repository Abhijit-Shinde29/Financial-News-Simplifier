"""
Configuration module for Financial News Simplifier.
Loads settings from environment variables and sets up project paths.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for the project (folder containing config.py)
BASE_DIR = Path(__file__).resolve().parent

# Ensure the data directory exists
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Load environment variables from .env file
ENV_PATH = BASE_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()  # Fallback to system env or root .env

# Application Branding
APP_TITLE = "Financial News Simplifier"
APP_TAGLINE = "Complex financial news. Made simple."
APP_SUBTITLE = "Understand complex financial news in simple language."

# AI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
DEFAULT_MODEL = "gpt-4o-mini"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL

# Database Configuration
DEFAULT_DB_FILE = DATA_DIR / "news_history.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_FILE.as_posix()}").strip()

# Parsing & Scraping Configuration
REQUEST_TIMEOUT = 15  # seconds
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (FinancialNewsSimplifier/1.0)"
)
MIN_ARTICLE_CHARS = int(os.getenv("MIN_ARTICLE_CHARS", "60"))
MAX_ARTICLE_CHARS = int(os.getenv("MAX_ARTICLE_CHARS", "25000"))

def is_api_key_configured() -> bool:
    """Check if OpenAI API key is properly set and not a placeholder."""
    if not OPENAI_API_KEY:
        return False
    placeholders = ["your_api_key_here", "your_openai_api_key_here", "sk-placeholder", "none", "null"]
    if OPENAI_API_KEY.lower() in placeholders or OPENAI_API_KEY.startswith("your_"):
        return False
    return len(OPENAI_API_KEY) > 10
