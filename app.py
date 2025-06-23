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

# Handle % change color formatting
def format_pct(change):
    emoji = "🔺" if change > 0 else "🔻"
    color = "#00cc44" if change > 0 else "#ff4d4d"
    return f"<span style='color:{color}'>{emoji} {change:.2f}%</span>"

df['change_display'] = df['change_pct'].apply(format_pct)

# Format prediction with emoji
def format_prediction(row):
    emoji = "📈" if row['prediction'] == 'UP' else "📉"
    color = "#00cc44" if row['prediction'] == 'UP' else "#ff4d4d"
    return f"<span style='color:{color}'>{emoji} {row['prediction']}</span>"

df['prediction_display'] = df.apply(format_prediction, axis=1)

# Title & timestamp
st.title("📊 AI Market Predictions")
st.caption("Predicted movement for the next trading session")
st.caption(f"Updated: {datetime.now().strftime('%B %d, %Y @ %I:%M %p')}")

# Filters
sort_by = st.selectbox("Sort by:", ["confidence", "symbol"])
ascending = st.checkbox("Ascending order", value=False)
min_conf = st.slider("Minimum Confidence", 0.0, 1.0, 0.5)

# Filtered DataFrame
df_filtered = df[df['confidence'] >= min_conf].sort_values(by=sort_by, ascending=ascending)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Stocks", "💰 Crypto", "🟢 UP", "🔴 DOWN"])

# Stocks vs Crypto separation
stock_assets = df_filtered[~df_filtered['symbol'].str.contains("-USD")]
crypto_assets = df_filtered[df_filtered['symbol'].str.contains("-USD")]

with tab1:
    st.subheader("Stock Predictions")
    st.write(stock_assets[["name", "prediction_display", "confidence", "change_display", "open_price", "close_price"]].to_html(escape=False, index=False), unsafe_allow_html=True)

with tab2:
    st.subheader("Crypto Predictions")
    st.write(crypto_assets[["name", "prediction_display", "confidence", "change_display", "open_price", "close_price"]].to_html(escape=False, index=False), unsafe_allow_html=True)

with tab3:
    st.subheader("🟢 UP Predictions")
    up_df = df_filtered[df_filtered['prediction'] == 'UP']
    st.write(up_df[["name", "confidence", "change_display"]].to_html(escape=False, index=False), unsafe_allow_html=True)

with tab4:
    st.subheader("🔴 DOWN Predictions")
    down_df = df_filtered[df_filtered['prediction'] == 'DOWN']
    st.write(down_df[["name", "confidence", "change_display"]].to_html(escape=False, index=False), unsafe_allow_html=True)

# Most confident picks
st.subheader("🔥 Most Confident Picks (70%+)")
confident = df_filtered[df_filtered['confidence'] > 0.7]
if confident.empty:
    st.write("No high-confidence picks today.")
else:
    for _, row in confident.iterrows():
        direction = "⬆️" if row['prediction'] == 'UP' else "⬇️"
        st.write(
            f"**{row['name']}** → {direction} `{row['prediction']}` "
            f"(Confidence: `{row['confidence']:.2f}` | Open: `${row['open_price']}` → Close: `${row['close_price']}` | Change: `{row['change_pct']:.2f}%`)"
        )

# Confidence Bar Chart
st.subheader("📊 Confidence by Asset")
fig = px.bar(df_filtered, x='name', y='confidence', color='prediction', title='Confidence per Asset', text='confidence')
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
    This app uses an AI model trained on historical data with technical indicators (RSI, MACD, Bollinger Bands, ATR, and more).
    It predicts whether each asset's price will go UP or DOWN in the next session with confidence levels from XGBoost.
    """)

# Padding
st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
    padding-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)
