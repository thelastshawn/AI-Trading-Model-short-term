import streamlit as st
import json
import pandas as pd

# Page setup
st.set_page_config(page_title="Ninja Licks – AI Market Predictions", layout="wide")
st.title("💹 Ninja Licks – AI Stocks/ETF/Crypto Market Predictions")
st.caption("A bold, beginner-friendly trading dashboard powered by AI.")

# Load JSON
with open("daily_predictions.json", "r") as f:
    data = json.load(f)

# Convert JSON to DataFrame
df = pd.DataFrame(data)

# Extract features into columns
features_df = df["features"].apply(pd.Series)
df = pd.concat([df.drop(columns=["features"]), features_df], axis=1)

# Fix missing asset types
df["category"] = df["category"].fillna("Unknown")
df["predicted_label_name"] = df["predicted_label_name"].str.capitalize()

# Sidebar Filters
st.sidebar.header("🎯 Filters")
confidence_range = st.sidebar.slider("Min Confidence", 0.5, 1.0, 0.65)
asset_types = st.sidebar.multiselect("Asset Type", options=df["category"].unique(), default=df["category"].unique())
search_term = st.sidebar.text_input("🔍 Search Symbol")

# Filter data
filtered_df = df[df["confidence"] >= confidence_range]
filtered_df = filtered_df[filtered_df["category"].isin(asset_types)]
if search_term:
    filtered_df = filtered_df[filtered_df["symbol"].str.contains(search_term.upper(), na=False)]

# Sort by confidence
filtered_df = filtered_df.sort_values(by="confidence", ascending=False)

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Picks", "📘 Glossary", "📊 Trends"])

# --- TAB 1: PICKS ---
with tab1:
    st.header("⭐ Today's Most Confident Picks")

    for _, row in filtered_df.iterrows():
        emoji = "📉" if row["predicted_label_name"].lower() == "bearish" else "📈"
        box_color = "🧠" if row["confidence"] > 0.8 else "💡"
        label_display = f"{emoji} {row['predicted_label_name']} ({round(row['confidence'] * 100, 2)}% confidence)"
        pick_header = f"{box_color} **{row['symbol']}** – {label_display}"
        with st.expander(pick_header):
            st.markdown(f"**Asset Type:** {row['category']}  |  **Edge:** {round(row['edge'] * 100, 2)}%")
            st.markdown("---")
            st.subheader("📊 Trader Signals")

            signals = {
                "Close": row.get("close", None),
                "Open": row.get("open", None),
                "High": row.get("high", None),
                "Low": row.get("low", None),
                "Volume": row.get("volume", None),
                "RSI": row.get("rsi", None),
                "MACD": row.get("macd", None),
                "MACD Signal": row.get("macd_signal", None),
                "Bollinger Upper": row.get("bb_upper", None),
                "Bollinger Lower": row.get("bb_lower", None),
                "EMA 20": row.get("ema_20", None),
                "EMA 50": row.get("ema_50", None),
                "ROC": row.get("roc", None),
            }

            # Display signals in clean layout
            col1, col2 = st.columns(2)
            for i, (label, val) in enumerate(signals.items()):
                if pd.notna(val):
                    col = col1 if i % 2 == 0 else col2
                    col.markdown(f"**{label}:** `{round(val, 4)}`")

# --- TAB 2: GLOSSARY ---
with tab2:
    st.header("📘 Glossary – Learn Your Licks")
    st.markdown("""
    - **RSI (Relative Strength Index):** Measures momentum. Above 70 = Overbought, Below 30 = Oversold.
    - **MACD (Moving Average Convergence Divergence):** A trend-following indicator for momentum shifts.
    - **MACD Signal:** The EMA of MACD — used to identify signals.
    - **Bollinger Bands (Upper/Lower):** Show price volatility; bands widen when volatility increases.
    - **EMA (Exponential Moving Average):** Weighted average favoring recent prices.
    - **ROC (Rate of Change):** Percentage change in price from past periods.
    - **Confidence:** The AI model’s probability behind its prediction.
    - **Edge:** Your statistical advantage based on implied market probabilities.
    """)

# --- TAB 3: TRENDS (coming soon placeholder) ---
with tab3:
    st.header("📊 Trends")
    st.info("📅 Trends & momentum visualizations will be available in a future update. Stay tuned!")

# Footer
st.markdown("---")
st.caption("🧠 Built by Ninja Licks AI • Designed for aspiring traders 🚀")
