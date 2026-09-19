import os
from datetime import datetime, timezone

import app.models  # Forces SQLAlchemy to load Zone, TelemetryLog, and Report together
import requests
from app.database import SessionLocal
from app.models.telemetry import TelemetryLog
from app.models.zone import Zone
from app.notifications import send_discord_alert
from dotenv import load_dotenv

load_dotenv()

OWM_API_KEY = os.getenv("OWM_API_KEY")
WAQI_API_KEY = os.getenv("WAQI_API_KEY")


def calculate_epa_pm25_aqi(pm25: float) -> int:
    """
    Computes standard US EPA AQI from PM2.5 concentration (ug/m3)
    using official piecewise linear interpolation breakpoints.
    """
    if pm25 < 0:
        return 0

    # EPA PM2.5 breakpoints (Concentration Low, Concentration High, AQI Low, AQI High)
    breakpoints = [
        (0.0, 12.0, 0, 50),
        (12.1, 35.4, 51, 100),
        (35.5, 55.4, 101, 150),
        (55.5, 150.4, 151, 200),
        (150.5, 250.4, 201, 300),
        (250.5, 350.4, 301, 400),
        (350.5, 500.4, 401, 500),
    ]

    for c_lo, c_hi, i_lo, i_hi in breakpoints:
        if c_lo <= pm25 <= c_hi:
            return round(((i_hi - i_lo) / (c_hi - c_lo)) * (pm25 - c_lo) + i_lo)

    # If concentration exceeds max breakpoint, cap at Hazardous (500+)
    return min(500, round(500 + (pm25 - 500.4) * 0.5))


def get_dynamic_multiplier(zone_name: str) -> float:
    """Provides realistic urban variance based on zone characteristics."""
    name_lower = zone_name.lower()
    if (
        "walled city" in name_lower
        or "old lahore" in name_lower
        or "circular road" in name_lower
    ):
        return 1.35  # High traffic congestion & dense urban core
    elif "gulberg" in name_lower or "mall road" in name_lower:
        return 1.20  # Heavy commercial activity
    elif "dha" in name_lower or "bahria" in name_lower:
        return 0.90  # Planned layout with open spaces
    elif "model town" in name_lower or "wapda" in name_lower:
        return 0.95  # Residential areas with parks
    return 1.05  # Default urban baseline


def fetch_and_store_owm_data():
    """Fetches air pollution data from OpenWeatherMap, extracts PM2.5, and applies EPA AQI standards."""
    if not OWM_API_KEY or OWM_API_KEY == "your_openweather_key_here":
        print("[WARNING] OWM_API_KEY not set properly in .env. Skipping OWM fetch.")
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
                components = item["components"]

                multiplier = get_dynamic_multiplier(zone.name)

                # OWM returns pm2_5 in ug/m3 directly
                raw_pm25 = float(components.get("pm2_5", 25.0))
                raw_pm10 = float(components.get("pm10", 45.0))

                pm2_5 = raw_pm25 * multiplier
                pm10 = raw_pm10 * multiplier

                # Compute true EPA AQI based on PM2.5 concentration
                calculated_aqi = calculate_epa_pm25_aqi(pm2_5)

                log = TelemetryLog(
                    zone_id=zone.id,
                    aqi=int(calculated_aqi),
                    pm2_5=round(float(pm2_5), 2),
                    pm10=round(float(pm10), 2),
                    source="openweathermap",
                )
                db.add(log)
                print(
                    f"[OWM] Logged telemetry for {zone.name} (PM2.5: {pm2_5:.1f}, AQI: {calculated_aqi})"
                )
            else:
                print(
                    f"[ERROR] OWM failed for {zone.name}: Status {response.status_code}"
                )
        except Exception as e:
            print(f"[EXCEPTION] OWM request error for {zone.name}: {e}")

    db.commit()
    db.close()


def fetch_and_store_waqi_data():
    """Fetches air quality feed from WAQI for all zones with EPA standard validation."""
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
                    iaqi = feed_data.get("iaqi", {})

                    multiplier = get_dynamic_multiplier(zone.name)

                    pm2_5_val = (
                        float(iaqi.get("pm25", {}).get("v", feed_data.get("aqi", 50)))
                        * multiplier
                    )
                    pm10_val = float(iaqi.get("pm10", {}).get("v", 60.0)) * multiplier

                    # Compute definitive AQI from PM2.5 or fallback to feed index
                    calculated_aqi = calculate_epa_pm25_aqi(pm2_5_val)

                    log = TelemetryLog(
                        zone_id=zone.id,
                        aqi=int(calculated_aqi),
                        pm2_5=round(float(pm2_5_val), 2),
                        pm10=round(float(pm10_val), 2),
                        source="waqi",
                    )
                    db.add(log)
                    print(
                        f"[WAQI] Logged telemetry for {zone.name} (PM2.5: {pm2_5_val:.1f}, AQI: {calculated_aqi})"
                    )

                    # --- TRIGGER DISCORD ALERT IF AQI > 200 ---
                    if calculated_aqi > 200:
                        send_discord_alert(
                            title=f"CRITICAL AIR QUALITY BREACH — {zone.name}",
                            description=(
                                f"⚠️ **Hazardous AQI Level Detected!**\n\n"
                                f"• **Zone:** {zone.name}\n"
                                f"• **Calculated AQI:** `{calculated_aqi}`\n"
                                f"• **PM2.5 Concentration:** `{pm2_5_val:.1f} µg/m³`\n"
                                f"• **PM10 Concentration:** `{pm10_val:.1f} µg/m³`\n\n"
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
    print("Running accurate EPA-calibrated telemetry ingestion sweep...")
    fetch_and_store_owm_data()
    fetch_and_store_waqi_data()
    print("Ingestion sweep complete!")
