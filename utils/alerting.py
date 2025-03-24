import requests
import os

# Set this in a local secrets.py or your environment
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", None)

def send_slack_alert(message):
    if not SLACK_WEBHOOK_URL:
        print("[ALERT] Slack webhook not configured.")
        return

    payload = {"text": message}
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=payload)
        if response.status_code != 200:
            print(f"[ALERT ERROR] Slack response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[ALERT ERROR] Slack send failed: {e}")