import streamlit as st
import yfinance as yf
import datetime

# --- Recommendation Logic ---
def get_recommendation(data):
    score = 0

    try:
        price = data["last_price"]
        high_52 = data["high_52"]
        low_52 = data["low_52"]
        volume = data["volume"]
        avg_volume = data["avg_volume"]
        previous_close = data["prev_close"]

        # 1. Price near 52W high
        if price > 0.9 * high_52:
            score += 1

        # 2. Volume surge
        if avg_volume and volume > 1.5 * avg_volume:
            score += 1

        # 3. Positive momentum
        if price > previous_close:
            score += 1

    except Exception as e:
        st.warning(f"Error in recommendation logic: {e}")

    if score >= 2:
        return "✅ Buy"
    elif score == 1:
        return "👀 Watch"
    else:
        return "❌ Avoid"

# --- Breakout Detection ---
def detect_breakout(data):
    try:
        price = data["last_price"]
        high_52 = data["high_52"]
        previous_close = data["prev_close"]
        volume = data["volume"]
        avg_volume = data["avg_volume"]

        near_high = price >= 0.95 * high_52
        price_up = price > previous_close
        volume_spike = avg_volume and volume > 1.2 * avg_volume

        if near_high and price_up and volume_spike:
            return "⚡ Potential Breakout Detected!"
        else:
            return "No breakout signal"
    except Exception as e:
        return f"Error detecting breakout: {e}"

# --- Fetch Stock Data ---
def fetch_stock_data(symbol):
    try:
        ticker = yf.Ticker(f"{symbol.upper()}.NS")
        info = ticker.info

        hist = ticker.history(period="1mo")
        volume_series = hist["Volume"]
        avg_volume = volume_series.mean() if not volume_series.empty else 0

        return {
            "name": info.get("shortName", symbol.upper()),
            "last_price": info.get("currentPrice", 0),
            "day_low": info.get("dayLow", 0),
            "day_high": info.get("dayHigh", 0),
            "low_52": info.get("fiftyTwoWeekLow", 0),
            "high_52": info.get("fiftyTwoWeekHigh", 0),
            "volume": info.get("volume", 0),
            "avg_volume": avg_volume,
            "prev_close": info.get("previousClose", 0),
            "market_cap": info.get("marketCap", "N/A"),
        }

    except Exception as e:
        return {"error": str(e)}

# --- Streamlit App ---
st.set_page_config(page_title="NSE Stock Analyzer", layout="centered")
st.title("📈 NSE Stock Analyzer")

symbol = st.text_input("Enter NSE stock symbol (e.g., INFY, TCS, RELIANCE)").upper()

if symbol:
    with st.spinner("Fetching data..."):
        data = fetch_stock_data(symbol)

        if "error" in data:
            st.error(f"Error fetching data: {data['error']}")
        elif data["last_price"] == 0:
            st.error("No data available for this symbol.")
        else:
            st.subheader(f"{data['name']} ({symbol}.NS)")
            st.metric("Last Price (₹)", data["last_price"])

            # 🔎 Recommendation
            recommendation = get_recommendation(data)
            st.markdown(f"### 🔎 Recommendation: {recommendation}")

            # 📊 Breakout
            breakout = detect_breakout(data)
            st.markdown(f"### 📊 Breakout Status: {breakout}")

            # 📈 Extra Info
            st.write("**Day Range:**", f"{data['day_low']} - {data['day_high']}")
            st.write("**52W Range:**", f"{data['low_52']} - {data['high_52']}")
            st.write("**Volume:**", f"{data['volume']:,}")
            st.write("**Avg Volume (1 mo):**", f"{int(data['avg_volume']):,}")
            st.write("**Market Cap:**", f"{data['market_cap']:,}" if isinstance(data['market_cap'], (int, float)) else data['market_cap'])
