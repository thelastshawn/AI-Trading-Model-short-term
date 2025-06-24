import streamlit as st
import pandas as pd
import json

# Page config
st.set_page_config(
    page_title="Ninja Licks – AI Stocks/ETF/Crypto Market Predictions",
    layout="wide",
)

st.markdown(
    "<h1 style='text-align: center;'>💵 Ninja Licks – AI Stocks/ETF/Crypto Market Predictions</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align: center;'>A bold, beginner-friendly trading dashboard powered by AI.</p>",
    unsafe_allow_html=True,
)

# Load predictions from GitHub-tracked file
with open("daily_predictions.json", "r") as f:
    predictions = json.load(f)

df = pd.DataFrame(predictions)

# Add asset type label
df["asset_type"] = df["symbol"].apply(lambda x: "Crypto" if x.endswith("-USD") else "Stock/ETF")

# Sort by confidence descending
df = df.sort_values(by="confidence", ascending=False)

# Sidebar Filters
st.sidebar.header("🔍 Filters")
min_confidence = st.sidebar.slider("Minimum Confidence", 50, 100, 60)

selected_assets = st.sidebar.multiselect(
    "Asset Type", ["Stock/ETF", "Crypto"], default=["Stock/ETF", "Crypto"]
)

symbols = sorted(df["symbol"].unique())
selected_symbol = st.sidebar.selectbox("Search Symbol", ["All"] + symbols)

# Apply filters
filtered_df = df[df["confidence"] * 100 >= min_confidence]
filtered_df = filtered_df[filtered_df["asset_type"].isin(selected_assets)]

if selected_symbol != "All":
    filtered_df = filtered_df[filtered_df["symbol"] == selected_symbol]

# --- Display ---
st.markdown("### 🌟 Today's Most Confident Picks")

def format_prediction(row):
    icon = "📈" if row["prediction"] == 1 else "📉"
    label = "Bullish" if row["prediction"] == 1 else "Bearish"
    conf = round(row["confidence"] * 100, 2)
    return f"{icon} {label} ({conf}% confidence)"

# Render cards
for _, row in filtered_df.iterrows():
    col1, col2 = st.columns([1, 4])
    with col1:
        st.markdown("🧠")
    with col2:
        st.markdown(
            f"""
            <div style='border: 1px solid #333; border-radius: 10px; padding: 10px; margin-bottom: 10px; background-color: #111;'>
                <h4 style='margin: 0;'>{row['symbol']}</h4>
                <p style='margin: 4px 0;'>{format_prediction(row)}</p>
                {"<p style='margin: 4px 0;'>💥 Edge: {:.2f}%</p>".format(row['edge'] * 100) if 'edge' in row and row['edge'] is not None else ""}
            </div>
            """,
            unsafe_allow_html=True,
        )