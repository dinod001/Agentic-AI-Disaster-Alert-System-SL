import requests
from datetime import datetime
import os
import sys
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)

sys.path.append(parent_dir)

from config import settings
from utils.logger import setup_logger

logger = setup_logger("RainfallCollector")

# OpenWeatherMap Current Weather API
OWM_URL = "https://api.openweathermap.org/data/2.5/weather"


class RainfallCollector:
    def __init__(self):
        self.api_key = settings.OPENWEATHERMAP_API_KEY
        self.flood_stations = settings.flood_stations
        self.landslide_zones = settings.landslide_zones

    def _fetch_weather(self, lat, lon):
        """Call OWM API for a single lat/lon and return raw JSON."""
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
        }
        try:
            response = requests.get(OWM_URL, params=params, timeout=15)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error("OWM request failed for lat=%.4f, lon=%.4f: %s", lat, lon, e)
            return None

    def _extract_fields(self, data):
        """Extract disaster-relevant fields from OWM response."""
        rain = data.get("rain", {})
        main = data.get("main", {})
        wind = data.get("wind", {})

        return {
            "rain_1h_mm":    rain.get("1h", 0),
            "rain_3h_mm":    rain.get("3h", 0),
            "humidity":      main.get("humidity", 0),
            "wind_speed_ms": wind.get("speed", 0),
            "wind_gust_ms":  wind.get("gust", 0),
            "temp_celsius":  main.get("temp", 0),
            "cloud_cover":   data.get("clouds", {}).get("all", 0),
            "description":   data.get("weather", [{}])[0].get("description", ""),
        }

    def _collect_stations(self, stations, station_type):
        """Fetch weather for a dict of stations and return a list of results."""
        results = []
        for name, coords in stations.items():
            lat, lon = coords["lat"], coords["lon"]
            logger.info("Fetching weather for %s [%s]", name, station_type)

            raw = self._fetch_weather(lat, lon)
            if raw is None:
                continue

            weather = self._extract_fields(raw)
            weather["station"] = name
            weather["type"] = station_type
            weather["lat"] = lat
            weather["lon"] = lon

            results.append(weather)
            logger.info("%s -> rain=%.1fmm/h, humidity=%d%%, wind=%.1fm/s",
                        name, weather["rain_1h_mm"], weather["humidity"],
                        weather["wind_speed_ms"])
        return results

    def collect_flood_data(self):
        """Fetch weather for flood stations only."""
        logger.info("Collecting weather for %d flood stations", len(self.flood_stations))
        return self._collect_stations(self.flood_stations, "flood")

    def collect_landslide_data(self):
        """Fetch weather for landslide zones only."""
        logger.info("Collecting weather for %d landslide zones", len(self.landslide_zones))
        return self._collect_stations(self.landslide_zones, "landslide")

    def collect_all(self):
        """Fetch weather for both (convenience method)."""
        flood_data = self.collect_flood_data()
        landslide_data = self.collect_landslide_data()
        logger.info("Done - %d flood + %d landslide = %d total",
                    len(flood_data), len(landslide_data),
                    len(flood_data) + len(landslide_data))
        return {"flood": flood_data, "landslide": landslide_data}


# ── Quick test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    collector = RainfallCollector()
    data = collector.collect_all()
    print(f"\nFlood stations: {len(data['flood'])}")
    print(f"Landslide zones: {len(data['landslide'])}")

