import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

from engine.flood_engine import FloodEngine
from engine.landslide_engine import LandslideEngine
from utils.logger import setup_logger
from utils.alert_state import has_changed
from agents.llm import generate_llm_response

logger = setup_logger("MonitorAgent")

class MonitorAgent:
    def __init__(self):
        self.flood_engine = FloodEngine()
        self.landslide_engine = LandslideEngine()

    def monitor_disasters(self):
        """
        Monitor both flood and landslide conditions and return warnings.
        """
        flood_warnings = self.flood_engine.custom_logic_for_flood_engine()
        landslide_warnings = self.landslide_engine.custom_logic_for_landslide()

        return flood_warnings, landslide_warnings

    def generate_report(self):
        """
        Run a monitoring cycle. Generates and returns an LLM alert only if
        the warning zones have changed since the last sent alert.
        Returns None if nothing has changed (no alert to send).
        """
        flood_warnings, landslide_warnings = self.monitor_disasters()

        # Check if anything changed vs the last saved state
        if not has_changed(flood_warnings, landslide_warnings):
            logger.info("Alert suppressed — no change since last cycle")
            return None

        logger.info("State changed — generating new alert")
        alert = generate_llm_response(flood_warnings, landslide_warnings)
        return alert


# ── Quick test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    agent = MonitorAgent()
    alert = agent.generate_report()
    print(f"\n=== Monitor Agent Test ===")
    if alert:
        print(alert)
    else:
        print("No change detected — alert suppressed.")