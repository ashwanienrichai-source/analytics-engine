import streamlit as st
import pandas as pd
import numpy as np
import io

st.set_page_config(
    page_title="Analytics Engine",
    page_icon="📊",
    layout="wide"
)

# ---------- STYLE ----------
st.markdown("""
<style>

.main-title{
    font-size:42px;
    font-weight:700;
    color:#2c3e50;
}

.section-title{
    font-size:22px;
    font-weight:600;
    color:#34495e;
}

.info-box{
    background-color:#f4f7fb;
    border-left:6px solid #3498db;
    padding:15px;
    border-radius:8px;
    margin-bottom:15px;
}

.table-box{
    background-color:#ffffff;
    padding:10px;
    border-radius:8px;
}

.coming-soon{
    text-align:center;
    font-size:60px;
    font-weight:700;
    color:#7f8c8d;
    animation: pulse 2s infinite;
}

@keyframes pulse {
 0% {opacity:0.3}
 50% {opacity:1}
 100% {opacity:0.3}
}

</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">📊 Analytics Engine</p>', unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("Navigation")

engine = st.sidebar.radio(
    "Select Engine",
    [
        "Cohort Analytics Engine",
        "Customer Analytics Engine"
    ]
)

# -----------------------------------------------------------
# CUSTOMER ANALYTICS ENGINE
# -----------------------------------------------------------

if engine == "Customer Analytics Engine":

    st.markdown('<p class="coming-soon">Coming Soon!</p>', unsafe_allow_html=True)

# -----------------------------------------------------------
# COHORT ANALYTICS ENGINE
# -----------------------------------------------------------

if engine == "Cohort Analytics Engine":

    st.sidebar.markdown("---")

    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV or Excel File",
        type=["csv","xlsx"]
    )

    # ---------- METHODOLOGY ----------
    with st.expander("📘 Cohort Methodology (Basis of Understanding)"):

        col1, col2 = st.columns([1,1])

        with col1:

            st.markdown("### Size Group")

            st.table(pd.DataFrame({
                "Rank Range":[
                    "1–10",
                    "11–25",
                    "26–50",
                    ">50"
                ],
                "Group":[
                    "Top 10",
                    "11-25",
                    "26-50",
                    "Others"
                ]
            }))

        with col2:

            st.markdown("""
<div class="info-box">
Entities are ranked using the selected metric.

This helps identify the <b>largest contributors by size</b>
(customer, product, geography, etc.).
</div>
""", unsafe_allow_html=True)

        col1, col2 = st.columns([1,1])

        with col1:

            st.markdown("### Percentile Group")

            st.table(pd.DataFrame({
                "Percentile":[
                    "0–5%",
                    "5–10%",
                    "10–20%",
                    "20–50%",
                    "50–100%"
                ],
                "Group":[
                    "Top 5%",
                    "Top 10%",
                    "Top 20%",
                    "Top 50%",
                    "Bottom 50%"
                ]
            }))

        with col2:

            st.markdown("""
<div class="info-box">
Entities grouped based on relative rank distribution.

Useful for identifying <b>top performers vs the long tail</b>.
</div>
""", unsafe_allow_html=True)

        col1, col2 = st.columns([1,1])

        with col1:

            st.markdown("### Revenue Contribution")

            st.table(pd.DataFrame({
                "Revenue Share":[
                    "0–20%",
                    "20–50%",
                    "50–80%",
                    "80–100%"
                ],
                "Group":[
                    "Top Drivers",
                    "Mid Tier",
                    "Long Tail",
                    "Bottom Tail"
                ]
            }))

        with col2:

            st.markdown("""
<div class="info-box">
Entities grouped by cumulative contribution to total revenue.

Helps understand <b>revenue concentration and dependency risk</b>.
</div>
""", unsafe_allow_html=True)

    if uploaded_file:

        # ---------- READ FILE ----------
        if uploaded_file.name.endswith(".csv"):

            file_bytes = uploaded_file.read()

            try:
                df = pd.read_csv(io.BytesIO(file_bytes), encoding="utf-8", sep=None, engine="python")
            except:
                df = pd.read_csv(io.BytesIO(file_bytes), encoding="latin1", sep=None, engine="python")

        else:
            df = pd.read_excel(uploaded_file)

        st.success("File Loaded Successfully")

        st.dataframe(df.head())

        columns = df.columns.tolist()

        # ---------- CONFIGURATION ----------
        metric = st.sidebar.selectbox("Metric Column", columns)

        period_column = st.sidebar.selectbox(
            "Period Column",
            ["None"] + columns
        )

        if period_column != "None":

            periods = sorted(df[period_column].dropna().unique())

            period_logic = st.sidebar.radio(
                "Period Logic",
                ["Latest Period","Select Periods","All Periods"]
            )

            if period_logic == "Select Periods":
                selected_periods = st.sidebar.multiselect("Select Periods", periods)

        st.sidebar.markdown("---")

        st.sidebar.subheader("Cohort Types")

        rank_flag = st.sidebar.checkbox("Size Group (SG_)")
        pct_flag = st.sidebar.checkbox("Percentile Group (PC_)")
        rev_flag = st.sidebar.checkbox("Revenue Contribution (RC_)")

        # ---------- INDIVIDUAL ----------
        st.markdown('<p class="section-title">Individual Cohorts</p>', unsafe_allow_html=True)

        individual_cols = st.multiselect(
            "Columns for Individual Cohorts",
            columns
        )

        # ---------- HIERARCHY ----------
        st.markdown('<p class="section-title">Hierarchical Cohorts</p>', unsafe_allow_html=True)

        hierarchy_count = st.number_input(
            "Number of Hierarchies",
            0,
            10,
            0
        )

        hierarchies = []

        for i in range(hierarchy_count):

            cols = st.multiselect(
                f"Hierarchy {i+1} Columns",
                columns,
                key=f"h{i}"
            )

            if cols:
                hierarchies.append(cols)

        generate = st.button("Generate Cohorts")

        if generate:

            errors = []

            if not (rank_flag or pct_flag or rev_flag):
                errors.append("Select at least one Cohort Type")

            if not individual_cols and len(hierarchies) == 0:
                errors.append("Select at least one Cohort Definition")

            if period_column != "None" and period_logic == "Select Periods":
                if not selected_periods:
                    errors.append("Select Periods")

            if errors:

                st.error(
                    "⚠️ Please complete the following:\n\n"
                    + "\n".join([f"• {e}" for e in errors])
                )

                st.stop()

            working_df = df.copy()

            if period_column != "None":

                if period_logic == "Latest Period":

                    latest = working_df[period_column].max()

                    working_df = working_df[
                        working_df[period_column] == latest
                    ]

                elif period_logic == "Select Periods":

                    working_df = working_df[
                        working_df[period_column].isin(selected_periods)
                    ]

            result = df.copy()

            def clean_name(cols):
                return "_".join([c.replace(" ","").replace("-","") for c in cols])

            def cohort_engine(group_cols):

                temp = (
                    working_df.groupby(group_cols)[metric]
                    .sum()
                    .reset_index()
                    .sort_values(metric, ascending=False)
                )

                temp["Rank"] = temp[metric].rank(method="dense", ascending=False)

                max_rank = temp["Rank"].max()

                outputs = {}

                name = clean_name(group_cols)

                if rank_flag:

                    def rank_bucket(x):
                        if x <= 10: return "Top 10"
                        elif x <= 25: return "11-25"
                        elif x <= 50: return "26-50"
                        else: return "Others"

                    outputs[f"SG_{name}"] = temp["Rank"].apply(rank_bucket)

                if pct_flag:

                    temp["Percentile"] = temp["Rank"]/max_rank

                    def pct_bucket(x):
                        if x <= .05: return "Top 5%"
                        elif x <= .10: return "Top 10%"
                        elif x <= .20: return "Top 20%"
                        elif x <= .50: return "Top 50%"
                        else: return "Bottom 50%"

                    outputs[f"PC_{name}"] = temp["Percentile"].apply(pct_bucket)

                if rev_flag:

                    temp["CumRevenue"] = temp[metric].cumsum()
                    total = temp[metric].sum()

                    temp["CumPct"] = temp["CumRevenue"]/total

                    def rev_bucket(x):
                        if x <= .20: return "Top Drivers"
                        elif x <= .50: return "Mid Tier"
                        elif x <= .80: return "Long Tail"
                        else: return "Bottom Tail"

                    outputs[f"RC_{name}"] = temp["CumPct"].apply(rev_bucket)

                return temp, outputs

            for col in individual_cols:

                temp, outputs = cohort_engine([col])

                for name, values in outputs.items():

                    temp[name] = values

                    result = result.merge(
                        temp[[col,name]],
                        on=col,
                        how="left"
                    )

            for group_cols in hierarchies:

                temp, outputs = cohort_engine(group_cols)

                for name, values in outputs.items():

                    temp[name] = values

                    result = result.merge(
                        temp[group_cols+[name]],
                        on=group_cols,
                        how="left"
                    )

            cohort_cols = [c for c in result.columns if c.startswith(("SG_","PC_","RC_"))]

            result[cohort_cols] = result[cohort_cols].fillna("Others")

            st.success("Cohorts Generated Successfully")

            st.dataframe(result.head())

            csv = result.to_csv(index=False)

            st.download_button(
                "Download Output File",
                csv,
                "cohort_output.csv",
                "text/csv"
            )