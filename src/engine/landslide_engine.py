import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

from collectors.weather_api import RainfallCollector
from utils.logger import setup_logger

logger = setup_logger("LandslideEngine")


class LandslideEngine:
    def __init__(self):
        self.rainfall_collector = RainfallCollector()

    def custom_logic_for_landslide(self):
        """
        Analyse weather data for landslide-prone zones and identify warning areas.
        Risk is scored from rainfall intensity, humidity (soil saturation), and wind.
        """
        warning_zones = []

        # 1. Fetch weather for all landslide zones
        landslide_data = self.rainfall_collector.collect_landslide_data()

        # 2. Evaluate each zone
        for zone in landslide_data:
            name = zone["station"]
            rain_1h = zone.get("rain_1h_mm", 0)
            rain_3h = zone.get("rain_3h_mm", 0)
            humidity = zone.get("humidity", 0)
            wind_speed = zone.get("wind_speed_ms", 0)
            wind_gust = zone.get("wind_gust_ms", 0)
            cloud_cover = zone.get("cloud_cover", 0)

            # --- Risk Score Calculation (0 - 100) ---
            risk_score = 0

            # Factor 1: Rainfall intensity (0 - 40 points)
            # Rainfall is the NUMBER ONE trigger for landslides
            if rain_1h >= 50:
                risk_score += 40         # Extreme - very high landslide risk
            elif rain_1h >= 30:
                risk_score += 30         # Heavy
            elif rain_1h >= 15:
                risk_score += 20         # Moderate-heavy
            elif rain_1h >= 5:
                risk_score += 10         # Light-moderate

            # Bonus for sustained rain over 3h (saturates soil)
            if rain_3h >= 40:
                risk_score += 10
            elif rain_3h >= 20:
                risk_score += 5

            # Factor 2: Humidity / soil saturation (0 - 25 points)
            # High humidity = soil already holds moisture = easier to slide
            if humidity >= 95:
                risk_score += 25
            elif humidity >= 85:
                risk_score += 15
            elif humidity >= 75:
                risk_score += 10
            elif humidity >= 60:
                risk_score += 5

            # Factor 3: Wind (0 - 15 points)
            # Strong wind destabilizes slopes, uproots trees on hillsides
            gust = max(wind_speed, wind_gust)
            if gust >= 20:
                risk_score += 15         # Storm-force
            elif gust >= 12:
                risk_score += 10         # Strong wind
            elif gust >= 7:
                risk_score += 5          # Moderate wind

            # Factor 4: Cloud cover as storm indicator (0 - 10 points)
            if cloud_cover >= 90 and rain_1h >= 5:
                risk_score += 10         # Overcast + raining = sustained threat
            elif cloud_cover >= 80:
                risk_score += 5

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
                warning_zones.append({
                    "station":       name,
                    "rain_1h_mm":    rain_1h,
                    "rain_3h_mm":    rain_3h,
                    "humidity":      humidity,
                    "wind_speed_ms": wind_speed,
                    "wind_gust_ms":  wind_gust,
                    "cloud_cover":   cloud_cover,
                    "risk_score":    risk_score,
                    "risk_level":    risk_level,
                    "lat":           zone["lat"],
                    "lon":           zone["lon"],
                })
                logger.warning("LANDSLIDE %s: %s - score=%d, rain=%.1fmm/h, humidity=%d%%, wind=%.1fm/s",
                               risk_level, name, risk_score, rain_1h, humidity, gust)

        # Sort by risk score descending (most dangerous first)
        warning_zones.sort(key=lambda x: x["risk_score"], reverse=True)
        logger.info("Landslide analysis complete: %d warning zones out of %d monitored areas",
                    len(warning_zones), len(landslide_data))

        return warning_zones


# ── Quick test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = LandslideEngine()
    zones = engine.custom_logic_for_landslide()
    print(f"\n=== {len(zones)} Landslide Warning Zones ===")
    for z in zones:
        print(f"  [{z['risk_level']}] {z['station']} "
              f"(score={z['risk_score']}, rain={z['rain_1h_mm']}mm/h, "
              f"humidity={z['humidity']}%, wind={z['wind_speed_ms']}m/s)")
