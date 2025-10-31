import streamlit as st
from nsetools import Nse

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
                st.write("**Day Range:**", f"{data['dayLow']} - {data['dayHigh']}")
                st.write("**52W Range:**", f"{data['low52']} - {data['high52']}")
                st.write("**Volume Traded:**", data["quantityTraded"])
                st.write("**Market Cap:**", data.get("marketCapFull", "N/A"))
            else:
                st.error("Invalid symbol or no data found.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
