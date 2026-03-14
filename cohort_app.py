import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Analytics Engine", layout="wide")

# ---------------------------------------------------------
# ADMIN EMAIL (ALLOWED TO DOWNLOAD)
# ---------------------------------------------------------

ADMIN_EMAIL = "ashwanivatsalarya@gmail.com"

# ---------------------------------------------------------
# USER EMAIL INPUT
# ---------------------------------------------------------

st.sidebar.title("User")

user_email = st.sidebar.text_input("Enter your email")

if "user_email" not in st.session_state:
    st.session_state.user_email = ""

if user_email:
    st.session_state.user_email = user_email


# ---------------------------------------------------------
# SESSION
# ---------------------------------------------------------

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
# COMING SOON MODULES
# ---------------------------------------------------------

if module in ["Product Bundling","ACV Analysis","Revenue Concentration"]:

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


# =========================================================
# COHORT ANALYTICS MODULE (UNCHANGED)
# =========================================================

if module == "Cohort Analytics":

    st.title("Cohort Analytics Engine")

    left, right = st.columns([1,1.7])

    with left:

        st.subheader("Upload & Configure")

        uploaded_file = st.file_uploader(
            "Upload CSV or Excel",
            type=["csv","xlsx"]
        )

        if uploaded_file:

            df = load_file(uploaded_file)

            columns = df.columns.tolist()

            st.success("File Loaded")

            st.markdown("### Field Mapping")

            metric = st.selectbox("Metric Column", columns)

            customer_col = st.selectbox("Customer Column", ["None"] + columns)

            date_col = st.selectbox("Date Column", ["None"] + columns)

            geo_col = st.selectbox("Geography Column", ["None"] + columns)

            product_col = st.selectbox("Product Column", ["None"] + columns)

            fiscal_col = st.selectbox("Fiscal Year Column", ["None"] + columns)

            if fiscal_col != "None":

                fy_vals = sorted(df[fiscal_col].dropna().unique())

                logic = st.selectbox(
                    "Period Logic",
                    ["All Periods","Latest Period","Select Fiscal Year"]
                )

                if logic == "Latest Period":

                    latest = fy_vals[-1]
                    df = df[df[fiscal_col] == latest]

                if logic == "Select Fiscal Year":

                    fy = st.selectbox("Fiscal Year", fy_vals)
                    df = df[df[fiscal_col] == fy]


            st.markdown("### Individual Cohorts")

            individual_cols = st.multiselect(
                "Select Columns",
                columns
            )

            st.markdown("### Hierarchical Cohorts")

            hierarchy_count = st.number_input(
                "Number of Hierarchies",
                0,10,0
            )

            hierarchies = []

            for i in range(hierarchy_count):

                cols = st.multiselect(
                    f"Hierarchy {i+1}",
                    columns,
                    key=i
                )

                if cols:
                    hierarchies.append(cols)

            st.markdown("### Cohort Types")

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

                for group in hierarchies:

                    name = "_".join(group)

                    if sg:

                        sg_temp = cohort_engine(df, metric, group, "SG")

                        result = result.merge(
                            sg_temp[group+[f"SG_{name}"]],
                            on=group,
                            how="left"
                        )

                    if pc:

                        pc_temp = cohort_engine(df, metric, group, "PC")

                        result = result.merge(
                            pc_temp[group+[f"PC_{name}"]],
                            on=group,
                            how="left"
                        )

                    if rc:

                        rc_temp = cohort_engine(df, metric, group, "RC")

                        result = result.merge(
                            rc_temp[group+[f"RC_{name}"]],
                            on=group,
                            how="left"
                        )

                st.session_state.result = result
                st.session_state.df = df
                st.session_state.metric = metric
                st.session_state.customer_col = customer_col
                st.session_state.fiscal_col = fiscal_col


    with right:

        if st.session_state.result is not None:

            df = st.session_state.df
            metric = st.session_state.metric
            result = st.session_state.result
            fiscal_col = st.session_state.fiscal_col

            tabs = st.tabs(["Summary","Output"])

            with tabs[0]:

                if fiscal_col != "None":

                    summary = (
                        df.groupby(fiscal_col)
                        .agg(
                            Revenue=(metric,"sum"),
                            Customers=(st.session_state.customer_col,"nunique")
                        )
                        .reset_index()
                    )

                    summary["Revenue per Customer"] = summary["Revenue"] / summary["Customers"]

                    st.dataframe(summary)

            with tabs[1]:

                st.dataframe(result)

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
                        "🔒 Download is available only for subscribed users."
                    )


# =========================================================
# CUSTOMER ANALYTICS MODULE
# =========================================================

if module == "Customer Analytics":

    st.title("Customer Analytics Engine")

    uploaded_file = st.file_uploader(
        "Upload Dataset",
        type=["csv","xlsx"],
        key="customer_upload"
    )

    if uploaded_file:

        df = load_file(uploaded_file)

        columns = df.columns.tolist()

        metric = st.selectbox("ARR / MRR Column", columns)

        customer_col = st.selectbox("Customer Column", columns)

        date_col = st.selectbox("Date Column", columns)

        quantity_col = st.selectbox("Quantity Column", ["None"] + columns)

        df[date_col] = pd.to_datetime(df[date_col])

        df = df.sort_values([customer_col,date_col])

        df["Prior_ARR"] = df.groupby(customer_col)[metric].shift(1).fillna(0)

        df["Bridge_Value"] = df[metric] - df["Prior_ARR"]

        conditions = [

            (df["Prior_ARR"] == 0) & (df[metric] > 0),

            (df["Prior_ARR"] > 0) & (df[metric] == 0),

            (df[metric] > df["Prior_ARR"]),

            (df[metric] < df["Prior_ARR"])

        ]

        choices = ["New","Churn","Upsell","Downsell"]

        df["Bridge"] = np.select(conditions,choices,"No Change")

        st.subheader("Revenue Bridge")

        bridge = df.groupby("Bridge")["Bridge_Value"].sum().reset_index()

        fig = px.bar(bridge,x="Bridge",y="Bridge_Value")

        st.plotly_chart(fig,use_container_width=True)

        st.subheader("Top Customers")

        top = (
            df.groupby(customer_col)[metric]
            .sum()
            .reset_index()
            .sort_values(metric,ascending=False)
            .head(10)
        )

        fig2 = px.bar(top,x=customer_col,y=metric)

        st.plotly_chart(fig2,use_container_width=True)

        st.dataframe(df)
