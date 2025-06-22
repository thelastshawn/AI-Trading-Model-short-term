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
    'TSLA': 'Tesla Inc (TSLA)',
    'NVDA': 'NVIDIA Corp (NVDA)',
    'META': 'Meta Platforms Inc (META)',
    'AMZN': 'Amazon.com Inc (AMZN)',
    'ARKK': 'ARK Innovation ETF (ARKK)',
    'DIA': 'SPDR Dow Jones ETF (DIA)',
    'IWM': 'Russell 2000 ETF (IWM)',
    'BNB-USD': 'BNB (BNB-USD)',
    'XRP-USD': 'Ripple (XRP-USD)',
    'DOGE-USD': 'Dogecoin (DOGE-USD)',
    'ADA-USD': 'Cardano (ADA-USD)'
}
df['full_name'] = df['asset'].map(asset_names)

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

# Filters
sort_by = st.selectbox("Sort by:", ["confidence", "asset"])
ascending = st.checkbox("Ascending order", value=False)
min_conf = st.slider("Minimum Confidence", 0.0, 1.0, 0.5)

# Filtered and sorted dataframe
df_filtered = df[df['confidence'] >= min_conf].sort_values(by=sort_by, ascending=ascending)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Stocks", "💰 Crypto", "🟢 UP", "🔴 DOWN"])

with tab1:
    stock_assets = [k for k in asset_names if k not in ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'XRP-USD', 'DOGE-USD', 'ADA-USD']]
    stock_df = df_filtered[df_filtered['asset'].isin(stock_assets)]
    st.subheader("Stock Predictions")
    st.write(stock_df[['full_name', 'prediction_display', 'confidence']].to_html(escape=False, index=False), unsafe_allow_html=True)

with tab2:
    crypto_assets = [k for k in asset_names if k not in stock_assets]
    crypto_df = df_filtered[df_filtered['asset'].isin(crypto_assets)]
    st.subheader("Crypto Predictions")
    st.write(crypto_df[['full_name', 'prediction_display', 'confidence']].to_html(escape=False, index=False), unsafe_allow_html=True)

with tab3:
    up_df = df_filtered[df_filtered['prediction'] == 'UP']
    st.subheader("🟢 UP Predictions")
    st.write(up_df[['full_name', 'confidence']].to_html(escape=False, index=False), unsafe_allow_html=True)

with tab4:
    down_df = df_filtered[df_filtered['prediction'] == 'DOWN']
    st.subheader("🔴 DOWN Predictions")
    st.write(down_df[['full_name', 'confidence']].to_html(escape=False, index=False), unsafe_allow_html=True)

# Most confident picks
st.subheader("🔥 Most Confident Picks (70%+)")
confident = df_filtered[df_filtered['confidence'] > 0.7]
if confident.empty:
    st.write("No high-confidence picks today.")
else:
    for _, row in confident.iterrows():
        st.write(f"**{asset_names[row['asset']]}** → `{row['prediction']}` (Confidence: `{row['confidence']}`)")

# Confidence Bar Chart
st.subheader("📊 Confidence by Asset")
fig = px.bar(df_filtered, x='full_name', y='confidence', color='prediction', title='Confidence per Asset', text='confidence')
fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
fig.update_layout(xaxis_tickangle=-45, height=600)
st.plotly_chart(fig, use_container_width=True)

# Download button
st.download_button(
    label="Download Predictions as CSV",
    data=df_filtered.to_csv(index=False).encode('utf-8'),
    file_name="daily_predictions.csv",
    mime="text/csv"
)

# Info section
with st.expander("🤖 How does this work?"):
    st.write("""
    This app uses an AI model trained on historical data with technical indicators like RSI, MACD, Bollinger Bands, ATR, and more.
    It predicts whether each asset's price will go UP or DOWN in the next trading session and gives a confidence score based on XGBoost probability.
    """)

# Acronym reference
with st.expander("ℹ️ Full Asset Name Reference"):
    for symbol, name in asset_names.items():
        st.write(f"- {name}")

# Padding
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)
