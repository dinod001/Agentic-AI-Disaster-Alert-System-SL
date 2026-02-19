"""
Alert State Manager — tracks the last sent warning zones in a JSON file.
Prevents duplicate hourly alerts when nothing has changed.

State file: data/alert_state.json
Valid for: current calendar day only (auto-wiped at midnight)
"""
import os
import sys
import json
from datetime import date

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from utils.logger import setup_logger

logger = setup_logger("AlertState")

# State file lives in data/ at the project root
STATE_FILE = os.path.join(parent_dir, "..", "data", "alert_state.json")


def _load_state() -> dict:
    """Load state from JSON. Returns empty state if file missing or outdated."""
    if not os.path.exists(STATE_FILE):
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            state = json.load(f)

        # Wipe if it's from a previous day
        stored_date = state.get("date")
        if stored_date != str(date.today()):
            logger.info("New day detected — clearing previous alert state (%s)", stored_date)
            return {}

        return state

    except (json.JSONDecodeError, OSError) as e:
        logger.warning("Failed to read alert state file: %s — starting fresh", e)
        return {}


def _save_state(flood_zones: list, landslide_zones: list):
    """Persist current warning zones to JSON."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

    state = {
        "date": str(date.today()),
        "flood": [
            {"station": z["station"], "risk_level": z["risk_level"]}
            for z in flood_zones
        ],
        "landslide": [
            {"station": z["station"], "risk_level": z["risk_level"]}
            for z in landslide_zones
        ],
    }

    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

    logger.info("Alert state saved — %d flood, %d landslide zones",
                len(flood_zones), len(landslide_zones))


def _to_signature(zones: list) -> set:
    """Convert a list of warning zones to a comparable set of (station, risk_level) tuples."""
    return {(z["station"], z["risk_level"]) for z in zones}


def has_changed(flood_zones: list, landslide_zones: list) -> bool:
    """
    Compare current warning zones against the last saved state.
    Returns True if anything changed (new zone, removed zone, or risk level upgrade/downgrade).
    Also saves the new state if changed.
    """
    state = _load_state()

    prev_flood = state.get("flood", [])
    prev_landslide = state.get("landslide", [])

    current_flood_sig = _to_signature(flood_zones)
    prev_flood_sig = _to_signature(prev_flood)

    current_landslide_sig = _to_signature(landslide_zones)
    prev_landslide_sig = _to_signature(prev_landslide)

    flood_changed = current_flood_sig != prev_flood_sig
    landslide_changed = current_landslide_sig != prev_landslide_sig

    if flood_changed:
        added = current_flood_sig - prev_flood_sig
        removed = prev_flood_sig - current_flood_sig
        if added:
            logger.info("Flood state CHANGED — new/updated: %s", added)
        if removed:
            logger.info("Flood state CHANGED — cleared: %s", removed)

    if landslide_changed:
        added = current_landslide_sig - prev_landslide_sig
        removed = prev_landslide_sig - current_landslide_sig
        if added:
            logger.info("Landslide state CHANGED — new/updated: %s", added)
        if removed:
            logger.info("Landslide state CHANGED — cleared: %s", removed)

    changed = flood_changed or landslide_changed

    if changed:
        _save_state(flood_zones, landslide_zones)
    else:
        logger.info("No alert state change — skipping Telegram send")

    return changed
