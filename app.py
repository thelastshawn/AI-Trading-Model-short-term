import streamlit as st
import pandas as pd
import datetime
from io import BytesIO
import base64
import plotly.express as px

# Load predictions
@st.cache_data
def load_predictions():
    try:
        df = pd.read_json("daily_predictions.json")
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    except:
        return pd.DataFrame()

df = load_predictions()
today = pd.Timestamp.now().normalize()

# Fallback to most recent per symbol if no data for today
def get_latest_per_symbol(df):
    return df.sort_values("Date").groupby("symbol", as_index=False).last()

fresh_df = df[df["Date"] == today]
if fresh_df.empty:
    fresh_df = get_latest_per_symbol(df)

# App Layout
st.set_page_config(page_title="Ninja Licks - AI Predictions", layout="wide")
st.title("💸 Ninja Licks – AI Stocks/ETF/Crypto Picks")
st.caption("Grouped by confidence. Fresh predictions daily. History included.")

tabs = st.tabs(["📈 Predictions", "📊 Charts", "📚 Glossary", "🕒 History"])

# ----------------------
# 📈 Predictions Tab
# ----------------------
with tabs[0]:
    st.header("🧮 Filter Settings")
    min_conf = st.selectbox("📉 Min Confidence", options=[50, 60, 65, 70, 75, 80, 85, 90], index=0)
    asset_type = st.selectbox("🧾 Asset Type", options=["All", "Stock/ETF", "Crypto"])
    symbol_filter = st.selectbox("🔍 Symbol", options=["All"] + sorted(df["symbol"].unique().tolist()))
    sort_by = st.selectbox("📊 Sort By", options=["Confidence", "Edge", "Symbol"])

    display_df = fresh_df.copy()
    if asset_type != "All":
        display_df = display_df[display_df["asset_type"] == asset_type]
    if symbol_filter != "All":
        display_df = display_df[display_df["symbol"] == symbol_filter]
    display_df = display_df[display_df["confidence"] >= min_conf / 100]
    display_df = display_df.sort_values(by=sort_by.lower(), ascending=False)

    st.subheader("🏆 Top 3 Picks for Today")
    top3 = display_df.head(3)
    if not top3.empty:
        for i, row in top3.iterrows():
            st.markdown(f"**{row['symbol']}** | {'📈 Bullish' if row['prediction'] == 1 else '📉 Bearish'} | **{row['confidence']:.2%}** 💥 {row['edge']:.2%} 📅 {row['Date'].date()}")
    else:
        st.warning("No predictions here today.")

    # Confidence bands
    st.markdown("""
    <style>
    .legend { display: flex; gap: 10px; margin-top: 10px; }
    .legend span { display: flex; align-items: center; gap: 5px; }
    </style>
    <div class='legend'>
        <span>🔴 High</span>
        <span>🟡 Medium</span>
        <span>⚪ Low</span>
    </div>
    """, unsafe_allow_html=True)

# ----------------------
# 📊 Charts Tab
# ----------------------
with tabs[1]:
    st.header("📊 Confidence & Edge Charts")
    chart_symbol = st.selectbox("Select Symbol", sorted(df["symbol"].unique()))
    chart_metric = st.radio("Metric", ["confidence", "edge"])
    df_chart = df[df["symbol"] == chart_symbol].sort_values("Date")
    fig = px.line(df_chart, x="Date", y=chart_metric, title=f"{chart_metric.title()} Over Time: {chart_symbol}")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------
# 📚 Glossary Tab
# ----------------------
with tabs[2]:
    st.header("📘 Beginner Glossary")
    glossary = {
        "Bullish": "Expecting the price to go up 📈",
        "Bearish": "Expecting the price to go down 📉",
        "Confidence": "How certain the AI is in its prediction (0-100%) 🤖",
        "Edge": "How much advantage this prediction has vs. market odds 🎯",
        "ETF": "Exchange-Traded Fund – a basket of stocks you can trade like a stock",
        "Symbol": "A shorthand code for a stock or crypto asset (e.g. AAPL or BTC-USD)",
        "Prediction": "The direction the AI believes the market will move",
        "AI-powered": "Backed by machine learning models trained on financial data 🧠",
        "RSI": "Relative Strength Index – tells if something is overbought or oversold",
        "MACD": "Moving Average Convergence Divergence – trend-following momentum indicator",
        "Volume": "How much of an asset is traded during a time period 📊"
    }
    for term, definition in glossary.items():
        st.markdown(f"**{term}** – {definition}")

# ----------------------
# 🕒 History Tab
# ----------------------
with tabs[3]:
    st.header("🕒 Prediction History")
    date_range = st.date_input("Select Date Range", value=(df["Date"].min(), df["Date"].max()))
    history_symbols = st.multiselect("Symbols", options=sorted(df["symbol"].unique()), default=list(df["symbol"].unique()))
    confidence_range = st.slider("Min Confidence", 50, 100, (50, 100))

    history_df = df[(df["Date"] >= pd.to_datetime(date_range[0])) &
                    (df["Date"] <= pd.to_datetime(date_range[1])) &
                    (df["symbol"].isin(history_symbols)) &
                    (df["confidence"] * 100 >= confidence_range[0]) &
                    (df["confidence"] * 100 <= confidence_range[1])]

    st.dataframe(history_df, use_container_width=True)

    csv = history_df.to_csv(index=False).encode("utf-8")
    xlsx = BytesIO()
    with pd.ExcelWriter(xlsx, engine='xlsxwriter') as writer:
        history_df.to_excel(writer, index=False, sheet_name='Predictions')
    xlsx.seek(0)

    st.download_button("⬇️ Download CSV", csv, "history.csv", "text/csv")
    st.download_button("📊 Download Excel", xlsx, "history.xlsx")

    st.markdown("---")
    st.subheader("🧾 Printable Report (PDF-style view)")
    for _, row in history_df.iterrows():
        st.markdown(f"**{row['symbol']}** | {'📈 Bullish' if row['prediction'] == 1 else '📉 Bearish'} | Confidence: {row['confidence']:.2%} | Edge: {row['edge']:.2%} | Date: {row['Date'].date()}")
