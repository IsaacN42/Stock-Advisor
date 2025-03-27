import streamlit as st
import json
import os

CONFIG_FILE = "config.json"

# Load config from local file
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
else:
    st.error("⚠️ config.json not found. Please make sure it exists.")
    st.stop()

st.title("📈 Advisor Bot Control Panel")

# ---- Watchlist ----
st.subheader("Manage Watchlist")
new_symbol = st.text_input("Add Ticker (e.g., AAPL, BTCUSD)")

if st.button("Add Ticker"):
    if new_symbol.upper() not in config['watchlist']:
        config['watchlist'].append(new_symbol.upper())
        st.success(f"Added {new_symbol.upper()}")

remove_symbol = st.selectbox("Remove Ticker", options=config['watchlist'])
if st.button("Remove Ticker"):
    config['watchlist'].remove(remove_symbol)
    st.warning(f"Removed {remove_symbol}")

# ---- RSI Threshold ----
st.subheader("RSI Threshold")
config['rsi_threshold'] = st.slider("Set RSI Threshold", 0, 100, config['rsi_threshold'])

# ---- Keywords ----
st.subheader("News Keywords")
new_keyword = st.text_input("Add Keyword")

if st.button("Add Keyword"):
    if new_keyword.lower() not in config['keywords']:
        config['keywords'].append(new_keyword.lower())
        st.success(f"Added keyword '{new_keyword.lower()}'")

remove_keyword = st.selectbox("Remove Keyword", options=config['keywords'])
if st.button("Remove Keyword"):
    config['keywords'].remove(remove_keyword)
    st.warning(f"Removed keyword '{remove_keyword}'")

# ---- Save Config ----
if st.button("Save Settings"):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    st.success("Settings saved! You may need to restart the advisor to apply changes.")

# Display config
st.subheader("Current Config")
st.json(config)
