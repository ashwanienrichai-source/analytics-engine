import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from supabase import create_client

st.set_page_config(page_title="Analytics Engine", layout="wide")

# ---------------- CONFIG ---------------- #

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
ADMIN_EMAIL = st.secrets.get("ADMIN_EMAIL", "")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------------- SESSION ---------------- #

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "premium" not in st.session_state:
    st.session_state.premium = False

# ---------------- SIGNUP ---------------- #

def signup():

    st.subheader("Create Account")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Signup"):

        if email == "" or password == "":
            st.warning("Enter email and password")
            return

        try:

            existing = supabase.table("users").select("email").eq("email", email).execute()

            if len(existing.data) > 0:
                st.warning("User already exists")
                return

            premium = False
            expiry = None

            if email == ADMIN_EMAIL:
                premium = True
                expiry = (datetime.now() + timedelta(days=365)).isoformat()

            supabase.table("users").insert({
                "email": email,
                "password": password,
                "premium": premium,
                "premium_expiry": expiry,
                "created_at": datetime.now().isoformat()
            }).execute()

            st.success("Account created. Please login.")

        except:
            st.error("Signup failed")

# ---------------- LOGIN ---------------- #

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

                premium = user.data[0]["premium"]
                expiry = user.data[0].get("premium_expiry")

                if premium and expiry:

                    if datetime.fromisoformat(expiry) > datetime.now():
                        st.session_state.premium = True

                if email == ADMIN_EMAIL:
                    st.session_state.premium = True

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

# ---------------- LOGIN PAGE ---------------- #

def auth_page():

    st.title("Analytics Engine")

    st.markdown("## Premium Analytics Subscription")

    st.write("**$25 per year**")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Free User")

        st.write("""
- Run analytics
- View results
- Cannot download outputs
""")

    with col2:

        st.markdown("### Premium User")

        st.write("""
- Run analytics
- Download results
- Full analytics access
- Priority updates
""")

    option = st.radio("Select Option", ["Login", "Signup"])

    if option == "Login":
        login()
    else:
        signup()

# ---------------- SUBSCRIPTION PAGE ---------------- #

def subscription_page():

    st.title("Premium Subscription")

    st.write("Upgrade to **Premium Analytics**")

    st.write("Price: **$25 / year**")

    if st.button("Activate Premium"):

        expiry = (datetime.now() + timedelta(days=365)).isoformat()

        try:

            supabase.table("users")\
                .update({
                    "premium": True,
                    "premium_expiry": expiry
                })\
                .eq("email", st.session_state.user_email)\
                .execute()

            st.session_state.premium = True

            st.success("Premium activated for 1 year")

        except:
            st.error("Subscription update failed")

# ---------------- FILE LOADER ---------------- #

def load_file(uploaded_file):

    uploaded_file.seek(0)

    if uploaded_file.name.endswith(".csv"):

        try:
            df = pd.read_csv(uploaded_file, encoding="utf-8", header=0)
        except:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, encoding="latin1", header=0)

    else:

        uploaded_file.seek(0)
        df = pd.read_excel(uploaded_file, header=0)

    df.columns = df.columns.str.strip()

    return df

# ---------------- COHORT ENGINE ---------------- #

def cohort_engine():

    st.title("Cohort Analytics Engine")

    uploaded_file = st.file_uploader(
        "Upload CSV or Excel",
        type=["csv", "xlsx"]
    )

    if uploaded_file:

        df = load_file(uploaded_file)

        st.success("File Loaded Successfully")

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

                st.warning("Please take subscription to download results")

                if st.button("Go to Subscription Page"):
                    subscription_page()

# ---------------- ADMIN DASHBOARD ---------------- #

def admin_dashboard():

    st.title("Admin Dashboard")

    st.subheader("Users")

    users = supabase.table("users").select("*").execute()

    if users.data:
        st.dataframe(pd.DataFrame(users.data))

    st.subheader("Login Logs")

    logs = supabase.table("login_logs").select("*").execute()

    if logs.data:
        st.dataframe(pd.DataFrame(logs.data))

# ---------------- MAIN ROUTER ---------------- #

if not st.session_state.logged_in:

    auth_page()

else:

    st.sidebar.title("Navigation")

    pages = ["Home", "Cohort Analytics Engine"]

    if st.session_state.user_email == ADMIN_EMAIL:
        pages.append("Admin Dashboard")

    nav = st.sidebar.radio("Select Page", pages)

    st.sidebar.write(f"Logged in as: {st.session_state.user_email}")

    if nav == "Home":

        subscription_page()

    elif nav == "Admin Dashboard":

        admin_dashboard()

    else:

        cohort_engine()
