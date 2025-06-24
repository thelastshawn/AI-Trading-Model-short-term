import streamlit as st
import pandas as pd
import json

# === PAGE CONFIG ===
st.set_page_config(page_title="📊 AI Predictions Dashboard", layout="wide")

# === HEADER ===
st.title("🤖 AI-Powered Market Predictions")
st.caption("Explore predictions by asset type, confidence, and detailed feature charts.")

# === LOAD DATA ===
uploaded_file = st.file_uploader("📤 Upload your predictions file (.json or .txt)", type=["json", "txt"])

if uploaded_file is not None:
    predictions = json.load(uploaded_file)
    df = pd.json_normalize(predictions)

    # === CLASSIFY SYMBOLS ===
    def classify(symbol):
        if "-USD" in symbol:
            return "Crypto"
        elif symbol in ["SPY", "QQQ", "VTI", "ARKK", "DIA", "XLF", "XLE", "XLK"]:
            return "ETF"
        else:
            return "Stock"

    df["Category"] = df["symbol"].apply(classify)
    df["Confidence %"] = (df["confidence"] * 100).round(2)
    df["Prediction Label"] = df["predicted_label_name"].apply(lambda x: "📈 Bullish" if x == "bullish" else "📉 Bearish")

    # === SIDEBAR FILTERS ===
    st.sidebar.header("🔍 Filters")
    min_conf = st.sidebar.slider("Minimum Confidence", 0.0, 1.0, 0.5, 0.01)
    category_filter = st.sidebar.multiselect("Category", ["Stock", "Crypto", "ETF"], default=["Stock", "Crypto", "ETF"])
    df = df[(df["confidence"] >= min_conf) & (df["Category"].isin(category_filter))]

    # === TABS BY CATEGORY ===
    tabs = st.tabs(["📈 Stocks", "🪙 Crypto", "📘 ETFs"])
    categories = ["Stock", "Crypto", "ETF"]

    for tab, cat in zip(tabs, categories):
        with tab:
            cat_df = df[df["Category"] == cat]
            if cat_df.empty:
                st.info(f"No {cat} predictions match the filters.")
            else:
                st.dataframe(cat_df[["Date", "symbol", "Prediction Label", "Confidence %", "edge"]], use_container_width=True)

                st.subheader("🧠 Feature Snapshots")
                for _, row in cat_df.iterrows():
                    with st.expander(f"{row['Date']} – {row['symbol']} ({row['Prediction Label']})"):
                        # SAFELY DISPLAY FEATURES
                        if "features" in row and isinstance(row["features"], dict):
                            st.json(row["features"])
                            feature_df = pd.DataFrame([row["features"]])
                        else:
                            # Reconstruct from flattened keys
                            feature_cols = [col for col in row.index if col.startswith("features.")]
                            features_dict = {col.split("features.")[-1]: row[col] for col in feature_cols}
                            st.json(features_dict)
                            feature_df = pd.DataFrame([features_dict])

                        indicators = ["rsi", "macd", "macd_signal", "ema_20", "ema_50", "bb_upper", "bb_lower"]
                        indicators = [i for i in indicators if i in feature_df.columns]
                        if indicators:
                            st.line_chart(feature_df[indicators].T.rename(columns={0: "Value"}))

    # === TOP PICKS ===
    st.sidebar.header("🎯 Top Picks")
    top_bull = df[df["predicted_label_name"] == "bullish"].sort_values("confidence", ascending=False).head(1)
    top_bear = df[df["predicted_label_name"] == "bearish"].sort_values("confidence", ascending=False).head(1)
    if not top_bull.empty:
        st.sidebar.success(f"Top Bullish: {top_bull.iloc[0]['symbol']} ({top_bull.iloc[0]['confidence']:.2%})")
    if not top_bear.empty:
        st.sidebar.error(f"Top Bearish: {top_bear.iloc[0]['symbol']} ({top_bear.iloc[0]['confidence']:.2%})")

    # === DOWNLOAD ===
    csv = df.to_csv(index=False)
    st.download_button("⬇️ Download Filtered Predictions", csv, "filtered_predictions.csv", "text/csv")

else:
    st.warning("Please upload your daily_predictions file to begin.")
