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

# --------------------------------------------------
# GOOGLE SHEET ID
# --------------------------------------------------
SHEET_ID = "1IStj3ZAU1yLbCsT6Pa6ioq6UJVdJBDbistzfEnVpK_0"

# --------------------------------------------------
# LOAD GOOGLE SHEET
# --------------------------------------------------
@st.cache_data(ttl=300)
def load_sheet(sheet_name: str) -> pd.DataFrame:
    encoded = urllib.parse.quote(sheet_name)
    url = (
        f"https://docs.google.com/spreadsheets/d/{SHEET_ID}"
        f"/gviz/tq?tqx=out:csv&sheet={encoded}"
    )
    return pd.read_csv(url, dtype=str)

# --------------------------------------------------
# CLEAN DATA
# --------------------------------------------------
def clean_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(axis=1, how="all")
    df = df.loc[:, ~df.columns.str.contains("^Unnamed")]
    return df.fillna("")

# --------------------------------------------------
# TEXT → NUMBER (FOR CALC ONLY)
# --------------------------------------------------
def to_number(val):
    try:
        return float(
            str(val)
            .replace("₹", "")
            .replace(",", "")
            .replace("%", "")
            .strip()
        )
    except:
        return 0.0

# --------------------------------------------------
# SECTION SUMMARY (SAFE)
# --------------------------------------------------
def section_summary(df):
    invested_col = df["Invested Total"] if "Invested Total" in df.columns else pd.Series(dtype=float)
    current_col  = df["Current Total"]  if "Current Total"  in df.columns else pd.Series(dtype=float)
    pnl_col      = df["P&L"]            if "P&L"            in df.columns else pd.Series(dtype=float)

    invested = invested_col.apply(to_number).sum()
    current  = current_col.apply(to_number).sum()
    pnl      = pnl_col.apply(to_number).sum()

    pct = (pnl / invested * 100) if invested != 0 else 0.0
    return invested, current, pnl, pct

# --------------------------------------------------
# ONLY INVESTED AMOUNT (FOR ALLOCATION)
# --------------------------------------------------
def invested_amount(df):
    if "Invested Total" in df.columns:
        return df["Invested Total"].apply(to_number).sum()
    return 0.0

# --------------------------------------------------
# SECTION DASHBOARD (CUSTOM)
# --------------------------------------------------
def section_card(label, value, color, delta=None):
    arrow_html = ""
    if delta is not None:
        arrow = "↑" if delta >= 0 else "↓"
        delta_color = "limegreen" if delta >= 0 else "tomato"
        arrow_html = (
            f"<div style='color:{delta_color};font-size:14px'>"
            f"{arrow} ₹{abs(delta):,.2f}</div>"
        )

    st.markdown(
        f"""
        <div>
            <div style="font-size:14px">{label}</div>
            <div style="font-size:30px;font-weight:700;color:{color}">
                {value}
            </div>
            {arrow_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_section_dashboard(inv, cur, pnl, pct):
    profit = pnl >= 0
    color = "limegreen" if profit else "tomato"

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        section_card("💰 Total Invested", f"₹{inv:,.2f}", "white")
    with c2:
        section_card("📈 Current Value", f"₹{cur:,.2f}", color, pnl)
    with c3:
        section_card("📊 P&L", f"₹{pnl:,.2f}", color)
    with c4:
        section_card("📈 Return %", f"{pct:.2f}%", color)

# --------------------------------------------------
# ROW COLORING
# --------------------------------------------------
def highlight_profit_loss(row):
    pnl = str(row.get("P&L", "")).strip()
    if pnl.startswith("-"):
        return ["background-color:#3a1d1d"] * len(row)
    if pnl != "":
        return ["background-color:#1d3a2a"] * len(row)
    return [""] * len(row)

# --------------------------------------------------
# TOP DASHBOARD + DATE IN TITLE
# --------------------------------------------------
dashboard = clean_df(load_sheet("Dashboard")).astype(str)

as_of_date = ""
if "Date Checked" in dashboard.columns:
    as_of_date = dashboard["Date Checked"].iloc[0].strip()

st.title(f"📊 My Investment Dashboard as of {as_of_date}")

total_inv = dashboard.iloc[0, 0].strip()
current_val = dashboard.iloc[0, 1].strip()
pnl_val = dashboard.iloc[0, 2].strip()
ret_pct = dashboard.iloc[0, 3].strip()

profit = not pnl_val.startswith("-")

def top_card(label, val, color):
    st.markdown(
        f"""
        <div>
            <div style="font-size:14px">{label}</div>
            <div style="font-size:32px;font-weight:700;color:{color}">
                {val}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

a, b, c, d = st.columns(4)

with a: top_card("💰 Total Invested", total_inv, "white")
with b: top_card("📈 Current Value", current_val, "limegreen" if profit else "tomato")
with c: top_card("📊 P&L", pnl_val, "limegreen" if profit else "tomato")
with d: top_card("📈 Return %", ret_pct, "limegreen" if not ret_pct.startswith("-") else "tomato")

# --------------------------------------------------
# INVESTED / SOLD
# --------------------------------------------------
st.divider()

config = clean_df(load_sheet("Config")).astype(str)
visible = config[config["Show"].str.upper() == "YES"]

invested_sheets = visible[visible["Sheet Name"].str.contains("Invested", case=False)]
sold_sheets = visible[visible["Sheet Name"].str.contains("Sold", case=False)]

tabs = st.tabs(["📥 Invested", "📤 Sold"])

# ---------------- INVESTED (WITH ALLOCATION %) ----------------
with tabs[0]:
    invested_dfs = []
    invested_vals = []

    for sheet in invested_sheets["Sheet Name"]:
        df_tmp = clean_df(load_sheet(sheet)).astype(str)
        invested_vals.append(invested_amount(df_tmp))
        invested_dfs.append(df_tmp)

    total_invested_all = sum(invested_vals)

    tab_titles = []
    for name, val in zip(invested_sheets["Display Name"], invested_vals):
        pct = (val / total_invested_all * 100) if total_invested_all else 0
        tab_titles.append(f"{name} ({pct:.0f}%)")

    subtabs = st.tabs(tab_titles)

    for tab, sheet, df in zip(subtabs, invested_sheets["Sheet Name"], invested_dfs):
        with tab:
            inv, cur, pnl, pct = section_summary(df)
            render_section_dashboard(inv, cur, pnl, pct)

            st.divider()

            st.dataframe(
                df.style.apply(highlight_profit_loss, axis=1),
                use_container_width=True,
                hide_index=True
            )

# ---------------- SOLD ----------------
with tabs[1]:
    subtabs = st.tabs(sold_sheets["Display Name"].tolist())

    for tab, sheet in zip(subtabs, sold_sheets["Sheet Name"]):
        with tab:
            df = clean_df(load_sheet(sheet)).astype(str)

            inv, cur, pnl, pct = section_summary(df)
            render_section_dashboard(inv, cur, pnl, pct)

            st.divider()

            st.dataframe(
                df.style.apply(highlight_profit_loss, axis=1),
                use_container_width=True,
                hide_index=True
            )

# --------------------------------------------------
# FOOTER
# --------------------------------------------------
st.divider()
st.caption("📊 Google Sheets powered | Allocation aware | Fully dynamic | Zero cost")
