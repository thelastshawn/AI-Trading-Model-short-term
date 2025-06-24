import streamlit as st
import pandas as pd
import json

st.set_page_config(page_title="🤑 Ninja Licks – AI Trading Picks", layout="wide")

st.title("💴 Ninja Licks – AI Stocks/ETF/Crypto Market Predictions")
st.caption("A bold, beginner-friendly trading dashboard powered by AI.")

# === GLOSSARIES ===
symbol_glossary = {
    "AAPL": "Apple Inc.",
    "TSLA": "Tesla Inc.",
    "DOGE-USD": "Dogecoin",
    "XRP-USD": "Ripple",
    "BTC-USD": "Bitcoin",
    "ETH-USD": "Ethereum",
    "QQQ": "Invesco QQQ Trust",
    "SPY": "SPDR S&P 500 ETF Trust"
}

indicator_glossary = {
    "RSI": "Relative Strength Index – shows if something is overbought/oversold.",
    "MACD": "Moving Average Convergence Divergence – shows momentum shift.",
    "EMA": "Exponential Moving Average – smoothed price trend.",
    "Bollinger Bands": "Bands showing price volatility boundaries.",
    "ROC": "Rate of Change – momentum strength.",
}

# === LOAD DATA ===
try:
    with open("daily_predictions.json", "r") as f:
        predictions = json.load(f)
    df = pd.json_normalize(predictions)

    def classify(symbol):
        if "-USD" in symbol:
            return "Crypto"
        elif symbol in ["SPY", "QQQ", "VTI", "ARKK", "DIA", "XLF", "XLE", "XLK"]:
            return "ETF"
        else:
            return "Stock"

    df["Category"] = df["symbol"].apply(classify)
    df["Confidence %"] = (df["confidence"] * 100).round(2)
    df["Label"] = df["predicted_label_name"].apply(lambda x: "📈 Bullish" if x == "bullish" else "📉 Bearish")
    df = df.sort_values("confidence", ascending=False)

    # === SIDEBAR FILTERS ===
    st.sidebar.header("🔎 Filters")
    min_conf = st.sidebar.slider("Min Confidence", 0.0, 1.0, 0.5, 0.01)
    asset_types = st.sidebar.multiselect("Asset Type", ["Stock", "ETF", "Crypto"], default=["Stock", "ETF", "Crypto"])
    search_symbol = st.sidebar.text_input("Search Symbol")

    filtered = df[df["confidence"] >= min_conf]
    if asset_types:
        filtered = filtered[filtered["Category"].isin(asset_types)]
    if search_symbol:
        filtered = filtered[filtered["symbol"].str.contains(search_symbol.upper(), na=False)]

    # === MAIN DISPLAY ===
    st.header("⭐ Today's Most Confident Picks")

    for _, row in filtered.iterrows():
        sym = row["symbol"]
        full_name = f"{symbol_glossary.get(sym, '🔎 Unknown')} ({sym})"
        edge = round(row['edge'] * 100, 2)

        with st.expander(f"🧠 {full_name} – {row['Label']} ({row['Confidence %']}% confidence)"):
            st.markdown(f"**Asset Type**: {row['Category']}  \n**Edge**: {edge}%")

            st.markdown("#### 🔬 Trade Juice")
            feature_cols = [col for col in row.index if col.startswith("features.")]
            feature_dict = {col.split("features.")[-1]: row[col] for col in feature_cols if pd.notnull(row[col])}

            cols = st.columns(2)
            for i, (key, val) in enumerate(feature_dict.items()):
                pretty = key.upper().replace("_", " ")
                if key == "rsi":
                    pretty = "RSI"
                elif key == "macd":
                    pretty = "MACD"
                elif key == "macd_signal":
                    pretty = "MACD Signal"
                elif key == "ema_20":
                    pretty = "EMA 20"
                elif key == "ema_50":
                    pretty = "EMA 50"
                elif key == "bb_upper":
                    pretty = "Bollinger Upper"
                elif key == "bb_lower":
                    pretty = "Bollinger Lower"
                elif key == "roc":
                    pretty = "Rate of Change"
                cols[i % 2].metric(pretty, round(val, 2))

    # === GLOSSARY ===
    with st.expander("📘 Glossary: Symbols & Signals"):
        st.markdown("#### 💡 Symbols")
        for k, v in symbol_glossary.items():
            st.markdown(f"- **{k}**: {v}")
        st.markdown("#### 📊 Indicators")
        for k, v in indicator_glossary.items():
            st.markdown(f"- **{k}**: {v}")

    # === DISCORD CTA ===
    st.markdown("---")
    st.markdown(
        '''
        <div style='padding: 1rem; border-radius: 10px; background: #222; text-align: center;'>
            <h4 style='color: #fff;'>🔥 Love Ninja Licks?</h4>
            <p style='color: #ccc;'>Get exclusive AI picks, live trade alerts, and connect with other traders.</p>
            <a href='https://discord.gg/yourserver' target='_blank' style='display:inline-block; padding:10px 20px; background:#5865F2; color:white; border-radius:5px; text-decoration:none; font-weight:bold;'>💬 Join Our Discord</a>
        </div>
        ''',
        unsafe_allow_html=True
    )

except Exception as e:
    st.error("❌ Failed to load predictions. Check your JSON file or contact support.")
