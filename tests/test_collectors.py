"""
Quick smoke tests for the data collectors.
Run:  python tests/test_collectors.py
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from collectors.irrigation_api import IrrigationCollector
from collectors.weather_api import RainfallCollector


def test_irrigation_collector():
    print("=" * 60)
    print("TEST: IrrigationCollector.fetch_irrigation_data()")
    print("=" * 60)

    collector = IrrigationCollector()
    data = collector.fetch_irrigation_data()

    assert isinstance(data, list), "Expected a list"
    assert len(data) > 0, "Expected at least 1 station"

    # Check structure of first record
    sample = data[0]
    required_keys = ["station", "river_basin", "level_m", "rate_of_rise",
                     "alert_level", "minor_level", "major_level", "measured_at"]
    for key in required_keys:
        assert key in sample, f"Missing key: {key}"

    print(f"  PASSED - {len(data)} stations fetched")
    print(f"  Sample: {sample['station']} | level={sample['level_m']}m | basin={sample['river_basin']}")
    print()


def test_rainfall_collector_flood():
    print("=" * 60)
    print("TEST: RainfallCollector.collect_flood_data()")
    print("=" * 60)

    collector = RainfallCollector()
    data = collector.collect_flood_data()

    assert isinstance(data, list), "Expected a list"
    assert len(data) > 0, "Expected at least 1 station"

    sample = data[0]
    required_keys = ["station", "rain_1h_mm", "humidity", "wind_speed_ms", "lat", "lon"]
    for key in required_keys:
        assert key in sample, f"Missing key: {key}"

    print(f"  PASSED - {len(data)} flood stations fetched")
    print(f"  Sample: {sample['station']} | rain={sample['rain_1h_mm']}mm/h | humidity={sample['humidity']}%")
    print()


def test_rainfall_collector_landslide():
    print("=" * 60)
    print("TEST: RainfallCollector.collect_landslide_data()")
    print("=" * 60)

    collector = RainfallCollector()
    data = collector.collect_landslide_data()

    assert isinstance(data, list), "Expected a list"
    assert len(data) > 0, "Expected at least 1 zone"

    sample = data[0]
    required_keys = ["station", "rain_1h_mm", "humidity", "wind_speed_ms", "lat", "lon"]
    for key in required_keys:
        assert key in sample, f"Missing key: {key}"

    print(f"  PASSED - {len(data)} landslide zones fetched")
    print(f"  Sample: {sample['station']} | rain={sample['rain_1h_mm']}mm/h | humidity={sample['humidity']}%")
    print()


if __name__ == "__main__":
    test_irrigation_collector()
    test_rainfall_collector_flood()
    test_rainfall_collector_landslide()
    print("ALL COLLECTOR TESTS PASSED!")
