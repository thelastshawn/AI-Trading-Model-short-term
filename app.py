
import streamlit as st
import json
import pandas as pd

# Page config
st.set_page_config(page_title="Ninja Licks – AI Market Predictions", layout="wide")

# Load data
with open("daily_predictions.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Infer 'category' if missing
if 'category' not in df.columns:
    def infer_category(symbol):
        if '-USD' in symbol:
            return 'Crypto'
        elif symbol.isupper() and len(symbol) <= 5:
            return 'Stock'
        else:
            return 'ETF'
    df['category'] = df['symbol'].apply(infer_category)

# Sidebar filters
st.sidebar.header("🔍 Filters")
min_conf = st.sidebar.slider("Min Confidence", 0.5, 1.0, 0.6, 0.01)
asset_types = st.sidebar.multiselect("Asset Type", ["Stock", "ETF", "Crypto"], default=["Stock", "ETF", "Crypto"])
search_query = st.sidebar.text_input("Search Symbol")

# Main tabs
tabs = st.tabs(["📈 Picks", "📘 Glossary", "📊 Trends"])

with tabs[0]:
    st.markdown("## ⭐ Today's Most Confident Picks")
    filtered_df = df[df["confidence"] >= min_conf]
    filtered_df = filtered_df[filtered_df["category"].isin(asset_types)]
    if search_query:
        filtered_df = filtered_df[filtered_df["symbol"].str.contains(search_query, case=False)]
    filtered_df = filtered_df.sort_values(by="confidence", ascending=False)

    for _, row in filtered_df.iterrows():
        with st.expander(f"🧠 {row.get('name', row['symbol'])} ({row['symbol']}) – {'📈 Bullish' if row['prediction'] == 1 else '📉 Bearish'} ({row['confidence']*100:.2f}% confidence)"):
            st.write(f"**Asset Type**: {row['category']}  |  **Edge**: {row['edge']*100:.2f}%")
            st.subheader("📊 Trader Signals")
            features = row.get("features", {})
            for key, val in features.items():
                st.write(f"**{key.replace('_', ' ').title()}**: {val}")

with tabs[1]:
    st.markdown("## 📘 Glossary")
    glossary = {
        "RSI": "Relative Strength Index – a momentum indicator that measures the speed and change of price movements.",
        "MACD": "Moving Average Convergence Divergence – shows the relationship between two EMAs.",
        "EMA": "Exponential Moving Average – a type of moving average that gives more weight to recent prices.",
        "ROC": "Rate of Change – measures the speed at which a price is changing.",
        "BB": "Bollinger Bands – volatility bands placed above and below a moving average."
    }
    for term, definition in glossary.items():
        st.markdown(f"**{term}**: {definition}")

with tabs[2]:
    st.markdown("## 🔮 Upcoming Features")
    st.write("📈 Weekly trend heatmaps")
    st.write("📤 Discord signal bot integration")
    st.write("💡 Beginner trade guides")
    st.write("💰 Premium signal access")
    st.markdown("**Want to join our early Discord?** [Click here](https://discord.gg/yourserver) 🚀")

