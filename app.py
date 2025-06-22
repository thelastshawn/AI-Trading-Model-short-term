import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# Set page config
st.set_page_config(page_title="AI Market Predictions", layout="centered")

# Load predictions
json_path = "daily_predictions.json"
if not os.path.exists(json_path):
    st.error("Prediction file not found.")
    st.stop()

with open(json_path, 'r') as f:
    predictions = json.load(f)

df = pd.DataFrame(predictions)

# Add full names for assets
asset_names = {
    'AAPL': 'Apple Inc (AAPL)',
    'MSFT': 'Microsoft Corp (MSFT)',
    'GOOG': 'Alphabet Inc (GOOG)',
    'QQQ': 'Invesco QQQ ETF (QQQ)',
    'SPY': 'SPDR S&P 500 ETF (SPY)',
    'BTC-USD': 'Bitcoin (BTC-USD)',
    'ETH-USD': 'Ethereum (ETH-USD)',
    'SOL-USD': 'Solana (SOL-USD)',
    'AMZN': 'Amazon.com Inc (AMZN)',
    'NVDA': 'NVIDIA Corporation (NVDA)',
    'TSLA': 'Tesla Inc (TSLA)',
    'META': 'Meta Platforms Inc (META)',
    'BRK-B': 'Berkshire Hathaway Inc (BRK-B)',
    'BABA': 'Alibaba Group (BABA)',
    'TSM': 'Taiwan Semiconductor (TSM)',
    'EWJ': 'iShares MSCI Japan ETF (EWJ)',
    'FXI': 'iShares China Large-Cap ETF (FXI)',
    'EWG': 'iShares MSCI Germany ETF (EWG)',
    'GLD': 'SPDR Gold Shares (GLD)',
    'SLV': 'iShares Silver Trust (SLV)',
    'UUP': 'Invesco US Dollar Index (UUP)',
    'FXE': 'Invesco Euro ETF (FXE)',
    'USO': 'United States Oil Fund (USO)',
    'XRP-USD': 'XRP (XRP-USD)',
    'DOGE-USD': 'Dogecoin (DOGE-USD)',
    'ADA-USD': 'Cardano (ADA-USD)',
    'AVAX-USD': 'Avalanche (AVAX-USD)'
}
df['full_name'] = df['asset'].map(asset_names).fillna(df['asset'])

# Format prediction with color and emoji
def format_prediction(row):
    emoji = "📈" if row['prediction'] == 'UP' else "📉"
    color = "#00cc44" if row['prediction'] == 'UP' else "#ff4d4d"
    return f"<span style='color:{color}'>{emoji} {row['prediction']}</span>"

df['prediction_display'] = df.apply(format_prediction, axis=1)

# Title & timestamp
st.title("📊 AI Market Predictions")
st.caption(f"Predicted movement for the next trading session")
st.caption(f"Updated: {datetime.now().strftime('%B %d, %Y @ %I:%M %p')}")

# Sorting and filtering
sort_by = st.selectbox("Sort by:", ["confidence", "asset"])
ascending = st.checkbox("Ascending order", value=False)
min_conf = st.slider("Minimum Confidence", 0.0, 1.0, 0.5)

# Filtered and sorted dataframe
df_filtered = df[df['confidence'] >= min_conf].sort_values(by=sort_by, ascending=ascending)

# Define categories
stock_assets = ['AAPL', 'MSFT', 'GOOG', 'QQQ', 'SPY', 'AMZN', 'NVDA', 'TSLA', 'META', 'BRK-B']
global_assets = ['BABA', 'TSM', 'EWJ', 'FXI', 'EWG']
commodity_assets = ['GLD', 'SLV', 'UUP', 'FXE', 'USO']
crypto_assets = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'XRP-USD', 'DOGE-USD', 'ADA-USD', 'AVAX-USD']

# Filter by category
def render_category(title, symbols):
    category_df = df_filtered[df_filtered['asset'].isin(symbols)]
    if not category_df.empty:
        st.subheader(title)
        st.write(category_df[['full_name', 'prediction_display', 'confidence']].to_html(escape=False, index=False), unsafe_allow_html=True)

render_category("📈 U.S. Stocks", stock_assets)
render_category("🌍 Global Stocks/ETFs", global_assets)
render_category("🪙 Commodities & Currencies", commodity_assets)
render_category("💰 Cryptocurrencies", crypto_assets)

# Most confident picks
st.subheader("🔥 Most Confident Picks (70%+)")
confident = df_filtered[df_filtered['confidence'] > 0.7]
if confident.empty:
    st.write("No high-confidence picks today.")
else:
    for _, row in confident.iterrows():
        st.write(f"**{asset_names.get(row['asset'], row['asset'])}** → `{row['prediction']}` (Confidence: `{row['confidence']}`)")

# Optional: Acronym reference tab
with st.expander("ℹ️ Full Asset Name Reference"):
    for symbol, name in sorted(asset_names.items()):
        st.write(f"- {name}")

# Style adjustment for padding
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)
