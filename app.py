import streamlit as st
import pandas as pd
import json

# === PAGE CONFIG ===
st.set_page_config(page_title="📈 Nova Picks – AI Market Predictions", layout="wide")

# === HEADER ===
st.title("🚀 Nova Picks – AI Market Predictions")
st.caption("Your beginner-friendly AI assistant for smart trading decisions.")

# === HELPER FUNCTIONS ===
symbol_names = {
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla, Inc.",
    "MSFT": "Microsoft Corp.",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.",
    "META": "Meta Platforms",
    "NFLX": "Netflix Inc.",
    "NVDA": "NVIDIA Corp.",
    "SPY": "S&P 500 ETF",
    "QQQ": "Nasdaq 100 ETF",
    "VTI": "Total Stock Market ETF",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum"
}

def get_name(symbol):
    return f"{symbol_names.get(symbol, 'Unknown Company')} ({symbol})"

glossary = {
    "RSI": "Relative Strength Index – measures momentum and overbought/oversold levels.",
    "MACD": "Moving Average Convergence Divergence – tracks trend and momentum changes.",
    "EMA": "Exponential Moving Average – a weighted moving average.",
    "Bollinger Bands": "Volatility bands set above/below a moving average."
}

# === LOAD DATA ===
uploaded_file = st.file_uploader("📤 Upload your predictions file (.json or .txt)", type=["json", "txt"])

if uploaded_file is not None:
    predictions = json.load(uploaded_file)
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
    df["Name"] = df["symbol"].apply(get_name)
    df["Confidence %"] = (df["confidence"] * 100).round(2)
    df["Prediction Label"] = df["predicted_label_name"].apply(lambda x: "📈 Bullish" if x == "bullish" else "📉 Bearish")

    # === FILTERS ===
    st.sidebar.header("🔍 Filters")
    min_conf = st.sidebar.slider("Minimum Confidence", 0.0, 1.0, 0.5, 0.01)
    category_filter = st.sidebar.multiselect("Asset Type", ["Stock", "Crypto", "ETF"], default=["Stock", "Crypto", "ETF"])
    df = df[(df["confidence"] >= min_conf) & (df["Category"].isin(category_filter))]
    df = df.sort_values("confidence", ascending=False)

    # === DISPLAY PICKS ===
    st.header("🎯 Today's Most Confident Picks")
    for _, row in df.iterrows():
        with st.expander(f"{row['Name']} – {row['Prediction Label']} ({row['Confidence %']}% Confidence)"):
            st.markdown("#### 🔍 Overview")
            st.markdown(f"**Category:** {row['Category']}")
            st.markdown(f"**Edge:** `{round(row['edge']*100, 2)}%`")

            # === BUILD FEATURES CLEANLY ===
            feature_cols = [col for col in row.index if col.startswith("features.")]
            feature_dict = {col.split("features.")[-1]: row[col] for col in feature_cols if pd.notnull(row[col])}
            if feature_dict:
                st.markdown("#### 📊 Trader Signals")
                for key, value in feature_dict.items():
                    label = key.upper()
                    if "rsi" in key.lower():
                        label = "RSI (Relative Strength Index)"
                    elif "macd_signal" in key.lower():
                        label = "MACD Signal Line"
                    elif "macd" in key.lower():
                        label = "MACD"
                    elif "ema_20" in key.lower():
                        label = "EMA 20"
                    elif "ema_50" in key.lower():
                        label = "EMA 50"
                    elif "bb_upper" in key.lower():
                        label = "Bollinger Upper Band"
                    elif "bb_lower" in key.lower():
                        label = "Bollinger Lower Band"
                    st.markdown(f"- **{label}:** `{round(value, 2)}`")

    # === GLOSSARY ===
    with st.expander("📘 What do these terms mean?"):
        for term, definition in glossary.items():
            st.markdown(f"**{term}:** {definition}")

    # === TOP PICKS (SIDEBAR) ===
    st.sidebar.header("📈 Top Bullish & Bearish Picks")
    top_bull = df[df["predicted_label_name"] == "bullish"].head(1)
    top_bear = df[df["predicted_label_name"] == "bearish"].head(1)
    if not top_bull.empty:
        st.sidebar.success(f"Top Bullish: {top_bull.iloc[0]['Name']} ({top_bull.iloc[0]['Confidence %']}%)")
    if not top_bear.empty:
        st.sidebar.error(f"Top Bearish: {top_bear.iloc[0]['Name']} ({top_bear.iloc[0]['Confidence %']}%)")

    # === DOWNLOAD ===
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Download Predictions as CSV", csv, "nova_predictions.csv", "text/csv")

else:
    st.info("Upload a `.json` or `.txt` prediction file to get started.")
