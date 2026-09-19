# seed_zones.py
from app.database import SessionLocal, init_db

# Import ALL models so SQLAlchemy registers relationships properly
from app.models.report import Report
from app.models.telemetry import TelemetryLog
from app.models.zone import Zone


def seed_lahore_zones():
    # Ensure tables are created first to prevent 'no such table' errors
    init_db()

    db = SessionLocal()

    zones_data = [
        {"name": "Old Lahore (Walled City)", "latitude": 31.5824, "longitude": 74.3294},
        {"name": "Garhi Shahu", "latitude": 31.5625, "longitude": 74.3435},
        {"name": "Gulberg", "latitude": 31.5204, "longitude": 74.3587},
        {"name": "Johar Town", "latitude": 31.4697, "longitude": 74.2728},
        {"name": "Model Town", "latitude": 31.4904, "longitude": 74.3262},
        {"name": "DHA Phase 5", "latitude": 31.4795, "longitude": 74.4063},
        {"name": "Badshahi & Circular Road", "latitude": 31.5880, "longitude": 74.3090},
        {"name": "Thokar Niaz Baig", "latitude": 31.4776, "longitude": 74.2585},
        {"name": "Iqbal Town", "latitude": 31.5032, "longitude": 74.2885},
        {"name": "Gulberg III (Liberty)", "latitude": 31.5100, "longitude": 74.3487},
        {"name": "DHA Phase 8", "latitude": 31.4821, "longitude": 74.4533},
        {"name": "Cantt / Fortress", "latitude": 31.5375, "longitude": 74.3688},
    ]

    for data in zones_data:
        existing = db.query(Zone).filter(Zone.name == data["name"]).first()
        if not existing:
            zone = Zone(
                name=data["name"],
                latitude=data["latitude"],
                longitude=data["longitude"],
            )
            db.add(zone)
            print(f"Added zone: {data['name']}")
        else:
            print(f"Zone already exists: {data['name']}")

    db.commit()
    db.close()
    print("All zones seeded successfully!")


if __name__ == "__main__":
    seed_lahore_zones()
