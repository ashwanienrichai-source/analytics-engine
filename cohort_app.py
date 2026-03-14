import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Analytics Engine", layout="wide")

# ---------------------------------------------------------
# ADMIN EMAIL
# ---------------------------------------------------------

ADMIN_EMAIL = "ashwanivatsalarya@gmail.com"

# ---------------------------------------------------------
# USER LOGIN
# ---------------------------------------------------------

st.sidebar.title("User")
user_email = st.sidebar.text_input("Enter your email")

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if user_email:
    st.session_state.user_email = user_email


# ---------------------------------------------------------
# SESSION VARIABLES
# ---------------------------------------------------------

if "validated_df" not in st.session_state:
    st.session_state.validated_df = None

if "result" not in st.session_state:
    st.session_state.result = None


# ---------------------------------------------------------
# SIDEBAR MODULES
# ---------------------------------------------------------

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

# ---------------------------------------------------------
# FILE LOADER
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# COHORT ENGINE
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

def customer_engine(df, customer_col, date_col, metric):

    df = df.sort_values([customer_col, date_col])

    df["Prior_ARR"] = df.groupby(customer_col)[metric].shift(1).fillna(0)

    df["Bridge_Value"] = df[metric] - df["Prior_ARR"]

    conditions = [

        (df["Prior_ARR"] == 0) & (df[metric] > 0),

        (df["Prior_ARR"] > 0) & (df[metric] == 0),

        (df[metric] > df["Prior_ARR"]),

        (df[metric] < df["Prior_ARR"]),

    ]

    choices = ["New","Churn","Upsell","Downsell"]

    df["Bridge"] = np.select(conditions,choices,"No Change")

    return df


# ---------------------------------------------------------
# MAIN PAGE
# ---------------------------------------------------------

st.title("Revenue Analytics Engine")

left, right = st.columns([1,1.7])

# ---------------------------------------------------------
# LEFT PANEL (UPLOAD + MAPPING)
# ---------------------------------------------------------

with left:

    st.subheader("Upload & Map Data")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv","xlsx"]
    )

    if uploaded_file:

        df = load_file(uploaded_file)

        columns = df.columns.tolist()

        dataset_type = st.radio(
            "Dataset Type",
            ["Bookings Data","Revenue Data","Billings Data"]
        )

        st.markdown("### Map Columns")

        customer_col = st.selectbox("Customer Column", columns)
        date_col = st.selectbox("Date Column", columns)
        metric = st.selectbox("Revenue Column", columns)

        product_col = st.selectbox("Product Column", ["None"] + columns)
        region_col = st.selectbox("Region Column", ["None"] + columns)

        if st.button("Validate Data"):

            df[date_col] = pd.to_datetime(df[date_col])

            st.session_state.validated_df = df
            st.session_state.customer_col = customer_col
            st.session_state.date_col = date_col
            st.session_state.metric = metric

            st.success("Data validated successfully")


# ---------------------------------------------------------
# RIGHT PANEL (ANALYTICS)
# ---------------------------------------------------------

with right:

    if st.session_state.validated_df is not None:

        df = st.session_state.validated_df
        customer_col = st.session_state.customer_col
        date_col = st.session_state.date_col
        metric = st.session_state.metric

        # ---------------------------------------------------------
        # COHORT ANALYTICS
        # ---------------------------------------------------------

        if module == "Cohort Analytics":

            st.subheader("Cohort Analytics")

            columns = df.columns.tolist()

            cohort_cols = st.multiselect(
                "Select Cohort Columns",
                columns
            )

            cohort_type = st.selectbox(
                "Cohort Type",
                ["SG","PC","RC"]
            )

            if st.button("Analyze Metrics"):

                result = cohort_engine(df, metric, cohort_cols, cohort_type)

                st.session_state.result = result

                st.dataframe(result)

        # ---------------------------------------------------------
        # CUSTOMER ANALYTICS
        # ---------------------------------------------------------

        elif module == "Customer Analytics":

            st.subheader("Customer Analytics")

            df = customer_engine(df, customer_col, date_col, metric)

            beginning = df["Prior_ARR"].sum()
            ending = df[metric].sum()

            churn = df.loc[df["Bridge"]=="Churn","Bridge_Value"].sum()
            expansion = df.loc[df["Bridge"]=="Upsell","Bridge_Value"].sum()

            nrr = (beginning + expansion + churn) / beginning if beginning !=0 else 0
            grr = (beginning + churn) / beginning if beginning !=0 else 0

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Beginning ARR", round(beginning,2))
            col2.metric("Ending ARR", round(ending,2))
            col3.metric("NRR %", round(nrr*100,2))
            col4.metric("GRR %", round(grr*100,2))

            st.markdown("### Revenue Bridge")

            bridge = df.groupby("Bridge")["Bridge_Value"].sum().reset_index()

            fig = px.bar(
                bridge,
                x="Bridge",
                y="Bridge_Value"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Top Customers")

            top = (
                df.groupby(customer_col)[metric]
                .sum()
                .reset_index()
                .sort_values(metric,ascending=False)
                .head(10)
            )

            fig2 = px.bar(
                top,
                x=customer_col,
                y=metric
            )

            st.plotly_chart(fig2, use_container_width=True)

            st.session_state.result = df


        else:

            st.markdown(
                """
                <h1 style='text-align:center;color:#7C3AED;
                font-size:80px;margin-top:200px;'>
                Coming Soon 🚀
                </h1>
                """,
                unsafe_allow_html=True
            )


        # ---------------------------------------------------------
        # DOWNLOAD OUTPUT
        # ---------------------------------------------------------

        if st.session_state.result is not None:

            csv = st.session_state.result.to_csv(index=False)

            if st.session_state.user_email == ADMIN_EMAIL:

                st.download_button(
                    "Download Results",
                    csv,
                    "analytics_output.csv"
                )

            else:

                st.download_button(
                    "Download Results",
                    csv,
                    disabled=True
                )

                st.warning("🔒 Download is available only for subscribed users.")
