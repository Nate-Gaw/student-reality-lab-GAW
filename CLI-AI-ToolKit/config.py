"""Configuration module for loading API keys from .env file."""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from shared repository-level .env file
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(dotenv_path=env_path)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Validate keys are loaded
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in student-reality-lab-GAW/.env")

# Output directories
OUTPUT_DIR = Path(__file__).parent / "outputs"
IMAGES_DIR = OUTPUT_DIR / "images"
SCREENSHOTS_DIR = OUTPUT_DIR / "screenshots"

# Ensure output directories exist
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
