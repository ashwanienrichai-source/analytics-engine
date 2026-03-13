import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Analytics Engine", layout="wide")

# -----------------------------------------------------
# SESSION
# -----------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None


# -----------------------------------------------------
# SIDEBAR
# -----------------------------------------------------

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

if module != "Cohort Analytics":

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

# -----------------------------------------------------
# FILE LOADER
# -----------------------------------------------------

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


# -----------------------------------------------------
# COHORT ENGINE
# -----------------------------------------------------

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

        temp["Pct"] = temp["Rank"]/max_rank

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

        temp["Share"] = temp["Cum"]/total

        def bucket(x):

            if x <= .2: return "Top Drivers"
            elif x <= .5: return "Mid Tier"
            elif x <= .8: return "Long Tail"
            else: return "Bottom Tail"

        temp[f"RC_{name}"] = temp["Share"].apply(bucket)

    return temp


# -----------------------------------------------------
# PAGE
# -----------------------------------------------------

st.title("Cohort Analytics Engine")

left, right = st.columns([1,1.7])

# -----------------------------------------------------
# LEFT CONFIGURATION
# -----------------------------------------------------

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

        customer_col = st.selectbox(
            "Customer Column",
            ["None"] + columns
        )

        date_col = st.selectbox(
            "Date Column",
            ["None"] + columns
        )

        geo_col = st.selectbox(
            "Geography Column",
            ["None"] + columns
        )

        product_col = st.selectbox(
            "Product Column",
            ["None"] + columns
        )

        fiscal_col = st.selectbox(
            "Fiscal Year Column",
            ["None"] + columns
        )

        # ---------------------------------------------
        # Fiscal filtering
        # ---------------------------------------------

        if fiscal_col != "None":

            fiscal_values = sorted(df[fiscal_col].dropna().unique())

            period_logic = st.selectbox(
                "Period Logic",
                ["All Periods","Latest Period","Select Fiscal Year"]
            )

            if period_logic == "Latest Period":

                latest = fiscal_values[-1]

                df = df[df[fiscal_col] == latest]

            if period_logic == "Select Fiscal Year":

                fy = st.selectbox(
                    "Fiscal Year",
                    fiscal_values
                )

                df = df[df[fiscal_col] == fy]

        # ---------------------------------------------
        # Cohort columns
        # ---------------------------------------------

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
            st.session_state.date_col = date_col
            st.session_state.geo_col = geo_col
            st.session_state.product_col = product_col
            st.session_state.fiscal_col = fiscal_col


# -----------------------------------------------------
# RIGHT ANALYTICS
# -----------------------------------------------------

