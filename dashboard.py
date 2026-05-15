import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# --------------------------------------------------
# Page Configuration (MUST be first Streamlit call)
# --------------------------------------------------
st.set_page_config(
    page_title="AVGO Options Dashboard",
    layout="centered"
)

# --------------------------------------------------
# User Controls
# --------------------------------------------------
option_type = st.radio(
    "Option Type",
    ["CALL", "PUT", "BOTH"],
    horizontal=True
)

st.title("AVGO Weekly Options")


ticker = yf.Ticker("AVGO")
price = ticker.fast_info["last_price"]

st.metric("AVGO Price", f"${price:,.2f}")


change = ticker.fast_info.get("last_price") - ticker.fast_info.get("previous_close")

st.metric(
    label="AVGO Price",
    value=f"${price:,.2f}",
    delta=f"{change:+.2f}"
)

st.caption("Strike prices relative to current spot")


# --------------------------------------------------
# Data Loading
# --------------------------------------------------
DATA_PATH = Path("C:/Users/B Dog/Documents/options_scanner/avgo_options.csv")

if not DATA_PATH.exists():
    st.error("Data file not found. Run the scanner first.")
    st.stop()

df = pd.read_csv(DATA_PATH)

if df.empty:
    st.warning("No data available.")
    st.stop()

# --------------------------------------------------
# Latest Scan Filtering
# --------------------------------------------------
latest_date = df["date"].max()
today_df = df[df["date"] == latest_date]

if option_type != "BOTH":
    today_df = today_df[today_df["optionType"] == option_type]

st.subheader(f"Latest Scan: {latest_date}")

st.dataframe(
    today_df[["optionType", "strike", "volume", "openInterest"]],
    width="stretch"
)

# --------------------------------------------------
# Volume by Strike
# --------------------------------------------------
st.subheader("Volume by Strike")

plot_df = today_df.sort_values("strike")

plt.figure()
plt.bar(plot_df["strike"], plot_df["volume"])
plt.xlabel("Strike")
plt.ylabel("Volume")
plt.title(f"{option_type} Volume by Strike")
st.pyplot(plt)
plt.clf()

# --------------------------------------------------
# Total Volume Over Time
# --------------------------------------------------
st.subheader("Total Volume Over Time")

if option_type == "BOTH":
    volume_by_day = (
        df.groupby(["date", "optionType"])["volume"]
        .sum()
        .reset_index()
    )

    for opt in ["CALL", "PUT"]:
        opt_df = volume_by_day[volume_by_day["optionType"] == opt]
        plt.plot(opt_df["date"], opt_df["volume"], label=opt)

    plt.legend()

else:
    volume_by_day = (
        df[df["optionType"] == option_type]
        .groupby("date")["volume"]
        .sum()
        .reset_index()
    )
    plt.plot(volume_by_day["date"], volume_by_day["volume"])

plt.xticks(rotation=45)
plt.ylabel("Total Volume")
plt.title("Total Options Volume Over Time")
st.pyplot(plt)
plt.clf()

# --------------------------------------------------
# Side-by-Side Tables
# --------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Calls")
    calls_df = today_df[today_df["optionType"] == "CALL"]
    st.dataframe(calls_df)

with col2:
    st.subheader("Puts")
    puts_df = today_df[today_df["optionType"] == "PUT"]
    st.dataframe(puts_df)
