import json
import os
from datetime import datetime, timedelta
from utils.alerting import send_slack_alert

def send_daily_summary(trade_log_path="logs/trades.json"):
    if not os.path.exists(trade_log_path):
        send_slack_alert("[DAILY SUMMARY] No trades logged yet.")
        return

    with open(trade_log_path, "r") as f:
        trades = json.load(f)

    last_24h = [
        t for t in trades
        if datetime.strptime(t["date"], "%Y-%m-%d %H:%M:%S") > datetime.now() - timedelta(hours=24)
    ]

    if not last_24h:
        send_slack_alert("[DAILY SUMMARY] No trades in the last 24 hours.")
        return

    num_trades = len(last_24h)
    total_premium = sum(t["premium"] for t in last_24h)
    calls = sum(1 for t in last_24h if t["side"] == "CALL")
    puts = num_trades - calls
    avg_score = sum(t["score"] for t in last_24h) / num_trades

    msg = (
        f"*Daily NVDA Options Bot Summary*
"
        f"- Trades: {num_trades}
"
        f"- Premium Collected: ${total_premium:.2f}
"
        f"- Calls: {calls}, Puts: {puts}
"
        f"- Avg Score: {avg_score:.2f}"
    )
    send_slack_alert(msg)

if __name__ == "__main__":
    send_daily_summary()