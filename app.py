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
# TEXT → NUMBER (CALC ONLY)
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
# SECTION SUMMARY
# --------------------------------------------------
def section_summary(df):
    invested = df["Invested Total"].apply(to_number).sum() if "Invested Total" in df.columns else 0.0
    current  = df["Current Total"].apply(to_number).sum() if "Current Total" in df.columns else 0.0
    pnl      = df["P&L"].apply(to_number).sum() if "P&L" in df.columns else 0.0
    pct      = (pnl / invested * 100) if invested else 0.0
    return invested, current, pnl, pct

# --------------------------------------------------
# UI CARD
# --------------------------------------------------
def section_card(label, value, color, delta=None):
    arrow_html = ""
    if delta is not None:
        arrow = "↑" if delta >= 0 else "↓"
        arrow_color = "limegreen" if delta >= 0 else "tomato"
        arrow_html = f"<div style='color:{arrow_color};font-size:14px'>{arrow} ₹{abs(delta):,.2f}</div>"

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

# --------------------------------------------------
# SECTION DASHBOARD
# --------------------------------------------------
def render_section_dashboard(inv, cur, pnl, pct):
    if inv == 0 and cur == 0:
        color = "white"
        delta = None
    else:
        color = "limegreen" if pnl >= 0 else "tomato"
        delta = pnl

    c1, c2, c3, c4 = st.columns(4)
    with c1: section_card("💰 Total Invested", f"₹{inv:,.2f}", "white")
    with c2: section_card("📈 Current Value", f"₹{cur:,.2f}", color, delta)
    with c3: section_card("📊 P&L", f"₹{pnl:,.2f}", color)
    with c4: section_card("📈 Return %", f"{pct:.2f}%", color)

# --------------------------------------------------
# ROW COLORING
# --------------------------------------------------
def highlight_profit_loss(row):
    pnl = str(row.get("P&L", "")).strip()
    if pnl.startswith("-"):
        return ["background-color:#3a1d1d"] * len(row)
    if pnl:
        return ["background-color:#1d3a2a"] * len(row)
    return [""] * len(row)

# --------------------------------------------------
# TOP DASHBOARD
# --------------------------------------------------
dashboard = clean_df(load_sheet("Dashboard")).astype(str)
as_of_date = dashboard["Date Checked"].iloc[0] if "Date Checked" in dashboard.columns else ""

st.markdown(
    f"""
    <h1 style="margin-bottom:0">
        📊 My Investment Dashboard
        <span style="font-size:16px; font-weight:400; color:#9ca3af">
            &nbsp;as of {as_of_date}
        </span>
    </h1>
    """,
    unsafe_allow_html=True
)


total_inv, current_val, pnl_val, ret_pct = dashboard.iloc[0, 0:4].astype(str)
profit = not pnl_val.startswith("-")

def top_card(label, val, color):
    st.markdown(
        f"<div><div style='font-size:14px'>{label}</div>"
        f"<div style='font-size:32px;font-weight:700;color:{color}'>{val}</div></div>",
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

# ---------------- INVESTED ----------------
with tabs[0]:
    dfs, vals, pnls = [], [], []

    for sheet in invested_sheets["Sheet Name"]:
        df = clean_df(load_sheet(sheet)).astype(str)
        inv, cur, pnl, pct = section_summary(df)
        dfs.append(df)
        vals.append(inv)
        pnls.append(pnl)

    total_inv_all = sum(vals)
    titles = []

    for name, inv, pnl in zip(invested_sheets["Display Name"], vals, pnls):
        if inv == 0:
            icon = "⚪"
        elif pnl >= 0:
            icon = "🟢"
        else:
            icon = "🔴"
        pct = (inv / total_inv_all * 100) if total_inv_all else 0
        titles.append(f"{icon} {name} ({pct:.0f}%)")

    subtabs = st.tabs(titles)

    for tab, df in zip(subtabs, dfs):
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
    titles = []

    for sheet in sold_sheets["Sheet Name"]:
        df = clean_df(load_sheet(sheet)).astype(str)
        inv, cur, pnl, pct = section_summary(df)
        icon = "⚪" if inv == 0 and cur == 0 else ("🟢" if pnl >= 0 else "🔴")
        titles.append(icon + " " + sheet.replace(" Sold", ""))

    subtabs = st.tabs(titles)

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
st.caption("📊 Google Sheets Powered")
