# seed_zones.py
import os
import sys

# Add root directory to python path so app imports work cleanly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, init_db
from app.models.report import Report

# Crucial: Import dependent models so SQLAlchemy mapper resolves relationships correctly
from app.models.telemetry import TelemetryLog
from app.models.zone import Zone

# Define your core zones plus any new areas you want to add
EXPANDED_ZONES = [
    # Existing core zones
    {"name": "Old Lahore (Walled City)", "latitude": 31.5820, "longitude": 74.3294},
    {"name": "Gulberg", "latitude": 31.5204, "longitude": 74.3587},
    {"name": "Johar Town", "latitude": 31.4697, "longitude": 74.2728},
    {"name": "Model Town", "latitude": 31.4849, "longitude": 74.3223},
    {"name": "DHA Phase 5", "latitude": 31.4690, "longitude": 74.4020},
    {"name": "Garhi Shahu", "latitude": 31.5710, "longitude": 74.3140},
    {"name": "Badshahi & Circular Road", "latitude": 31.5710, "longitude": 74.3140},
    {"name": "Thokar Niaz Baig", "latitude": 31.4826, "longitude": 74.2259},
    {"name": "Iqbal Town", "latitude": 31.5090, "longitude": 74.2980},
    {"name": "Gulberg III (Liberty)", "latitude": 31.5120, "longitude": 74.3400},
    {"name": "DHA Phase 8", "latitude": 31.4350, "longitude": 74.4500},
    {"name": "Cantt / Fortress", "latitude": 31.5354, "longitude": 74.4071},
    # New areas to add safely
    {"name": "Bahria Town Lahore", "latitude": 31.3525, "longitude": 74.1787},
    {"name": "Ferozepur Road (Ichhra)", "latitude": 31.5326, "longitude": 74.3336},
    {"name": "Mall Road", "latitude": 31.5658, "longitude": 74.3323},
    {"name": "Wapda Town", "latitude": 31.4489, "longitude": 74.2691},
]


def seed_new_zones():
    # Ensure tables are created first
    init_db()

    db = SessionLocal()
    added_count = 0
    try:
        for zone_data in EXPANDED_ZONES:
            # Check if zone already exists by name to avoid duplicate constraint errors
            existing = db.query(Zone).filter(Zone.name == zone_data["name"]).first()
            if not existing:
                new_zone = Zone(
                    name=zone_data["name"],
                    latitude=zone_data["latitude"],
                    longitude=zone_data["longitude"],
                )
                db.add(new_zone)
                added_count += 1
                print(f"[Seeder] Adding new zone: {zone_data['name']}")
            else:
                print(f"[Seeder] Zone already exists (skipped): {zone_data['name']}")

        db.commit()
        print(f"\n[Seeder] Successfully completed! Added {added_count} new zones.")
    except Exception as e:
        db.rollback()
        print(f"[Seeder Error] Failed to seed zones: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_new_zones()
