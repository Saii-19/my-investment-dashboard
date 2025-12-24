import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="My Investments", layout="wide")

st.title("📊 My Investment Dashboard")

SHEET_ID = "1IStj3ZAU1yLbCsT6Pa6ioq6UJVdJBDbistzfEnVpK_0"

import urllib.parse
import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)
def load_sheet(sheet_name):
    encoded_sheet = urllib.parse.quote(sheet_name)
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
    return pd.read_csv(url, dtype=str)


# ---------------- Dashboard ----------------
st.header("📌 Portfolio Summary")

dashboard = load_sheet("Dashboard")

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Invested", str(dashboard.iloc[0, 0]))
col2.metric("📈 Current Value", str(dashboard.iloc[0, 1]))
col3.metric("📊 P&L", str(dashboard.iloc[0, 2]))
col4.metric("📈 Return %", str(dashboard.iloc[0, 3]))


st.divider()

# ---------------- Tabs ----------------
tabs = st.tabs([
    "📈 Stocks Invested",
    "📉 Stocks Sold",
    "📊 MF Invested",
    "📉 MF Sold",
    "🏦 FD Invested",
    "🏦 FD Sold"
])

sheet_map = {
    "📈 Stocks Invested": "Stocks Invested",
    "📉 Stocks Sold": "Stocks Sold",
    "📊 MF Invested": "Index Mutual Funds Invested",
    "📉 MF Sold": "Index Mutual Funds Sold",
    "🏦 FD Invested": "Fixed Deposits Invested",
    "🏦 FD Sold": "Fixed Deposits Sold"
}

for tab, sheet_name in zip(tabs, sheet_map.values()):
    with tab:
        df = load_sheet(sheet_name)
        st.dataframe(df, use_container_width=True)

        num_cols = df.select_dtypes(include='number').columns
        if len(num_cols) > 0:
            fig = px.bar(df, x=df.columns[0], y=num_cols[0])
            st.plotly_chart(fig, use_container_width=True)
