# check_keys.py
import os

import requests
from dotenv import load_dotenv

load_dotenv()

OWM_API_KEY = os.getenv("OWM_API_KEY")
WAQI_API_KEY = os.getenv("WAQI_API_KEY")

print(f"Checking OpenWeatherMap API Key...")
if not OWM_API_KEY or OWM_API_KEY == "your_openweather_key_here":
    print("❌ OWM_API_KEY is missing or set to placeholder in .env")
else:
    # Test with Lahore coordinates (Gulberg)
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat=31.5204&lon=74.3587&appid={OWM_API_KEY}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            print("✅ OpenWeatherMap API Key is WORKING! Response received.")
        else:
            print(
                f"❌ OpenWeatherMap API Key failed with status {res.status_code}: {res.text}"
            )
    except Exception as e:
        print(f"❌ OpenWeatherMap request error: {e}")

print("\nChecking WAQI API Key...")
if not WAQI_API_KEY or WAQI_API_KEY == "your_waqi_key_here":
    print("❌ WAQI_API_KEY is missing or set to placeholder in .env")
else:
    # Test with WAQI geo feed endpoint
    url = f"https://api.waqi.info/feed/geo:31.5204;74.3587/?token={WAQI_API_KEY}"
    try:
        res = requests.get(url, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "ok":
                print(
                    f"✅ WAQI API Key is WORKING! Current AQI fetched: {data['data'].get('aqi')}"
                )
            else:
                print(f"❌ WAQI returned non-ok status: {data}")
        else:
            print(f"❌ WAQI API Key failed with status {res.status_code}: {res.text}")
    except Exception as e:
        print(f"❌ WAQI request error: {e}")
