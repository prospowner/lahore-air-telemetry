import os

import requests
from dotenv import load_dotenv

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "YOUR_DISCORD_WEBHOOK_URL_HERE")


def send_discord_alert(title: str, description: str, severity_color: int = 15158332):
    """
    Sends a rich embed notification to a Discord channel via Webhook.
    """
    if (
        not DISCORD_WEBHOOK_URL
        or DISCORD_WEBHOOK_URL == "YOUR_DISCORD_WEBHOOK_URL_HERE"
    ):
        print("Discord Webhook URL not configured.")
        return

    payload = {
        "embeds": [
            {
                "title": f"🚨 LahorePulse Hazard Dispatch: {title}",
                "description": description,
                "color": severity_color,
                "fields": [
                    {
                        "name": "Platform",
                        "value": "GIS Telemetry Engine",
                        "inline": True,
                    },
                    {"name": "Status", "value": "Automated Trigger", "inline": True},
                ],
                "footer": {"text": "LexHack 2026 Emergency Telemetry System"},
            }
        ]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code not in [200, 204]:
            print(f"Failed to send Discord alert: {response.text}")
    except Exception as e:
        print(f"Error dispatching Discord webhook: {e}")
