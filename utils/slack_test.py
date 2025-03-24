import os
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def send_slack_alert(message):
    if not SLACK_WEBHOOK_URL:
        print("SLACK_WEBHOOK_URL not configured.")
        return
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        print("Slack message sent.")
    else:
        print(f"Slack error {response.status_code}: {response.text}")

if __name__ == "__main__":
    send_slack_alert("Test message from your NVDA bot!")