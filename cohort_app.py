import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from supabase import create_client

st.set_page_config(page_title="Analytics Engine", layout="wide")

# -------------------------
# SUPABASE CONFIG
# -------------------------

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
UPI_ID = st.secrets["UPI_ID"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------
# SESSION STATE
# -------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "premium" not in st.session_state:
    st.session_state.premium = False

# -------------------------
# SIGNUP
# -------------------------

def signup():

    st.subheader("Create Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):

        if email == "" or password == "":
            st.warning("Please enter email and password")
            return

        try:

            existing = supabase.table("users").select("email").eq("email", email).execute()

            if len(existing.data) > 0:
                st.warning("User already exists")
                return

            supabase.table("users").insert({
                "email": email,
                "password": password,
                "premium": False,
                "created_at": datetime.now().isoformat()
            }).execute()

            st.success("Account created. Please login.")

        except:
            st.error("Signup failed")

# -------------------------
# LOGIN
# -------------------------

def login():

    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        try:

            user = supabase.table("users")\
                .select("*")\
                .eq("email", email)\
                .eq("password", password)\
                .execute()

            if len(user.data) > 0:

                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.premium = user.data[0]["premium"]

                try:
                    supabase.table("login_logs").insert({
                        "email": email,
                        "login_time": datetime.now().isoformat()
                    }).execute()
                except:
                    pass

                st.rerun()

            else:
                st.error("Invalid login")

        except:
            st.error("Login failed")

# -------------------------
# AUTH PAGE
# -------------------------

def auth_page():

    st.title("Analytics Engine")

    option = st.radio(
        "Select Option",
        ["Login", "Signup"]
    )

    if option == "Login":
        login()
    else:
        signup()

# -------------------------
# PAYMENT LOCK
# -------------------------

def payment_gate():

    st.warning("Premium subscription required to download output")

    st.write("Pay **$25 via UPI**")

    st.code(UPI_ID)

    txn = st.text_input("Enter UPI Transaction ID")

    if st.button("Submit Payment"):

        if txn == "":
            st.warning("Please enter transaction ID")
            return

        try:

            supabase.table("payments").insert({
                "email": st.session_state.user_email,
                "upi_txn": txn,
                "amount": 25,
                "verified": False
            }).execute()

            st.success("Payment submitted. Waiting verification.")

        except:
            st.error("Payment submission failed")

# -------------------------
# FILE LOADER (FIXED)
# -------------------------

def load_file(uploaded_file):

    try:

        uploaded_file.seek(0)

        if uploaded_file.name.lower().endswith(".csv"):

            try:

                df = pd.read_csv(
                    uploaded_file,
                    encoding="utf-8",
                    header=0,
                    engine="python"
                )

            except:

                uploaded_file.seek(0)

                df = pd.read_csv(
                    uploaded_file,
                    encoding="latin1",
                    header=0,
                    engine="python"
                )

        elif uploaded_file.name.lower().endswith(".xlsx"):

            uploaded_file.seek(0)
            df = pd.read_excel(uploaded_file, header=0)

        else:

            st.error("Unsupported file format")
            return None

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
            .str.replace("\n", " ")
        )

        return df

    except Exception as e:

        st.error("File could not be read")
        st.write(e)
        return None

# -------------------------
# COHORT ENGINE
# -------------------------

def cohort_engine():

    st.title("Cohort Analytics Engine")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx"]
    )

    if uploaded_file:

        df = load_file(uploaded_file)

        if df is None:
            return

        st.success("File Loaded Successfully")

        st.write("Detected Columns:")
        st.write(list(df.columns))

        st.dataframe(df.head(10))

        columns = df.columns.tolist()

        metric = st.selectbox("Metric Column", columns)

        df[metric] = pd.to_numeric(df[metric], errors="coerce")

        period_col = st.selectbox("Period Column", ["None"] + columns)

        if period_col != "None":

            periods = sorted(df[period_col].dropna().unique())

            logic = st.radio(
                "Period Logic",
                ["Latest Period", "Select Periods", "All Periods"]
            )

            if logic == "Latest Period":

                latest = max(periods)
                df = df[df[period_col] == latest]

            elif logic == "Select Periods":

                selected = st.multiselect("Choose Periods", periods)

                if selected:
                    df = df[df[period_col].isin(selected)]

        st.subheader("Individual Cohorts")

        individual_cols = st.multiselect("Select Columns", columns)

        st.subheader("Hierarchical Cohorts")

        hierarchy_count = st.number_input("Number of Hierarchies", 0, 10, 0)

        hierarchies = []

        for i in range(hierarchy_count):

            cols = st.multiselect(f"Hierarchy {i+1}", columns, key=i)

            if cols:
                hierarchies.append(cols)

        st.sidebar.subheader("Cohort Types")

        rank_flag = st.sidebar.checkbox("Size Group (SG_)")
        pct_flag = st.sidebar.checkbox("Percentile (PC_)")
        rev_flag = st.sidebar.checkbox("Revenue Contribution (RC_)")

        if st.button("Generate Cohorts"):

            if not rank_flag and not pct_flag and not rev_flag:
                st.warning("Select at least one cohort type")
                return

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

            st.subheader("Analytics Dashboard")

            col1, col2, col3 = st.columns(3)

            col1.metric("Rows", len(result))
            col2.metric("Cohort Columns", len(cohort_cols))
            col3.metric("Metric Total", round(df[metric].sum(), 2))

            st.dataframe(result)

            csv = result.to_csv(index=False)

            if st.session_state.premium:

                st.download_button(
                    "Download Output",
                    csv,
                    "cohort_output.csv"
                )

            else:

                payment_gate()

# -------------------------
# MAIN ROUTER
# -------------------------

if not st.session_state.logged_in:

    auth_page()

else:

    st.sidebar.title("Navigation")

    nav = st.sidebar.radio(
        "Select Engine",
        [
            "Cohort Analytics Engine",
            "Customer Analytics Engine"
        ]
    )

    st.sidebar.write(f"Logged in as: {st.session_state.user_email}")

    if nav == "Customer Analytics Engine":

        st.title("Customer Analytics Engine")
        st.markdown("## Coming Soon")

    else:

        cohort_engine()
