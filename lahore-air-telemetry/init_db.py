# init_db.py
from app.database import Base, engine
from app.models.report import Report
from app.models.telemetry import TelemetryLog
from app.models.zone import Zone


def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    init_db()
