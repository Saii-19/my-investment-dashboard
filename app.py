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
# GOOGLE SHEET ID
# --------------------------------------------------
SHEET_ID = "PASTE_YOUR_SHEET_ID_HERE"

# --------------------------------------------------
# LOAD GOOGLE SHEET (TEXT ONLY, SAFE)
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
# CLEAN DATAFRAME
# --------------------------------------------------
def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df = df.dropna(axis=1, how="all")        # remove empty columns
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]  # remove Unnamed
    df = df.fillna("")                       # remove nan text
    return df

# --------------------------------------------------
# ROW COLORING (PROFIT / LOSS)
# --------------------------------------------------
def highlight_profit_loss(row):
    text = " ".join(row.astype(str))

    if "-" in text:
        return ["background-color: #3a1d1d"] * len(row)  # red
    if "+" in text:
        return ["background-color: #1d3a2a"] * len(row)  # green

    return [""] * len(row)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
st.header("📌 Portfolio Summary")

dashboard = clean_df(load_sheet("Dashboard"))
dashboard = dashboard.astype(str)

def colored_metric(label, value):
    color = "limegreen" if value.strip().startswith("+") or "-" not in value else "tomato"
    st.markdown(
        f"""
        <div>
            <div style="font-size:14px;">{label}</div>
            <div style="font-size:32px; font-weight:bold; color:{color};">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

col1, col2, col3, col4 = st.columns(4)

with col1:
    colored_metric("💰 Total Invested", dashboard.iloc[0, 0])
with col2:
    colored_metric("📈 Current Value", dashboard.iloc[0, 1])
with col3:
    colored_metric("📊 P&L", dashboard.iloc[0, 2])
with col4:
    colored_metric("📈 Return %", dashboard.iloc[0, 3])

# --------------------------------------------------
# CONFIG-DRIVEN TABS
# --------------------------------------------------
st.divider()

config = clean_df(load_sheet("Config"))
config = config.astype(str)

visible = config[config["Show"].str.upper() == "YES"]

tab_titles = visible["Display Name"].tolist()
sheet_names = visible["Sheet Name"].tolist()

tabs = st.tabs(tab_titles)

for tab, sheet_name in zip(tabs, sheet_names):
    with tab:
        df = clean_df(load_sheet(sheet_name))
        df = df.astype(str)

        styled_df = df.style.apply(highlight_profit_loss, axis=1)

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True
        )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption("📊 Data source: Google Sheets | Auto-updated | Text-only replication")
