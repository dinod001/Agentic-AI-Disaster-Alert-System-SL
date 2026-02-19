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

logger = setup_logger("IrrigationCollector")

class IrrigationCollector:
    def __init__(self):
        self.github_url = settings.IRRIGATION_DATA_URL
        self.arcgis_url = settings.ARCGIS_URL

    def fetch_arcgis_metadata(self):
        logger.info("Fetching ArcGIS metadata from: %s", self.arcgis_url)
        params = {
            "where":             "1=1",
            "outFields":         "basin,gauge,alertpull,minorpull,majorpull",
            "returnDistinctValues": "true",
            "resultRecordCount": 1000,
            "f":                 "json"
        }
        try:
            response = requests.get(self.arcgis_url, params=params, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error("Failed to fetch ArcGIS metadata: %s", e)
            raise

        features = response.json().get("features", [])
        logger.info("Received %d features from ArcGIS", len(features))

        metadata = {}
        for feature in features:
            a = feature["attributes"]
            metadata[a["gauge"]] = {
                "river_basin": a["basin"],
                "alert_level": a["alertpull"],
                "minor_level": a["minorpull"],
                "major_level": a["majorpull"],
            }
        return metadata

    def parse_datetime(self,date_str, time_str):
        try:
            return datetime.strptime(date_str + time_str[:6], "%Y%m%d%H%M%S")
        except ValueError:
            return None

    def fetch_irrigation_data(self):
        logger.info("Fetching irrigation data from GitHub: %s", self.github_url)
        try:
            github_raw = requests.get(self.github_url, timeout=15).json()
        except requests.RequestException as e:
            logger.error("Failed to fetch GitHub data: %s", e)
            raise

        arcgis_meta = self.fetch_arcgis_metadata()

        results = []

        for station, dates in github_raw["event_data"].items():
            readings = []
            for date_str, times in dates.items():
                for time_str, level in times.items():
                    dt = self.parse_datetime(date_str, time_str)
                    if dt is not None:
                        readings.append((dt, float(level)))

            if not readings:
                logger.debug("No valid readings for station: %s, skipping", station)
                continue

            readings.sort(key=lambda x: x[0])
            latest_dt, latest_level = readings[-1]

            # Rate of rise (m/hr)
            rate = None
            if len(readings) >= 2:
                prev_dt, prev_level = readings[-2]
                hours = (latest_dt - prev_dt).total_seconds() / 3600.0
                if hours > 0:
                    rate = round((latest_level - prev_level) / hours, 3)

            # Merge with ArcGIS metadata
            meta = arcgis_meta.get(station, {})

            results.append({
                "measured_at":  latest_dt.strftime("%Y-%m-%d %H:%M:%S"),
                "station":      station,
                "river_basin":  meta.get("river_basin", "Unknown"),
                "level_m":      round(latest_level, 2),
                "rate_of_rise": rate,
                "alert_level":  meta.get("alert_level"),
                "minor_level":  meta.get("minor_level"),
                "major_level":  meta.get("major_level"),
            })

        results.sort(key=lambda x: x["measured_at"], reverse=True)
        logger.info("Successfully processed %d stations", len(results))
        return results


if __name__ == "__main__":
    collector = IrrigationCollector()
    data = collector.fetch_irrigation_data()
    logger.info("Total stations fetched: %d", len(data))
    for station in data:
        logger.info("Station: %s | Level: %s m | Basin: %s", 
                     station['station'], station['level_m'], station['river_basin'])