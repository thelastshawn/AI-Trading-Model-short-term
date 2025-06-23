import streamlit as st
import pandas as pd
import json
from PIL import Image
import plotly.express as px

# === PAGE CONFIG ===
st.set_page_config(page_title="📊 AI Trading Model", layout="wide")

# === CUSTOM CSS ===
st.markdown("""
<style>
    .main {
        background-color: #0f1117;
        color: #f0f0f0;
    }
    h1, h2, h3 {
        color: #00ffe5;
    }
    .stButton > button {
        background-color: #1f77b4;
        color: white;
        font-weight: bold;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# === HEADER ===
st.image("https://i.imgur.com/J2pAq.png", use_column_width=True)
st.title("📈 AI-Powered Short-Term Trading Predictions")
st.caption("💡 Powered by XGBoost | Confidence & Edge Calculated Live")

# === LOAD DATA ===
with open("daily_predictions.json", "r") as f:
    predictions = json.load(f)

if not predictions or not all("features" in p for p in predictions):
    st.error("🚨 Missing required columns: ['features']")
    st.stop()

df = pd.json_normalize(predictions)
df.rename(columns={"symbol": "Symbol", "Date": "Date", "confidence": "Confidence",
                   "edge": "Edge", "predicted_label_name": "Prediction", "features": "features"}, inplace=True)

# === CATEGORY TAGGING ===
def classify(symbol):
    if symbol.upper() in ["BTC", "ETH", "SOL", "DOGE"]:
        return "Crypto"
    elif symbol.upper() in ["SPY", "QQQ", "VTI", "ARKK"]:
        return "ETF"
    else:
        return "Stock"

df["Category"] = df["Symbol"].apply(classify)

# === FILTER SIDEBAR ===
st.sidebar.title("🧭 Controls")
selected_category = st.sidebar.radio("Category", ["All", "Stock", "ETF", "Crypto"])
min_conf = st.sidebar.slider("🔍 Min Confidence", 0.0, 1.0, 0.6)
min_edge = st.sidebar.slider("💸 Min Edge", 0.0, 1.0, 0.1)

# === APPLY FILTERS ===
filtered_df = df[(df["Confidence"] >= min_conf) & (df["Edge"] >= min_edge)]
if selected_category != "All":
    filtered_df = filtered_df[filtered_df["Category"] == selected_category]

# === TOP PICK HIGHLIGHT ===
if not filtered_df.empty:
    top_pick = filtered_df.loc[filtered_df["Confidence"].idxmax()]
    st.success(f"🚀 **Top Pick:** `{top_pick['Symbol']}` | {top_pick['Prediction'].upper()} | Confidence: `{top_pick['Confidence']:.2%}`")

# === TABBED OUTPUT ===
tabs = st.tabs(["📈 Stocks", "📘 ETFs", "🪙 Crypto"])
categories = ["Stock", "ETF", "Crypto"]
for tab, cat in zip(tabs, categories):
    with tab:
        cat_df = filtered_df[filtered_df["Category"] == cat]
        if cat_df.empty:
            st.info(f"No {cat.lower()} match current filters.")
        else:
            for _, row in cat_df.iterrows():
                with st.expander(f"🔍 {row['Symbol']} | {row['Prediction'].upper()}"):
                    st.markdown(f"""
**🗓️ Date**: {row['Date']}  
**📈 Confidence**: {row['Confidence']:.2%}  
**💸 Edge**: {row['Edge']:.2%}  
**🧠 Features**:
""")
                    st.json(row["features"])

# === INTERACTIVE SCATTER PLOT ===
if not filtered_df.empty:
    st.subheader("📊 Confidence vs Edge")
    fig = px.scatter(filtered_df, x="Edge", y="Confidence", color="Category", hover_data=["Symbol", "Prediction"])
    st.plotly_chart(fig, use_container_width=True)

# === DOWNLOAD CSV ===
st.download_button("📥 Download Filtered Predictions", filtered_df.to_csv(index=False), "filtered_predictions.csv", "text/csv")