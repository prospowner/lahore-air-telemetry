# seed_zones.py
from app.database import SessionLocal, init_db
from app.models.zone import Zone


def seed_lahore_zones():
    # Ensure tables are created first to prevent 'no such table' errors
    init_db()

    db = SessionLocal()

    zones_data = [
        {"name": "Gulberg", "latitude": 31.5204, "longitude": 74.3587},
        {"name": "DHA Phase 5", "latitude": 31.4795, "longitude": 74.4063},
        {"name": "Johar Town", "latitude": 31.4697, "longitude": 74.2728},
        {"name": "Old Lahore (Walled City)", "latitude": 31.5824, "longitude": 74.3294},
        {"name": "Model Town", "latitude": 31.4904, "longitude": 74.3262},
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
    print("Zone seeding complete!")


if __name__ == "__main__":
    seed_lahore_zones()
