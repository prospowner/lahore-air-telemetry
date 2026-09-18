import os
from datetime import datetime, timezone

import app.models  # This forces SQLAlchemy to load Zone, TelemetryLog, and Report together
import requests
from app.database import SessionLocal
from app.models.telemetry import TelemetryLog
from app.models.zone import Zone

# IMPORT DISCORD NOTIFIER HERE
# (Adjust import path depending on whether notifications.py is in root or app/)
from app.notifications import send_discord_alert
from dotenv import load_dotenv

load_dotenv()

OWM_API_KEY = os.getenv("OWM_API_KEY")
WAQI_API_KEY = os.getenv("WAQI_API_KEY")

# Realistic urban variance multipliers to introduce localized differences
ZONE_MULTIPLIERS = {
    "Old Lahore (Walled City)": 1.25,
    "Gulberg": 1.12,
    "Johar Town": 1.02,
    "Model Town": 0.94,
    "DHA Phase 5": 0.82,
    "Garhi Shahu": 1.28,
    "Badshahi & Circular Road": 1.30,
    "Thokar Niaz Baig": 1.35,
    "Iqbal Town": 1.18,
    "Gulberg III (Liberty)": 1.15,
    "DHA Phase 8": 0.85,
    "Cantt / Fortress": 0.95,
}


def fetch_and_store_owm_data():
    """Fetches air pollution data from OpenWeatherMap for all zones with local scaling."""
    if not OWM_API_KEY or OWM_API_KEY == "your_openweather_key_here":
        print(
            "[WARNING] OWM_API_KEY not set properly in .env. Skipping OpenWeatherMap fetch."
        )
        return

    db = SessionLocal()
    zones = db.query(Zone).all()

    for zone in zones:
        url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={zone.latitude}&lon={zone.longitude}&appid={OWM_API_KEY}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                item = data["list"][0]
                raw_aqi = item["main"]["aqi"]
                components = item["components"]

                multiplier = ZONE_MULTIPLIERS.get(zone.name, 1.0)
                adjusted_aqi = max(1, min(5, round(raw_aqi * multiplier)))

                pm2_5 = float(components.get("pm2_5", 0.0)) * multiplier
                pm10 = float(components.get("pm10", 0.0)) * multiplier

                # Save log entry
                log = TelemetryLog(
                    zone_id=zone.id,
                    aqi=int(adjusted_aqi),
                    pm2_5=round(float(pm2_5), 2),
                    pm10=round(float(pm10), 2),
                    source="openweathermap",
                )
                db.add(log)
                print(f"[OWM] Logged telemetry for {zone.name} (AQI: {adjusted_aqi})")
            else:
                print(
                    f"[ERROR] OWM failed for {zone.name}: Status {response.status_code}"
                )
        except Exception as e:
            print(f"[EXCEPTION] OWM request error for {zone.name}: {e}")

    db.commit()
    db.close()


def fetch_and_store_waqi_data():
    """Fetches air quality feed from WAQI for all zones with local scaling."""
    if not WAQI_API_KEY or WAQI_API_KEY == "your_waqi_key_here":
        print("[WARNING] WAQI_API_KEY not set properly in .env. Skipping WAQI fetch.")
        return

    db = SessionLocal()
    zones = db.query(Zone).all()

    for zone in zones:
        url = f"https://api.waqi.info/feed/geo:{zone.latitude};{zone.longitude}/?token={WAQI_API_KEY}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "ok":
                    feed_data = data["data"]
                    raw_aqi = feed_data.get("aqi", 0)
                    iaqi = feed_data.get("iaqi", {})

                    multiplier = ZONE_MULTIPLIERS.get(zone.name, 1.0)
                    adjusted_aqi = max(0, round(raw_aqi * multiplier))

                    pm2_5 = float(iaqi.get("pm25", {}).get("v", 0.0)) * multiplier
                    pm10 = float(iaqi.get("pm10", {}).get("v", 0.0)) * multiplier

                    log = TelemetryLog(
                        zone_id=zone.id,
                        aqi=int(adjusted_aqi),
                        pm2_5=round(float(pm2_5), 2),
                        pm10=round(float(pm10), 2),
                        source="waqi",
                    )
                    db.add(log)
                    print(
                        f"[WAQI] Logged telemetry for {zone.name} (AQI: {adjusted_aqi})"
                    )

                    # --- TRIGGER DISCORD ALERT IF AQI > 200 ---
                    if adjusted_aqi > 200:
                        send_discord_alert(
                            title=f"CRITICAL AIR QUALITY BREACH — {zone.name}",
                            description=(
                                f"⚠️ **Hazardous AQI Level Detected!**\n\n"
                                f"• **Zone:** {zone.name}\n"
                                f"• **Calculated AQI:** `{adjusted_aqi}`\n"
                                f"• **PM2.5 Concentration:** `{pm2_5:.1f} µg/m³`\n"
                                f"• **PM10 Concentration:** `{pm10:.1f} µg/m³`\n\n"
                                f"*Immediate citizen advisory active for this area.*"
                            ),
                            severity_color=10181046,  # Dark Red / Purple
                        )

                else:
                    print(
                        f"[ERROR] WAQI returned non-ok status for {zone.name}: {data}"
                    )
            else:
                print(
                    f"[ERROR] WAQI failed for {zone.name}: Status {response.status_code}"
                )
        except Exception as e:
            print(f"[EXCEPTION] WAQI request error for {zone.name}: {e}")

    db.commit()
    db.close()


if __name__ == "__main__":
    print("Running manual telemetry ingestion sweep...")
    fetch_and_store_owm_data()
    fetch_and_store_waqi_data()
    print("Ingestion sweep complete!")
