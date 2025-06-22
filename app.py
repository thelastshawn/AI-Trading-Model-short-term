import streamlit as st
import pandas as pd
import json
import os

# Set page config
st.set_page_config(page_title="AI Market Predictions", layout="centered")

# Load predictions
json_path = "daily_predictions.json"  # Local file or use absolute Google Drive path
if not os.path.exists(json_path):
    st.error("Prediction file not found.")
    st.stop()

with open(json_path, 'r') as f:
    predictions = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(predictions)

# Title
st.title("📊 AI Market Predictions")

# Date or update note
st.caption("Predicted movement for the next trading session")

# Sorting options
sort_by = st.selectbox("Sort by:", ["confidence", "asset"])
ascending = st.checkbox("Ascending order", value=False)
df_sorted = df.sort_values(by=sort_by, ascending=ascending)

# Display predictions
st.dataframe(df_sorted, use_container_width=True)

# Highlight high-confidence picks
st.subheader("🔥 Most Confident Picks")
confident = df_sorted[df_sorted['confidence'] > 0.7]
if confident.empty:
    st.write("No high-confidence picks today.")
else:
    for _, row in confident.iterrows():
        st.write(f"**{row['asset']}** → `{row['prediction']}` (Confidence: `{row['confidence']}`)")
