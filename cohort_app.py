import streamlit as st
import pandas as pd
import numpy as np
import io
import plotly.express as px

st.set_page_config(
    page_title="Analytics Engine",
    page_icon="📊",
    layout="wide"
)

# ---------------- STYLE ---------------- #

st.markdown("""
<style>

.main-title{
font-size:40px;
font-weight:700;
color:#1f2937;
}

.subtitle{
font-size:16px;
color:#6b7280;
margin-bottom:20px;
}

.kpi-card{
background:#f9fafb;
padding:20px;
border-radius:10px;
border:1px solid #e5e7eb;
text-align:center;
}

.info-box{
background:#f1f5f9;
padding:15px;
border-left:6px solid #3b82f6;
border-radius:8px;
}

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📊 Analytics Engine</div>', unsafe_allow_html=True)

st.markdown(
"""
<div class="subtitle">
Analytics Engine performs cohort segmentation and revenue concentration analysis across customers, products and markets.
Identify top performers, long-tail segments and revenue concentration patterns instantly.
</div>
""",
unsafe_allow_html=True
)

# ---------------- SIDEBAR ---------------- #

st.sidebar.title("Navigation")

engine = st.sidebar.radio(
    "Select Engine",
    [
        "Cohort Analytics Engine",
        "Customer Analytics Engine"
    ]
)

# ---------------- CUSTOMER ENGINE ---------------- #

if engine == "Customer Analytics Engine":

    st.markdown(
        "<h1 style='text-align:center;color:#9ca3af;'>Coming Soon</h1>",
        unsafe_allow_html=True
    )

# ---------------- COHORT ENGINE ---------------- #

if engine == "Cohort Analytics Engine":

    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV or Excel File",
        type=["csv","xlsx"]
    )

    st.sidebar.markdown("---")

    # Sample dataset
    sample_df = pd.DataFrame({
        "Customer":["A","B","C","D"],
        "Product":["P1","P2","P3","P4"],
        "Geography":["US","EU","APAC","US"],
        "Revenue":[100,80,60,40],
        "Period":["FY23","FY23","FY23","FY23"]
    })

    st.sidebar.download_button(
        "Download Sample Dataset",
        sample_df.to_csv(index=False),
        "sample_data.csv"
    )

    # Methodology

    with st.expander("📘 Cohort Methodology"):

        col1,col2 = st.columns(2)

        with col1:

            st.table(pd.DataFrame({
                "Rank":["1-10","11-25","26-50",">50"],
                "Group":["Top 10","11-25","26-50","Others"]
            }))

        with col2:

            st.markdown("""
<div class="info-box">
Entities ranked using the selected metric.
This highlights largest contributors by size.
</div>
""",unsafe_allow_html=True)

    if uploaded_file:

        # -------- READ FILE -------- #

        if uploaded_file.name.endswith(".csv"):

            file_bytes = uploaded_file.read()

            try:
                df = pd.read_csv(io.BytesIO(file_bytes),encoding="utf-8",sep=None,engine="python")
            except:
                df = pd.read_csv(io.BytesIO(file_bytes),encoding="latin1",sep=None,engine="python")

        else:
            df = pd.read_excel(uploaded_file)

        st.success("File Loaded Successfully")

        columns = df.columns.tolist()

        metric = st.sidebar.selectbox("Metric Column",columns)

        period_column = st.sidebar.selectbox("Period Column",["None"]+columns)

        if period_column!="None":

            periods = sorted(df[period_column].dropna().unique())

            period_logic = st.sidebar.radio(
                "Period Logic",
                ["Latest Period","Select Periods","All Periods"]
            )

            if period_logic=="Select Periods":
                selected_periods = st.sidebar.multiselect("Select Periods",periods)

        st.sidebar.subheader("Cohort Types")

        rank_flag = st.sidebar.checkbox("Size Group (SG_)")
        pct_flag = st.sidebar.checkbox("Percentile Group (PC_)")
        rev_flag = st.sidebar.checkbox("Revenue Contribution (RC_)")

        # -------- COHORT SETTINGS -------- #

        st.subheader("Individual Cohorts")

        individual_cols = st.multiselect(
            "Columns for Individual Cohorts",
            columns
        )

        st.subheader("Hierarchical Cohorts")

        hierarchy_count = st.number_input("Number of Hierarchies",0,10,0)

        hierarchies=[]

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

            errors=[]

            if not(rank_flag or pct_flag or rev_flag):
                errors.append("Select at least one cohort type")

            if not individual_cols and len(hierarchies)==0:
                errors.append("Select at least one cohort")

            if errors:

                st.error("\n".join(errors))
                st.stop()

            working_df=df.copy()

            if period_column!="None":

                if period_logic=="Latest Period":

                    latest=working_df[period_column].max()
                    working_df=working_df[working_df[period_column]==latest]

                elif period_logic=="Select Periods":

                    working_df=working_df[
                        working_df[period_column].isin(selected_periods)
                    ]

            result=df.copy()

            def clean_name(cols):
                return "_".join(cols)

            def cohort_engine(group_cols):

                temp=(working_df.groupby(group_cols)[metric]
                .sum()
                .reset_index()
                .sort_values(metric,ascending=False))

                temp["Rank"]=temp[metric].rank(method="dense",ascending=False)

                max_rank=temp["Rank"].max()

                outputs={}

                name=clean_name(group_cols)

                if rank_flag:

                    def bucket(x):
                        if x<=10:return"Top 10"
                        elif x<=25:return"11-25"
                        elif x<=50:return"26-50"
                        else:return"Others"

                    outputs[f"SG_{name}"]=temp["Rank"].apply(bucket)

                if pct_flag:

                    temp["Pct"]=temp["Rank"]/max_rank

                    def bucket(x):
                        if x<=.05:return"Top 5%"
                        elif x<=.10:return"Top 10%"
                        elif x<=.20:return"Top 20%"
                        elif x<=.50:return"Top 50%"
                        else:return"Bottom 50%"

                    outputs[f"PC_{name}"]=temp["Pct"].apply(bucket)

                if rev_flag:

                    temp["CumRev"]=temp[metric].cumsum()
                    total=temp[metric].sum()

                    temp["Share"]=temp["CumRev"]/total

                    def bucket(x):
                        if x<=.2:return"Top Drivers"
                        elif x<=.5:return"Mid Tier"
                        elif x<=.8:return"Long Tail"
                        else:return"Bottom Tail"

                    outputs[f"RC_{name}"]=temp["Share"].apply(bucket)

                return temp,outputs

            for col in individual_cols:

                temp,outputs=cohort_engine([col])

                for name,val in outputs.items():

                    temp[name]=val

                    result=result.merge(temp[[col,name]],on=col,how="left")

            for group in hierarchies:

                temp,outputs=cohort_engine(group)

                for name,val in outputs.items():

                    temp[name]=val

                    result=result.merge(
                        temp[group+[name]],
                        on=group,
                        how="left"
                    )

            cohort_cols=[c for c in result.columns if c.startswith(("SG_","PC_","RC_"))]

            result[cohort_cols]=result[cohort_cols].fillna("Others")

            # -------- DASHBOARD -------- #

            st.subheader("Analytics Dashboard")

            col1,col2,col3 = st.columns(3)

            col1.metric("Total Rows",len(result))
            col2.metric("Columns",len(result.columns))
            col3.metric("Cohort Columns",len(cohort_cols))

            st.subheader("Revenue Concentration")

            top = (
                working_df.groupby(individual_cols[0])[metric]
                .sum()
                .sort_values(ascending=False)
                .reset_index()
            )

            fig = px.bar(
                top.head(10),
                x=individual_cols[0],
                y=metric,
                title="Top Contributors"
            )

            st.plotly_chart(fig,use_container_width=True)

            st.subheader("Output Data")

            st.dataframe(result)

            csv=result.to_csv(index=False)

            st.download_button(
                "Download Output",
                csv,
                "cohort_output.csv"
            )
