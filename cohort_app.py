import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

st.set_page_config(page_title="Analytics Engine", layout="wide")

# ---------------- SESSION ---------------- #

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "premium" not in st.session_state:
    st.session_state.premium = False


# ---------------- STYLE ---------------- #

st.markdown("""
<style>

.main-title{
font-size:40px;
font-weight:700;
}

.subtitle{
color:gray;
margin-bottom:20px;
}

.login-box{
background:#f3f4f6;
padding:30px;
border-radius:10px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- LOGIN PAGE ---------------- #

def login_page():

    st.markdown('<div class="main-title">Analytics Engine</div>', unsafe_allow_html=True)

    st.markdown(
    """
Login to access the analytics platform and unlock premium features.
"""
    )

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        st.markdown('<div class="login-box">',unsafe_allow_html=True)

        email = st.text_input("Email")
        password = st.text_input("Password",type="password")

        if st.button("Login"):

            if email and password:

                st.session_state.logged_in=True
                st.success("Login successful")
                st.rerun()

            else:

                st.error("Enter credentials")

        st.markdown("---")

        st.subheader("Premium Subscription")

        st.markdown("""
Premium unlocks:

• Download analytics output  
• Advanced reporting  
• Future analytics modules
""")

        st.markdown("### Price: **$25**")

        if st.button("Upgrade to Premium ($25)"):

            st.session_state.premium=True
            st.success("Premium activated")

        st.markdown("</div>",unsafe_allow_html=True)


# ---------------- CUSTOMER ENGINE ---------------- #

def customer_engine():

    st.title("Customer Analytics Engine")

    st.markdown(
        "<h1 style='text-align:center;color:gray;margin-top:120px;'>Coming Soon</h1>",
        unsafe_allow_html=True
    )


# ---------------- COHORT ENGINE ---------------- #

def cohort_engine():

    st.markdown('<div class="main-title">📊 Cohort Analytics Engine</div>',unsafe_allow_html=True)

    st.markdown(
    """
Segmentation and revenue concentration analytics across customers,
products and markets.
"""
    )

    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV or Excel",
        type=["csv","xlsx"]
    )

    if uploaded_file:

        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        columns = df.columns.tolist()

        metric = st.sidebar.selectbox("Metric Column",columns)

        period_column = st.sidebar.selectbox(
            "Period Column",
            ["None"]+columns
        )

        if period_column!="None":

            periods = sorted(df[period_column].dropna().unique())

            period_logic = st.sidebar.radio(
                "Period Logic",
                ["Latest Period","Select Periods","All Periods"]
            )

            if period_logic=="Select Periods":
                selected_periods = st.sidebar.multiselect(
                    "Select Periods",
                    periods
                )

        st.sidebar.subheader("Cohort Types")

        rank_flag = st.sidebar.checkbox("Size Group (SG_)")
        pct_flag = st.sidebar.checkbox("Percentile (PC_)")
        rev_flag = st.sidebar.checkbox("Revenue Contribution (RC_)")

        st.subheader("Individual Cohorts")

        individual_cols = st.multiselect(
            "Select Columns",
            columns
        )

        st.subheader("Hierarchical Cohorts")

        hierarchy_count = st.number_input(
            "Number of Hierarchies",
            0,10,0
        )

        hierarchies=[]

        for i in range(hierarchy_count):

            cols = st.multiselect(
                f"Hierarchy {i+1}",
                columns,
                key=i
            )

            if cols:
                hierarchies.append(cols)

        generate = st.button("Generate Analytics")

        if generate:

            if not(rank_flag or pct_flag or rev_flag):

                st.error("Select at least one cohort type")
                st.stop()

            if not individual_cols and len(hierarchies)==0:

                st.error("Select cohorts")
                st.stop()

            working_df = df.copy()

            if period_column!="None":

                if period_logic=="Latest Period":

                    latest = working_df[period_column].max()
                    working_df = working_df[
                        working_df[period_column]==latest
                    ]

                elif period_logic=="Select Periods":

                    working_df = working_df[
                        working_df[period_column].isin(selected_periods)
                    ]

            result=df.copy()

            def clean_name(cols):

                return "_".join(cols)

            def cohort_engine_calc(group_cols):

                temp=(working_df.groupby(group_cols)[metric]
                .sum()
                .reset_index()
                .sort_values(metric,ascending=False))

                temp["Rank"]=temp[metric].rank(
                    method="dense",
                    ascending=False
                )

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

                    temp["Cum"]=temp[metric].cumsum()
                    total=temp[metric].sum()

                    temp["Share"]=temp["Cum"]/total

                    def bucket(x):

                        if x<=.2:return"Top Drivers"
                        elif x<=.5:return"Mid Tier"
                        elif x<=.8:return"Long Tail"
                        else:return"Bottom Tail"

                    outputs[f"RC_{name}"]=temp["Share"].apply(bucket)

                return temp,outputs

            for col in individual_cols:

                temp,outputs=cohort_engine_calc([col])

                for name,val in outputs.items():

                    temp[name]=val

                    result=result.merge(
                        temp[[col,name]],
                        on=col,
                        how="left"
                    )

            for group in hierarchies:

                temp,outputs=cohort_engine_calc(group)

                for name,val in outputs.items():

                    temp[name]=val

                    result=result.merge(
                        temp[group+[name]],
                        on=group,
                        how="left"
                    )

            cohort_cols=[c for c in result.columns if c.startswith(("SG_","PC_","RC_"))]

            result[cohort_cols]=result[cohort_cols].fillna("Others")

            st.subheader("Analytics Dashboard")

            col1,col2,col3 = st.columns(3)

            col1.metric("Rows",len(result))
            col2.metric("Cohort Columns",len(cohort_cols))
            col3.metric("Metric Total",round(df[metric].sum(),2))

            st.subheader("Top Contributors")

            chart_df = (
                working_df.groupby(individual_cols[0])[metric]
                .sum()
                .reset_index()
                .sort_values(metric,ascending=False)
            )

            fig = px.bar(
                chart_df.head(10),
                x=individual_cols[0],
                y=metric
            )

            st.plotly_chart(fig,use_container_width=True)

            st.subheader("Output")

            st.dataframe(result)

            csv=result.to_csv(index=False)

            if not st.session_state.premium:

                st.warning("Premium subscription ($25) required to download output")

            else:

                st.download_button(
                    "Download Output",
                    csv,
                    "cohort_output.csv"
                )


# ---------------- ROUTER ---------------- #

if not st.session_state.logged_in:

    login_page()

else:

    st.sidebar.title("Navigation")

    nav = st.sidebar.radio(
        "Select Engine",
        [
            "Cohort Analytics Engine",
            "Customer Analytics Engine"
        ]
    )

    if nav=="Customer Analytics Engine":

        customer_engine()

    else:

        cohort_engine()
