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
        }
        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            logger.info("Telegram message sent (part %d/%d)", i + 1, len(chunks))
        except requests.RequestException as e:
            logger.error("Failed to send Telegram message (part %d): %s", i + 1, e)
            success = False

    return success


def _split_message(text: str, limit: int = 4000) -> list:
    """
    Split long messages into readable chunks.
    Tries to break at: newline → sentence (.) → word (space) → hard cut.
    Uses 4000 instead of 4096 for safety margin.
    """
    if len(text) <= limit:
        return [text]

    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break

        # Priority 1: Split at last newline
        split_at = text.rfind("\n", 0, limit)

        # Priority 2: Split at last sentence (period + space)
        if split_at == -1 or split_at < limit // 2:
            better = text.rfind(". ", 0, limit)
            if better != -1 and better > split_at:
                split_at = better + 1  # include the period

        # Priority 3: Split at last space (word boundary)
        if split_at == -1 or split_at < limit // 2:
            better = text.rfind(" ", 0, limit)
            if better != -1 and better > split_at:
                split_at = better

        # Priority 4: Hard cut (should never happen with normal text)
        if split_at == -1:
            split_at = limit

        chunks.append(text[:split_at].rstrip())
        text = text[split_at:].lstrip()

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
