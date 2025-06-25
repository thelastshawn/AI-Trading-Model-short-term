# --- START OF FILE ---
import streamlit as st
import pandas as pd
import json
import datetime
from io import BytesIO
import plotly.express as px
from datetime import date

# Load predictions
def load_predictions():
    try:
        with open("daily_predictions.json", "r") as f:
            data = json.load(f)
        return pd.DataFrame(data)
    except Exception as e:
        st.error("Error loading predictions.")
        return pd.DataFrame()

# Convert date string to date object
def parse_date(d):
    try:
        return datetime.datetime.strptime(d, "%Y-%m-%d").date()
    except:
        return None

# Confidence coloring
CONFIDENCE_COLOR = {
    "High": "🔴",
    "Medium": "🟡",
    "Low": "⚪",
}

def get_confidence_label(conf):
    if conf >= 0.66:
        return "High"
    elif conf >= 0.4:
        return "Medium"
    else:
        return "Low"

# Export helpers
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    return output.getvalue()

# Set up Streamlit app
st.set_page_config(page_title="Ninja Licks", layout="wide")
st.markdown("""
    <h1>🥷💸 Ninja Licks – AI Stocks/ETF/Crypto Picks</h1>
    <p>Grouped by confidence. Fresh predictions daily. History included.</p>
""", unsafe_allow_html=True)

# Load data
df = load_predictions()
df['Date'] = df['Date'].apply(parse_date)

# Tabs
tabs = st.tabs(["📊 Predictions", "📈 Charts", "📁 Reports & Exports", "📘 Glossary"])

# ----------------------------
# 📊 Predictions Tab
# ----------------------------
with tabs[0]:
    st.subheader("🏆 Top 3 Picks for Today")
    today = date.today()
    todays = df[df['Date'] == today]

    if todays.empty:
        todays = df[df['Date'] == df['Date'].max()]

    top3 = todays.sort_values(by="confidence", ascending=False).head(3)
    for i, row in top3.iterrows():
        label = get_confidence_label(row['confidence'])
        emoji = CONFIDENCE_COLOR[label]
        st.markdown(f"**{i+1}. {row['symbol']}** | 📈 {row['predicted_label_name'].capitalize()} | **{round(row['confidence']*100,2)}%** {emoji} | {round(row['edge']*100,2)}% | 📅 {row['Date']}")

    st.divider()
    st.markdown("### 🔻 Other Picks")
    rest = todays.sort_values(by="confidence", ascending=False).iloc[3:20]
    if not rest.empty:
        for i, row in rest.iterrows():
            label = get_confidence_label(row['confidence'])
            emoji = CONFIDENCE_COLOR[label]
            st.markdown(f"**{row['symbol']}** | 📈 {row['predicted_label_name'].capitalize()} | **{round(row['confidence']*100,2)}%** {emoji} | {round(row['edge']*100,2)}% | 📅 {row['Date']}")
    else:
        st.markdown("*No additional picks today.*")

    st.markdown("**Confidence Key:** 🔴 High | 🟡 Medium | ⚪ Low")

# ----------------------------
# 📈 Charts Tab
# ----------------------------
with tabs[1]:
    st.subheader("📈 Visual Trends")
    st.markdown("Select an asset to view confidence trends over time.")
    selected_symbol = st.selectbox("Choose Symbol", sorted(df['symbol'].unique()))
    chart_df = df[df['symbol'] == selected_symbol].sort_values(by='Date')
    fig = px.line(chart_df, x='Date', y='confidence', title=f"Confidence Over Time – {selected_symbol}")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# 📁 Reports & Exports Tab
# ----------------------------
with tabs[2]:
    st.subheader("🕓 Prediction History")
    start_date, end_date = st.date_input("Select Date Range", value=[df['Date'].min(), df['Date'].max()])
    symbols = st.multiselect("Symbols", options=sorted(df['symbol'].unique()), default=sorted(df['symbol'].unique()))
    min_conf = st.slider("Min Confidence", 0, 100, 50)

    filtered = df[
        (df['Date'] >= start_date) &
        (df['Date'] <= end_date) &
        (df['symbol'].isin(symbols)) &
        (df['confidence']*100 >= min_conf)
    ].copy()

    if 'features' in filtered.columns:
        del filtered['features']

    st.dataframe(filtered)

    csv = filtered.to_csv(index=False).encode('utf-8')
    xlsx = to_excel(filtered)
    st.download_button("📥 Download CSV", csv, "predictions.csv")
    st.download_button("📊 Download Excel", xlsx, "predictions.xlsx")

# ----------------------------
# 📘 Glossary Tab
# ----------------------------
with tabs[3]:
    st.subheader("📘 Beginner Glossary")
    st.markdown("""
    - **Confidence**: The AI's belief in its prediction (higher = more confident)
    - **Edge**: How much better the AI thinks this trade is than a coin flip
    - **Bullish/Bearish**: Predicting price will go up/down
    - **RSI**: Relative Strength Index – helps spot overbought/oversold levels
    - **MACD**: Moving Average Convergence Divergence – momentum indicator
    - **EMA**: Exponential Moving Average – used to smooth price data
    - **Predicted Label**: AI's decision (bullish or bearish)
    - **Symbol**: Ticker symbol (e.g., AAPL, ETH-USD, SPY)
    - **Asset Type**: Stock, ETF, or Crypto
    - **Volume**: The number of shares or tokens traded
    - **ROC**: Rate of Change – percentage speed of price movement
    - **BB Upper/Lower**: Bollinger Bands – range volatility indicators
""")
# --- END OF FILE ---
