import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Analytics Engine", layout="wide")

# ------------------------------------------------
# SESSION
# ------------------------------------------------

if "result" not in st.session_state:
    st.session_state.result = None


# ------------------------------------------------
# SIDEBAR MODULES
# ------------------------------------------------

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


# ------------------------------------------------
# FILE LOADER
# ------------------------------------------------

def load_file(uploaded_file):

    if uploaded_file.name.endswith(".csv"):

        try:
            df = pd.read_csv(uploaded_file, header=0, encoding="utf-8")

        except:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, header=0, encoding="latin1")

    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip()

    return df


# ------------------------------------------------
# COHORT ENGINE
# ------------------------------------------------

def cohort_engine(df, metric, individual_cols, hierarchies, rank_flag, pct_flag, rev_flag):

    result = df.copy()

    def clean(cols):
        return "_".join(cols)

    def cohort_calc(cols):

        temp = (
            df.groupby(cols)[metric]
            .sum()
            .reset_index()
            .sort_values(metric, ascending=False)
        )

        temp["Rank"] = temp[metric].rank(method="dense", ascending=False)

        max_rank = temp["Rank"].max()

        outputs = {}

        name = clean(cols)

        if rank_flag:

            def bucket(x):
                if x <= 10: return "Top 10"
                elif x <= 25: return "11-25"
                elif x <= 50: return "26-50"
                else: return "Others"

            outputs[f"SG_{name}"] = temp["Rank"].apply(bucket)

        if pct_flag:

            temp["Pct"] = temp["Rank"] / max_rank

            def bucket(x):
                if x <= .05: return "Top 5%"
                elif x <= .10: return "Top 10%"
                elif x <= .20: return "Top 20%"
                elif x <= .50: return "Top 50%"
                else: return "Bottom 50%"

            outputs[f"PC_{name}"] = temp["Pct"].apply(bucket)

        if rev_flag:

            temp["Cum"] = temp[metric].cumsum()
            total = temp[metric].sum()

            temp["Share"] = temp["Cum"] / total

            def bucket(x):
                if x <= .2: return "Top Drivers"
                elif x <= .5: return "Mid Tier"
                elif x <= .8: return "Long Tail"
                else: return "Bottom Tail"

            outputs[f"RC_{name}"] = temp["Share"].apply(bucket)

        return temp, outputs


    for col in individual_cols:

        temp, outputs = cohort_calc([col])

        for name, val in outputs.items():

            temp[name] = val

            result = result.merge(
                temp[[col, name]],
                on=col,
                how="left"
            )

    for group in hierarchies:

        temp, outputs = cohort_calc(group)

        for name, val in outputs.items():

            temp[name] = val

            result = result.merge(
                temp[group + [name]],
                on=group,
                how="left"
            )

    cohort_cols = [
        c for c in result.columns
        if c.startswith(("SG_", "PC_", "RC_"))
    ]

    result[cohort_cols] = result[cohort_cols].fillna("Others")

    return result


# ------------------------------------------------
# MAIN PAGE
# ------------------------------------------------

st.title("Cohort Analytics Engine")

left, right = st.columns([1,1.6])


# ------------------------------------------------
# LEFT PANEL
# ------------------------------------------------

with left:

    st.subheader("Upload & Configure")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv","xlsx"]
    )

    if uploaded_file:

        df = load_file(uploaded_file)

        st.success("File Loaded Successfully")

        columns = df.columns.tolist()

        st.markdown("### Map Fields")

        metric = st.selectbox("Revenue / Metric Column", columns)

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

        if date_col != "None":

            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

            df["Year"] = df[date_col].dt.year

            year_filter = st.selectbox(
                "Fiscal Year",
                ["All"] + sorted(df["Year"].dropna().unique())
            )

            if year_filter != "All":
                df = df[df["Year"] == year_filter]


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

        rank_flag = st.checkbox("Size Group (SG_)")
        pct_flag = st.checkbox("Percentile (PC_)")
        rev_flag = st.checkbox("Revenue Contribution (RC_)")

        if st.button("Generate Cohorts"):

            result = cohort_engine(
                df,
                metric,
                individual_cols,
                hierarchies,
                rank_flag,
                pct_flag,
                rev_flag
            )

            st.session_state.result = result
            st.session_state.df = df
            st.session_state.metric = metric
            st.session_state.customer_col = customer_col
            st.session_state.date_col = date_col
            st.session_state.geo_col = geo_col
            st.session_state.product_col = product_col


