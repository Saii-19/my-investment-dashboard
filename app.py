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
SHEET_ID = "1IStj3ZAU1yLbCsT6Pa6ioq6UJVdJBDbistzfEnVpK_0"

# --------------------------------------------------
# LOAD GOOGLE SHEET (TEXT ONLY)
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
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    df = df.fillna("")
    return df

# --------------------------------------------------
# ROW COLORING — PROFIT / LOSS
# --------------------------------------------------
def highlight_profit_loss(row):
    pnl = str(row.get("P&L", "")).strip()
    pct = str(row.get("Percentage", "")).strip()

    if pnl.startswith("+") or pct.startswith("+"):
        return ["background-color: #1d3a2a"] * len(row)
    if pnl.startswith("-") or pct.startswith("-"):
        return ["background-color: #3a1d1d"] * len(row)

    return [""] * len(row)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------
st.header("📌 Portfolio Summary")

dashboard = clean_df(load_sheet("Dashboard")).astype(str)

def colored_metric(label, value):
    value = value.strip()
    color = "limegreen" if value.startswith("+") or not value.startswith("-") else "tomato"
    st.markdown(
        f"""
        <div>
            <div style="font-size:14px;">{label}</div>
            <div style="font-size:32px; font-weight:700; color:{color};">
                {value}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

c1, c2, c3, c4 = st.columns(4)

with c1:
    colored_metric("💰 Total Invested", dashboard.iloc[0, 0])
with c2:
    colored_metric("📈 Current Value", dashboard.iloc[0, 1])
with c3:
    colored_metric("📊 P&L", dashboard.iloc[0, 2])
with c4:
    colored_metric("📈 Return %", dashboard.iloc[0, 3])

# --------------------------------------------------
# INVESTED / SOLD SEPARATION
# --------------------------------------------------
st.divider()

config = clean_df(load_sheet("Config")).astype(str)
visible = config[config["Show"].str.upper() == "YES"]

invested_sheets = visible[visible["Sheet Name"].str.contains("Invested", case=False)]
sold_sheets = visible[visible["Sheet Name"].str.contains("Sold", case=False)]

main_tabs = st.tabs(["📥 Invested", "📤 Sold"])

# ---------------- INVESTED ----------------
with main_tabs[0]:
    subtabs = st.tabs(invested_sheets["Display Name"].tolist())

    for tab, sheet_name in zip(subtabs, invested_sheets["Sheet Name"]):
        with tab:
            df = clean_df(load_sheet(sheet_name)).astype(str)
            st.dataframe(
                df.style.apply(highlight_profit_loss, axis=1),
                use_container_width=True,
                hide_index=True
            )

# ---------------- SOLD ----------------
with main_tabs[1]:
    subtabs = st.tabs(sold_sheets["Display Name"].tolist())

    for tab, sheet_name in zip(subtabs, sold_sheets["Sheet Name"]):
        with tab:
            df = clean_df(load_sheet(sheet_name)).astype(str)
            st.dataframe(
                df.style.apply(highlight_profit_loss, axis=1),
                use_container_width=True,
                hide_index=True
            )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption("📊 Google Sheets powered | Fully dynamic | Zero-cost personal dashboard")
