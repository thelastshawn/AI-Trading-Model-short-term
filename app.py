import streamlit as st
import pandas as pd
import json

# === Load JSON Predictions ===
with open("daily_predictions.json", "r") as f:
    data = json.load(f)

df = pd.DataFrame(data)

# === Type Conversions ===
if "confidence" in df.columns:
    df["confidence"] = df["confidence"].astype(float)

if "edge" in df.columns:
    df["edge"] = pd.to_numeric(df["edge"], errors="coerce").fillna(0.0)

if "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

# === UI Header ===
st.title("📈 AI Daily Trading Predictions")
st.subheader("Model Output (Short-Term)")

# === Filters ===
st.markdown("### Filters:")
min_conf = st.slider("Minimum Confidence", 0.5, 1.0, 0.7, 0.01)

# Handle optional filters safely
if "edge" in df.columns:
    min_edge = st.slider("Minimum Edge (%)", 0.0, 10.0, 1.0, 0.1)
else:
    min_edge = 0.0

category = st.multiselect(
    "Confidence Category",
    options=df["confidence_category"].unique() if "confidence_category" in df.columns else [],
    default=df["confidence_category"].unique() if "confidence_category" in df.columns else []
)

direction = st.multiselect(
    "Direction",
    options=df["direction"].unique() if "direction" in df.columns else [],
    default=df["direction"].unique() if "direction" in df.columns else []
)

sortable_columns = [col for col in ["confidence", "edge", "symbol", "date"] if col in df.columns]
sort_by = st.selectbox("Sort by:", sortable_columns)
ascending = st.checkbox("Ascending", value=False)

# === Filter Logic ===
df_filtered = df[df["confidence"] >= min_conf]

if "edge" in df.columns:
    df_filtered = df_filtered[df_filtered["edge"] >= min_edge]

if "confidence_category" in df.columns and category:
    df_filtered = df_filtered[df_filtered["confidence_category"].isin(category)]

if "direction" in df.columns and direction:
    df_filtered = df_filtered[df_filtered["direction"].isin(direction)]

df_filtered = df_filtered.sort_values(by=sort_by, ascending=ascending)

# === Display Results ===
st.markdown(f"### 🔍 Showing {len(df_filtered)} predictions")

columns_to_display = [col for col in [
    "symbol", "prediction", "direction", "confidence", "edge",
    "confidence_category", "note", "date"
] if col in df_filtered.columns]

st.dataframe(df_filtered[columns_to_display], use_container_width=True)
