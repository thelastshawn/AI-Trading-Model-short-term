import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import plotly.express as px

# Set page config
st.set_page_config(page_title="AI Market Predictions", layout="wide")

# Load predictions
json_path = "daily_predictions.json"
if not os.path.exists(json_path):
    st.error("Prediction file not found.")
    st.stop()

with open(json_path, 'r') as f:
    predictions = json.load(f)

df = pd.DataFrame(predictions)

# Full asset name mapping
asset_names = {
    'AAPL': 'Apple Inc (AAPL)',
    'MSFT': 'Microsoft Corp (MSFT)',
    'GOOG': 'Alphabet Inc (GOOG)',
    'QQQ': 'Invesco QQQ ETF (QQQ)',
    'SPY': 'SPDR S&P 500 ETF (SPY)',
    'TSLA': 'Tesla Inc (TSLA)',
    'NVDA': 'NVIDIA Corp (NVDA)',
    'AMZN': 'Amazon.com Inc (AMZN)',
    'META': 'Meta Platforms Inc (META)',
    'NFLX': 'Netflix Inc (NFLX)',
    'AMD': 'Advanced Micro Devices Inc (AMD)',
    'INTC': 'Intel Corp (INTC)',
    'DIS': 'Walt Disney Co (DIS)',
    'V': 'Visa Inc (V)',
    'JNJ': 'Johnson & Johnson (JNJ)',
    'WMT': 'Walmart Inc (WMT)',
    'JPM': 'JPMorgan Chase & Co (JPM)',
    'BA': 'Boeing Co (BA)',
    'PYPL': 'PayPal Holdings Inc (PYPL)',
    'KO': 'Coca-Cola Co (KO)',
    'BTC-USD': 'Bitcoin (BTC-USD)',
    'ETH-USD': 'Ethereum (ETH-USD)',
    'SOL-USD': 'Solana (SOL-USD)',
    'XRP-USD': 'Ripple (XRP-USD)',
    'ADA-USD': 'Cardano (ADA-USD)',
    'AVAX-USD': 'Avalanche (AVAX-USD)',
    'DOGE-USD': 'Dogecoin (DOGE-USD)'
}

# Map full names
df['full_name'] = df['asset'].map(asset_names)

# Format prediction with color and emoji
def format_prediction(row):
    emoji = "📈" if row['prediction'] == 'UP' else "📉"
    color = "#00cc44" if row['prediction'] == 'UP' else "#ff4d4d"
    return f"<span style='color:{color}'>{emoji} {row['prediction']}</span>"

df['prediction_display'] = df.apply(format_prediction, axis=1)

# Title & timestamp
st.title("📊 AI Market Predictions")
st.caption("Predicted movement for the next trading session")
st.caption(f"Updated: {datetime.now().strftime('%B %d, %Y @ %I:%M %p')}")

# Sidebar options
with st.sidebar:
    st.header("⚙️ Filters")
    sort_by = st.selectbox("Sort by:", ["confidence", "asset"])
    ascending = st.checkbox("Ascending order", value=False)
    min_conf = st.slider("Minimum Confidence", 0.0, 1.0, 0.5)

# Filter and sort data
df_filtered = df[df['confidence'] >= min_conf].sort_values(by=sort_by, ascending=ascending)

# Categorize assets
stock_assets = list(asset_names.keys())[:20]
crypto_assets = list(asset_names.keys())[20:]

stock_df = df_filtered[df_filtered['asset'].isin(stock_assets)]
crypto_df = df_filtered[df_filtered['asset'].isin(crypto_assets)]

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Stocks & ETFs", "💰 Crypto", "🔥 Top Picks"])

with tab1:
    st.subheader("Stock & ETF Predictions")
    st.write(stock_df[['full_name', 'prediction_display', 'confidence']].to_html(escape=False, index=False), unsafe_allow_html=True)

with tab2:
    st.subheader("Crypto Predictions")
    st.write(crypto_df[['full_name', 'prediction_display', 'confidence']].to_html(escape=False, index=False), unsafe_allow_html=True)

with tab3:
    st.subheader("Most Confident Picks (70%+)")
    confident = df_filtered[df_filtered['confidence'] > 0.7]
    if confident.empty:
        st.write("No high-confidence picks today.")
    else:
        for _, row in confident.iterrows():
            st.write(f"**{asset_names.get(row['asset'], row['asset'])}** → `{row['prediction']}` (Confidence: `{row['confidence']}`)")

# Optional: Acronym reference tab
with st.expander("ℹ️ Full Asset Name Reference"):
    for symbol, name in asset_names.items():
        st.write(f"- {name}")

# Plot confidence bar chart
st.subheader("📊 Confidence Levels by Asset")
fig = px.bar(df_filtered, x='full_name', y='confidence', color='prediction', title="Prediction Confidence", color_discrete_map={'UP': 'green', 'DOWN': 'red'})
st.plotly_chart(fig, use_container_width=True)

# Style
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)
