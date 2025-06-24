import streamlit as st
import pandas as pd
import json
from datetime import datetime

# App settings
st.set_page_config(page_title="Ninja Licks – AI Market Predictions", layout="wide")

st.markdown("<h1 style='text-align: center;'>💵 Ninja Licks – AI Stocks/ETF/Crypto Picks</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Grouped by confidence. Fresh predictions daily. History included.</p>", unsafe_allow_html=True)

# Load data
with open("daily_predictions.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)
df["confidence_pct"] = (df["confidence"] * 100).round(2)
df["edge_pct"] = (df["edge"] * 100).round(2)
df["asset_type"] = df["symbol"].apply(lambda x: "Crypto" if x.endswith("-USD") else "Stock/ETF")
df["Date"] = pd.to_datetime(df["Date"]).dt.date

# Today’s date
today = datetime.now().date()
today_df = df[df["Date"] == today]
history_df = df[df["Date"] < today]

# Dropdown for confidence
conf_options = ["All", "70%+", "60%+", "50%+", "<50%"]
asset_options = ["All", "Crypto", "Stock/ETF"]
symbol_options = ["All"] + sorted(df["symbol"].unique())
sort_options = ["Confidence", "Edge", "Symbol"]

# Filter bar
st.markdown("### 🎛️ Filter Settings")
col1, col2, col3, col4 = st.columns(4)
with col1:
    min_conf_sel = st.selectbox("🔽 Min Confidence", conf_options)
with col2:
    asset_filter = st.selectbox("💼 Asset Type", asset_options)
with col3:
    symbol_filter = st.selectbox("🔍 Symbol", symbol_options)
with col4:
    sort_option = st.selectbox("⬇️ Sort By", sort_options)

# Filter logic
def apply_filters(df):
    if min_conf_sel == "70%+":
        df = df[df["confidence_pct"] >= 70]
    elif min_conf_sel == "60%+":
        df = df[df["confidence_pct"] >= 60]
    elif min_conf_sel == "50%+":
        df = df[df["confidence_pct"] >= 50]
    elif min_conf_sel == "<50%":
        df = df[df["confidence_pct"] < 50]

    if asset_filter != "All":
        df = df[df["asset_type"] == asset_filter]
    if symbol_filter != "All":
        df = df[df["symbol"] == symbol_filter]
    if sort_option == "Confidence":
        df = df.sort_values(by="confidence", ascending=False)
    elif sort_option == "Edge":
        df = df.sort_values(by="edge", ascending=False)
    else:
        df = df.sort_values(by="symbol")
    return df

today_df = apply_filters(today_df)

# Top 3 Picks
st.markdown("### 🏆 Top 3 Picks for Today")
top3 = today_df.head(3)
if top3.empty:
    st.write("No fresh picks for today.")
else:
    medals = ["🥇", "🥈", "🥉"]
    for i, (_, row) in enumerate(top3.iterrows()):
        emoji = "📈" if row["prediction"] == 1 else "📉"
        st.markdown(
            f"<div style='padding:8px 12px;border:1px solid #444;border-radius:6px;margin-bottom:6px;background-color:#111;'>"
            f"<strong>{medals[i]} {row['symbol']}</strong> | {emoji} {row['predicted_label_name'].capitalize()} "
            f"| <span style='color:#00FF00'>{row['confidence_pct']}%</span> | 💥 {row['edge_pct']}% | 🗓️ {row['Date']}</div>",
            unsafe_allow_html=True
        )

# Grouped prediction display
high = today_df[today_df["confidence_pct"] >= 60]
medium = today_df[(today_df["confidence_pct"] >= 50) & (today_df["confidence_pct"] < 60)]
low = today_df[today_df["confidence_pct"] < 50]

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🔥 High", "🟡 Medium", "⚪ Low", "📘 Glossary", "🕘 History"])
groups = [(tab1, high), (tab2, medium), (tab3, low)]

def render_rows(group):
    if group.empty:
        st.markdown("<i>No predictions here today.</i>", unsafe_allow_html=True)
    else:
        for _, row in group.iterrows():
            emoji = "📈" if row["prediction"] == 1 else "📉"
            color = "#00FF00" if row["confidence_pct"] >= 60 else "#FFD700" if row["confidence_pct"] >= 50 else "#FF4444"
            st.markdown(
                f"<div style='font-size:15px;padding:6px 10px;border-bottom:1px solid #333;'>"
                f"<strong>{row['symbol']}</strong> | {emoji} {row['predicted_label_name'].capitalize()} "
                f"| <span style='color:{color}'>{row['confidence_pct']}%</span> "
                f"| 💥 {row['edge_pct']}% | 🗓️ {row['Date']}</div>",
                unsafe_allow_html=True
            )

# Show groups
for tab, group in groups:
    with tab:
        render_rows(group)

# Glossary
with tab4:
    st.markdown("### 📘 Glossary")
    st.markdown("""
    - **Symbol**: Stock or crypto ticker (e.g. BTC-USD, AAPL)
    - **Prediction**: 📈 Bullish (expected up), 📉 Bearish (expected down)
    - **Confidence**: AI certainty in the prediction
    - **Edge**: AI advantage over market pricing
    - **Date**: Day the prediction applies to
    """)

# History
with tab5:
    st.markdown("### 🕘 Prediction History")
    history_date = st.date_input("📅 Select Past Date", value=today)
    past_df = apply_filters(df[df["Date"] == history_date])
    if past_df.empty:
        st.write("No predictions found for that date.")
    else:
        render_rows(past_df)