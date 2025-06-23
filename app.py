import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import io

# === LOAD DATA ===
with open("daily_predictions.json", "r") as f:
    predictions = json.load(f)

# Validate and convert to DataFrame
if not predictions or not all("features" in p for p in predictions):
    st.error("🚨 Missing required columns: ['features']")
    st.stop()

# Flatten and normalize
df = pd.json_normalize(predictions)

# Rename for consistency
df.rename(columns={"symbol": "Symbol", "Date": "Date", "confidence": "Confidence",
                   "edge": "Edge", "predicted_label_name": "Prediction", "features": "features"}, inplace=True)

# === UI CONFIG ===
st.set_page_config(page_title="📊 AI Stock Predictions", layout="wide")
st.title("📈 AI-Powered Stock Predictions Dashboard")
st.caption("💡 Built with XGBoost & Streamlit | Live edge & confidence insights")

# === FILTERS ===
col1, col2, col3 = st.columns(3)
symbols = sorted(df["Symbol"].unique())
selected_symbols = col1.multiselect("🔎 Filter by Symbols", symbols, default=symbols[:10])
min_conf = col2.slider("📶 Min Confidence", 0.5, 1.0, 0.55, 0.01)
pred_choice = col3.radio("📌 Prediction Type", ["All", "bullish", "bearish"])

# === FILTERED DATA ===
df_filtered = df[df["Symbol"].isin(selected_symbols)]
df_filtered = df_filtered[df_filtered["Confidence"] >= min_conf]
if pred_choice != "All":
    df_filtered = df_filtered[df_filtered["Prediction"] == pred_choice]

# === SORTING ===
sort_by = st.selectbox("🔃 Sort by", ["Confidence", "Edge", "Symbol", "Date"])
ascending = st.checkbox("⬆️ Sort ascending?", value=False)
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
    with st.expander(f"{row['Date']} - {row['Symbol']} ({row['Prediction']})"): 
        st.json(row["features"])

        # Line chart for technical indicators
        feature_df = pd.DataFrame([row["features"]])
        indicators = ["rsi", "macd", "macd_signal", "ema_20", "ema_50", "bb_upper", "bb_lower"]
        indicator_values = feature_df[indicators].T.rename(columns={0: "value"})
        st.line_chart(indicator_values)

# === SUMMARY ===
st.subheader("📊 Rolling Summary")
st.metric("Total Predictions", len(df_filtered))
st.metric("Avg Confidence", f"{df_filtered['Confidence'].mean():.2f}")
st.metric("Avg Edge", f"{df_filtered['Edge'].mean():.3f}")
