import streamlit as st
import json
import pandas as pd

# Page setup
st.set_page_config(page_title="Ninja Licks – AI Trading Dashboard", layout="wide")

# Load prediction data
with open("daily_predictions.json", "r") as f:
    data = json.load(f)
df = pd.DataFrame(data)

# Header
st.markdown("### 💸 **Ninja Licks – AI Stocks/ETF/Crypto Market Predictions**")
st.markdown("_A bold, beginner-friendly trading dashboard powered by AI._")

# Tabs
tabs = st.tabs(["📈 Picks", "📚 Glossary", "📊 Trends"])

# 1. PICKS TAB
with tabs[0]:
    st.markdown("## ⭐ Today's Most Confident Picks")

    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        min_conf = st.slider("Min Confidence", 0.5, 1.0, 0.7, 0.01)
        asset_types = st.multiselect("Asset Type", options=["Stock", "ETF", "Crypto"], default=["Stock", "ETF", "Crypto"])
        search = st.text_input("Search Symbol")

    filtered_df = df[(df["confidence"] >= min_conf)]
    if asset_types:
        filtered_df = filtered_df[filtered_df["category"].isin(asset_types)]
    if search:
        filtered_df = filtered_df[filtered_df["symbol"].str.contains(search.upper())]

    filtered_df = filtered_df.sort_values(by="confidence", ascending=False)

    # Display predictions
    for _, row in filtered_df.iterrows():
        with st.expander(f"🧠 {row['symbol']} — {'📈 Bullish' if row['prediction']==1 else '📉 Bearish'} ({round(row['confidence']*100, 2)}% confidence)"):
            st.markdown(f"**Asset Type:** {row['category']}  |  **Edge:** {round(row['edge']*100, 2)}%")
            st.divider()
            st.markdown("#### 📊 Trade Juice")
            try:
                feat = row["features"]
                col1, col2, col3 = st.columns(3)
                for i, (k, v) in enumerate(feat.items()):
                    if isinstance(v, float) or isinstance(v, int):
                        with [col1, col2, col3][i % 3]:
                            st.metric(label=k.replace("_", " ").upper(), value=round(v, 2))
            except Exception:
                st.warning("⚠️ No signals available for this asset.")

# 2. GLOSSARY TAB
with tabs[1]:
    st.markdown("## 📚 Glossary of Key Terms")
    glossary = {
        "RSI": "Relative Strength Index – measures momentum. >70 = overbought, <30 = oversold.",
        "MACD": "Moving Average Convergence Divergence – trend-following momentum indicator.",
        "Bollinger Bands": "Volatility bands set above/below a moving average.",
        "EMA 20 / 50": "Exponential Moving Average over 20 or 50 days.",
        "ROC": "Rate of Change – how fast price is changing. Can show momentum.",
        "Edge": "How much our model sees advantage vs the market's implied odds.",
        "Confidence": "How sure our AI is that the signal will go the predicted direction.",
    }
    for term, explanation in glossary.items():
        st.markdown(f"**{term}** — {explanation}")

# 3. TRENDS TAB (Placeholder for now)
with tabs[2]:
    st.markdown("## 📊 Trends & Insights")
    st.info("🚧 Coming soon: this section will visualize bullish/bearish volume trends, top movers, and signal accuracy over time.")

# CTA
st.markdown("""
<hr>
<div style='text-align: center; padding: 10px 0;'>
    <h4>💬 Want more? Join our trading Discord for bonus picks + alerts!</h4>
    <a href='https://discord.gg/yourserver' target='_blank' style='background:#5865F2; padding:10px 20px; color:white; border-radius:5px; text-decoration:none;'>Join Ninja Licks Discord</a>
</div>
""", unsafe_allow_html=True)
