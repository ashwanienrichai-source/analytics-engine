"""
SaaS Revenue Analytics Platform — Streamlit App
=================================================
Run: streamlit run app.py
Requirements: pip install streamlit pandas plotly numpy openpyxl
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SaaS Revenue Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── CUSTOM CSS (Dark theme matching your Excel look) ─────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap');

    /* Global */
    .stApp { background-color: #060b18; font-family: 'Outfit', sans-serif; }
    header[data-testid="stHeader"] { background-color: #060b18; }
    .block-container { padding-top: 1rem; }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display: none;}

    /* Landing page styles */
    .landing-container {
        display: flex; min-height: 92vh; gap: 0;
        background: linear-gradient(160deg, #081530, #0a1628, #060e20);
        border-radius: 16px; overflow: hidden;
        border: 1px solid #1a2540;
    }
    .landing-left {
        flex: 1; padding: 60px 56px; display: flex;
        flex-direction: column; justify-content: center;
        position: relative;
    }
    .landing-left::before {
        content: ''; position: absolute; top: -80px; left: -80px;
        width: 400px; height: 400px; border-radius: 50%;
        background: radial-gradient(circle, rgba(14,165,233,0.06) 0%, transparent 70%);
    }
    .landing-right {
        flex: 1; padding: 60px 56px; display: flex;
        align-items: center; justify-content: center;
        border-left: 1px solid #1a2540;
        background: linear-gradient(200deg, #0a1628, #070d1c);
    }
    .logo-row { display: flex; align-items: center; gap: 10px; margin-bottom: 36px; }
    .logo-icon {
        width: 40px; height: 40px; border-radius: 10px;
        background: linear-gradient(135deg, #0ea5e9, #06b6d4);
        display: flex; align-items: center; justify-content: center;
        font-size: 18px; font-weight: 900; color: #fff;
        box-shadow: 0 0 25px rgba(14,165,233,0.25);
    }
    .logo-text { font-size: 19px; font-weight: 700; color: #f8fafc; }
    .hero-title {
        font-size: 42px; font-weight: 900; color: #f8fafc;
        line-height: 1.08; letter-spacing: -1.5px; margin-bottom: 14px;
    }
    .hero-title span { color: #0ea5e9; }
    .hero-sub {
        font-size: 15px; color: #8896b0; line-height: 1.7;
        margin-bottom: 36px; max-width: 420px;
    }
    .stats-row { display: flex; gap: 14px; margin-bottom: 32px; }
    .stat-box {
        padding: 14px 16px; border-radius: 10px;
        background: rgba(14,165,233,0.05); border: 1px solid rgba(14,165,233,0.1);
        min-width: 100px;
    }
    .stat-label {
        font-size: 9px; font-weight: 700; color: #0ea5e9;
        letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 5px;
    }
    .stat-value { font-size: 22px; font-weight: 800; color: #f8fafc; }
    .pills { display: flex; flex-wrap: wrap; gap: 7px; }
    .pill {
        padding: 6px 13px; border-radius: 16px; font-size: 11px; font-weight: 500;
        background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
        color: #8896b0;
    }
    .login-card {
        width: 100%; max-width: 380px;
        background: rgba(15,23,41,0.85); backdrop-filter: blur(16px);
        border-radius: 16px; border: 1px solid rgba(255,255,255,0.06);
        padding: 40px 32px; box-shadow: 0 20px 60px rgba(0,0,0,0.4);
    }
    .login-card h2 { font-size: 24px; font-weight: 700; color: #f8fafc; margin-bottom: 4px; }
    .login-card p { font-size: 13px; color: #8896b0; margin-bottom: 24px; }

    /* Dashboard KPI cards */
    .kpi-card {
        background: #0f1729; border-radius: 12px; padding: 18px;
        border: 1px solid #1a2540; transition: border-color 0.2s;
    }
    .kpi-card:hover { border-color: rgba(14,165,233,0.2); }
    .kpi-label {
        font-size: 10px; font-weight: 600; color: #4a5a78;
        text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 6px;
    }
    .kpi-value { font-size: 24px; font-weight: 800; color: #f8fafc; margin-bottom: 4px; }
    .kpi-change { font-size: 11px; font-weight: 700; }
    .kpi-up { color: #22c55e; }
    .kpi-down { color: #ef4444; }
    .kpi-yoy { color: #4a5a78; font-weight: 400; }

    /* Section headers */
    .section-title {
        font-size: 13px; font-weight: 700; color: #0ea5e9;
        margin: 18px 0 8px; padding-left: 2px; letter-spacing: 0.3px;
    }

    /* Style dataframes / tables */
    .stDataFrame { border-radius: 8px; overflow: hidden; }
    div[data-testid="stDataFrame"] > div { border-radius: 8px; }

    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px; background: rgba(255,255,255,0.015);
        border-radius: 10px; padding: 3px;
        border: 1px solid #1a2540;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px; padding: 8px 20px;
        font-weight: 600; font-size: 13px;
        color: #8896b0; background: transparent;
    }
    .stTabs [aria-selected="true"] {
        background: #0ea5e9 !important; color: #fff !important;
    }
    .stTabs [data-baseweb="tab-panel"] {
        background: #0f1729; border-radius: 14px; padding: 24px;
        border: 1px solid #1a2540;
    }

    /* Metric cards in columns */
    div[data-testid="stMetric"] {
        background: #0f1729; border-radius: 12px; padding: 16px;
        border: 1px solid #1a2540;
    }
    div[data-testid="stMetric"] label { color: #4a5a78 !important; font-size: 11px !important; }
    div[data-testid="stMetric"] [data-testid="stMetricValue"] { color: #f8fafc !important; font-size: 24px !important; }

    /* Plotly charts background */
    .js-plotly-plot .plotly .bg { fill: #0f1729 !important; }

    /* Streamlit input styling */
    .stTextInput input, .stPasswordInput input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        color: #f8fafc !important; border-radius: 9px !important;
    }
    .stTextInput input:focus, .stPasswordInput input:focus {
        border-color: rgba(14,165,233,0.4) !important;
    }
    .stButton > button {
        width: 100%; border-radius: 9px; font-weight: 700; font-size: 14px;
        padding: 10px 20px; transition: all 0.15s;
    }
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE ────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


# ─── DATA ─────────────────────────────────────────────────────────────────────
def get_product_data():
    """KPI data matching the Excel screenshot exactly."""
    data = {
        "Product Parent": ["IMS", "CMMS", "Requests, Tasks & Other", "Conversations", "Security", "Advanced Analytics", "Grand Total"],
        "FY23 ARR": [4720, 1616, 1302, 1304, 715, 484, 10140],
        "FY24 ARR": [5371, 2040, 1540, 1513, 924, 791, 12180],
        "FY25 ARR": [5756, 2305, 1675, 1634, 1091, 1050, 13512],
        "CAGR": ["10.4%", "19.4%", "13.4%", "11.9%", "23.5%", "47.4%", "15.4%"],
        "FY23 Cust": [190, 91, 126, 148, 43, 9, 233],
        "FY24 Cust": [199, 100, 124, 153, 48, 20, 238],
        "FY25 Cust": [211, 121, 137, 166, 59, 35, 256],
        "FY23 EARR": [24.8, 17.8, 10.3, 8.8, 16.6, 53.7, 43.5],
        "FY24 EARR": [27.0, 20.4, 12.4, 9.9, 19.3, 39.5, 51.2],
        "FY25 EARR": [27.3, 19.0, 12.2, 9.8, 18.5, 30.0, 52.8],
        "FY23 Gross $ Ret": ["97.6%", "98.7%", "98.4%", "97.4%", "98.7%", "100.0%", "98.0%"],
        "FY24 Gross $ Ret": ["95.2%", "96.7%", "94.8%", "95.2%", "98.3%", "100.0%", "95.8%"],
        "FY25 Gross $ Ret": ["96.8%", "92.7%", "98.4%", "97.0%", "98.3%", "100.0%", "96.7%"],
        "FY23 Gross $ Rate": ["94.7%", "95.4%", "93.0%", "93.3%", "87.7%", "100.0%", "93.9%"],
        "FY24 Gross $ Rate": ["93.2%", "91.5%", "93.8%", "96.0%", "96.9%", "104.3%", "94.2%"],
        "FY25 Gross $ Rate": ["95.2%", "92.1%", "96.6%", "95.8%", "98.4%", "97.2%", "95.3%"],
        "FY23 NRR": ["108.4%", "113.3%", "110.5%", "103.8%", "101.8%", "265.6%", "111.4%"],
        "FY24 NRR": ["105.0%", "115.3%", "113.5%", "110.4%", "108.6%", "155.1%", "112.0%"],
        "FY25 NRR": ["98.9%", "102.1%", "102.0%", "100.0%", "107.6%", "126.8%", "102.4%"],
        "FY23 Net $ Ret": ["107.3%", "113.3%", "109.8%", "103.0%", "101.8%", "265.6%", "110.8%"],
        "FY24 Net $ Ret": ["104.8%", "115.3%", "115.4%", "109.7%", "118.7%", "155.8%", "111.7%"],
        "FY25 Net $ Ret": ["99.9%", "102.1%", "102.6%", "106.7%", "106.7%", "127.3%", "103.1%"],
        "FY23 Logo Ret": ["96.7%", "97.7%", "96.8%", "97.3%", "97.8%", "100.0%", "94.7%"],
        "FY24 Logo Ret": ["92.8%", "95.6%", "93.7%", "93.9%", "97.7%", "100.0%", "90.1%"],
        "FY25 Logo Ret": ["94.5%", "96.0%", "96.8%", "95.4%", "97.9%", "100.0%", "92.4%"],
        "FY23 New Logo": [16.1, 14.6, 12.5, 12.5, 12.5, None, 31.0],
        "FY24 New Logo": [18.2, 16.1, 5.3, 6.9, 15.8, 35.0, 29.3],
        "FY25 New Logo": [17.8, 11.7, 7.1, 7.0, 13.1, 30.6, 28.2],
        "FY23 Churn": [16.7, 9.0, 4.4, 7.8, 8.4, None, 14.7],
        "FY24 Churn": [16.2, 13.2, 8.5, 7.0, 12.0, None, 18.4],
        "FY25 Churn": [None, 37.2, 6.2, 6.6, 13.2, 1.4, 22.5],
    }
    return pd.DataFrame(data)


def get_industry_data():
    return pd.DataFrame({
        "Industry": ["Sports", "Entertainment", "Places of Attraction", "Convention Center", "Others"],
        "FY23 ARR": [7937, 948, 649, 435, 171],
        "FY24 ARR": [9120, 1382, 1085, 446, 145],
        "FY25 ARR": [10295, 1545, 992, 512, 164],
        "CAGR": ["13.9%", "27.6%", "23.6%", "8.4%", "(2.0)%"],
        "FY23 Gross $ Rate": ["95.0%", "98.3%", "89.1%", "81.5%", "93.9%"],
        "FY24 Gross $ Rate": ["95.4%", "92.2%", "90.5%", "85.5%", "94.2%"],
        "FY25 Gross $ Rate": ["96.6%", "94.5%", "85.6%", "94.7%", "95.3%"],
        "FY23 NRR": ["111.2%", "124.4%", "125.6%", "90.6%", "110.8%"],
        "FY24 NRR": ["110.0%", "111.9%", "157.1%", "85.1%", "110.8%"],
        "FY25 NRR": ["104.0%", "102.9%", "98.3%", "109.7%", "103.1%"],
        "FY23 Logo Ret": ["95.8%", "100.0%", "88.9%", "85.7%", "94.7%"],
        "FY24 Logo Ret": ["91.7%", "92.9%", "90.0%", "78.6%", "90.1%"],
        "FY25 Logo Ret": ["93.3%", "94.6%", "66.7%", "100.0%", "92.4%"],
    })


def get_region_data():
    return pd.DataFrame({
        "Region": ["US & Canada", "APAC", "EMEA", "LATAM"],
        "FY23 ARR": [9612, 317, 212, None],
        "FY24 ARR": [11336, 400, 421, 23],
        "FY25 ARR": [12331, 597, 561, 23],
        "CAGR": ["13.3%", "37.2%", "62.8%", "—"],
        "FY23 Gross $ Rate": ["93.9%", "95.4%", "100.0%", ""],
        "FY24 Gross $ Rate": ["93.8%", "100.0%", "94.9%", ""],
        "FY25 Gross $ Rate": ["95.2%", "100.0%", "100.0%", "100.0%"],
        "FY23 NRR": ["111.0%", "128.3%", "107.5%", ""],
        "FY24 NRR": ["112.1%", "115.1%", "111.5%", ""],
        "FY25 NRR": ["101.8%", "107.3%", "112.1%", "103.0%"],
        "FY23 Logo Ret": ["95.0%", "75.0%", "100.0%", ""],
        "FY24 Logo Ret": ["89.8%", "100.0%", "100.0%", ""],
        "FY25 Logo Ret": ["92.3%", "100.0%", "90.0%", "100.0%"],
    })


def get_vintage_data():
    return pd.DataFrame({
        "Vintage": ["Pre 2023", "2023", "2024", "2025"],
        "FY23 ARR": [9552, 589, None, None],
        "FY24 ARR": [10679, 650, 851, None],
        "FY25 ARR": [11062, 613, 878, 959],
        "CAGR": ["7.6%", "2.1%", "—", "—"],
        "FY23 Gross $ Rate": ["93.9%", "", "", ""],
        "FY24 Gross $ Rate": ["94.0%", "96.5%", "", ""],
        "FY25 Gross $ Rate": ["95.5%", "92.7%", "94.5%", ""],
        "FY23 NRR": ["111.4%", "", "", ""],
        "FY24 NRR": ["112.1%", "110.4%", "", ""],
        "FY25 NRR": ["102.8%", "94.4%", "103.2%", ""],
        "FY23 Logo Ret": ["94.7%", "", "", ""],
        "FY24 Logo Ret": ["90.0%", "84.2%", "", ""],
        "FY25 Logo Ret": ["92.7%", "87.5%", "93.1%", ""],
    })


def get_cohort_data():
    """Cohort heatmap — yearly vintage view."""
    return pd.DataFrame({
        "Vintage": ["Pre FY20", "FY20", "FY21", "FY22", "FY23", "FY24", "FY25"],
        "Start ARR ($K)": [4200, 1850, 2100, 2450, 3200, 3800, 4100],
        "FY20": [None, 100.0, None, None, None, None, None],
        "FY21": [96.2, 97.1, 100.0, None, None, None, None],
        "FY22": [93.1, 94.3, 96.8, 100.0, None, None, None],
        "FY23": [91.4, 92.0, 93.5, 95.7, 100.0, None, None],
        "FY24": [88.7, 89.5, 91.2, 92.8, 94.0, 100.0, None],
        "FY25": [86.3, 87.2, 88.9, 90.1, 91.5, 93.2, 100.0],
    })


def get_retention_data():
    """Retention % by cohort over time."""
    return pd.DataFrame({
        "Vintage": ["FY20", "FY21", "FY22", "FY23", "FY24", "FY25"],
        "M0": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
        "M3": [98.2, 97.8, 97.5, 96.9, 96.5, 95.8],
        "M6": [96.8, 96.1, 95.7, 95.0, 94.2, None],
        "M9": [95.1, 94.5, 93.9, 93.2, 92.0, None],
        "M12": [93.1, 92.4, 91.8, 90.5, None, None],
        "M18": [89.5, 88.9, 88.1, None, None, None],
        "M24": [86.3, 85.7, None, None, None, None],
        "M36": [81.2, None, None, None, None, None],
    })


def get_segmentation_data():
    """Segmentation by year."""
    return pd.DataFrame({
        "Year": ["FY20", "FY21", "FY22", "FY23", "FY24", "FY25"],
        "New Logo": [42, 55, 68, 78, 85, 92],
        "Expansion": [28, 35, 42, 52, 58, 65],
        "Contraction": [-12, -15, -18, -20, -22, -25],
        "Churn": [-18, -20, -22, -25, -28, -30],
    })


def get_bridge_data():
    """ARR bridge — post cross-tab & transpose."""
    return pd.DataFrame({
        "Bridge Classification": ["Beginning ARR", "New Logo", "Expansion", "Price Impact",
                                   "Contraction", "Downsell", "Churn", "Ending ARR"],
        "FY23": [8200, 1250, 820, 180, -150, -60, -100, 10140],
        "FY24": [10140, 1480, 950, 210, -280, -90, -230, 12180],
        "FY25": [12180, 1620, 1080, 165, -350, -120, -380, 13512],
    })


# ─── STYLING HELPERS ──────────────────────────────────────────────────────────
def color_pct(val, metric_type="retention"):
    """Return CSS color based on metric value and type."""
    if pd.isna(val) or val == "" or val == "—":
        return "color: #4a5a78"
    try:
        n = float(str(val).replace("%", "").replace("(", "-").replace(")", ""))
    except (ValueError, TypeError):
        return ""
    if metric_type == "nrr":
        if n >= 110: return "color: #22c55e; font-weight: 700"
        if n >= 100: return "color: #0ea5e9; font-weight: 600"
        return "color: #ef4444; font-weight: 700"
    else:  # retention, logo ret, gross ret
        if n >= 95: return "color: #22c55e; font-weight: 600"
        if n >= 90: return "color: #eab308; font-weight: 600"
        return "color: #ef4444; font-weight: 700"


def style_kpi_table(df, name_col):
    """Apply Excel-like conditional formatting to KPI tables."""
    def style_cell(val, col):
        if pd.isna(val) or val is None or val == "":
            return "color: #4a5a78; background-color: #0f1729"
        base = "background-color: #0f1729; "
        s = str(val)
        if "NRR" in col or "Net $ Ret" in col:
            return base + color_pct(val, "nrr")
        elif "Ret" in col or "Logo" in col or "Gross" in col:
            return base + color_pct(val, "retention")
        elif "CAGR" in col:
            return base + "color: #0ea5e9; font-weight: 700"
        elif "New Logo" in col:
            return base + "color: #22c55e"
        elif "Churn" in col:
            return base + "color: #ef4444"
        elif "ARR" in col and "EARR" not in col:
            return base + "color: #f8fafc; font-weight: 600"
        return base + "color: #e2e8f0"

    styled = df.style.apply(
        lambda row: [style_cell(row[col], col) for col in df.columns],
        axis=1
    ).set_properties(**{
        "font-size": "12px",
        "text-align": "right",
        "padding": "6px 10px",
        "border-bottom": "1px solid #1a2540",
        "font-family": "'JetBrains Mono', monospace",
    }).set_properties(
        subset=[name_col], **{
            "text-align": "left",
            "font-weight": "600",
            "color": "#f8fafc",
            "font-family": "'Outfit', sans-serif",
            "font-size": "12px",
            "min-width": "160px",
        }
    ).set_table_styles([
        {"selector": "th", "props": [
            ("background-color", "#0f1729"), ("color", "#0ea5e9"),
            ("font-size", "10px"), ("font-weight", "700"),
            ("text-transform", "uppercase"), ("letter-spacing", "0.5px"),
            ("padding", "8px 10px"), ("text-align", "right"),
            ("border-bottom", "2px solid #0ea5e9"), ("white-space", "nowrap"),
        ]},
        {"selector": "th:first-child", "props": [("text-align", "left")]},
        {"selector": "tbody tr:last-child td", "props": [
            ("font-weight", "700"), ("border-top", "2px solid #0ea5e9"),
            ("background-color", "rgba(14,165,233,0.06) !important"),
        ]},
        {"selector": "table", "props": [
            ("border-collapse", "collapse"), ("width", "100%"),
        ]},
    ]).format(
        na_rep="", precision=1
    ).hide(axis="index")

    return styled


def style_heatmap_table(df, value_cols):
    """Apply heatmap coloring — blanks for None/NaN/0."""
    def heat_style(val):
        if pd.isna(val) or val is None or val == 0:
            return "background-color: transparent; color: transparent"
        if val >= 100:
            return "background-color: rgba(14,165,233,0.50); color: #fff; font-weight: 700"
        if val >= 95:
            return "background-color: rgba(34,197,94,0.38); color: #fff; font-weight: 600"
        if val >= 90:
            return "background-color: rgba(34,197,94,0.18); color: #22c55e; font-weight: 600"
        if val >= 85:
            return "background-color: rgba(234,179,8,0.18); color: #eab308; font-weight: 600"
        return "background-color: rgba(239,68,68,0.18); color: #ef4444; font-weight: 700"

    styled = df.style.applymap(
        heat_style, subset=value_cols
    ).set_properties(**{
        "font-size": "12px", "text-align": "center", "padding": "9px 14px",
        "border-bottom": "1px solid #1a2540",
        "font-family": "'JetBrains Mono', monospace",
    }).set_properties(
        subset=["Vintage"], **{
            "text-align": "left", "font-weight": "600", "color": "#f8fafc",
            "font-family": "'Outfit', sans-serif",
        }
    ).set_table_styles([
        {"selector": "th", "props": [
            ("background-color", "#0f1729"), ("color", "#0ea5e9"),
            ("font-size", "11px"), ("font-weight", "700"),
            ("text-align", "center"), ("padding", "9px 14px"),
            ("border-bottom", "2px solid #0ea5e9"),
        ]},
        {"selector": "th:first-child", "props": [("text-align", "left")]},
    ]).format(
        lambda v: "" if pd.isna(v) or v == 0 else f"{v:.1f}%",
        subset=value_cols
    ).hide(axis="index")

    return styled


# ─── CHART BUILDERS ───────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="#0f1729",
    plot_bgcolor="#0f1729",
    font=dict(family="Outfit, sans-serif", color="#e2e8f0", size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    xaxis=dict(gridcolor="#1a2540", zerolinecolor="#1a2540"),
    yaxis=dict(gridcolor="#1a2540", zerolinecolor="#1a2540"),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11)),
)


def build_segmentation_chart(df):
    """Stacked bar chart — yearly segmentation."""
    fig = go.Figure()

    # Positive bars
    fig.add_trace(go.Bar(
        name="New Logo", x=df["Year"], y=df["New Logo"],
        marker_color="#0ea5e9", marker_line_width=0,
    ))
    fig.add_trace(go.Bar(
        name="Expansion", x=df["Year"], y=df["Expansion"],
        marker_color="#22c55e", marker_line_width=0,
    ))
    # Negative bars
    fig.add_trace(go.Bar(
        name="Contraction", x=df["Year"], y=df["Contraction"],
        marker_color="#eab308", marker_line_width=0,
    ))
    fig.add_trace(go.Bar(
        name="Churn", x=df["Year"], y=df["Churn"],
        marker_color="#ef4444", marker_line_width=0,
    ))

    # Net line
    net = df["New Logo"] + df["Expansion"] + df["Contraction"] + df["Churn"]
    fig.add_trace(go.Scatter(
        name="Net", x=df["Year"], y=net,
        mode="lines+markers+text", text=[f"+{v}" for v in net],
        textposition="top center", textfont=dict(color="#22c55e", size=11, family="JetBrains Mono"),
        line=dict(color="#22c55e", width=2, dash="dot"),
        marker=dict(size=7, color="#22c55e"),
    ))

    fig.update_layout(
        **CHART_LAYOUT,
        barmode="relative",
        title=dict(text="Customer Movement by Year", font=dict(size=16, color="#f8fafc")),
        height=420,
        legend=dict(orientation="h", y=1.12, x=0),
    )
    return fig


def build_bridge_chart(df, year_col):
    """Waterfall chart for ARR bridge."""
    vals = df[year_col].tolist()
    labels = df["Bridge Classification"].tolist()

    measures = []
    for i, label in enumerate(labels):
        if label in ("Beginning ARR", "Ending ARR"):
            measures.append("total")
        else:
            measures.append("relative")

    colors_inc = "#0ea5e9"
    colors_dec = "#ef4444"
    colors_tot = "#0ea5e9"

    fig = go.Figure(go.Waterfall(
        name=year_col, orientation="v",
        measure=measures, x=labels, y=vals,
        connector={"line": {"color": "#1a2540", "width": 1}},
        increasing={"marker": {"color": colors_inc}},
        decreasing={"marker": {"color": colors_dec}},
        totals={"marker": {"color": colors_tot}},
        textposition="outside",
        text=[f"${abs(v)/1000:.1f}M" for v in vals],
        textfont=dict(size=11, family="JetBrains Mono", color="#e2e8f0"),
    ))

    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text=f"ARR Bridge — {year_col}", font=dict(size=16, color="#f8fafc")),
        height=420, showlegend=False,
        yaxis_title="ARR ($000s)",
    )
    return fig


# ─── LANDING PAGE ─────────────────────────────────────────────────────────────
def render_landing():
    st.markdown("""
    <div class="landing-container">
        <div class="landing-left">
            <div class="logo-row">
                <div class="logo-icon">S</div>
                <div class="logo-text">SaaS Analytics</div>
            </div>
            <h1 class="hero-title">Real‑Time Revenue<br><span>Analytics Engine</span></h1>
            <p class="hero-sub">Upload billing or revenue data and instantly get cohort analysis,
            ARR bridge breakdowns, retention metrics, and customer segmentation — zero lag, zero manual work.</p>
            <div class="stats-row">
                <div class="stat-box">
                    <div class="stat-label">⚡ Processing</div>
                    <div class="stat-value">&lt;2s</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">◆ Records</div>
                    <div class="stat-value">14.6M</div>
                </div>
                <div class="stat-box">
                    <div class="stat-label">✓ Accuracy</div>
                    <div class="stat-value">99.9%</div>
                </div>
            </div>
            <div class="pills">
                <div class="pill">Cohort SG/PC/RC</div>
                <div class="pill">ARR / MRR Bridge</div>
                <div class="pill">NRR, GRR, Logo Ret.</div>
                <div class="pill">Price vs Volume</div>
                <div class="pill">PE‑grade Waterfall</div>
                <div class="pill">New Logo / Churn Flags</div>
            </div>
        </div>
        <div class="landing-right">
            <div class="login-card">
                <h2>Welcome back</h2>
                <p>Sign in to access the platform, or explore as guest.</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Streamlit login form (rendered inside the right column area)
    # We use columns to position the form on the right
    col1, col2, col3 = st.columns([1.2, 0.1, 1])
    with col1:
        st.write("")  # spacer — left side is handled by HTML above
    with col3:
        st.write("")  # small spacer
        email = st.text_input("Email address", placeholder="you@company.com", key="email_input")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="pass_input")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🔐 Sign In", type="primary", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()
        with col_b:
            if st.button("👁 Guest Demo", use_container_width=True):
                st.session_state.logged_in = True
                st.rerun()


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
def render_dashboard():
    # Top bar
    col1, col2, col3 = st.columns([3, 4, 1])
    with col1:
        st.markdown("""
        <div style="display:flex;align-items:center;gap:10px;padding:4px 0;">
            <div style="width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#0ea5e9,#06b6d4);
                        display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:900;color:#fff;">S</div>
            <span style="font-size:15px;font-weight:700;color:#f8fafc;">SaaS Analytics</span>
            <span style="font-size:9px;font-weight:700;padding:3px 8px;border-radius:5px;
                         background:rgba(14,165,233,0.12);color:#0ea5e9;letter-spacing:0.8px;">ARR WATERFALL</span>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown('<p style="font-size:11px;color:#4a5a78;font-style:italic;text-align:right;padding-top:8px;">FY represents Dec of the fiscal year</p>', unsafe_allow_html=True)
    with col3:
        if st.button("Sign Out", key="signout"):
            st.session_state.logged_in = False
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── KPI Summary Cards ──
    kpi_cards = [
        ("Total ARR", "$13.5M", "+11.0%", True),
        ("Customers", "256", "+7.6%", True),
        ("NRR", "102.4%", "-9.6pp", False),
        ("Logo Retention", "92.4%", "+2.3pp", True),
        ("Avg ARR/Cust", "$52.8K", "+3.1%", True),
        ("Gross $ Ret.", "95.3%", "+1.1pp", True),
    ]
    cols = st.columns(6)
    for i, (label, value, change, is_up) in enumerate(kpi_cards):
        with cols[i]:
            arrow = "▲" if is_up else "▼"
            cls = "kpi-up" if is_up else "kpi-down"
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-label">{label}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-change {cls}">{arrow} {change} <span class="kpi-yoy">YoY</span></div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Tabs ──
    tab_kpi, tab_cohort, tab_retention, tab_seg, tab_bridge = st.tabs([
        "📊 KPI Summary", "🔥 Cohort Heatmap", "📈 Retention %",
        "🧩 Segmentation", "🌉 ARR Bridge"
    ])

    # ── TAB: KPI Summary ──
    with tab_kpi:
        st.markdown('<div class="panel-header"><span style="font-size:18px;font-weight:800;color:#f8fafc;">KPI Summary — YoY</span>'
                    '<span style="font-size:11px;color:#4a5a78;margin-left:12px;">All values in $000s unless noted</span></div>',
                    unsafe_allow_html=True)

        # Product Parent
        st.markdown('<div class="section-title">▸ Product Parent</div>', unsafe_allow_html=True)
        df_prod = get_product_data()
        st.dataframe(
            style_kpi_table(df_prod, "Product Parent"),
            use_container_width=True, height=320,
        )

        # Industry
        st.markdown('<div class="section-title">▸ Industry</div>', unsafe_allow_html=True)
        df_ind = get_industry_data()
        st.dataframe(
            style_kpi_table(df_ind, "Industry"),
            use_container_width=True, height=250,
        )

        # Region
        st.markdown('<div class="section-title">▸ Region</div>', unsafe_allow_html=True)
        df_reg = get_region_data()
        st.dataframe(
            style_kpi_table(df_reg, "Region"),
            use_container_width=True, height=220,
        )

        # Vintage
        st.markdown('<div class="section-title">▸ Vintage</div>', unsafe_allow_html=True)
        df_vin = get_vintage_data()
        st.dataframe(
            style_kpi_table(df_vin, "Vintage"),
            use_container_width=True, height=220,
        )

    # ── TAB: Cohort Heatmap ──
    with tab_cohort:
        st.markdown('<div style="font-size:18px;font-weight:800;color:#f8fafc;margin-bottom:4px;">Cohort Retention Heatmap — By Vintage Year</div>'
                    '<div style="font-size:11px;color:#4a5a78;margin-bottom:14px;">$ Retention % · Blank = no data for that period</div>',
                    unsafe_allow_html=True)

        # Legend
        st.markdown("""
        <div style="display:flex;gap:14px;margin-bottom:14px;flex-wrap:wrap;">
            <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:rgba(14,165,233,0.50);"></div><span style="font-size:11px;color:#8896b0;">100% (base)</span></div>
            <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:rgba(34,197,94,0.38);"></div><span style="font-size:11px;color:#8896b0;">95%+</span></div>
            <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:rgba(34,197,94,0.18);"></div><span style="font-size:11px;color:#8896b0;">90–95%</span></div>
            <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:rgba(234,179,8,0.18);"></div><span style="font-size:11px;color:#8896b0;">85–90%</span></div>
            <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:rgba(239,68,68,0.18);"></div><span style="font-size:11px;color:#8896b0;">&lt;85%</span></div>
        </div>
        """, unsafe_allow_html=True)

        df_cohort = get_cohort_data()
        value_cols = [c for c in df_cohort.columns if c.startswith("FY")]
        st.dataframe(
            style_heatmap_table(df_cohort, value_cols),
            use_container_width=True, height=340,
        )

    # ── TAB: Retention % ──
    with tab_retention:
        st.markdown('<div style="font-size:18px;font-weight:800;color:#f8fafc;margin-bottom:4px;">Gross $ Retention % — By Cohort</div>'
                    '<div style="font-size:11px;color:#4a5a78;margin-bottom:14px;">Tracking dollar retention over time · Blank = insufficient tenure</div>',
                    unsafe_allow_html=True)

        # Legend
        st.markdown("""
        <div style="display:flex;gap:14px;margin-bottom:14px;flex-wrap:wrap;">
            <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:rgba(34,197,94,0.38);"></div><span style="font-size:11px;color:#8896b0;">95%+</span></div>
            <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:rgba(34,197,94,0.18);"></div><span style="font-size:11px;color:#8896b0;">90–95%</span></div>
            <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:rgba(234,179,8,0.18);"></div><span style="font-size:11px;color:#8896b0;">85–90%</span></div>
            <div style="display:flex;align-items:center;gap:5px;"><div style="width:14px;height:14px;border-radius:3px;background:rgba(239,68,68,0.18);"></div><span style="font-size:11px;color:#8896b0;">&lt;85%</span></div>
        </div>
        """, unsafe_allow_html=True)

        df_ret = get_retention_data()
        ret_value_cols = [c for c in df_ret.columns if c != "Vintage"]
        st.dataframe(
            style_heatmap_table(df_ret, ret_value_cols),
            use_container_width=True, height=300,
        )

    # ── TAB: Segmentation ──
    with tab_seg:
        st.markdown('<div style="font-size:18px;font-weight:800;color:#f8fafc;margin-bottom:4px;">Customer Segmentation — By Year</div>'
                    '<div style="font-size:11px;color:#4a5a78;margin-bottom:14px;">New Logo + Expansion vs Contraction + Churn · Shows year-over-year shift</div>',
                    unsafe_allow_html=True)

        df_seg = get_segmentation_data()
        fig_seg = build_segmentation_chart(df_seg)
        st.plotly_chart(fig_seg, use_container_width=True, config={"displayModeBar": False})

        # Summary table
        df_seg_display = df_seg.copy()
        df_seg_display["Net"] = df_seg_display["New Logo"] + df_seg_display["Expansion"] + df_seg_display["Contraction"] + df_seg_display["Churn"]
        st.dataframe(
            df_seg_display.style.set_properties(**{
                "font-size": "12px", "padding": "8px 14px",
                "border-bottom": "1px solid #1a2540",
                "background-color": "#0f1729", "color": "#e2e8f0",
                "font-family": "'JetBrains Mono', monospace",
            }).set_table_styles([
                {"selector": "th", "props": [
                    ("background-color", "#0f1729"), ("color", "#0ea5e9"),
                    ("font-size", "10px"), ("font-weight", "700"),
                    ("text-transform", "uppercase"), ("border-bottom", "2px solid #0ea5e9"),
                ]},
            ]).hide(axis="index"),
            use_container_width=True, height=280,
        )

    # ── TAB: ARR Bridge ──
    with tab_bridge:
        st.markdown('<div style="font-size:18px;font-weight:800;color:#f8fafc;margin-bottom:4px;">ARR Bridge Waterfall</div>'
                    '<div style="font-size:11px;color:#4a5a78;margin-bottom:14px;">Post Cross-Tab &amp; Transpose — Bridge Classification → Bridge Values ($000s)</div>',
                    unsafe_allow_html=True)

        bridge_year = st.radio(
            "Select Year", ["FY23", "FY24", "FY25"],
            index=2, horizontal=True, key="bridge_yr"
        )

        df_bridge = get_bridge_data()
        fig_bridge = build_bridge_chart(df_bridge, bridge_year)
        st.plotly_chart(fig_bridge, use_container_width=True, config={"displayModeBar": False})

        # Bridge detail table
        st.dataframe(
            df_bridge.style.set_properties(**{
                "font-size": "12px", "padding": "8px 14px",
                "border-bottom": "1px solid #1a2540",
                "background-color": "#0f1729", "color": "#e2e8f0",
                "font-family": "'JetBrains Mono', monospace",
                "text-align": "right",
            }).set_properties(
                subset=["Bridge Classification"], **{
                    "text-align": "left", "font-weight": "600", "color": "#f8fafc",
                    "font-family": "'Outfit', sans-serif",
                }
            ).set_table_styles([
                {"selector": "th", "props": [
                    ("background-color", "#0f1729"), ("color", "#0ea5e9"),
                    ("font-size", "10px"), ("font-weight", "700"),
                    ("text-transform", "uppercase"), ("border-bottom", "2px solid #0ea5e9"),
                ]},
            ]).format(
                lambda v: f"{v:,.0f}" if isinstance(v, (int, float)) else v,
                subset=["FY23", "FY24", "FY25"]
            ).hide(axis="index"),
            use_container_width=True, height=360,
        )


# ─── MAIN ─────────────────────────────────────────────────────────────────────
def main():
    if not st.session_state.logged_in:
        render_landing()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
