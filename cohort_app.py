import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Analytics Engine", layout="wide")

# -------------------------------------------------
# ADMIN EMAIL FOR DOWNLOAD ACCESS
# -------------------------------------------------

ADMIN_EMAIL = "ashwanivatsalarya@gmail.com"

# -------------------------------------------------
# USER EMAIL INPUT
# -------------------------------------------------

st.sidebar.title("User Login")

user_email = st.sidebar.text_input("Enter Email")

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if user_email:
    st.session_state.user_email = user_email

# -------------------------------------------------
# MODULE SELECTOR
# -------------------------------------------------

st.sidebar.title("Analytics Modules")

module = st.sidebar.radio(
    "Select Module",
    [
        "Cohort Analytics",
        "Customer Analytics",
        "Product Bundling",
        "ACV Analysis",
        "Revenue Concentration"
    ]
)

if module in [
    "Product Bundling",
    "ACV Analysis",
    "Revenue Concentration"
]:

    st.title(module)

    st.markdown(
        """
        <h1 style='text-align:center;color:#7C3AED;
        font-size:80px;margin-top:200px;'>
        Coming Soon 🚀
        </h1>
        """,
        unsafe_allow_html=True
    )

    st.stop()

# -------------------------------------------------
# FILE UPLOAD
# -------------------------------------------------

st.title("Analytics Engine")

uploaded_file = st.file_uploader(
    "Upload CSV or Excel",
    type=["csv","xlsx"]
)

# -------------------------------------------------
# FILE LOADER
# -------------------------------------------------

def load_file(uploaded_file):

    if uploaded_file.name.endswith(".csv"):

        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8")
        except:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="latin1")

    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip()

    return df


# -------------------------------------------------
# COHORT ENGINE
# -------------------------------------------------

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


# -------------------------------------------------
# LOAD DATA
# -------------------------------------------------

if uploaded_file:

    df = load_file(uploaded_file)

    st.success("File Loaded Successfully")

    columns = df.columns.tolist()

# -------------------------------------------------
# FIELD MAPPING
# -------------------------------------------------

    st.subheader("Field Mapping")

    metric = st.selectbox("Metric Column", columns)

    customer_col = st.selectbox("Customer Column", ["None"] + columns)

    date_col = st.selectbox("Date Column", ["None"] + columns)

    geo_col = st.selectbox("Geography Column", ["None"] + columns)

    fiscal_col = st.selectbox("Fiscal Year Column", ["None"] + columns)

# -------------------------------------------------
# CUSTOMER ANALYTICS
# -------------------------------------------------

    if module == "Customer Analytics":

        st.header("Customer Analytics")

        cust_rev = (
            df.groupby(customer_col)[metric]
            .sum()
            .reset_index()
            .sort_values(metric, ascending=False)
        )

        total_customers = cust_rev[customer_col].nunique()
        total_revenue = cust_rev[metric].sum()
        rev_per_customer = total_revenue / total_customers

        c1,c2,c3 = st.columns(3)

        c1.metric("Customers", total_customers)
        c2.metric("Revenue", round(total_revenue,2))
        c3.metric("Revenue / Customer", round(rev_per_customer,2))

        fig = px.histogram(
            cust_rev,
            x=metric,
            nbins=30,
            title="Customer Revenue Distribution"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Top Customers")

        st.dataframe(cust_rev.head(20))

        fig2 = px.bar(
            cust_rev.head(10),
            x=customer_col,
            y=metric,
            title="Top Customers"
        )

        st.plotly_chart(fig2, use_container_width=True)

# -------------------------------------------------
# COHORT ANALYTICS
# -------------------------------------------------

    if module == "Cohort Analytics":

        st.header("Cohort Analytics")

        individual_cols = st.multiselect(
            "Individual Cohorts",
            columns
        )

        sg = st.checkbox("Size Group (SG_)")
        pc = st.checkbox("Percentile (PC_)")
        rc = st.checkbox("Revenue Contribution (RC_)")

        if st.button("Generate Cohorts"):

            result = df.copy()

            for col in individual_cols:

                if sg:

                    sg_temp = cohort_engine(df, metric, [col], "SG")

                    result = result.merge(
                        sg_temp[[col,f"SG_{col}"]],
                        on=col,
                        how="left"
                    )

                if pc:

                    pc_temp = cohort_engine(df, metric, [col], "PC")

                    result = result.merge(
                        pc_temp[[col,f"PC_{col}"]],
                        on=col,
                        how="left"
                    )

                if rc:

                    rc_temp = cohort_engine(df, metric, [col], "RC")

                    result = result.merge(
                        rc_temp[[col,f"RC_{col}"]],
                        on=col,
                        how="left"
                    )

            st.subheader("Output Dataset")

            st.dataframe(result)

# -------------------------------------------------
# DOWNLOAD PAYWALL
# -------------------------------------------------

            csv = result.to_csv(index=False)

            if st.session_state.user_email == ADMIN_EMAIL:

                st.download_button(
                    "Download Output",
                    csv,
                    "cohort_output.csv"
                )

            else:

                st.download_button(
                    "Download Output",
                    csv,
                    disabled=True
                )

                st.warning(
                    "🔒 Download is available only for subscribed users. "
                    "Please pay the subscription fee to download reports."
                )
