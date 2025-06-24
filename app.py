import streamlit as st
import pandas as pd
import json

# Page config
st.set_page_config(page_title="Ninja Licks – AI Market Predictions", layout="wide")

st.markdown("<h1 style='text-align: center;'>💵 Ninja Licks – AI Stocks/ETF/Crypto Picks</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Grouped by confidence level, optimized for clarity.</p>", unsafe_allow_html=True)

# Load predictions from file
with open("daily_predictions.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)
df["confidence_pct"] = (df["confidence"] * 100).round(2)
df["edge_pct"] = (df["edge"] * 100).round(2)
df["asset_type"] = df["symbol"].apply(lambda x: "Crypto" if x.endswith("-USD") else "Stock/ETF")
df = df.sort_values(by="confidence", ascending=False)

# Filter bar
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

# Grouping
high = filtered[filtered["confidence_pct"] >= 60]
medium = filtered[(filtered["confidence_pct"] >= 50) & (filtered["confidence_pct"] < 60)]
low = filtered[filtered["confidence_pct"] < 50]

# Tab Layout
tabs = st.tabs(["🔥 High Confidence (60%+)", "🟡 Medium (50–59.9%)", "⚪ Low (< 50%)"])
groups = [high, medium, low]

for tab, group in zip(tabs, groups):
    with tab:
        if group.empty:
            st.markdown("No predictions in this range.")
        else:
            for _, row in group.iterrows():
                emoji = "📈" if row["prediction"] == 1 else "📉"
                color = "#00FF00" if row["confidence_pct"] >= 60 else "#FFD700" if row["confidence_pct"] >= 50 else "#FF5555"
                st.markdown(
                    f"<div style='padding:6px 10px;border-bottom:1px solid #333;'>"
                    f"<strong>{row['symbol']}</strong> | {emoji} {row['predicted_label_name'].capitalize()} "
                    f"| <span style='color:{color}'>{row['confidence_pct']}%</span> "
                    f"| 💥 {row['edge_pct']}% | 🗓️ {row['Date']}"
                    f"</div>",
                    unsafe_allow_html=True
                )