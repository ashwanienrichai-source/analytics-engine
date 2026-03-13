import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io

st.set_page_config(
    page_title="Analytics Engine",
    page_icon="📊",
    layout="wide"
)

# ---------------- SESSION ---------------- #

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "premium" not in st.session_state:
    st.session_state.premium = False

if "page" not in st.session_state:
    st.session_state.page = "app"

# ---------------- STYLE ---------------- #

st.markdown("""
<style>

.main-title{
font-size:42px;
font-weight:700;
color:#1f2937;
}

.subtitle{
font-size:16px;
color:#6b7280;
margin-bottom:20px;
}

.card{
background:#f9fafb;
padding:20px;
border-radius:10px;
border:1px solid #e5e7eb;
}

.login-box{
background:#f1f5f9;
padding:30px;
border-radius:10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOGIN PAGE ---------------- #

def login_page():

    st.markdown('<div class="main-title">Analytics Engine</div>', unsafe_allow_html=True)

    st.markdown(
        "Login to unlock downloads and premium analytics features."
    )

    col1,col2,col3 = st.columns([1,2,1])

    with col2:

        st.markdown('<div class="login-box">',unsafe_allow_html=True)

        email = st.text_input("Email")

        password = st.text_input("Password", type="password")

        if st.button("Login"):

            if email and password:

                st.session_state.logged_in = True
                st.session_state.premium = True

                st.success("Login successful")

                st.session_state.page = "app"

                st.rerun()

            else:

                st.error("Please enter credentials")

        st.markdown("</div>",unsafe_allow_html=True)

# ---------------- CUSTOMER ENGINE ---------------- #

def customer_engine():

    st.markdown('<div class="main-title">Customer Analytics Engine</div>',unsafe_allow_html=True)

    st.markdown(
        "<h1 style='text-align:center;color:#9ca3af;margin-top:100px;'>Coming Soon</h1>",
        unsafe_allow_html=True
    )

# ---------------- COHORT ENGINE ---------------- #

def cohort_engine():

    st.markdown('<div class="main-title">📊 Analytics Engine</div>',unsafe_allow_html=True)

    st.markdown("""
<div class="subtitle">
Cohort segmentation and revenue concentration analytics across customers,
products and markets.
</div>
""",unsafe_allow_html=True)

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

    uploaded_file = st.sidebar.file_uploader(
        "Upload CSV or Excel",
        type=["csv","xlsx"]
    )

    if uploaded_file:

        if uploaded_file.name.endswith(".csv"):

            df = pd.read_csv(uploaded_file)

        else:

            df = pd.read_excel(uploaded_file)

        st.success("File loaded successfully")

        columns = df.columns.tolist()

        metric = st.sidebar.selectbox("Metric Column",columns)

        cohort_cols = st.multiselect(
            "Select Cohort Columns",
            columns
        )

        generate = st.button("Generate Cohorts")

        if generate:

            if not cohort_cols:

                st.error("Please select cohort columns")

                st.stop()

            summary = (
                df.groupby(cohort_cols)[metric]
                .sum()
                .reset_index()
                .sort_values(metric,ascending=False)
            )

            summary["Rank"] = summary[metric].rank(
                method="dense",
                ascending=False
            )

            # ---------- DASHBOARD ---------- #

            st.subheader("Analytics Dashboard")

            col1,col2,col3 = st.columns(3)

            col1.metric("Rows",len(df))
            col2.metric("Segments",len(summary))
            col3.metric("Metric Total",round(df[metric].sum(),2))

            # ---------- CHART ---------- #

            st.subheader("Top Contributors")

            fig = px.bar(

                summary.head(10),

                x=cohort_cols[0],

                y=metric,

                color=metric

            )

            st.plotly_chart(fig,use_container_width=True)

            # ---------- TABLE ---------- #

            st.subheader("Cohort Results")

            st.dataframe(summary)

            csv = summary.to_csv(index=False)

            # ---------- DOWNLOAD CONTROL ---------- #

            if not st.session_state.logged_in:

                st.warning("Login required to download results")

                if st.button("Login to Download"):

                    st.session_state.page = "login"

                    st.rerun()

            else:

                if st.session_state.premium:

                    st.download_button(
                        "Download Results",
                        csv,
                        "cohort_output.csv"
                    )

                else:

                    st.warning("Upgrade to premium to download")

# ---------------- NAVIGATION ---------------- #

st.sidebar.title("Navigation")

nav = st.sidebar.radio(

    "Select Engine",

    [
        "Cohort Analytics Engine",
        "Customer Analytics Engine",
        "Login"
    ]

)

# ---------------- ROUTING ---------------- #

if st.session_state.page == "login":

    login_page()

else:

    if nav == "Login":

        login_page()

    elif nav == "Customer Analytics Engine":

        customer_engine()

    else:

        cohort_engine()
