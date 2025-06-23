import streamlit as st
import pandas as pd
import json
import os

# === SETUP ===
st.set_page_config(page_title="AI Trading Predictions", layout="wide")
st.title("📈 AI-Powered Trading Predictions")

# === LOAD PREDICTIONS ===
json_path = "daily_predictions.json"

if not os.path.exists(json_path):
    st.error("Prediction file not found.")
    st.stop()

with open(json_path, "r") as f:
    data = json.load(f)

if not isinstance(data, list) or len(data) == 0:
    st.error("No predictions available.")
    st.stop()

df = pd.DataFrame(data)

# Show available columns for debugging
# st.write("Loaded columns:", df.columns.tolist())

# === FILTERING OPTIONS ===
min_conf = st.slider("Minimum Confidence", min_value=0.0, max_value=1.0, value=0.5, step=0.01)

# Check for required columns and filter accordingly
if "confidence" not in df.columns:
    st.error("Missing 'confidence' column in prediction data.")
    st.stop()

# Handle sort options dynamically
default_sort_columns = ["confidence", "symbol"]
available_sort_columns = [col for col in default_sort_columns if col in df.columns]

if not available_sort_columns:
    st.error("No valid columns available for sorting.")
    st.stop()

sort_by = st.selectbox("Sort by:", available_sort_columns)
ascending = st.checkbox("Sort Ascending?", value=False)

# === DISPLAY RESULTS ===
df_filtered = df[df["confidence"] >= min_conf].sort_values(by=sort_by, ascending=ascending)

st.markdown(f"### 🔍 Filtered Predictions (Total: {len(df_filtered)})")
st.dataframe(df_filtered.reset_index(drop=True), use_container_width=True)
