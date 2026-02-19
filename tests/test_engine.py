"""
Quick smoke tests for the disaster engines.
Run:  python tests/test_engine.py
"""
import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from engine.flood_engine import FloodEngine
from engine.landslide_engine import LandslideEngine


def test_flood_engine():
    print("=" * 60)
    print("TEST: FloodEngine.custom_logic_for_flood_engine()")
    print("=" * 60)

    engine = FloodEngine()
    zones = engine.custom_logic_for_flood_engine()

    assert isinstance(zones, list), "Expected a list"

    # Check structure if there are warning zones
    if zones:
        sample = zones[0]
        required_keys = ["station", "river_basin", "level_m", "risk_score",
                         "risk_level", "rain_1h_mm", "measured_at"]
        for key in required_keys:
            assert key in sample, f"Missing key: {key}"

        assert sample["risk_level"] in ["CRITICAL", "WARNING", "WATCH"], \
            f"Unexpected risk level: {sample['risk_level']}"
        assert 0 <= sample["risk_score"] <= 100, "Risk score out of range"

        print(f"  PASSED - {len(zones)} warning zones detected")
        for z in zones:
            print(f"    [{z['risk_level']}] {z['station']} "
                  f"(score={z['risk_score']}, level={z['level_m']}m)")
    else:
        print(f"  PASSED - 0 warning zones (all stations NORMAL)")
    print()


def test_landslide_engine():
    print("=" * 60)
    print("TEST: LandslideEngine.custom_logic_for_landslide()")
    print("=" * 60)

    engine = LandslideEngine()
    zones = engine.custom_logic_for_landslide()

    assert isinstance(zones, list), "Expected a list"

    if zones:
        sample = zones[0]
        required_keys = ["station", "rain_1h_mm", "humidity",
                         "wind_speed_ms", "risk_score", "risk_level"]
        for key in required_keys:
            assert key in sample, f"Missing key: {key}"

        assert sample["risk_level"] in ["CRITICAL", "WARNING", "WATCH"], \
            f"Unexpected risk level: {sample['risk_level']}"
        assert 0 <= sample["risk_score"] <= 100, "Risk score out of range"

        print(f"  PASSED - {len(zones)} warning zones detected")
        for z in zones:
            print(f"    [{z['risk_level']}] {z['station']} "
                  f"(score={z['risk_score']}, rain={z['rain_1h_mm']}mm/h, "
                  f"humidity={z['humidity']}%)")
    else:
        print(f"  PASSED - 0 warning zones (all areas NORMAL)")
    print()


if __name__ == "__main__":
    test_flood_engine()
    test_landslide_engine()
    print("ALL ENGINE TESTS PASSED!")
