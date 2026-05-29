from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import yfinance as yf
import seaborn as sns

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

hist = ticker.history(period="2d", interval="1d")
prev_close = hist["Close"].iloc[-2]

change = price - prev_close
pct_change = (change / prev_close) * 100

st.metric(
    label="AVGO Price",
    value=f"${price:,.2f}",
    delta=f"{change:+.2f} ({pct_change:+.2f}%)"
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
latest_scan = df["scan_time"].max()
today_df = df[df["scan_time"] == latest_scan]

if option_type != "BOTH":
    today_df = today_df[today_df["optionType"] == option_type]

st.subheader(f"Latest Scan: {latest_scan}")

st.dataframe(
    today_df[["optionType", "strike", "volume", "openInterest"]],
    width="stretch",
    hide_index=True
)

# --------------------------------------------------
# Volume by Strike
# --------------------------------------------------
st.subheader("Volume by Strike")

fig, ax = plt.subplots()

if option_type == "BOTH":

    calls = (
        today_df[today_df["optionType"] == "CALL"]
        .groupby("strike")["volume"]
        .sum()
    )

    puts = (
        today_df[today_df["optionType"] == "PUT"]
        .groupby("strike")["volume"]
        .sum()
    )

    strikes = sorted(
        set(calls.index).union(puts.index)
    )

    call_volumes = [calls.get(s, 0) for s in strikes]
    put_volumes = [puts.get(s, 0) for s in strikes]

    width = 0.45

    ax.bar(
        [s - width/2 for s in strikes],
        call_volumes,
        width=width,
        color="green",
        alpha=0.7,
        label="Calls"
    )

    ax.bar(
        [s + width/2 for s in strikes],
        put_volumes,
        width=width,
        color="red",
        alpha=0.7,
        label="Puts"
    )

    ax.legend()

else:

    plot_df = (
        today_df
        .groupby("strike")["volume"]
        .sum()
        .reset_index()
        .sort_values("strike")
    )

    color = "green" if option_type == "CALL" else "red"

    ax.bar(
        plot_df["strike"],
        plot_df["volume"],
        color=color
    )

ax.set_xlabel("Strike")
ax.set_ylabel("Volume")
ax.set_title(f"{option_type} Volume by Strike")

st.pyplot(fig)
plt.close(fig)

# --------------------------------------------------
# Options Pressure Heatmap
# --------------------------------------------------
st.subheader("Pressure Heatmap")

heatmap_df = (
    today_df.groupby(
        ["strike", "optionType"],
        as_index=False
    )[["volume", "openInterest"]]
    .sum()
)

# Pressure score
heatmap_df["pressure"] = (
    heatmap_df["volume"]
    + heatmap_df["openInterest"] * 0.25
)

# Pivot into heatmap shape
pivot = heatmap_df.pivot(
    index="strike",
    columns="optionType",
    values="pressure"
)

pivot = pivot.fillna(0)

fig, ax = plt.subplots(figsize=(5, 8))

sns.heatmap(
    pivot,
    cmap="RdYlGn",
    linewidths=.5,
    annot=True,
    fmt=".0f",
    ax=ax
)

# Dynamic title
option_types = set(pivot.columns)

if option_types == {"CALL"}:
    title = "Call Pressure by Strike"
elif option_types == {"PUT"}:
    title = "Put Pressure by Strike"
elif option_types == {"CALL", "PUT"}:
    title = "Call vs Put Pressure by Strike"
else:
    title = "Options Pressure by Strike"

ax.set_title(title)

st.pyplot(fig)
plt.close(fig)

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
display_cols = [
    "strike",
    "volume",
    "openInterest",
    "lastPrice"
]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Calls")

    calls_df = (
        today_df[today_df["optionType"] == "CALL"]
        .sort_values("volume", ascending=False)
        .head(10)
    )
    
    st.dataframe(
        (
            calls_df[display_cols]
            .style
            .format({
                "strike": "{:.2f}",
                "volume": "{:,.0f}",
                "openInterest": "{:,.0f}",
                "lastPrice": "${:.2f}"
            })
            .background_gradient(subset=["volume"], cmap="Greens")
            .background_gradient(subset=["openInterest"], cmap="Blues")
        ),
        hide_index=True,
        width='stretch'
    )

with col2:
    st.subheader("Puts")

    puts_df = (
        today_df[today_df["optionType"] == "PUT"]
        .sort_values("volume", ascending=False)
        .head(10)
    )

    st.dataframe(
        (
            puts_df[display_cols]
            .style
            .format({
                "strike": "{:.2f}",
                "volume": "{:,.0f}",
                "openInterest": "{:,.0f}",
                "lastPrice": "${:.2f}"
            })
            .background_gradient(subset=["volume"], cmap="Greens")
            .background_gradient(subset=["openInterest"], cmap="Blues")
        ),
        hide_index=True,
        width='stretch'
    )