import streamlit as st
import pandas as pd
import json
import yfinance as yf

# === CONFIG ===
st.set_page_config(page_title="🚀 Nova Picks – AI Market Predictions", layout="wide")

# === HEADER ===
st.title("💹 Nova Picks – AI Market Predictions")
st.caption("A bold, beginner-friendly trading dashboard powered by AI.")

# === SYMBOL NAME LOOKUP ===
@st.cache_data
def fetch_name(symbol):
    try:
        ticker = yf.Ticker(symbol)
        return ticker.info.get("shortName", None)
    except:
        return None

# === GLOSSARY ===
glossary = {
    "RSI": "Relative Strength Index – shows if something is overbought/oversold.",
    "MACD": "Moving Average Convergence Divergence – shows momentum shift.",
    "EMA": "Exponential Moving Average – weighted moving average.",
    "Bollinger Bands": "Bands that show price volatility boundaries."
}

# === LOAD JSON FROM GITHUB REPO ===
try:
    with open("daily_predictions.json", "r") as f:
        predictions = json.load(f)
    df = pd.json_normalize(predictions)

    # === CLASSIFY SYMBOLS ===
    def classify(symbol):
        if "-USD" in symbol:
            return "Crypto"
        elif symbol in ["SPY", "QQQ", "VTI", "ARKK", "DIA", "XLF", "XLE", "XLK"]:
            return "ETF"
        else:
            return "Stock"

    df["Category"] = df["symbol"].apply(classify)
    df["Full Name"] = df["symbol"].apply(lambda s: f"{fetch_name(s)} ({s})" if fetch_name(s) else s)
    df["Confidence %"] = (df["confidence"] * 100).round(2)
    df["Prediction Label"] = df["predicted_label_name"].apply(lambda x: "📈 Bullish" if x == "bullish" else "📉 Bearish")
    df = df.sort_values("confidence", ascending=False)

    # === FILTERS ===
    st.sidebar.header("🔍 Filters")
    min_conf = st.sidebar.slider("Minimum Confidence", 0.0, 1.0, 0.5, 0.01)
    asset_type = st.sidebar.multiselect("Asset Type", ["Stock", "ETF", "Crypto"], default=["Stock", "ETF", "Crypto"])
    df = df[(df["confidence"] >= min_conf) & (df["Category"].isin(asset_type))]

    # === DISPLAY PICKS IN CARD STYLE ===
    st.header("🌟 Today's Most Confident Picks")

    for _, row in df.iterrows():
        with st.container():
            st.markdown(
                f"""
                <div style='border: 1px solid #444; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; background-color: #111;'>
                    <h3 style='color:#fff;'>🧠 {row['Full Name']} – {row['Prediction Label']} <span style='font-size: 16px;'>({row['Confidence %']}% confidence)</span></h3>
                    <p><b>Asset Type:</b> {row['Category']} &nbsp;&nbsp;|&nbsp;&nbsp; <b>Edge:</b> {round(row['edge']*100, 2)}%</p>
                """, unsafe_allow_html=True
            )

            feature_cols = [col for col in row.index if col.startswith("features.")]
            feature_dict = {col.split("features.")[-1]: row[col] for col in feature_cols if pd.notnull(row[col])}

            if feature_dict:
                st.markdown("#### 📊 Trader Signals")
                cols = st.columns(3)
                keys = list(feature_dict.keys())
                for i, key in enumerate(keys):
                    val = round(feature_dict[key], 2)
                    label = key.upper()
                    if key == "rsi":
                        label = "RSI (Momentum)"
                    elif key == "macd":
                        label = "MACD"
                    elif key == "macd_signal":
                        label = "MACD Signal"
                    elif key == "ema_20":
                        label = "EMA 20"
                    elif key == "ema_50":
                        label = "EMA 50"
                    elif key == "bb_upper":
                        label = "Bollinger Upper"
                    elif key == "bb_lower":
                        label = "Bollinger Lower"
                    elif key == "roc":
                        label = "Rate of Change"
                    elif key == "volume":
                        label = "Volume"
                    elif key == "open":
                        label = "Open Price"
                    elif key == "close":
                        label = "Close Price"
                    elif key == "high":
                        label = "High"
                    elif key == "low":
                        label = "Low"
                    elif key == "dayofweek":
                        label = "Day of Week"
                    elif key == "month":
                        label = "Month"
                    cols[i % 3].metric(label, val)

            st.markdown("</div>", unsafe_allow_html=True)

    # === GLOSSARY ===
    with st.expander("📘 What do these trading signals mean?"):
        for term, definition in glossary.items():
            st.markdown(f"**{term}:** {definition}")

    # === TOP PICKS SIDEBAR ===
    st.sidebar.header("🏆 Top Picks")
    top_bull = df[df["predicted_label_name"] == "bullish"].head(1)
    top_bear = df[df["predicted_label_name"] == "bearish"].head(1)
    if not top_bull.empty:
        st.sidebar.success(f"Top Bullish: {top_bull.iloc[0]['Full Name']}")
    if not top_bear.empty:
        st.sidebar.error(f"Top Bearish: {top_bear.iloc[0]['Full Name']}")

    # === DOWNLOAD ===
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Download Full Predictions", csv, "nova_predictions.csv", "text/csv")

except Exception as e:
    st.error(f"❌ Error loading predictions: {e}")
