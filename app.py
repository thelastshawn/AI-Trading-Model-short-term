import streamlit as st
import pandas as pd
import json

# Page settings
st.set_page_config(page_title="Ninja Licks – AI Market Predictions", layout="wide")

st.markdown("<h1 style='text-align: center;'>💵 Ninja Licks – AI Stocks/ETF/Crypto Picks</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Grouped by confidence level. Beginner-friendly. AI-powered.</p>", unsafe_allow_html=True)

# Load predictions
with open("daily_predictions.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)
df["confidence_pct"] = (df["confidence"] * 100).round(2)
df["edge_pct"] = (df["edge"] * 100).round(2)
df["asset_type"] = df["symbol"].apply(lambda x: "Crypto" if x.endswith("-USD") else "Stock/ETF")
df = df.sort_values(by="confidence", ascending=False)

# Top Filters
st.markdown("### 🎛️ Filter Settings")
col1, col2, col3, col4 = st.columns([2, 2, 2, 2])
with col1:
    min_conf = st.slider("📊 Min Confidence", 0, 100, 50)
with col2:
    asset_filter = st.selectbox("💼 Asset Type", ["All", "Crypto", "Stock/ETF"])
with col3:
    all_symbols = ["All"] + sorted(df["symbol"].unique())
    symbol_filter = st.selectbox("🔍 Symbol", all_symbols)
with col4:
    sort_option = st.selectbox("⬇️ Sort By", ["Confidence", "Edge", "Symbol"])

# Apply filters
filtered = df[df["confidence_pct"] >= min_conf]
if asset_filter != "All":
    filtered = filtered[filtered["asset_type"] == asset_filter]
if symbol_filter != "All":
    filtered = filtered[filtered["symbol"] == symbol_filter]
if sort_option == "Confidence":
    filtered = filtered.sort_values(by="confidence", ascending=False)
elif sort_option == "Edge":
    filtered = filtered.sort_values(by="edge", ascending=False)
else:
    filtered = filtered.sort_values(by="symbol")

# Top 3 Picks
top3 = filtered.head(3)
st.markdown("### 🏆 Top 3 Picks Overall")
if top3.empty:
    st.write("No high-confidence picks available.")
else:
    medals = ["🥇", "🥈", "🥉"]
    for i, (_, row) in enumerate(top3.iterrows()):
        emoji = "📈" if row["prediction"] == 1 else "📉"
        st.markdown(
            f"<div style='padding:8px 12px;border:1px solid #444;border-radius:6px;margin-bottom:6px;"
            f"background-color:#111;'><strong>{medals[i]} {row['symbol']}</strong> | {emoji} {row['predicted_label_name'].capitalize()} "
            f"| <span style='color:#00FF00'>{row['confidence_pct']}%</span> | 💥 {row['edge_pct']}% | 🗓️ {row['Date']}</div>",
            unsafe_allow_html=True
        )

# Group tabs
high = filtered[filtered["confidence_pct"] >= 60]
medium = filtered[(filtered["confidence_pct"] >= 50) & (filtered["confidence_pct"] < 60)]
low = filtered[filtered["confidence_pct"] < 50]

tab1, tab2, tab3, tab4 = st.tabs(["🔥 High Confidence", "🟡 Medium", "⚪ Low", "📘 Glossary"])
groups = [(tab1, high), (tab2, medium), (tab3, low)]

# Terminal-style prediction rows
def render_rows(group):
    if group.empty:
        st.markdown("<i>No predictions in this range.</i>", unsafe_allow_html=True)
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

# Render grouped tabs
for tab, group in groups:
    with tab:
        render_rows(group)

# Glossary tab
with tab4:
    st.markdown("### 📘 Glossary – What It All Means")
    st.markdown("""
    - **Symbol**: The stock, ETF, or crypto ticker (e.g. AAPL, BTC-USD).
    - **Prediction**: 📈 Bullish = expected to go up. 📉 Bearish = expected to drop.
    - **Confidence**: How sure the AI model is about the direction — higher = stronger signal.
    - **Edge**: Difference between predicted success and implied market odds (higher is better).
    - **Date**: The date the prediction applies to.
    """)