"""Configuration module for loading API keys from .env file."""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate keys are loaded
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in .env file")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")

# Output directories
OUTPUT_DIR = Path(__file__).parent / "outputs"
IMAGES_DIR = OUTPUT_DIR / "images"
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"

# Ensure output directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
