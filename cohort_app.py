import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Analytics Engine", layout="wide")

# ------------------------------------------------
# SESSION
# ------------------------------------------------

if "premium" not in st.session_state:
    st.session_state.premium = True   # change to False if needed

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

# ------------------------------------------------
# COMING SOON MODULES
# ------------------------------------------------

if module != "Cohort Analytics":

    st.title(module)

    st.markdown(
        """
        <h1 style='text-align:center;
        color:#7C3AED;
        font-size:80px;
        margin-top:200px;'>
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
                if x <= 10:
                    return "Top 10"
                elif x <= 25:
                    return "11-25"
                elif x <= 50:
                    return "26-50"
                else:
                    return "Others"

            outputs[f"SG_{name}"] = temp["Rank"].apply(bucket)

        if pct_flag:

            temp["Pct"] = temp["Rank"] / max_rank

            def bucket(x):
                if x <= .05:
                    return "Top 5%"
                elif x <= .10:
                    return "Top 10%"
                elif x <= .20:
                    return "Top 20%"
                elif x <= .50:
                    return "Top 50%"
                else:
                    return "Bottom 50%"

            outputs[f"PC_{name}"] = temp["Pct"].apply(bucket)

        if rev_flag:

            temp["Cum"] = temp[metric].cumsum()
            total = temp[metric].sum()

            temp["Share"] = temp["Cum"] / total

            def bucket(x):
                if x <= .2:
                    return "Top Drivers"
                elif x <= .5:
                    return "Mid Tier"
                elif x <= .8:
                    return "Long Tail"
                else:
                    return "Bottom Tail"

            outputs[f"RC_{name}"] = temp["Share"].apply(bucket)

        return temp, outputs


    # --------------------------
    # INDIVIDUAL COHORTS
    # --------------------------

    for col in individual_cols:

        temp, outputs = cohort_calc([col])

        for name, val in outputs.items():

            temp[name] = val

            result = result.merge(
                temp[[col, name]],
                on=col,
                how="left"
            )


    # --------------------------
    # HIERARCHICAL COHORTS
    # --------------------------

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
# MAIN LAYOUT
# ------------------------------------------------

st.title("Cohort Analytics Engine")

left, right = st.columns([1, 1.5])

# ------------------------------------------------
# LEFT PANEL
# ------------------------------------------------

with left:

    st.subheader("Upload & Configure")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx"]
    )

    if uploaded_file:

        df = load_file(uploaded_file)

        st.success("File Loaded Successfully")

        columns = df.columns.tolist()

        metric = st.selectbox(
            "Metric Column",
            columns
        )

        st.subheader("Individual Cohorts")

        individual_cols = st.multiselect(
            "Select Columns",
            columns
        )

        st.subheader("Hierarchical Cohorts")

        hierarchy_count = st.number_input(
            "Number of Hierarchies",
            0, 10, 0
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

        st.subheader("Cohort Types")

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


# ------------------------------------------------
# RIGHT PANEL
# ------------------------------------------------

with right:

    st.subheader("Cohort Analytics")

    if st.session_state.result is not None:

        result = st.session_state.result
        df = st.session_state.df
        metric = st.session_state.metric

        tabs = st.tabs(
            [
                "Summary",
                "Charts",
                "Cohort Heatmap",
                "Output"
            ]
        )

        # ------------------------------------
        # SUMMARY
        # ------------------------------------

        with tabs[0]:

            c1, c2, c3 = st.columns(3)

            c1.metric("Rows", len(result))

            cohort_cols = [
                c for c in result.columns
                if c.startswith(("SG_", "PC_", "RC_"))
            ]

            c2.metric("Cohort Columns", len(cohort_cols))

            c3.metric("Metric Total", round(df[metric].sum(), 2))


        # ------------------------------------
        # CHARTS
        # ------------------------------------

        with tabs[1]:

            if len(df.columns) > 0:

                group_col = df.columns[0]

                chart_df = (
                    df.groupby(group_col)[metric]
                    .sum()
                    .reset_index()
                    .sort_values(metric, ascending=False)
                )

                fig = px.bar(
                    chart_df.head(15),
                    x=group_col,
                    y=metric
                )

                st.plotly_chart(fig, use_container_width=True)


        # ------------------------------------
        # HEATMAP
        # ------------------------------------

        with tabs[2]:

            cohort_cols = [
                c for c in result.columns
                if c.startswith(("SG_", "PC_", "RC_"))
            ]

            if cohort_cols:

                heat = (
                    result.groupby(cohort_cols[0])[metric]
                    .sum()
                    .reset_index()
                )

                fig = px.bar(
                    heat,
                    x=cohort_cols[0],
                    y=metric
                )

                st.plotly_chart(fig, use_container_width=True)


        # ------------------------------------
        # OUTPUT
        # ------------------------------------

        with tabs[3]:

            st.dataframe(result)

            csv = result.to_csv(index=False)

            if st.session_state.premium:

                st.download_button(
                    "Download Output",
                    csv,
                    "cohort_output.csv"
                )

            else:

                st.warning(
                    "Please subscribe to download output."
                )
