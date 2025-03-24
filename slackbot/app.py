import json
from flask import Flask, request, jsonify
from utils.alerting import send_slack_alert
import os

app = Flask(__name__)

@app.route("/slack", methods=["POST"])
def slack_commands():
    data = request.form
    text = data.get("text", "").strip().lower()
    user = data.get("user_name", "user")

    try:
        with open("logs/trades.json", "r") as f:
            trades = json.load(f)
    except Exception:
        return jsonify({"text": "No trade data available."})

    if text == "summary":
        num_trades = len(trades)
        total_premium = sum(t["premium"] for t in trades)
        calls = sum(1 for t in trades if t["side"] == "CALL")
        puts = num_trades - calls
        return jsonify({
            "text": f"*Summary for {user}:*
Trades: {num_trades}
Premium: ${total_premium:.2f}
Calls: {calls}, Puts: {puts}"
        })

    elif text == "score":
        avg_score = sum(t["score"] for t in trades) / len(trades)
        return jsonify({"text": f"*Average Score:* {avg_score:.2f}"})

    elif text == "last trade":
        last = trades[-1]
        return jsonify({
            "text": f"*Last Trade:* {last['side']} {last['strike']} exp {last['expiry']}, premium ${last['premium']}, score {last['score']}"
        })

    else:
        return jsonify({"text": "Commands: `summary`, `score`, `last trade`"})

if __name__ == "__main__":
    app.run(port=5000)