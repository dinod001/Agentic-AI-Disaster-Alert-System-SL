import os
from dotenv import load_dotenv


load_dotenv()

class Config:

    """
    Central configuration class. 
    Loads secrets from .env and constants for the system.
    """
    
    # --- SECRETS (from .env) ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

    # --- CONSTANTS ---
    # Irrigation Data Source (Standard URL)
    IRRIGATION_DATA_URL = os.getenv("IRRIGATION_DATA_URL")
    ARCGIS_URL = os.getenv("ARCGIS_URL")

settings = Config()

