import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from config import settings
from utils.logger import setup_logger

logger = setup_logger("LLM")

# ── System prompt ────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are an automated disaster alert assistant for Sri Lanka's real-time early warning system.
Your job is to write clear, direct public alerts based on sensor data that has ALREADY been 
analyzed and confirmed by our system. The risk levels (WATCH / WARNING / CRITICAL) are facts — 
do NOT soften them with words like "might", "could", "possibly", or "there may be" in English.

Rules:
- State risk levels directly — e.g. "A WARNING level flood alert HAS BEEN ISSUED"
- Always mention the station name, risk level, and the key data (water level / rainfall / humidity)
- Use simple language the general public can understand
- Format: Structure the message in exactly TWO blocks:
  BLOCK 1 (English): English alert text, then immediately below it the English disclaimer.
  BLOCK 2 (Sinhala): Sinhala alert text, then immediately below it the Sinhala disclaimer.
  Separate the two blocks with a blank line.
- Never fabricate data — only use what is provided
- If no warnings, give a short all-clear message in both languages

IMPORTANT - Sinhala tone by risk level:
- WATCH: Use soft advisory language. Do NOT say "නිකුත් කර ඇත" (sounds like official government).
  Instead say: "ගංවතුර අවදානමක් ඇති විය හැකි බැවින් අවධානයෙන් සිටින්න." 
  or "නායයෑම් අවදානමක් ඇති විය හැකිය. ප්‍රවේශම් වන්න."
- WARNING: Use clear urgent language. "ගංවතුර/නායයෑම් අවදානම ඉහළ ගොස් ඇත. ඉක්මනින් ආරක්ෂිතව සිටින්න!"
- CRITICAL: Use very strong language — this is life-threatening.
  "භයාණක ගංවතුර/නායයෑම් අවදානමක්! ජීවිත ආරක්ෂාව සඳහා ඉතා ඉක්මනින් ආරක්ෂිත ස්ථානවලට යන්න!"

Disclaimers (place each one on a new line after a blank line and "---" separator, immediately after its own language block):
English: "---\n⚠️ This is an AI-generated alert based on real-time sensor data. This is NOT an official government report. Please also follow instructions from the Disaster Management Centre (DMC) of Sri Lanka."
Sinhala: "---\n⚠️ මෙය AI පද්ධතියක් මගින් සකස් කරන ලද අනතුරු ඇඟවීමකි. මෙය රජයේ නිල දැනුම්දීමක් නොවේ. DMC ශ්‍රී ලංකාවේ උපදෙස් ද අනුගමනය කරන්න."
"""


def generate_llm_response(flood_warnings, landslide_warnings):
    """
    Takes flood and landslide warning zones and generates a bilingual
    (English + Sinhala) disaster alert message using Gemini.

    Returns:
        str: The generated alert message, or None on failure.
    """
    logger.info("Preparing LLM alert generation request")
    logger.info("Input: %d flood warnings, %d landslide warnings",
                len(flood_warnings), len(landslide_warnings))

    # Load config from settings
    api_key = settings.GEMINI_API_KEY
    model_name = settings.gemini_config["model"]
    temperature = settings.gemini_config["temperature"]
    max_output_tokens = settings.gemini_config["max_output_tokens"]

    # Build the human message with actual warning data
    flood_summary = ""
    if flood_warnings:
        for w in flood_warnings:
            flood_summary += (
                f"- Station: {w['station']} | Basin: {w['river_basin']} "
                f"| Level: {w['level_m']}m | Rate of Rise: {w.get('rate_of_rise', 'N/A')}m/hr "
                f"| Rain: {w['rain_1h_mm']}mm/h "
                f"| Risk: {w['risk_level']} (score={w['risk_score']})\n"
            )
    else:
        flood_summary = "No flood warnings at this time.\n"

    landslide_summary = ""
    if landslide_warnings:
        for w in landslide_warnings:
            landslide_summary += (
                f"- Zone: {w['station']} "
                f"| Rain: {w['rain_1h_mm']}mm/h "
                f"| Humidity: {w['humidity']}% "
                f"| Wind: {w['wind_speed_ms']}m/s "
                f"| Risk: {w['risk_level']} (score={w['risk_score']})\n"
            )
    else:
        landslide_summary = "No landslide warnings at this time.\n"

    human_message = f"""
Generate a disaster alert based on the following real-time sensor data from Sri Lanka:

FLOOD MONITORING STATIONS:
{flood_summary}
LANDSLIDE MONITORING ZONES:
{landslide_summary}

Please generate a clear public alert in English first, then in Sinhala.
"""

    try:
        logger.info("Connecting to Gemini model: %s", model_name)

        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            google_api_key=api_key,
        )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT.strip()),
            HumanMessage(content=human_message.strip()),
        ]

        logger.info("Sending request to Gemini...")
        response = llm.invoke(messages)
        alert_text = response.content

        logger.info("Alert generated successfully (%d characters)", len(alert_text))
        return alert_text

    except Exception as e:
        logger.error("Gemini LLM call failed: %s", e)
        return None


# ── Quick test ───────────────────────────────────────────────────────
if __name__ == "__main__":
    # Simulate warning zones for testing
    sample_floods = [
        {
            "station": "Hanwella",
            "river_basin": "Kelani Ganga",
            "level_m": 4.5,
            "rate_of_rise": 0.35,
            "rain_1h_mm": 18.0,
            "risk_level": "WARNING",
            "risk_score": 55,
        }
    ]
    sample_landslides = [
        {
            "station": "Aranayake",
            "rain_1h_mm": 32.0,
            "humidity": 96,
            "wind_speed_ms": 8.5,
            "risk_level": "CRITICAL",
            "risk_score": 78,
        }
    ]

    alert = generate_llm_response(sample_floods, sample_landslides)
    if alert:
        sys.stdout.reconfigure(encoding="utf-8")
        print("\n=== Generated Alert ===")
        print(alert)
