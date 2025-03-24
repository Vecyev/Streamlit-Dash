
import streamlit as st
import pandas as pd
import os
import json
import subprocess
from utils.auto_tuner import StrategyAutoTuner
from utils.alerting import send_slack_alert

LOG_PATH = "logs/nvda_trading_log.txt"
TRADE_DATA = "logs/trades.json"
CONFIG_FILE = "config.py"

st.title("NVDA Covered Call + CSP Bot Dashboard")

# Log viewer
if os.path.exists(LOG_PATH):
    with open(LOG_PATH, "r") as f:
        logs = f.readlines()
    st.subheader("Recent Log Entries")
    st.text("".join(logs[-40:]))
else:
    st.warning("Log file not found.")

# P&L and trade count
if os.path.exists(TRADE_DATA):
    with open(TRADE_DATA, "r") as f:
        trades = json.load(f)
    df = pd.DataFrame(trades)
    df["date"] = pd.to_datetime(df["date"])
    df["cumulative_pnl"] = df["premium"].cumsum()

    st.subheader("Cumulative P&L")
    st.line_chart(df.set_index("date")["cumulative_pnl"])

    st.subheader("Daily Premium Collected")
    st.bar_chart(df.set_index("date")["premium"])

    st.metric("Total Trades", len(df))
    st.metric("Total Premium", f"${df['premium'].sum():.2f}")
else:
    st.info("No trade data available yet.")

# Auto-tuner section
st.subheader("Auto-Tune Strategy Parameters")
if st.button("Run Auto-Tuner"):
    tuner = StrategyAutoTuner()
    suggestions = tuner.tune()

    if suggestions:
        st.success("Suggested Strategy Adjustments:")
        for k, v in suggestions.items():
            st.write(f"**{k}**: {v}")

        if st.button("Apply to config.py and Restart Bot"):
            with open(CONFIG_FILE, "r") as f:
                lines = f.readlines()

            with open(CONFIG_FILE, "w") as f:
                for line in lines:
                    updated = False
                    for key, val in suggestions.items():
                        if line.strip().startswith(f"{key}"):
                            f.write(f"{key} = {val}\n")
                            updated = True
                            break
                    if not updated:
                        f.write(line)

            st.success("Configuration updated. Restarting strategy...")
            send_slack_alert("[AUTO-TUNER] Config updated and strategy restarted via dashboard")")
            subprocess.Popen(["python3", "main.py"])
    else:
        st.warning("Not enough trade data to tune strategy.")


# === ML Dashboard Section ===
import dashboard.ml_panel
