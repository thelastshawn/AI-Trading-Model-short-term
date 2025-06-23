import streamlit as st
import pandas as pd
import json
import os

# === LOAD DATA ===
json_path = "daily_predictions.json"

if not os.path.exists(json_path):
    st.error(f"Prediction file not found at {json_path}")
    st.stop()

with open(json_path, "r") as f:
    predictions = json.load(f)

# Convert to DataFrame
df = pd.json_normalize(predictions)

# Ensure required columns exist
required_cols = ["symbol", "Date", "confidence", "prediction", "predicted_label_name", "edge", "features"]
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Missing required columns: {missing_cols}")
    st.stop()

# Rename columns
df.rename(columns={
    "symbol": "Symbol",
    "Date": "Date",
    "confidence": "Confidence",
    "edge": "Edge",
    "predicted_label_name": "Prediction",
    "features": "Features"
}, inplace=True)

# === UI CONFIG ===
st.set_page_config(page_title="AI Trading Predictions", layout="wide")
st.title("📈 AI-Powered Stock Predictions")

# === FILTERS ===
col1, col2, col3 = st.columns(3)

symbols = sorted(df["Symbol"].unique())
selected_symbols = col1.multiselect("Select Symbols", symbols, default=symbols[:10])
min_conf = col2.slider("Minimum Confidence", 0.5, 1.0, 0.55, 0.01)
pred_choice = col3.radio("Prediction Type", ["All", "bullish", "bearish"])

# === FILTER DATA ===
df_filtered = df[df["Symbol"].isin(selected_symbols)]
df_filtered = df_filtered[df_filtered["Confidence"] >= min_conf]
if pred_choice != "All":
    df_filtered = df_filtered[df_filtered["Prediction"] == pred_choice]

# === SORTING ===
sort_by = st.selectbox("Sort by:", ["Confidence", "Edge", "Symbol", "Date"])
ascending = st.checkbox("Sort ascending?", value=False)
df_filtered = df_filtered.sort_values(by=sort_by, ascending=ascending)

# === DISPLAY TABLE ===
st.subheader("Filtered Predictions")
st.dataframe(df_filtered[["Date", "Symbol", "Prediction", "Confidence", "Edge"]])

# === DISPLAY FEATURE DETAILS ===
st.subheader("Feature Snapshot")
for idx, row in df_filtered.iterrows():
    with st.expander(f"{row['Date']} - {row['Symbol']} ({row['Prediction']})"): 
        if isinstance(row["Features"], dict):
            st.json(row["Features"])
        else:
            st.write("No feature data available.")
