import os
import sys
import requests

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from config import settings
from utils.logger import setup_logger

logger = setup_logger("TelegramBot")

TELEGRAM_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def send_alert(message: str) -> bool:
    """
    Send a text message to the configured Telegram chat.

    Args:
        message: The alert text to send (supports Markdown).

    Returns:
        True if sent successfully, False otherwise.
    """
    token = settings.TELEGRAM_TOKEN
    chat_id = settings.TELEGRAM_CHAT_ID

    if not token or not chat_id:
        logger.error("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set in .env")
        return False

    url = TELEGRAM_API_URL.format(token=token)

    # Telegram has a 4096 character limit per message — split if needed
    chunks = _split_message(message, limit=4096)

    success = True
    for i, chunk in enumerate(chunks):
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "parse_mode": "Markdown",
        }
        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            logger.info("Telegram message sent (part %d/%d)", i + 1, len(chunks))
        except requests.RequestException as e:
            logger.error("Failed to send Telegram message (part %d): %s", i + 1, e)
            success = False

    return success


def _split_message(text: str, limit: int = 4096) -> list:
    """Split long messages into chunks that fit Telegram's limit."""
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        chunks.append(text[:limit])
        text = text[limit:]
    return chunks


# ── Quick test ───────────────────────────────────────────────────────
if __name__ == "__main__":
    test_message = (
        "*Test Alert - Disaster Alert System*\n\n"
        "This is a test message from the Sri Lanka Disaster Alert System.\n"
        "If you see this, Telegram integration is working correctly! ✅"
    )
    ok = send_alert(test_message)
    print("Sent successfully!" if ok else "Send failed — check logs above.")
