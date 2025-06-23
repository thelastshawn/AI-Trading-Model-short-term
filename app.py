import streamlit as st
import pandas as pd
import json

# === Load JSON Predictions ===
with open("daily_predictions.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# === Convert Types ===
df["confidence"] = df["confidence"].astype(float)
df["edge"] = df["edge"].astype(float)
df["date"] = pd.to_datetime(df["date"])

# === UI Layout ===
st.title("📈 AI Daily Trading Predictions")
st.subheader("Model Output (Short-Term)")

# === Filters ===
st.markdown("### Filters:")
min_conf = st.slider("Minimum Confidence", 0.5, 1.0, 0.7, 0.01)
min_edge = st.slider("Minimum Edge (%)", 0.0, 10.0, 1.0, 0.1)
category = st.multiselect("Confidence Category", options=df["confidence_category"].unique(), default=df["confidence_category"].unique())
direction = st.multiselect("Direction", options=df["direction"].unique(), default=df["direction"].unique())
sort_by = st.selectbox("Sort by:", ["confidence", "edge", "symbol", "date"])
ascending = st.checkbox("Ascending", value=False)

# === Filter Data ===
df_filtered = df[
    (df["confidence"] >= min_conf) &
    (df["edge"] >= min_edge) &
    (df["confidence_category"].isin(category)) &
    (df["direction"].isin(direction))
].sort_values(by=sort_by, ascending=ascending)

# === Display ===
st.markdown(f"### 🔍 Showing {len(df_filtered)} predictions")
st.dataframe(
    df_filtered[["symbol", "prediction", "direction", "confidence", "edge", "confidence_category", "note", "date"]],
    use_container_width=True
)
