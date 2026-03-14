import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Revenue Analytics Engine", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------
# CUSTOM CSS — Premium SaaS Dark Theme
# ---------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Hide streamlit default elements */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Main background */
.stApp {
    background: #0A0D14;
    color: #E8EAF0;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0E1117 !important;
    border-right: 1px solid #1E2433 !important;
}
[data-testid="stSidebar"] .stRadio label {
    color: #8892A4 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 6px 8px !important;
    border-radius: 6px !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
    color: #E8EAF0 !important;
    background: #1A2035 !important;
}
[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    color: #8892A4 !important;
}

/* Cards */
.metric-card {
    background: #111827;
    border: 1px solid #1E2B3C;
    border-radius: 12px;
    padding: 20px 24px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #3B82F6, #8B5CF6);
}
.metric-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6B7A99;
    margin-bottom: 8px;
}
.metric-value {
    font-size: 28px;
    font-weight: 700;
    color: #E8EAF0;
    letter-spacing: -0.02em;
    font-family: 'DM Mono', monospace;
}
.metric-change-pos {
    font-size: 12px;
    color: #34D399;
    font-weight: 500;
    margin-top: 4px;
}
.metric-change-neg {
    font-size: 12px;
    color: #F87171;
    font-weight: 500;
    margin-top: 4px;
}
.metric-date {
    font-size: 10px;
    color: #4B5568;
    font-weight: 500;
    position: absolute;
    top: 16px;
    right: 16px;
}

/* Section headers */
.section-header {
    font-size: 14px;
    font-weight: 600;
    color: #8892A4;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin: 24px 0 12px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #1E2433;
}

/* Status badge */
.badge-live {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(52, 211, 153, 0.1);
    border: 1px solid rgba(52, 211, 153, 0.2);
    color: #34D399;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.05em;
}
.badge-soon {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(139, 92, 246, 0.1);
    border: 1px solid rgba(139, 92, 246, 0.2);
    color: #8B5CF6;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.05em;
}

/* Page title */
.page-title {
    font-size: 26px;
    font-weight: 700;
    color: #E8EAF0;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
}
.page-subtitle {
    font-size: 13px;
    color: #6B7A99;
    font-weight: 400;
    margin-bottom: 28px;
}

/* Step indicator */
.step-row {
    display: flex;
    gap: 8px;
    align-items: center;
    margin-bottom: 24px;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    font-weight: 500;
}
.step-num-active {
    width: 24px; height: 24px;
    background: #3B82F6;
    color: white;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700;
}
.step-num-done {
    width: 24px; height: 24px;
    background: #34D399;
    color: #0A0D14;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700;
}
.step-num-inactive {
    width: 24px; height: 24px;
    background: #1E2433;
    color: #4B5568;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700;
}
.step-label-active { color: #E8EAF0; }
.step-label-inactive { color: #4B5568; }
.step-divider {
    flex: 1; height: 1px;
    background: #1E2433;
    max-width: 40px;
}

/* Upload panel */
.upload-panel {
    background: #111827;
    border: 1px solid #1E2B3C;
    border-radius: 12px;
    padding: 24px;
}

/* Coming soon big */
.coming-soon-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 40px;
    text-align: center;
}
.coming-soon-icon {
    font-size: 64px;
    margin-bottom: 20px;
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 0.6; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.05); }
}
.coming-soon-title {
    font-size: 36px;
    font-weight: 700;
    background: linear-gradient(135deg, #8B5CF6, #3B82F6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 12px;
}
.coming-soon-sub {
    font-size: 15px;
    color: #6B7A99;
    max-width: 360px;
}

/* Selectbox, input styling overrides */
.stSelectbox > div > div {
    background: #111827 !important;
    border: 1px solid #1E2B3C !important;
    color: #E8EAF0 !important;
    border-radius: 8px !important;
}
.stTextInput input {
    background: #111827 !important;
    border: 1px solid #1E2B3C !important;
    color: #E8EAF0 !important;
    border-radius: 8px !important;
}
.stMultiSelect > div > div {
    background: #111827 !important;
    border: 1px solid #1E2B3C !important;
    border-radius: 8px !important;
}
.stCheckbox label {
    color: #8892A4 !important;
    font-size: 13px !important;
}
.stButton > button {
    background: linear-gradient(135deg, #3B82F6, #2563EB) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 13px !important;
    padding: 10px 24px !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.3) !important;
}
.stButton > button:disabled {
    background: #1E2433 !important;
    color: #4B5568 !important;
    cursor: not-allowed !important;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1E2433 !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6B7A99 !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 10px 20px !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color: #E8EAF0 !important;
    border-bottom: 2px solid #3B82F6 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding-top: 20px !important;
}

/* Dataframe */
.stDataFrame {
    border: 1px solid #1E2433 !important;
    border-radius: 8px !important;
}

/* Divider */
hr {
    border-color: #1E2433 !important;
}

/* Warning / info */
.stWarning {
    background: rgba(251, 191, 36, 0.08) !important;
    border: 1px solid rgba(251, 191, 36, 0.2) !important;
    border-radius: 8px !important;
}
.stSuccess {
    background: rgba(52, 211, 153, 0.08) !important;
    border: 1px solid rgba(52, 211, 153, 0.2) !important;
    border-radius: 8px !important;
}

/* Number input */
.stNumberInput input {
    background: #111827 !important;
    border: 1px solid #1E2B3C !important;
    color: #E8EAF0 !important;
    border-radius: 8px !important;
}

/* Radio buttons */
.stRadio > div {
    gap: 8px !important;
}

/* Plotly chart background */
.js-plotly-plot .plotly .bg {
    fill: transparent !important;
}

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# PLOTLY DARK THEME CONFIG
# ---------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.6)",
    font=dict(family="DM Sans", color="#8892A4", size=12),
    xaxis=dict(
        gridcolor="#1E2433",
        zerolinecolor="#1E2433",
        tickfont=dict(color="#6B7A99", size=11),
        linecolor="#1E2433",
    ),
    yaxis=dict(
        gridcolor="#1E2433",
        zerolinecolor="#1E2433",
        tickfont=dict(color="#6B7A99", size=11),
        linecolor="#1E2433",
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color="#8892A4", size=11),
    ),
    margin=dict(l=12, r=12, t=36, b=12),
)

