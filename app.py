import streamlit as st
import pandas as pd
import urllib.parse

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="My Investment Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 My Investment Dashboard")

# --------------------------------------------------
# GOOGLE SHEET ID (REPLACE THIS)
# --------------------------------------------------
SHEET_ID = "1IStj3ZAU1yLbCsT6Pa6ioq6UJVdJBDbistzfEnVpK_0"

# --------------------------------------------------
# LOAD GOOGLE SHEET (TEXT-ONLY, SPACE-SAFE)
# --------------------------------------------------
@st.cache_data(ttl=300)
def load_sheet(sheet_name: str) -> pd.DataFrame:
    encoded_sheet = urllib.parse.quote(sheet_name)
    url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
    )
    return pd.read_csv(url, dtype=str)

# --------------------------------------------------
# DASHBOARD (TEXT-ONLY REPLICATION)
# --------------------------------------------------
st.header("📌 Portfolio Summary")

dashboard = load_sheet("Dashboard")

dashboard = dashboard.astype(str)

col1, col2, col3, col4 = st.columns(4)

col1.metric("💰 Total Invested", dashboard.iloc[0, 0])
col2.metric("📈 Current Value", dashboard.iloc[0, 1])
col3.metric("📊 P&L", dashboard.iloc[0, 2])
col4.metric("📈 Return %", dashboard.iloc[0, 3])

# --------------------------------------------------
# CONFIG-DRIVEN TABS
# --------------------------------------------------
st.divider()

config = load_sheet("Config")
config = config.astype(str)

# Show only rows marked YES
visible = config[config["Show"].str.upper() == "YES"]

tab_titles = visible["Display Name"].tolist()
sheet_names = visible["Sheet Name"].tolist()

tabs = st.tabs(tab_titles)

for tab, sheet_name in zip(tabs, sheet_names):
    with tab:
        df = load_sheet(sheet_name)
        df = df.astype(str)  # replicate sheet exactly
        st.dataframe(df, use_container_width=True)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption("📊 Data source: Google Sheets | Updated dynamically")
