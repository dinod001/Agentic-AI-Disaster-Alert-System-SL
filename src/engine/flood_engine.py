import requests
from datetime import datetime
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

from collectors.irrigation_api import IrrigationCollector
from collectors.weather_api import RainfallCollector
from utils.logger import setup_logger

logger = setup_logger("FloodEngine")


class FloodEngine:
    def __init__(self):
        self.irrigation_collector = IrrigationCollector()
        self.rainfall_collector = RainfallCollector()

    def custom_logic_for_flood_engine(self):
        """
        Merge irrigation water-level data with rainfall data to identify flood warning zones.
        Risk is scored from water level ratio, rate of rise, and current rainfall.
        """
        warning_zones = []

        # 1. Fetch data from both collectors
        irrigation_data = self.irrigation_collector.fetch_irrigation_data()
        rainfall_flood_data = self.rainfall_collector.collect_flood_data()

        # 2. Index rainfall by station name for fast lookup
        rainfall_map = {r["station"]: r for r in rainfall_flood_data}

        # 3. Evaluate each irrigation station
        for station in irrigation_data:
            name = station["station"]
            level = station["level_m"]
            rate = station["rate_of_rise"]
            alert_level = station.get("alert_level")
            minor_level = station.get("minor_level")
            major_level = station.get("major_level")

            # Skip stations without threshold data
            if not alert_level or alert_level == 0:
                logger.debug("Skipping %s - no alert thresholds", name)
                continue

            # --- Risk Score Calculation (0 - 100) ---
            risk_score = 0

            # Factor 1: Water level ratio vs alert level (0 - 40 points)
            level_ratio = level / alert_level if alert_level else 0
            if major_level and level >= major_level:
                risk_score += 40
            elif minor_level and level >= minor_level:
                risk_score += 30
            elif level >= alert_level:
                risk_score += 20
            elif level_ratio >= 0.8:
                risk_score += 10

            # Factor 2: Rate of rise (0 - 30 points)
            if rate is not None:
                if rate >= 0.5:
                    risk_score += 30     # Rapid rise
                elif rate >= 0.2:
                    risk_score += 20     # Moderate rise
                elif rate >= 0.1:
                    risk_score += 10     # Slow rise
                elif rate < 0:
                    risk_score -= 5      # Water is receding

            # Factor 3: Current rainfall (0 - 30 points)
            weather = rainfall_map.get(name, {})
            rain_1h = weather.get("rain_1h_mm", 0)
            rain_3h = weather.get("rain_3h_mm", 0)

            if rain_1h >= 50:
                risk_score += 30         # Extreme rainfall
            elif rain_1h >= 20:
                risk_score += 20         # Heavy rainfall
            elif rain_1h >= 7:
                risk_score += 10         # Moderate rainfall
            elif rain_3h >= 15:
                risk_score += 10         # Sustained rain over 3h

            # Clamp score to 0-100
            risk_score = max(0, min(100, risk_score))

            # --- Classify risk level ---
            if risk_score >= 70:
                risk_level = "CRITICAL"
            elif risk_score >= 45:
                risk_level = "WARNING"
            elif risk_score >= 20:
                risk_level = "WATCH"
            else:
                risk_level = "NORMAL"

            # Only append if there is some risk
            if risk_level != "NORMAL":
                zone = {
                    "station":      name,
                    "river_basin":  station["river_basin"],
                    "level_m":      level,
                    "alert_level":  alert_level,
                    "minor_level":  minor_level,
                    "major_level":  major_level,
                    "rate_of_rise": rate,
                    "rain_1h_mm":   rain_1h,
                    "rain_3h_mm":   rain_3h,
                    "risk_score":   risk_score,
                    "risk_level":   risk_level,
                    "measured_at":  station["measured_at"],
                }
                warning_zones.append(zone)
                logger.warning("FLOOD %s: %s - score=%d, level=%.2fm, rate=%s, rain_1h=%.1fmm",
                               risk_level, name, risk_score, level, rate, rain_1h)

        # Sort by risk score descending (most dangerous first)
        warning_zones.sort(key=lambda x: x["risk_score"], reverse=True)
        logger.info("Flood analysis complete: %d warning zones out of %d stations",
                    len(warning_zones), len(irrigation_data))

        return warning_zones
        
# ── Quick test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = FloodEngine()
    zones = engine.custom_logic_for_flood_engine()
    print(f"\n=== {len(zones)} Warning Zones ===")
    for z in zones:
        print(f"  [{z['risk_level']}] {z['station']} "
              f"(score={z['risk_score']}, level={z['level_m']}m, rain={z['rain_1h_mm']}mm/h)")