BRIDGE_COLORS = {
    "New Logo":      "#34D399",
    "New":           "#34D399",
    "Upsell":        "#60A5FA",
    "Cross Sell":    "#A78BFA",
    "Returning":     "#FCD34D",
    "Downsell":      "#FB923C",
    "Churn":         "#F87171",
    "Partial Churn": "#FCA5A5",
    "Lapsed":        "#94A3B8",
    "No Change":     "#374151",
    "Other In":      "#6EE7B7",
    "Other Out":     "#FCA5A5",
}

# ---------------------------------------------------------
# ADMIN EMAIL
# ---------------------------------------------------------
ADMIN_EMAIL = "ashwanivatsalarya@gmail.com"

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
for key, default in [
    ("user_email", ""),
    ("validated_df", None),
    ("result", None),
    ("mapping", {}),
    ("dataset_type", "Revenue Dataset"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown('<div style="padding: 8px 0 4px 0; font-size:11px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#4B5568;">WORKSPACE</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:14px; font-weight:600; color:#E8EAF0; margin-bottom:20px;">Revenue Analytics Engine</div>', unsafe_allow_html=True)

    st.markdown('<div style="font-size:11px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#4B5568; margin-bottom:8px;">USER</div>', unsafe_allow_html=True)
    user_email = st.text_input("", placeholder="Enter your email", label_visibility="collapsed")
    if user_email:
        st.session_state.user_email = user_email

    st.markdown('<hr style="margin:16px 0;">', unsafe_allow_html=True)

    st.markdown('<div style="font-size:11px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#4B5568; margin-bottom:12px;">ANALYTICS MODULES</div>', unsafe_allow_html=True)

    module = st.radio(
        "",
        ["Cohort Analytics", "Customer Analytics", "Product Bundling", "ACV Analysis", "Revenue Concentration"],
        label_visibility="collapsed"
    )

    st.markdown('<hr style="margin:16px 0;">', unsafe_allow_html=True)

    # Module status
    module_status = {
        "Cohort Analytics": ("🟢", "Live"),
        "Customer Analytics": ("🟢", "Live"),
        "Product Bundling": ("🔵", "Soon"),
        "ACV Analysis": ("🔵", "Soon"),
        "Revenue Concentration": ("🔵", "Soon"),
    }
    for m, (icon, status) in module_status.items():
        badge = "badge-live" if status == "Live" else "badge-soon"
        st.markdown(f'<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 0;"><span style="font-size:12px;color:#6B7A99;">{m}</span><span class="{badge}">{status}</span></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# COMING SOON PAGE
# ---------------------------------------------------------
if module in ["Product Bundling", "ACV Analysis", "Revenue Concentration"]:
    st.markdown(f'<div class="page-title">{module}</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="coming-soon-wrap">
        <div class="coming-soon-icon">🚀</div>
        <div class="coming-soon-title">Coming Soon</div>
        <div class="coming-soon-sub">This module is under development and will be available in the next release.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ---------------------------------------------------------
# FILE LOADER
# ---------------------------------------------------------
def load_file(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8")
        except Exception:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="latin1")
    else:
        df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip()
    return df

# ---------------------------------------------------------
# COHORT ENGINE (ORIGINAL — UNCHANGED)
# ---------------------------------------------------------
def cohort_engine(df, metric, cols, cohort_type):
    temp = (
        df.groupby(cols)[metric]
        .sum()
        .reset_index()
        .sort_values(metric, ascending=False)
    )
    temp["Rank"] = temp[metric].rank(method="dense", ascending=False)
    max_rank = temp["Rank"].max()
    name = "_".join(cols)

    if cohort_type == "SG":
        def bucket(x):
            if x <= 10: return "Top 10"
            elif x <= 25: return "11-25"
            elif x <= 50: return "26-50"
            else: return "Others"
        temp[f"SG_{name}"] = temp["Rank"].apply(bucket)

    if cohort_type == "PC":
        temp["Pct"] = temp["Rank"] / max_rank
        def bucket(x):
            if x <= .05: return "Top 5%"
            elif x <= .10: return "Top 10%"
            elif x <= .20: return "Top 20%"
            elif x <= .50: return "Top 50%"
            else: return "Bottom 50%"
        temp[f"PC_{name}"] = temp["Pct"].apply(bucket)

    if cohort_type == "RC":
        temp["Cum"] = temp[metric].cumsum()
        total = temp[metric].sum()
        temp["Share"] = temp["Cum"] / total
        def bucket(x):
            if x <= .2: return "Top Drivers"
            elif x <= .5: return "Mid Tier"
            elif x <= .8: return "Long Tail"
            else: return "Bottom Tail"
        temp[f"RC_{name}"] = temp["Share"].apply(bucket)

    return temp

# ---------------------------------------------------------
# CUSTOMER ANALYTICS ENGINE
# ---------------------------------------------------------
def generate_monthly_grid(df, customer_col, product_col, date_col, metric, qty_col):
    """Generate a complete monthly grid for every customer-product combination."""
    keys = [customer_col]
    if product_col and product_col != "None":
        keys.append(product_col)

    dataset_max = df[date_col].max()

    lifecycle = (
        df.groupby(keys)
        .agg(Min_Date=(date_col, "min"), Max_Date=(date_col, "max"))
        .reset_index()
    )
    lifecycle["End_Date"] = lifecycle["Max_Date"] + pd.DateOffset(months=12)
    lifecycle["End_Date"] = lifecycle["End_Date"].clip(upper=dataset_max + pd.DateOffset(months=12))

    full_date_range = pd.date_range(
        lifecycle["Min_Date"].min(),
        lifecycle["End_Date"].max(),
        freq="ME"
    )

    lifecycle["_key"] = 1
    months_df = pd.DataFrame({"Date_Grid": full_date_range, "_key": 1})
    grid = lifecycle.merge(months_df, on="_key").drop("_key", axis=1)

    grid = grid[(grid["Date_Grid"] >= grid["Min_Date"]) & (grid["Date_Grid"] <= grid["End_Date"])]
    grid = grid.rename(columns={"Min_Date": "Customer_Min_Date", "Max_Date": "Customer_Max_Date"})

    merge_cols = keys + [date_col]
    grid_cols = keys + ["Date_Grid", "Customer_Min_Date", "Customer_Max_Date", "End_Date"]

    # rename Date_Grid to date_col for merging
    grid = grid.rename(columns={"Date_Grid": date_col})
    df_full = grid[grid_cols[:-1] + ["Customer_Min_Date", "Customer_Max_Date"]].merge(
        df[merge_cols + [metric] + ([qty_col] if qty_col and qty_col != "None" else [])],
        on=keys + [date_col],
        how="left"
    )

    df_full[metric] = df_full[metric].fillna(0)
    if qty_col and qty_col != "None":
        df_full[qty_col] = df_full[qty_col].fillna(0)

    return df_full, keys, dataset_max


def run_customer_analytics(df_raw, customer_col, product_col, date_col, metric,
                            qty_col, channel_col, region_col, lookback_months):
    """Full SaaS revenue bridge engine with lookback windows."""

    df_raw = df_raw.copy()
    df_raw[date_col] = pd.to_datetime(df_raw[date_col])
    df_raw[metric] = pd.to_numeric(df_raw[metric], errors="coerce").fillna(0)
    df_raw = df_raw[df_raw[metric] > 0].copy()

    if qty_col and qty_col != "None":
        df_raw[qty_col] = pd.to_numeric(df_raw[qty_col], errors="coerce").fillna(0)

    # Normalize dates to month end
    df_raw[date_col] = df_raw[date_col] + pd.offsets.MonthEnd(0)

    keys = [customer_col]
    if product_col and product_col != "None":
        keys.append(product_col)

    # Compute dataset max
    dataset_max = df_raw[date_col].max()

    # Customer-level min/max dates
    cust_dates = df_raw.groupby(customer_col).agg(
        Cust_Min_Date=(date_col, "min"),
        Cust_Max_Date=(date_col, "max"),
    ).reset_index()

    # Product-level min/max dates (if product selected)
    if product_col and product_col != "None":
        prod_dates = df_raw.groupby(keys).agg(
            Prod_Min_Date=(date_col, "min"),
            Prod_Max_Date=(date_col, "max"),
        ).reset_index()

    # Generate full monthly grid
    lifecycle = df_raw.groupby(keys).agg(
        Min_Date=(date_col, "min"),
        Max_Date=(date_col, "max"),
    ).reset_index()
    lifecycle["Grid_End"] = (lifecycle["Max_Date"] + pd.DateOffset(months=max(lookback_months))).clip(
        upper=dataset_max + pd.DateOffset(months=max(lookback_months))
    )

    all_months = pd.date_range(lifecycle["Min_Date"].min(), lifecycle["Grid_End"].max(), freq="ME")
    lifecycle["_k"] = 1
    months_df = pd.DataFrame({"Date_Grid": all_months, "_k": 1})
    grid = lifecycle.merge(months_df, on="_k").drop("_k", axis=1)
    grid = grid[(grid["Date_Grid"] >= grid["Min_Date"]) & (grid["Date_Grid"] <= grid["Grid_End"])]
    grid = grid.rename(columns={"Date_Grid": date_col})

    merge_cols = keys + [date_col, metric] + ([qty_col] if qty_col and qty_col != "None" else [])
    df_grid = grid[keys + [date_col, "Min_Date", "Max_Date"]].merge(
        df_raw[merge_cols],
        on=keys + [date_col],
        how="left"
    )
    df_grid[metric] = df_grid[metric].fillna(0)
    if qty_col and qty_col != "None":
        df_grid[qty_col] = df_grid[qty_col].fillna(0)

    # Merge customer dates
    df_grid = df_grid.merge(cust_dates, on=customer_col, how="left")
    if product_col and product_col != "None":
        df_grid = df_grid.merge(prod_dates, on=keys, how="left")

    df_grid = df_grid.sort_values(keys + [date_col])

    # Run per lookback
    results = []
    for lb in lookback_months:
        temp = df_grid.copy()
        temp["Lookback"] = lb

        # Prior values
        temp[f"Prior_{metric}"] = temp.groupby(keys)[metric].shift(1).fillna(0)
        if qty_col and qty_col != "None":
            temp[f"Prior_{qty_col}"] = temp.groupby(keys)[qty_col].shift(1).fillna(0)

        # Flags
        temp["Expiry_Flag"] = np.where(temp[date_col] > temp["Max_Date"], 1, 0)
        temp["DTE"] = np.where(temp["Expiry_Flag"] == 1, temp[f"Prior_{metric}"], 0)

        # Filter noise rows
        mask = ~((temp[metric] == 0) & (temp[f"Prior_{metric}"] == 0) & (temp["DTE"] == 0))
        temp = temp[mask].copy()

        # Lookback date
        temp["Lookback_Date"] = temp[date_col] - pd.DateOffset(months=lb)
        temp["Lookback_Date"] = temp["Lookback_Date"] + pd.offsets.MonthEnd(0)

        # Past/Future flags
        temp["Past_Revenue"] = np.where(
            (temp[date_col] - temp["Cust_Min_Date"]).dt.days / 30 >= lb, "Yes", "No"
        )
        temp["Future_Revenue"] = np.where(
            temp["Cust_Max_Date"] > temp[date_col], "Yes", "No"
        )

        # Bridge classification (vectorized)
        if product_col and product_col != "None":
            conditions = [
                # New Logo
                (temp[f"Prior_{metric}"] == 0) & (temp[metric] > 0) & (temp["Past_Revenue"] == "No") &
                (temp["Cust_Min_Date"] > temp["Lookback_Date"]),
                # Cross Sell
                (temp[f"Prior_{metric}"] == 0) & (temp[metric] > 0) & (temp["Past_Revenue"] == "No") &
                (temp["Prod_Min_Date"] > temp["Lookback_Date"]) & (temp["Cust_Min_Date"] <= temp["Lookback_Date"]),
                # Other In
                (temp[f"Prior_{metric}"] == 0) & (temp[metric] > 0) & (temp["Past_Revenue"] == "No") &
                (temp["Prod_Min_Date"] <= temp["Lookback_Date"]),
                # Returning
                (temp[f"Prior_{metric}"] == 0) & (temp[metric] > 0) & (temp["Past_Revenue"] == "Yes"),
                # Upsell
                (temp[f"Prior_{metric}"] > 0) & (temp[metric] > temp[f"Prior_{metric}"]),
                # Downsell
                (temp[f"Prior_{metric}"] > 0) & (temp[metric] < temp[f"Prior_{metric}"]) & (temp[metric] > 0),
                # Churn
                (temp[f"Prior_{metric}"] > 0) & (temp[metric] == 0) & (temp["DTE"] > 0) &
                (temp["Future_Revenue"] == "No") & (temp["Cust_Max_Date"] < temp[date_col]),
                # Partial Churn
                (temp[f"Prior_{metric}"] > 0) & (temp[metric] == 0) & (temp["DTE"] > 0) &
                (temp["Future_Revenue"] == "No") & (temp["Cust_Max_Date"] >= temp[date_col]),
                # Lapsed
                (temp[metric] == 0) & (temp["Future_Revenue"] == "Yes"),
            ]
            choices = ["New Logo", "Cross Sell", "Other In", "Returning", "Upsell", "Downsell", "Churn", "Partial Churn", "Lapsed"]
        else:
            conditions = [
                (temp[f"Prior_{metric}"] == 0) & (temp[metric] > 0) & (temp["Past_Revenue"] == "No"),
                (temp[f"Prior_{metric}"] == 0) & (temp[metric] > 0) & (temp["Past_Revenue"] == "Yes"),
                (temp[f"Prior_{metric}"] > 0) & (temp[metric] > temp[f"Prior_{metric}"]),
                (temp[f"Prior_{metric}"] > 0) & (temp[metric] < temp[f"Prior_{metric}"]) & (temp[metric] > 0),
                (temp[f"Prior_{metric}"] > 0) & (temp[metric] == 0) & (temp["Future_Revenue"] == "No"),
                (temp[metric] == 0) & (temp["Future_Revenue"] == "Yes"),
            ]
            choices = ["New Logo", "Returning", "Upsell", "Downsell", "Churn", "Lapsed"]

        temp["Bridge"] = np.select(conditions, choices, default="No Change")

        # Bridge value
        temp["Bridge_Value"] = temp[metric] - temp[f"Prior_{metric}"]
        temp["Beginning_ARR"] = temp[f"Prior_{metric}"]
        temp["Ending_ARR"] = temp[metric]

        # Price / Volume (if quantity provided)
        if qty_col and qty_col != "None":
            temp["ASP"] = temp[metric] / temp[qty_col].replace(0, np.nan)
            temp["Prior_ASP"] = temp[f"Prior_{metric}"] / temp[f"Prior_{qty_col}"].replace(0, np.nan)
            temp["Volume_Impact"] = (
                (temp[qty_col] - temp[f"Prior_{qty_col}"]) *
                temp["Prior_ASP"].fillna(0)
            )
            temp["Price_Impact"] = (
                (temp["ASP"].fillna(0) - temp["Prior_ASP"].fillna(0)) *
                temp[f"Prior_{qty_col}"].fillna(0)
            )
            temp["PV_Misc"] = temp["Bridge_Value"] - (
                temp["Volume_Impact"].fillna(0) + temp["Price_Impact"].fillna(0)
            )

        # Vintage
        temp["Vintage"] = temp["Cust_Min_Date"].dt.year

        # Add extra dimension columns if present
        for extra_col in [channel_col, region_col]:
            if extra_col and extra_col != "None" and extra_col in df_raw.columns:
                extra_map = df_raw.drop_duplicates(subset=[customer_col])[[customer_col, extra_col]]
                temp = temp.merge(extra_map, on=customer_col, how="left", suffixes=("", "_extra"))

        results.append(temp)

    master = pd.concat(results, ignore_index=True)
    return master


def compute_retention_metrics(master, metric, lookback):
    """Compute NRR, GRR from the master table for a given lookback."""
    df = master[master["Lookback"] == lookback].copy()
    active_rows = df[df["Beginning_ARR"] > 0].copy()
    if active_rows.empty:
        return {"Beginning ARR": 0, "Ending ARR": 0, "NRR": 0, "GRR": 0, "New ARR": 0, "Lost ARR": 0}

    beginning = active_rows["Beginning_ARR"].sum()
    churn = active_rows.loc[active_rows["Bridge"].isin(["Churn", "Partial Churn"]), "Bridge_Value"].sum()
    downsell = active_rows.loc[active_rows["Bridge"] == "Downsell", "Bridge_Value"].sum()
    upsell = active_rows.loc[active_rows["Bridge"] == "Upsell", "Bridge_Value"].sum()
    cross = active_rows.loc[active_rows["Bridge"] == "Cross Sell", "Bridge_Value"].sum()
    new_arr = df.loc[df["Bridge"].isin(["New Logo"]), "Ending_ARR"].sum()
    ending = df["Ending_ARR"].sum()

    nrr = ((beginning + upsell + cross + churn + downsell) / beginning * 100) if beginning > 0 else 0
    grr = ((beginning + churn + downsell) / beginning * 100) if beginning > 0 else 0

    return {
        "Beginning ARR": beginning,
        "Ending ARR": ending,
        "NRR": round(nrr, 1),
        "GRR": round(grr, 1),
        "New ARR": new_arr,
        "Lost ARR": churn + downsell,
    }


def format_currency(val):
    if abs(val) >= 1_000_000:
        return f"${val/1_000_000:.1f}M"
    elif abs(val) >= 1_000:
        return f"${val/1_000:.0f}K"
    else:
        return f"${val:.0f}"


# ---------------------------------------------------------
# MAIN PAGE HEADER
# ---------------------------------------------------------
st.markdown(f'<div class="page-title">{"Cohort Analytics" if module == "Cohort Analytics" else "Customer Analytics"}</div>', unsafe_allow_html=True)
st.markdown('<div class="page-subtitle">Upload your dataset, map columns, and run analytics</div>', unsafe_allow_html=True)

left, right = st.columns([1, 1.7], gap="large")

# ---------------------------------------------------------
# LEFT PANEL — Upload & Map
# ---------------------------------------------------------
with left:
    # Step indicator
    data_loaded = st.session_state.validated_df is not None
    st.markdown(f"""
    <div class="step-row">
        <div class="step-item">
            <div class="step-num-{'done' if data_loaded else 'active'}">1</div>
            <span class="step-label-active">Upload</span>
        </div>
        <div class="step-divider"></div>
        <div class="step-item">
            <div class="step-num-{'done' if data_loaded else 'inactive'}">2</div>
            <span class="step-label-{'active' if data_loaded else 'inactive'}">Map</span>
        </div>
        <div class="step-divider"></div>
        <div class="step-item">
            <div class="step-num-{'active' if data_loaded else 'inactive'}">3</div>
            <span class="step-label-{'active' if data_loaded else 'inactive'}">Analyze</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="upload-panel">', unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"], label_visibility="collapsed")

    if uploaded_file:
        raw_df = load_file(uploaded_file)
        columns = raw_df.columns.tolist()

        st.markdown('<div class="section-header">Dataset Type</div>', unsafe_allow_html=True)
        dataset_type = st.radio(
            "",
            ["Revenue Dataset", "Billing Dataset", "Bookings Dataset"],
            label_visibility="collapsed",
            horizontal=True
        )
        st.session_state.dataset_type = dataset_type

        if dataset_type == "Bookings Dataset":
            metric_label = "ACV / TCV Column"
        elif dataset_type == "Billing Dataset":
            metric_label = "Billing Amount Column"
        else:
            metric_label = "MRR / ARR Column"

        st.markdown('<div class="section-header">Column Mapping</div>', unsafe_allow_html=True)

        metric = st.selectbox(metric_label, columns)
        customer_col = st.selectbox("Customer Column", columns)
        date_col = st.selectbox("Date Column", columns)
        product_col = st.selectbox("Product Column", ["None"] + columns)
        channel_col = st.selectbox("Channel Column", ["None"] + columns)
        region_col = st.selectbox("Geography / Region Column", ["None"] + columns)
        fiscal_col = st.selectbox("Fiscal Year Column", ["None"] + columns)
        qty_col = st.selectbox("Quantity Column (optional)", ["None"] + columns)

        if st.button("✓  Validate Data"):
            raw_df[date_col] = pd.to_datetime(raw_df[date_col], errors="coerce")
            st.session_state.validated_df = raw_df
            st.session_state.mapping = {
                "metric": metric,
                "customer_col": customer_col,
                "date_col": date_col,
                "product_col": product_col,
                "channel_col": channel_col,
                "region_col": region_col,
                "fiscal_col": fiscal_col,
                "qty_col": qty_col,
            }
            st.success(f"✓ Data validated — {len(raw_df):,} rows loaded")

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------
    # COHORT CONFIGURATION (LEFT PANEL, shown only for cohort module)
    # ---------------------------------------------------------
    if st.session_state.validated_df is not None and module == "Cohort Analytics":
        df = st.session_state.validated_df
        m = st.session_state.mapping
        metric = m["metric"]
        fiscal_col = m["fiscal_col"]
        columns = df.columns.tolist()

        # Fiscal filter
        if fiscal_col != "None":
            st.markdown('<div class="section-header">Period Filter</div>', unsafe_allow_html=True)
            fy_vals = sorted(df[fiscal_col].dropna().unique())
            logic = st.selectbox("Period Logic", ["All Periods", "Latest Period", "Select Fiscal Year"])
            if logic == "Latest Period":
                df = df[df[fiscal_col] == fy_vals[-1]]
            elif logic == "Select Fiscal Year":
                fy = st.selectbox("Fiscal Year", fy_vals)
                df = df[df[fiscal_col] == fy]

        st.markdown('<div class="section-header">Individual Cohorts</div>', unsafe_allow_html=True)
        individual_cols = st.multiselect("Select Columns", columns)

        st.markdown('<div class="section-header">Hierarchical Cohorts</div>', unsafe_allow_html=True)
        hierarchy_count = st.number_input("Number of Hierarchies", 0, 10, 0)
        hierarchies = []
        for i in range(hierarchy_count):
            hcols = st.multiselect(f"Hierarchy {i+1}", columns, key=f"h_{i}")
            if hcols:
                hierarchies.append(hcols)

        st.markdown('<div class="section-header">Cohort Types</div>', unsafe_allow_html=True)
        sg = st.checkbox("Size Group (SG_)")
        pc = st.checkbox("Percentile (PC_)")
        rc = st.checkbox("Revenue Contribution (RC_)")

        if st.button("⚡  Analyze Metrics"):
            result = df.copy()
            for col in individual_cols:
                for flag, ct in [(sg, "SG"), (pc, "PC"), (rc, "RC")]:
                    if flag:
                        t = cohort_engine(df, metric, [col], ct)
                        result = result.merge(t[[col, f"{ct}_{col}"]], on=col, how="left")
            for group in hierarchies:
                name = "_".join(group)
                for flag, ct in [(sg, "SG"), (pc, "PC"), (rc, "RC")]:
                    if flag:
                        t = cohort_engine(df, metric, group, ct)
                        result = result.merge(t[group + [f"{ct}_{name}"]], on=group, how="left")
            st.session_state.result = result

    # ---------------------------------------------------------
    # CUSTOMER ANALYTICS CONFIGURATION (LEFT PANEL)
    # ---------------------------------------------------------
    if st.session_state.validated_df is not None and module == "Customer Analytics":
        st.markdown('<div class="section-header">Analytics Settings</div>', unsafe_allow_html=True)
        lookback_options = st.multiselect(
            "Lookback Windows",
            [1, 3, 6, 12],
            default=[1, 12],
            help="Select lookback periods (months) for retention bridge analysis"
        )

        if st.button("⚡  Run Customer Analytics"):
            m = st.session_state.mapping
            df = st.session_state.validated_df.copy()
            with st.spinner("Running analytics engine..."):
                master = run_customer_analytics(
                    df_raw=df,
                    customer_col=m["customer_col"],
                    product_col=m["product_col"],
                    date_col=m["date_col"],
                    metric=m["metric"],
                    qty_col=m["qty_col"],
                    channel_col=m["channel_col"],
                    region_col=m["region_col"],
                    lookback_months=lookback_options if lookback_options else [1, 12],
                )
            st.session_state.result = master
            st.session_state.lookbacks = lookback_options if lookback_options else [1, 12]
            st.success("✓ Analytics complete")

# ---------------------------------------------------------
# RIGHT PANEL — Analytics Dashboard
# ---------------------------------------------------------
with right:

    # ============================================================
    # COHORT ANALYTICS RIGHT PANEL
    # ============================================================
    if module == "Cohort Analytics":

        if st.session_state.result is not None and st.session_state.validated_df is not None:
            result = st.session_state.result
            m = st.session_state.mapping
            metric = m["metric"]
            fiscal_col = m["fiscal_col"]
            customer_col = m["customer_col"]
            df = st.session_state.validated_df

            cohort_cols = [c for c in result.columns if c.startswith(("SG_", "PC_", "RC_"))]

            tab1, tab2, tab3 = st.tabs(["Summary", "Cohort Analytics", "Output"])

            with tab1:
                # KPI cards
                total_rev = df[metric].sum()
                customers = df[customer_col].nunique() if customer_col != "None" else 0
                rev_per_cust = total_rev / customers if customers > 0 else 0

                c1, c2, c3 = st.columns(3)
                with c1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Total Revenue</div>
                        <div class="metric-value">{format_currency(total_rev)}</div>
                    </div>""", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Customers</div>
                        <div class="metric-value">{customers:,}</div>
                    </div>""", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Revenue / Customer</div>
                        <div class="metric-value">{format_currency(rev_per_cust)}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("")

                # Revenue by fiscal year
                if fiscal_col != "None":
                    fy_summary = df.groupby(fiscal_col).agg(
                        Revenue=(metric, "sum"),
                        Customers=(customer_col, "nunique")
                    ).reset_index()
                    fy_summary["Rev_per_Cust"] = fy_summary["Revenue"] / fy_summary["Customers"]

                    fig = go.Figure()
                    fig.add_bar(x=fy_summary[fiscal_col], y=fy_summary["Revenue"],
                                name="Revenue", marker_color="#3B82F6", opacity=0.85)
                    fig.add_trace(go.Scatter(
                        x=fy_summary[fiscal_col], y=fy_summary["Revenue"],
                        mode="lines+markers", name="Trend",
                        line=dict(color="#8B5CF6", width=2),
                        marker=dict(size=6, color="#8B5CF6")
                    ))
                    fig.update_layout(title="Revenue by Fiscal Year", **PLOTLY_LAYOUT)
                    st.plotly_chart(fig, use_container_width=True)

                    c1, c2 = st.columns(2)
                    with c1:
                        fig2 = px.bar(fy_summary, x=fiscal_col, y="Customers",
                                      title="Customers by Fiscal Year",
                                      color_discrete_sequence=["#34D399"])
                        fig2.update_layout(**PLOTLY_LAYOUT)
                        st.plotly_chart(fig2, use_container_width=True)
                    with c2:
                        fig3 = px.bar(fy_summary, x=fiscal_col, y="Rev_per_Cust",
                                      title="Revenue per Customer",
                                      color_discrete_sequence=["#FCD34D"])
                        fig3.update_layout(**PLOTLY_LAYOUT)
                        st.plotly_chart(fig3, use_container_width=True)

                # Segmentation
                if customer_col != "None":
                    seg = df.groupby(customer_col)[metric].sum().reset_index()
                    seg["Rank"] = seg[metric].rank(method="dense", ascending=False)
                    seg["Pct"] = seg["Rank"] / seg["Rank"].max()
                    seg["Segment"] = pd.cut(seg["Pct"], bins=[0, .05, .1, .2, 1],
                                            labels=["Top 5%", "Top 10%", "Top 20%", "Long Tail"])
                    pie_data = seg.groupby("Segment")[metric].sum().reset_index()
                    fig4 = px.pie(pie_data, names="Segment", values=metric,
                                  title="Customer Segmentation",
                                  color_discrete_sequence=["#3B82F6", "#8B5CF6", "#34D399", "#6B7A99"])
                    fig4.update_layout(**PLOTLY_LAYOUT)
                    fig4.update_traces(textfont_color="#E8EAF0")
                    st.plotly_chart(fig4, use_container_width=True)

            with tab2:
                # Cohort heatmap
                date_col = m["date_col"]
                if customer_col != "None" and date_col != "None":
                    try:
                        hdf = df.copy()
                        hdf[date_col] = pd.to_datetime(hdf[date_col])
                        hdf["OrderMonth"] = hdf[date_col].dt.to_period("M").astype(str)
                        cohort_map = hdf.groupby(customer_col)["OrderMonth"].min()
                        hdf["CohortMonth"] = hdf[customer_col].map(cohort_map)
                        hdf["CohortIndex"] = (
                            pd.to_datetime(hdf["OrderMonth"]) - pd.to_datetime(hdf["CohortMonth"])
                        ).dt.days // 30

                        pivot = pd.pivot_table(
                            hdf, values=customer_col, index="CohortMonth",
                            columns="CohortIndex", aggfunc="nunique"
                        ).fillna(0)

                        fig_h = px.imshow(pivot, text_auto=True,
                                          color_continuous_scale="Blues",
                                          title="Cohort Heatmap — Customer Count",
                                          aspect="auto")
                        fig_h.update_layout(**PLOTLY_LAYOUT)
                        st.plotly_chart(fig_h, use_container_width=True)

                        retention = pivot.divide(pivot.iloc[:, 0], axis=0) * 100
                        fig_r = px.imshow(retention, text_auto=".0f",
                                          color_continuous_scale="Greens",
                                          title="Retention % by Cohort",
                                          aspect="auto")
                        fig_r.update_layout(**PLOTLY_LAYOUT)
                        st.plotly_chart(fig_r, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Cohort heatmap unavailable: {e}")
                else:
                    st.info("Map Customer and Date columns to see the cohort heatmap.")

            with tab3:
                st.markdown(f'<div class="section-header">Cohort Output — {len(result):,} rows · {len(cohort_cols)} cohort columns added</div>', unsafe_allow_html=True)
                st.dataframe(result, use_container_width=True, height=400)
                csv = result.to_csv(index=False)
                if st.session_state.user_email == ADMIN_EMAIL:
                    st.download_button("⬇  Download Output", csv, "cohort_output.csv", use_container_width=True)
                else:
                    st.download_button("⬇  Download Output", csv, disabled=True, use_container_width=True)
                    st.warning("🔒 Download is available only for subscribed users.")

        elif st.session_state.validated_df is None:
            st.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:80px 40px;text-align:center;">
                <div style="font-size:48px;margin-bottom:16px;">📊</div>
                <div style="font-size:20px;font-weight:600;color:#E8EAF0;margin-bottom:8px;">Upload your dataset to begin</div>
                <div style="font-size:13px;color:#6B7A99;">Map your columns and click Validate Data to get started</div>
            </div>
            """, unsafe_allow_html=True)

    # ============================================================
    # CUSTOMER ANALYTICS RIGHT PANEL
    # ============================================================
    elif module == "Customer Analytics":

        if st.session_state.result is not None and isinstance(st.session_state.result, pd.DataFrame) and "Bridge" in st.session_state.result.columns:

            master = st.session_state.result
            m = st.session_state.mapping
            metric = m["metric"]
            customer_col = m["customer_col"]
            date_col = m["date_col"]
            lookbacks = st.session_state.get("lookbacks", [1, 12])

            # Lookback selector
            selected_lb = st.selectbox(
                "Lookback Window",
                lookbacks,
                format_func=lambda x: f"{x} Month{'s' if x > 1 else ''}",
            )

            metrics = compute_retention_metrics(master, metric, selected_lb)
            df_lb = master[master["Lookback"] == selected_lb].copy()

            # KPI row
            c1, c2, c3, c4, c5, c6 = st.columns(6)
            cards = [
                ("Total ARR", format_currency(metrics["Ending ARR"]), ""),
                ("New ARR", format_currency(metrics["New ARR"]), "pos"),
                ("Lost ARR", format_currency(metrics["Lost ARR"]), "neg"),
                ("Net Retention", f"{metrics['NRR']}%", "pos" if metrics["NRR"] >= 100 else "neg"),
                ("Gross Retention", f"{metrics['GRR']}%", "pos" if metrics["GRR"] >= 80 else "neg"),
                ("Beginning ARR", format_currency(metrics["Beginning ARR"]), ""),
            ]
            for col_obj, (label, val, chg_class) in zip([c1, c2, c3, c4, c5, c6], cards):
                with col_obj:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">{label}</div>
                        <div class="metric-value" style="font-size:20px;">{val}</div>
                    </div>""", unsafe_allow_html=True)

            st.markdown("")

            tab1, tab2, tab3, tab4 = st.tabs(["Revenue Bridge", "Top Customers", "Retention Trends", "Output"])

            with tab1:
                # Waterfall bridge chart
                bridge_agg = df_lb.groupby("Bridge")["Bridge_Value"].sum().reset_index()
                bridge_agg = bridge_agg[bridge_agg["Bridge"] != "No Change"]
                bridge_agg["Color"] = bridge_agg["Bridge"].map(BRIDGE_COLORS).fillna("#6B7A99")
                bridge_agg = bridge_agg.sort_values("Bridge_Value", ascending=False)

                fig_b = go.Figure(go.Bar(
                    x=bridge_agg["Bridge"],
                    y=bridge_agg["Bridge_Value"],
                    marker_color=bridge_agg["Color"],
                    text=[format_currency(v) for v in bridge_agg["Bridge_Value"]],
                    textposition="outside",
                    textfont=dict(color="#8892A4", size=11),
                ))
                fig_b.update_layout(title=f"Revenue Bridge ({selected_lb}M Lookback)", **PLOTLY_LAYOUT)
                st.plotly_chart(fig_b, use_container_width=True)

                # Revenue bridge by period
                if date_col in df_lb.columns:
                    bridge_period = (
                        df_lb.groupby([date_col, "Bridge"])["Bridge_Value"]
                        .sum()
                        .reset_index()
                    )
                    bridge_period = bridge_period[bridge_period["Bridge"] != "No Change"]
                    top_bridges = bridge_period.groupby("Bridge")["Bridge_Value"].sum().abs().nlargest(6).index.tolist()
                    bridge_period = bridge_period[bridge_period["Bridge"].isin(top_bridges)]

                    fig_bp = px.bar(
                        bridge_period,
                        x=date_col, y="Bridge_Value", color="Bridge",
                        title=f"Revenue Movement Over Time",
                        color_discrete_map=BRIDGE_COLORS,
                        barmode="relative"
                    )
                    fig_bp.update_layout(**PLOTLY_LAYOUT)
                    st.plotly_chart(fig_bp, use_container_width=True)

                # Price vs Volume (if available)
                if "Price_Impact" in df_lb.columns:
                    pv_sum = {
                        "Price Impact": df_lb["Price_Impact"].fillna(0).sum(),
                        "Volume Impact": df_lb["Volume_Impact"].fillna(0).sum(),
                        "Mix / Other": df_lb["PV_Misc"].fillna(0).sum(),
                    }
                    pv_df = pd.DataFrame({"Driver": list(pv_sum.keys()), "Value": list(pv_sum.values())})
                    fig_pv = px.bar(pv_df, x="Driver", y="Value",
                                    title="Price vs Volume Decomposition",
                                    color="Driver",
                                    color_discrete_sequence=["#3B82F6", "#34D399", "#FCD34D"])
                    fig_pv.update_layout(**PLOTLY_LAYOUT)
                    st.plotly_chart(fig_pv, use_container_width=True)

            with tab2:
                # Top customers
                top_df = df_lb.groupby(customer_col).agg(
                    Ending_ARR=(metric, "sum"),
                    ARR_Change=("Bridge_Value", "sum"),
                ).reset_index().sort_values("Ending_ARR", ascending=False).head(20)
                top_df["Ending_ARR_Fmt"] = top_df["Ending_ARR"].apply(format_currency)
                top_df["ARR_Change_Fmt"] = top_df["ARR_Change"].apply(format_currency)

                fig_top = go.Figure(go.Bar(
                    x=top_df["Ending_ARR"].head(10),
                    y=top_df[customer_col].head(10),
                    orientation="h",
                    marker_color="#3B82F6",
                    text=[format_currency(v) for v in top_df["Ending_ARR"].head(10)],
                    textposition="outside",
                    textfont=dict(color="#8892A4", size=11),
                ))
                fig_top.update_layout(title="Top 10 Customers by ARR",
                                       yaxis=dict(autorange="reversed"),
                                       **PLOTLY_LAYOUT)
                st.plotly_chart(fig_top, use_container_width=True)

                # Top movers
                top_up = df_lb.groupby(customer_col)["Bridge_Value"].sum().reset_index()
                col_u, col_d = st.columns(2)

                with col_u:
                    upsell = top_up[top_up["Bridge_Value"] > 0].sort_values("Bridge_Value", ascending=False).head(10)
                    fig_u = go.Figure(go.Bar(
                        x=upsell["Bridge_Value"], y=upsell[customer_col],
                        orientation="h", marker_color="#34D399",
                        text=[format_currency(v) for v in upsell["Bridge_Value"]],
                        textposition="outside",
                        textfont=dict(color="#8892A4", size=10),
                    ))
                    fig_u.update_layout(title="Top Upsell Movers",
                                         yaxis=dict(autorange="reversed"),
                                         **PLOTLY_LAYOUT)
                    st.plotly_chart(fig_u, use_container_width=True)

                with col_d:
                    churn_df = top_up[top_up["Bridge_Value"] < 0].sort_values("Bridge_Value").head(10)
                    fig_d = go.Figure(go.Bar(
                        x=churn_df["Bridge_Value"], y=churn_df[customer_col],
                        orientation="h", marker_color="#F87171",
                        text=[format_currency(v) for v in churn_df["Bridge_Value"]],
                        textposition="outside",
                        textfont=dict(color="#8892A4", size=10),
                    ))
                    fig_d.update_layout(title="Top Churn / Contraction",
                                         yaxis=dict(autorange="reversed"),
                                         **PLOTLY_LAYOUT)
                    st.plotly_chart(fig_d, use_container_width=True)

                # Region / Geography breakdown (if available)
                region_col = m["region_col"]
                if region_col and region_col != "None" and region_col in df_lb.columns:
                    region_df = df_lb.groupby(region_col)[metric].sum().reset_index().sort_values(metric, ascending=False)
                    fig_reg = go.Figure(go.Bar(
                        x=region_df[metric], y=region_df[region_col],
                        orientation="h", marker_color="#8B5CF6",
                        text=[format_currency(v) for v in region_df[metric]],
                        textposition="outside",
                        textfont=dict(color="#8892A4", size=10),
                    ))
                    fig_reg.update_layout(title="ARR by Geography",
                                           yaxis=dict(autorange="reversed"),
                                           **PLOTLY_LAYOUT)
                    st.plotly_chart(fig_reg, use_container_width=True)

                st.dataframe(top_df[[customer_col, "Ending_ARR_Fmt", "ARR_Change_Fmt"]].rename(
                    columns={"Ending_ARR_Fmt": "Ending ARR", "ARR_Change_Fmt": "ARR Change"}
                ), use_container_width=True)

            with tab3:
                # NRR/GRR by period
                nrr_rows = []
                for lb in lookbacks:
                    df_t = master[master["Lookback"] == lb].copy()
                    if date_col not in df_t.columns:
                        continue
                    for period, grp in df_t.groupby(date_col):
                        beg = grp["Beginning_ARR"].sum()
                        churn_v = grp.loc[grp["Bridge"].isin(["Churn", "Partial Churn"]), "Bridge_Value"].sum()
                        down_v = grp.loc[grp["Bridge"] == "Downsell", "Bridge_Value"].sum()
                        up_v = grp.loc[grp["Bridge"] == "Upsell", "Bridge_Value"].sum()
                        cross_v = grp.loc[grp["Bridge"] == "Cross Sell", "Bridge_Value"].sum()
                        if beg > 0:
                            nrr = ((beg + up_v + cross_v + churn_v + down_v) / beg) * 100
                            grr = ((beg + churn_v + down_v) / beg) * 100
                            nrr_rows.append({"Period": period, "Lookback": f"{lb}M", "NRR": nrr, "GRR": grr})

                if nrr_rows:
                    nrr_df = pd.DataFrame(nrr_rows)
                    fig_nrr = px.line(nrr_df, x="Period", y="NRR", color="Lookback",
                                      title="Net Revenue Retention % Over Time",
                                      color_discrete_sequence=["#3B82F6", "#34D399", "#8B5CF6", "#FCD34D"])
                    fig_nrr.add_hline(y=100, line_dash="dot", line_color="#6B7A99", annotation_text="100%")
                    fig_nrr.update_layout(**PLOTLY_LAYOUT)
                    st.plotly_chart(fig_nrr, use_container_width=True)

                    fig_grr = px.line(nrr_df, x="Period", y="GRR", color="Lookback",
                                      title="Gross Revenue Retention % Over Time",
                                      color_discrete_sequence=["#F87171", "#FB923C", "#FCD34D", "#6B7A99"])
                    fig_grr.update_layout(**PLOTLY_LAYOUT)
                    st.plotly_chart(fig_grr, use_container_width=True)

                # Vintage cohort revenue
                if "Vintage" in df_lb.columns:
                    vintage_df = df_lb.groupby("Vintage")[metric].sum().reset_index()
                    fig_v = px.bar(vintage_df, x="Vintage", y=metric,
                                   title="ARR by Customer Vintage (Cohort Year)",
                                   color_discrete_sequence=["#A78BFA"])
                    fig_v.update_layout(**PLOTLY_LAYOUT)
                    st.plotly_chart(fig_v, use_container_width=True)

            with tab4:
                output_cols = [c for c in master.columns if not c.startswith(("_", "Prior_", "Cum", "Share", "Pct", "Past_", "Future_", "Expiry_", "DTE", "Lookback_Date"))]
                output_df = master[output_cols].copy()
                st.markdown(f'<div class="section-header">Master Analytics Table — {len(output_df):,} rows</div>', unsafe_allow_html=True)
                st.dataframe(output_df, use_container_width=True, height=400)

                csv_out = output_df.to_csv(index=False)
                if st.session_state.user_email == ADMIN_EMAIL:
                    st.download_button("⬇  Download Full Analytics Output", csv_out, "customer_analytics_output.csv", use_container_width=True)
                else:
                    st.download_button("⬇  Download Full Analytics Output", csv_out, disabled=True, use_container_width=True)
                    st.warning("🔒 Download is available only for subscribed users.")

        elif st.session_state.validated_df is None:
            st.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:80px 40px;text-align:center;">
                <div style="font-size:48px;margin-bottom:16px;">📈</div>
                <div style="font-size:20px;font-weight:600;color:#E8EAF0;margin-bottom:8px;">Upload your dataset to begin</div>
                <div style="font-size:13px;color:#6B7A99;">Map your columns and click Validate Data to get started</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 40px;text-align:center;">
                <div style="font-size:40px;margin-bottom:16px;">⚡</div>
                <div style="font-size:18px;font-weight:600;color:#E8EAF0;margin-bottom:8px;">Configure & Run Analytics</div>
                <div style="font-size:13px;color:#6B7A99;">Select lookback windows and click Run Customer Analytics</div>
            </div>
            """, unsafe_allow_html=True)
