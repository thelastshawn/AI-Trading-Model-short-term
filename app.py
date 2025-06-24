import streamlit as st
import pandas as pd
import json
from pathlib import Path

st.set_page_config(
    page_title="Ninja Licks",
    page_icon="🌟",
    layout="wide"
)

# Load predictions
file_path = Path("daily_predictions.json")
if not file_path.exists():
    st.error("daily_predictions.json not found.")
    st.stop()

with open(file_path) as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Parse nested feature data
features_df = pd.json_normalize(df["features"])
df = df.drop(columns=["features"])
df = pd.concat([df, features_df], axis=1)

# Add derived columns
df["Asset Type"] = df["symbol"].apply(lambda x: "Crypto" if x.endswith("-USD") else "Stock/ETF")
df["Confidence %"] = (df["confidence"] * 100).round(2)
df["Edge %"] = (df["edge"] * 100).round(2)

# ---------------- Sidebar Filters ---------------- #
st.sidebar.header("🔍 Filters")
min_conf = st.sidebar.slider("Minimum Confidence", 50, 100, 60)
asset_type = st.sidebar.multiselect("Asset Type", ["Stock/ETF", "Crypto"], default=["Stock/ETF", "Crypto"])
symbol_search = st.sidebar.text_input("Search Symbol")

filtered_df = df[df["Confidence %"] >= min_conf]
filtered_df = filtered_df[filtered_df["Asset Type"].isin(asset_type)]
if symbol_search:
    filtered_df = filtered_df[filtered_df["symbol"].str.contains(symbol_search.upper())]

# ---------------- Tab Layout ---------------- #
st.markdown("""
<h1 style='color:#90EE90;'>💵 Ninja Licks – AI Stocks/ETF/Crypto Market Predictions</h1>
<p>A bold, beginner-friendly trading dashboard powered by AI.</p>
""", unsafe_allow_html=True)

tabs = st.tabs(["📈 Picks", "📖 Glossary", "🔀 Trends"])

# ---------------- Picks Tab ---------------- #
with tabs[0]:
    st.subheader("🌟 Today's Most Confident Picks")

    for _, row in filtered_df.sort_values("Confidence %", ascending=False).iterrows():
        with st.expander(f"🧠 {row['symbol']} — {'📈 Bullish' if row['prediction'] == 1 else '📉 Bearish'} ({row['Confidence %']}% confidence)"):
            st.markdown(f"<b>Asset Type:</b> {row['Asset Type']}  |  <b>Edge:</b> {row['Edge %']}%", unsafe_allow_html=True)
            st.markdown("""
                <h5>🌐 Trader Signals</h5>
                <ul>
                <li><b>Close:</b> {:.2f}</li>
                <li><b>Open:</b> {:.2f}</li>
                <li><b>High:</b> {:.2f}</li>
                <li><b>Low:</b> {:.2f}</li>
                <li><b>Volume:</b> {:,.0f}</li>
                <li><b>RSI (Relative Strength Index):</b> {:.2f}</li>
                <li><b>MACD:</b> {:.2f}</li>
                <li><b>MACD Signal Line:</b> {:.2f}</li>
                <li><b>Bollinger Upper Band:</b> {:.2f}</li>
                <li><b>Bollinger Lower Band:</b> {:.2f}</li>
                <li><b>EMA 20:</b> {:.2f}</li>
                <li><b>EMA 50:</b> {:.2f}</li>
                <li><b>ROC (Rate of Change):</b> {:.2f}</li>
                </ul>
            """.format(
                row.get("close", 0),
                row.get("open", 0),
                row.get("high", 0),
                row.get("low", 0),
                row.get("volume", 0),
                row.get("rsi", 0),
                row.get("macd", 0),
                row.get("macd_signal", 0),
                row.get("bb_upper", 0),
                row.get("bb_lower", 0),
                row.get("ema_20", 0),
                row.get("ema_50", 0),
                row.get("roc", 0),
            ), unsafe_allow_html=True)

# ---------------- Glossary Tab ---------------- #
with tabs[1]:
    st.subheader("📖 Glossary & Acronyms")
    glossary = {
        "RSI": "Relative Strength Index - measures momentum of price movements (typically 0-100)",
        "MACD": "Moving Average Convergence Divergence - trend-following momentum indicator",
        "Bollinger Bands": "Volatility bands placed above/below a moving average",
        "EMA": "Exponential Moving Average - gives more weight to recent prices",
        "ROC": "Rate of Change - % change in price over a specific period",
        "Edge": "Predicted advantage over the implied market outcome",
        "Confidence": "Model's estimated probability of being correct"
    }
    for term, definition in glossary.items():
        st.markdown(f"**{term}**: {definition}")

# ---------------- Trends Tab ---------------- #
with tabs[2]:
    st.subheader("🔀 Market Trend Ideas (Coming Soon)")
    st.info("You'll soon be able to view historical predictions and performance trends here.")