with right:

    if st.session_state.result is not None:

        df = st.session_state.df
        metric = st.session_state.metric
        result = st.session_state.result

        customer_col = st.session_state.customer_col
        geo_col = st.session_state.geo_col
        product_col = st.session_state.product_col
        date_col = st.session_state.date_col
        fiscal_col = st.session_state.fiscal_col

        tabs = st.tabs([
            "Summary",
            "Revenue Charts",
            "Concentration",
            "Segmentation",
            "Cohort Heatmap",
            "Retention %",
            "Output"
        ])

        # ---------------------------------------------
        # SUMMARY
        # ---------------------------------------------

        with tabs[0]:

            total_rev = df[metric].sum()

            cust = df[customer_col].nunique() if customer_col!="None" else None

            rev_per = total_rev/cust if cust else None

            c1,c2,c3 = st.columns(3)

            c1.metric("Revenue", round(total_rev,2))
            c2.metric("Customers", cust)
            c3.metric("Revenue / Customer", round(rev_per,2) if rev_per else None)


        # ---------------------------------------------
        # REVENUE CHARTS
        # ---------------------------------------------

        with tabs[1]:

            if fiscal_col != "None":

                fy_rev = (
                    df.groupby(fiscal_col)[metric]
                    .sum()
                    .reset_index()
                )

                fig = go.Figure()

                fig.add_bar(
                    x=fy_rev[fiscal_col],
                    y=fy_rev[metric],
                    name="Revenue"
                )

                fig.add_trace(
                    go.Scatter(
                        x=fy_rev[fiscal_col],
                        y=fy_rev[metric],
                        mode="lines+markers",
                        name="Trend"
                    )
                )

                st.plotly_chart(fig,use_container_width=True)

            if geo_col != "None":

                geo_chart = (
                    df.groupby(geo_col)[metric]
                    .sum()
                    .reset_index()
                )

                fig = px.bar(
                    geo_chart,
                    x=geo_col,
                    y=metric
                )

                st.plotly_chart(fig,use_container_width=True)


        # ---------------------------------------------
        # CONCENTRATION
        # ---------------------------------------------

        with tabs[2]:

            if customer_col != "None":

                pareto = (
                    df.groupby(customer_col)[metric]
                    .sum()
                    .reset_index()
                    .sort_values(metric,ascending=False)
                )

                pareto["Cum"] = pareto[metric].cumsum()

                pareto["Share"] = pareto["Cum"]/pareto[metric].sum()

                fig = px.line(pareto,y="Share")

                st.plotly_chart(fig,use_container_width=True)


        # ---------------------------------------------
        # SEGMENTATION
        # ---------------------------------------------

        with tabs[3]:

            if customer_col != "None":

                seg = (
                    df.groupby(customer_col)[metric]
                    .sum()
                    .reset_index()
                )

                seg["Rank"] = seg[metric].rank(
                    method="dense",
                    ascending=False
                )

                seg["Pct"] = seg["Rank"]/seg["Rank"].max()

                seg["Segment"] = pd.cut(
                    seg["Pct"],
                    bins=[0,.05,.1,.2,1],
                    labels=[
                        "Top 5%",
                        "Top 10%",
                        "Top 20%",
                        "Long Tail"
                    ]
                )

                pie = (
                    seg.groupby("Segment")[metric]
                    .sum()
                    .reset_index()
                )

                fig = px.pie(
                    pie,
                    names="Segment",
                    values=metric
                )

                st.plotly_chart(fig)


        # ---------------------------------------------
        # COHORT HEATMAP
        # ---------------------------------------------

        with tabs[4]:

            if customer_col!="None" and date_col!="None":

                df[date_col] = pd.to_datetime(df[date_col])

                df["OrderMonth"] = df[date_col].dt.to_period("M").astype(str)

                cohort = df.groupby(customer_col)["OrderMonth"].min()

                df["CohortMonth"] = df[customer_col].map(cohort)

                df["CohortIndex"] = (
                    pd.to_datetime(df["OrderMonth"]) -
                    pd.to_datetime(df["CohortMonth"])
                ).dt.days // 30

                pivot = pd.pivot_table(
                    df,
                    values=customer_col,
                    index="CohortMonth",
                    columns="CohortIndex",
                    aggfunc="nunique"
                ).fillna(0)

                fig = px.imshow(
                    pivot,
                    text_auto=True,
                    color_continuous_scale="Blues"
                )

                st.plotly_chart(fig,use_container_width=True)


        # ---------------------------------------------
        # RETENTION
        # ---------------------------------------------

        with tabs[5]:

            if customer_col!="None" and date_col!="None":

                retention = pivot.divide(
                    pivot.iloc[:,0],
                    axis=0
                )

                fig = px.imshow(
                    retention,
                    text_auto=".0%",
                    color_continuous_scale="Greens"
                )

                st.plotly_chart(fig,use_container_width=True)


        # ---------------------------------------------
        # OUTPUT
        # ---------------------------------------------

        with tabs[6]:

            st.dataframe(result)

            csv = result.to_csv(index=False)

            st.download_button(
                "Download Output",
                csv,
                "cohort_output.csv"
            )