# ------------------------------------------------
# RIGHT PANEL
# ------------------------------------------------

with right:

    if st.session_state.result is not None:

        result = st.session_state.result
        df = st.session_state.df
        metric = st.session_state.metric

        customer_col = st.session_state.customer_col
        date_col = st.session_state.date_col
        geo_col = st.session_state.geo_col
        product_col = st.session_state.product_col

        tabs = st.tabs([
            "Summary",
            "Revenue",
            "Concentration",
            "Segmentation",
            "Cohort Heatmap",
            "Retention %",
            "Output"
        ])

        # ---------------- SUMMARY ----------------

        with tabs[0]:

            total_revenue = df[metric].sum()

            customers = (
                df[customer_col].nunique()
                if customer_col != "None"
                else None
            )

            rev_per_customer = (
                total_revenue/customers
                if customers else None
            )

            c1,c2,c3 = st.columns(3)

            c1.metric("Revenue", round(total_revenue,2))
            c2.metric("Customers", customers)
            c3.metric("Revenue / Customer", round(rev_per_customer,2) if rev_per_customer else None)


        # ---------------- REVENUE ----------------

        with tabs[1]:

            if geo_col != "None":

                geo_chart = (
                    df.groupby(geo_col)[metric]
                    .sum()
                    .reset_index()
                )

                fig = px.bar(
                    geo_chart,
                    x=geo_col,
                    y=metric,
                    title="Revenue by Geography"
                )

                st.plotly_chart(fig, use_container_width=True)


            if product_col != "None":

                prod_chart = (
                    df.groupby(product_col)[metric]
                    .sum()
                    .reset_index()
                    .sort_values(metric,ascending=False)
                )

                fig = px.bar(
                    prod_chart.head(15),
                    x=product_col,
                    y=metric,
                    title="Top Products"
                )

                st.plotly_chart(fig, use_container_width=True)


        # ---------------- CONCENTRATION ----------------

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

                fig = px.line(
                    pareto,
                    y="Share",
                    title="Revenue Concentration"
                )

                st.plotly_chart(fig, use_container_width=True)


        # ---------------- SEGMENTATION ----------------

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

                def bucket(x):

                    if x <= .05: return "Top 5%"
                    elif x <= .10: return "Top 10%"
                    elif x <= .20: return "Top 20%"
                    else: return "Long Tail"

                seg["Segment"] = seg["Pct"].apply(bucket)

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


        # ---------------- COHORT HEATMAP ----------------

        with tabs[4]:

            if customer_col != "None" and date_col != "None":

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
                    aspect="auto",
                    color_continuous_scale="Blues"
                )

                st.plotly_chart(fig, use_container_width=True)


        # ---------------- RETENTION % ----------------

        with tabs[5]:

            if customer_col != "None" and date_col != "None":

                retention = pivot.divide(
                    pivot.iloc[:,0],
                    axis=0
                )

                fig = px.imshow(
                    retention,
                    aspect="auto",
                    color_continuous_scale="Greens"
                )

                st.plotly_chart(fig, use_container_width=True)


        # ---------------- OUTPUT ----------------

        with tabs[6]:

            st.dataframe(result)

            csv = result.to_csv(index=False)

            st.download_button(
                "Download Output",
                csv,
                "cohort_output.csv"
            )
