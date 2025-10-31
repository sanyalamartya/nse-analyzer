import streamlit as st
from nsetools import Nse

# --- Recommendation Logic ---
def get_recommendation(data):
    score = 0

    try:
        # 1. Price strength vs 52W high
        price = data["lastPrice"]
        high_52 = data["high52"]
        if price > 0.9 * high_52:
            score += 1

        # 2. Volume momentum (vs average volume, fallback if not available)
        volume = data["quantityTraded"]
        avg_volume = data.get("averageVolume", 0) or 0
        if avg_volume and volume > 1.5 * avg_volume:
            score += 1

        # 3. Positive day gain %
        previous_close = data.get("previousClose", 0)
        if previous_close and price > previous_close:
            score += 1

    except Exception as e:
        st.warning(f"Error in recommendation logic: {e}")

    if score >= 2:
        return "✅ Buy"
    elif score == 1:
        return "👀 Watch"
    else:
        return "❌ Avoid"

# --- Breakout Detection Logic ---
def detect_breakout(data):
    try:
        price = data["lastPrice"]
        high_52 = data["high52"]
        previous_close = data.get("previousClose", 0)
        volume = data["quantityTraded"]
        avg_volume = data.get("averageVolume", 0) or 0

        near_high = price >= 0.95 * high_52
        price_up = price > previous_close
        volume_spike = avg_volume and volume > 1.2 * avg_volume

        if near_high and price_up and volume_spike:
            return "⚡ Potential Breakout Detected!"
        else:
            return "No breakout signal"
    except Exception as e:
        return f"Error detecting breakout: {e}"

# --- Streamlit App UI ---
nse = Nse()

st.set_page_config(page_title="NSE Stock Analyzer", layout="centered")
st.title("📈 NSE Stock Analyzer")

symbol = st.text_input("Enter NSE stock symbol (e.g., INFY, TCS, RELIANCE)").lower()

if symbol:
    with st.spinner("Fetching stock data..."):
        try:
            data = nse.get_quote(symbol)
            if data:
                st.subheader(f"{data['companyName']} ({symbol.upper()})")
                st.metric("Last Price (₹)", data["lastPrice"])

                # 🔎 Recommendation
                recommendation = get_recommendation(data)
                st.markdown(f"### 🔎 Recommendation: {recommendation}")

                # 📊 Breakout Detection
                breakout = detect_breakout(data)
                st.markdown(f"### 📊 Breakout Status: {breakout}")

                # 📈 Extra Info
                st.write("**Day Range:**", f"{data['dayLow']} - {data['dayHigh']}")
                st.write("**52W Range:**", f"{data['low52']} - {data['high52']}")
                st.write("**Volume Traded:**", data["quantityTraded"])
                st.write("**Market Cap:**", data.get("marketCapFull", "N/A"))
            else:
                st.error("Invalid symbol or no data found.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
