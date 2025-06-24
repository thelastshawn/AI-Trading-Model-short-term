import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import io

# === PAGE CONFIG ===
st.set_page_config(page_title="📊 AI Stock Predictions", layout="wide")

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
st.title("📈 AI-Powered Stock Predictions Dashboard")
st.caption("💡 Built with XGBoost & Streamlit | Live edge & confidence insights")

# === LOAD DATA ===
with open("daily_predictions.json", "r") as f:
    predictions = json.load(f)

if not predictions or not all("features" in p for p in predictions):
    st.error("🚨 Missing required columns: ['features']")
    st.stop()

df = pd.json_normalize(predictions)
df.rename(columns={"symbol": "Symbol", "Date": "Date", "confidence": "Confidence",
                   "edge": "Edge", "predicted_label_name": "Prediction", "features": "features"}, inplace=True)

# === FILTERS ===
st.sidebar.title("🧭 Filters")
symbols = sorted(df["Symbol"].unique())
selected_symbols = st.sidebar.multiselect("🔎 Symbols", symbols, default=symbols[:10])
min_conf = st.sidebar.slider("📶 Minimum Confidence", 0.5, 1.0, 0.55, 0.01)
pred_choice = st.sidebar.radio("📌 Prediction Type", ["All", "bullish", "bearish"])
sort_by = st.sidebar.selectbox("🔃 Sort by", ["Confidence", "Edge", "Symbol", "Date"])
ascending = st.sidebar.checkbox("⬆️ Sort ascending?", value=False)

# === FILTERED DATA ===
df_filtered = df[df["Symbol"].isin(selected_symbols)]
df_filtered = df_filtered[df_filtered["Confidence"] >= min_conf]
if pred_choice != "All":
    df_filtered = df_filtered[df_filtered["Prediction"] == pred_choice]
df_filtered = df_filtered.sort_values(by=sort_by, ascending=ascending)

# === DISPLAY TABLE ===
st.subheader("📋 Filtered Predictions")
st.dataframe(df_filtered[["Date", "Symbol", "Prediction", "Confidence", "Edge"]], use_container_width=True)

# === CSV DOWNLOAD ===
csv = df_filtered.to_csv(index=False)
st.download_button("⬇️ Download CSV", csv, "predictions.csv", "text/csv")

# === FEATURE SNAPSHOT ===
st.subheader("🧠 Feature Snapshot")
for idx, row in df_filtered.iterrows():
    with st.expander(f"🔍 {row['Date']} – {row['Symbol']} ({row['Prediction'].upper()})"):
        st.json(row["features"])

        # Line chart for technical indicators
        feature_df = pd.DataFrame([row["features"]])
        indicators = ["rsi", "macd", "macd_signal", "ema_20", "ema_50", "bb_upper", "bb_lower"]
        if all(indicator in feature_df.columns for indicator in indicators):
            indicator_values = feature_df[indicators].T.rename(columns={0: "Value"})
            st.line_chart(indicator_values)

# === SUMMARY METRICS ===
st.subheader("📊 Rolling Summary")
col1, col2, col3 = st.columns(3)
col1.metric("🧾 Total Predictions", len(df_filtered))
col2.metric("📶 Avg Confidence", f"{df_filtered['Confidence'].mean():.2f}")
col3.metric("💸 Avg Edge", f"{df_filtered['Edge'].mean():.3f}")
