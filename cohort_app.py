import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

st.set_page_config(
    page_title="Revenue Analytics Engine",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
ADMIN_EMAIL    = "ashwanivatsalarya@gmail.com"
ADMIN_NAME     = "ashwani"
ADMIN_PASSWORD = "Ashwani"

BRIDGE_ORDER = [
    "Beginning MRR or ARR",
    "New Logo", "Cross Sell", "Other In", "Returning",
    "Upsell", "Downsell", "Churn", "Partial Churn", "Lapsed",
    "Ending MRR or ARR",
]
BRIDGE_COLORS = {
    "New Logo":               "#16A34A",
    "Cross Sell":             "#0047AB",
    "Other In":               "#22C55E",
    "Returning":              "#F59E0B",
    "Upsell":                 "#3B82F6",
    "Downsell":               "#F97316",
    "Churn":                  "#EF4444",
    "Partial Churn":          "#FCA5A5",
    "Lapsed":                 "#94A3B8",
    "Beginning MRR or ARR":   "#1E3A5F",
    "Ending MRR or ARR":      "#1E3A5F",
    "No Change":              "#CBD5E1",
}

BRAND_BLUE   = "#0047AB"
BRAND_COLORS = ["#0047AB","#E8611A","#00897B","#8E24AA","#F4A900","#C62828"]

LIGHT_AXIS = dict(
    gridcolor="#F0F2F8", zerolinecolor="#E5E8EF",
    linecolor="#E5E8EF", tickfont=dict(color="#8C95A6", size=11),
)
LIGHT_AXIS_REV = dict(**LIGHT_AXIS, autorange="reversed")

def base_layout(title="", height=380):
    return dict(
        title=dict(text=title, font=dict(size=14, color="#1A1D23", family="Inter"), x=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="#FFFFFF",
        font=dict(family="Inter", color="#5A6478", size=11),
        height=height,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#5A6478", size=11),
                    orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=12, r=12, t=48, b=12),
    )

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for _k, _v in [
    ("authenticated", False), ("user_email", ""),
    ("validated_df", None), ("result", None),
    ("mapping", {}), ("lookbacks", [1, 12]), ("_cohort_df", None),
]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def fmt_currency(val):
    if val is None: return "—"
    v = float(val)
    if abs(v) >= 1_000_000: return f"${v/1_000_000:.1f}M"
    if abs(v) >= 1_000:     return f"${v/1_000:.0f}K"
    return f"${v:.0f}"

def load_file(uf):
    name = uf.name.lower()
    if name.endswith(".csv"):
        try:    return pd.read_csv(uf, encoding="utf-8")
        except: uf.seek(0); return pd.read_csv(uf, encoding="latin1")
    elif name.endswith((".xlsx", ".xls")):
        try:
            import openpyxl
            return pd.read_excel(uf, engine="openpyxl")
        except ImportError:
            return pd.read_excel(uf)
    else:
        st.error("Unsupported format. Please upload CSV or Excel (.xlsx/.xls).")
        return None

# ─────────────────────────────────────────────────────────────────────────────
# LANDING / LOGIN PAGE
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.authenticated:

    # ── Read query params set by the HTML form submit ──────────────────
    qp = st.query_params
    if "email" in qp and "pwd" in qp:
        em  = qp["email"].strip()
        pw  = qp["pwd"].strip()
        name_ok  = (em.lower() == ADMIN_NAME  and pw == ADMIN_PASSWORD)
        email_ok = (em.lower() == ADMIN_EMAIL.lower() and pw == ADMIN_PASSWORD)
        free_ok  = ("@" in em and len(pw) >= 1)
        guest_ok = (em == "__guest__")
        if name_ok or email_ok:
            st.session_state.authenticated = True
            st.session_state.user_email    = ADMIN_EMAIL
            st.query_params.clear()
            st.rerun()
        elif guest_ok or free_ok:
            st.session_state.authenticated = True
            st.session_state.user_email    = "guest@demo.com" if guest_ok else em
            st.query_params.clear()
            st.rerun()

    # ── Full-page landing in one HTML block with embedded JS form ────────
    # We use a real HTML form that submits as GET (so params go into URL/query string)
    # Streamlit will rerun and pick them up via st.query_params above.
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body, [class*="css"] { font-family:'Inter',sans-serif; }
    #MainMenu{visibility:hidden;} footer{visibility:hidden;} header{visibility:hidden;}
    .stApp { background: #0047AB !important; }
    [data-testid="stSidebar"] { display:none !important; }
    .block-container { padding:0 !important; max-width:100% !important; }
    section[data-testid="stMain"] { padding:0 !important; }
    section[data-testid="stMain"] > div { padding:0 !important; }
    div[data-testid="stVerticalBlockBorderWrapper"] { padding:0 !important; }
    .element-container { margin:0 !important; padding:0 !important; }

    /* ── Landing page layout ── */
    .landing-wrap {
        display: flex;
        min-height: 100vh;
        width: 100%;
        font-family: 'Inter', sans-serif;
    }
    .panel-left {
        flex: 0 0 57%;
        background: linear-gradient(150deg,#001F5B 0%,#0047AB 55%,#1565C0 100%);
        padding: 48px 48px 40px 48px;
        display: flex;
        flex-direction: column;
    }
    .panel-right {
        flex: 0 0 43%;
        background: #FFFFFF;
        padding: 48px 48px 40px 48px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    .logo-row { display:flex;align-items:center;gap:10px;margin-bottom:44px; }
    .logo-icon {
        width:34px;height:34px;background:rgba(255,255,255,0.15);border-radius:7px;
        display:flex;align-items:center;justify-content:center;color:white;
        font-size:16px;font-weight:800;border:1px solid rgba(255,255,255,0.25);
        flex-shrink:0;
    }
    .logo-text { color:white;font-size:15px;font-weight:700; }
    .badge {
        display:inline-block;background:rgba(255,255,255,0.12);color:rgba(255,255,255,0.85);
        font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;
        padding:5px 12px;border-radius:20px;border:1px solid rgba(255,255,255,0.2);
        margin-bottom:16px;
    }
    .hero-h1 {
        color:#FFFFFF;font-size:40px;font-weight:800;line-height:1.1;
        letter-spacing:-0.03em;margin-bottom:14px;
    }
    .hero-p { color:rgba(255,255,255,0.75);font-size:14px;line-height:1.65;max-width:430px;margin-bottom:24px; }
    .card-blue {
        background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.15);
        border-radius:12px;padding:16px 18px;margin-bottom:16px;
    }
    .card-label {
        color:rgba(255,255,255,0.5);font-size:10px;font-weight:700;
        letter-spacing:0.09em;text-transform:uppercase;margin-bottom:10px;
    }
    .feature-grid { display:grid;grid-template-columns:1fr 1fr;gap:6px; }
    .feature-item { color:rgba(255,255,255,0.85);font-size:12px; }
    .consult-row { display:flex;align-items:flex-start;gap:12px; }
    .consult-icon { font-size:24px;margin-top:2px;flex-shrink:0; }
    .consult-title { color:#FFFFFF;font-size:13px;font-weight:700;margin-bottom:4px; }
    .consult-text { color:rgba(255,255,255,0.65);font-size:12px;line-height:1.55; }
    .consult-text strong { color:rgba(255,255,255,0.85); }
    .rate-pills { display:flex;gap:8px;margin-top:8px;flex-wrap:wrap; }
    .rate-pill {
        background:rgba(255,255,255,0.12);color:rgba(255,255,255,0.9);
        font-size:11px;font-weight:600;padding:4px 10px;
        border-radius:6px;border:1px solid rgba(255,255,255,0.2);
    }
    .pricing-label {
        color:rgba(255,255,255,0.45);font-size:10px;font-weight:700;
        letter-spacing:0.1em;text-transform:uppercase;margin-bottom:10px;
    }
    .pricing-grid { display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px; }
    .price-card {
        background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.13);
        border-radius:10px;padding:14px;
    }
    .price-card-featured {
        background:rgba(255,255,255,0.13);border:1.5px solid rgba(255,255,255,0.3);
        border-radius:10px;padding:14px;position:relative;
    }
    .popular-badge {
        position:absolute;top:-9px;left:12px;background:#F59E0B;
        color:#1A1D23;font-size:9px;font-weight:700;padding:2px 8px;border-radius:10px;
    }
    .price-tier { color:rgba(255,255,255,0.5);font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:5px; }
    .price-num  { color:#FFFFFF;font-size:20px;font-weight:800; }
    .price-per  { color:rgba(255,255,255,0.45);font-size:10px;margin-bottom:7px; }
    .price-feat { color:rgba(255,255,255,0.7);font-size:11px;line-height:1.7; }

    /* ── Right panel / form ── */
    .welcome-title { font-size:24px;font-weight:800;color:#1A1D23;letter-spacing:-0.02em;margin-bottom:6px; }
    .welcome-sub   { font-size:13px;color:#8C95A6;line-height:1.55;margin-bottom:28px; }
    .form-label { font-size:12px;font-weight:600;color:#5A6478;letter-spacing:0.02em;margin-bottom:5px; }
    .form-input {
        width:100%;padding:11px 14px;font-size:14px;border:1.5px solid #E2E6EF;
        border-radius:8px;color:#1A1D23;background:#F8F9FC;
        font-family:'Inter',sans-serif;outline:none;margin-bottom:14px;
        transition:border-color 0.15s;
    }
    .form-input:focus { border-color:#0047AB; box-shadow:0 0 0 3px rgba(0,71,171,0.08); }
    .btn-primary {
        width:100%;padding:12px 24px;background:#0047AB;color:#FFFFFF;
        border:none;border-radius:8px;font-size:14px;font-weight:600;
        font-family:'Inter',sans-serif;cursor:pointer;transition:background 0.15s;
        margin-bottom:14px;
    }
    .btn-primary:hover { background:#003899; }
    .btn-secondary {
        width:100%;padding:11px 24px;background:#F8F9FC;color:#0047AB;
        border:1.5px solid #BFDBFE;border-radius:8px;font-size:14px;font-weight:600;
        font-family:'Inter',sans-serif;cursor:pointer;transition:background 0.15s;
        margin-bottom:20px;
    }
    .btn-secondary:hover { background:#EFF6FF; }
    .divider-row { display:flex;align-items:center;gap:12px;margin:4px 0 14px 0; }
    .divider-line { flex:1;height:1px;background:#E5E8EF; }
    .divider-or { font-size:11px;color:#8C95A6; }
    .info-card {
        padding:16px;background:#F8F9FC;border-radius:10px;
        border:1px solid #E5E8EF;margin-bottom:12px;
    }
    .info-card-title { font-size:12px;font-weight:700;color:#1A1D23;margin-bottom:7px; }
    .info-card-text  { font-size:12px;color:#5A6478;line-height:1.6; }
    .consult-card {
        padding:14px;background:#EFF6FF;border-radius:10px;
        border:1px solid #BFDBFE;margin-bottom:14px;
    }
    .consult-card-title { font-size:12px;font-weight:700;color:#1E40AF;margin-bottom:5px; }
    .consult-card-text  { font-size:12px;color:#3B5998;line-height:1.55; }
    .terms-text { font-size:11px;color:#8C95A6;margin-top:8px; }
    .err-box {
        background:#FEF2F2;border:1px solid #FCA5A5;color:#DC2626;
        border-radius:6px;padding:10px 14px;font-size:12px;margin-bottom:12px;
    }
    </style>

    <div class="landing-wrap">

      <!-- ═══ LEFT PANEL ═══ -->
      <div class="panel-left">

        <div class="logo-row">
          <div class="logo-icon">R</div>
          <span class="logo-text">Revenue Analytics Engine</span>
        </div>

        <div class="badge">Revenue Intelligence Platform</div>

        <h1 class="hero-h1">Turn revenue data<br>into strategic insight</h1>
        <p class="hero-p">
          Stop spending weeks in Excel. Upload your billing or revenue data and instantly
          get cohort analysis, ARR bridge breakdowns, retention metrics, and customer
          segmentation — all in one place.
        </p>

        <div class="card-blue">
          <div class="card-label">What you get instantly</div>
          <div class="feature-grid">
            <div class="feature-item">📊 Cohort segmentation (SG/PC/RC)</div>
            <div class="feature-item">📈 ARR / MRR revenue bridge</div>
            <div class="feature-item">🔄 NRR, GRR, logo retention</div>
            <div class="feature-item">💰 Price vs volume decomposition</div>
            <div class="feature-item">🎯 New logo / churn / upsell flags</div>
            <div class="feature-item">📋 PE-grade waterfall table</div>
          </div>
        </div>

        <div class="card-blue">
          <div class="consult-row">
            <div class="consult-icon">👨‍💼</div>
            <div>
              <div class="consult-title">Expert help — no full-time hire</div>
              <div class="consult-text">
                Need someone to interpret your data, build a revenue narrative for investors,
                or set up your analytics model? Book <strong>Ashwani</strong> for a focused
                1–2 hour session. Former PE analytics background with deep SaaS and
                subscription metrics expertise.
              </div>
              <div class="rate-pills">
                <span class="rate-pill">1 hr · $150</span>
                <span class="rate-pill">2 hrs · $280</span>
                <span class="rate-pill">Half day · $500</span>
              </div>
            </div>
          </div>
        </div>

        <div>
          <div class="pricing-label">Simple pricing</div>
          <div class="pricing-grid">
            <div class="price-card">
              <div class="price-tier">Free</div>
              <div class="price-num">$0</div>
              <div class="price-per">forever</div>
              <div class="price-feat">✓ Upload &amp; analyse<br>✓ View all dashboards<br>✗ Download results</div>
            </div>
            <div class="price-card-featured">
              <div class="popular-badge">POPULAR</div>
              <div class="price-tier">Premium</div>
              <div class="price-num">$25</div>
              <div class="price-per">once / year</div>
              <div class="price-feat">✓ Everything free<br>✓ Download results<br>✓ Export reports</div>
            </div>
            <div class="price-card">
              <div class="price-tier">Usage</div>
              <div class="price-num">$10</div>
              <div class="price-per">per run</div>
              <div class="price-feat">✓ Each analysis run<br>✓ All engine types<br>✓ Pay as you go</div>
            </div>
          </div>
        </div>

      </div>

      <!-- ═══ RIGHT PANEL ═══ -->
      <div class="panel-right">

        <div class="welcome-title">Welcome back</div>
        <div class="welcome-sub">Sign in to access the platform, or use the guest demo to explore without an account.</div>

        <form method="GET" action="">
          <div class="form-label">Email address</div>
          <input class="form-input" type="text"  name="email" placeholder="you@company.com" autocomplete="email" />
          <div class="form-label">Password</div>
          <input class="form-input" type="password" name="pwd" placeholder="••••••••" autocomplete="current-password" />
          <button class="btn-primary" type="submit">Sign in →</button>
        </form>

        <div class="divider-row">
          <div class="divider-line"></div>
          <span class="divider-or">or</span>
          <div class="divider-line"></div>
        </div>

        <form method="GET" action="">
          <input type="hidden" name="email" value="__guest__" />
          <input type="hidden" name="pwd"   value="guest" />
          <button class="btn-secondary" type="submit">Try free demo (no signup needed)</button>
        </form>

        <div class="info-card">
          <div class="info-card-title">🔒 How access works</div>
          <div class="info-card-text">
            <strong>Free users</strong> — sign in with any email, explore all dashboards and charts. Download is locked until you subscribe.<br><br>
            <strong>Premium ($25/yr)</strong> — unlocks CSV/Excel download and report export.<br><br>
            <strong>$10 per run</strong> — after your first subscription, each analytics run is billed at $10. Pay only for what you use.
          </div>
        </div>

        <div class="consult-card">
          <div class="consult-card-title">📞 Book a consulting session</div>
          <div class="consult-card-text">
            Ashwani is available for 1-on-1 analytics sessions — interpret your data,
            build investor narratives, or get your cohort model set up correctly.
            <br><strong>No retainer. Book by the hour.</strong>
          </div>
        </div>

        <div class="terms-text">By continuing you agree to our Terms of Service and Privacy Policy.</div>

      </div>
    </div>
    """, unsafe_allow_html=True)

    st.stop()



# ─────────────────────────────────────────────────────────────────────────────
# APP CSS (light professional theme)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family:'Inter',sans-serif; }
#MainMenu{visibility:hidden;} footer{visibility:hidden;} header{visibility:hidden;}
.stApp { background:#F8F9FC; color:#1A1D23; }
[data-testid="stSidebar"] {
    background:#FFFFFF !important; border-right:1px solid #E5E8EF !important;
    display:flex !important;
}
.block-container { padding:2rem 1rem 1rem 1rem !important; max-width:100% !important; }
[data-testid="stSidebar"] .stRadio label {
    color:#5A6478 !important; font-size:13px !important; font-weight:500 !important;
    padding:7px 10px !important; border-radius:6px !important; transition:all 0.15s !important;
}
[data-testid="stSidebar"] .stRadio label:hover { color:#1A1D23 !important; background:#F0F2F8 !important; }
.metric-card {
    background:#FFFFFF; border:1px solid #E5E8EF; border-radius:10px;
    padding:16px 18px; box-shadow:0 1px 3px rgba(0,0,0,0.05);
}
.metric-card-accent {
    background:#FFFFFF; border:1px solid #E5E8EF; border-top:3px solid #0047AB;
    border-radius:10px; padding:16px 18px; box-shadow:0 1px 3px rgba(0,0,0,0.05);
}
.metric-label {
    font-size:10px; font-weight:600; letter-spacing:0.09em;
    text-transform:uppercase; color:#8C95A6; margin-bottom:5px;
}
.metric-value { font-size:22px; font-weight:700; color:#1A1D23; letter-spacing:-0.02em; }
.metric-value-lg { font-size:24px; font-weight:700; color:#0047AB; letter-spacing:-0.02em; }
.page-title { font-size:22px; font-weight:700; color:#1A1D23; letter-spacing:-0.02em; margin-bottom:2px; }
.page-subtitle { font-size:13px; color:#8C95A6; margin-bottom:20px; }
.section-hdr {
    font-size:10px; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
    color:#8C95A6; margin:18px 0 8px 0; padding-bottom:6px; border-bottom:1px solid #E5E8EF;
}
.panel { background:#FFFFFF; border:1px solid #E5E8EF; border-radius:10px; padding:18px; box-shadow:0 1px 3px rgba(0,0,0,0.04); }
.badge-live { display:inline-block; background:#DCFCE7; color:#15803D; border:1px solid #BBF7D0; padding:2px 8px; border-radius:20px; font-size:10px; font-weight:600; }
.badge-soon { display:inline-block; background:#EFF6FF; color:#1D4ED8; border:1px solid #BFDBFE; padding:2px 8px; border-radius:20px; font-size:10px; font-weight:600; }
.coming-wrap { display:flex; flex-direction:column; align-items:center; justify-content:center; padding:80px 40px; text-align:center; }
.stSelectbox > div > div { background:#FFFFFF !important; border:1px solid #D1D5DB !important; border-radius:6px !important; color:#1A1D23 !important; }
.stTextInput input { background:#FFFFFF !important; border:1px solid #D1D5DB !important; border-radius:6px !important; color:#1A1D23 !important; }
.stMultiSelect > div > div { background:#FFFFFF !important; border:1px solid #D1D5DB !important; border-radius:6px !important; }
.stCheckbox label { color:#5A6478 !important; font-size:13px !important; }
.stButton > button { background:#0047AB !important; color:#FFFFFF !important; border:none !important; border-radius:6px !important; font-weight:600 !important; font-size:13px !important; padding:10px 24px !important; transition:background 0.15s !important; width:100% !important; }
.stButton > button:hover { background:#003899 !important; }
.stButton > button:disabled { background:#E5E8EF !important; color:#8C95A6 !important; }
.stTabs [data-baseweb="tab-list"] { background:transparent !important; border-bottom:2px solid #E5E8EF !important; }
.stTabs [data-baseweb="tab"] { background:transparent !important; color:#8C95A6 !important; font-size:13px !important; font-weight:500 !important; padding:10px 18px !important; border-radius:0 !important; border-bottom:2px solid transparent !important; margin-bottom:-2px !important; }
.stTabs [aria-selected="true"] { color:#0047AB !important; border-bottom:2px solid #0047AB !important; font-weight:600 !important; }
.stTabs [data-baseweb="tab-panel"] { background:transparent !important; padding-top:20px !important; }
.stDataFrame { border:1px solid #E5E8EF !important; border-radius:8px !important; }
hr { border-color:#E5E8EF !important; }
.stNumberInput input { background:#FFFFFF !important; border:1px solid #D1D5DB !important; border-radius:6px !important; color:#1A1D23 !important; }
.step-row { display:flex; align-items:center; gap:6px; margin-bottom:18px; }
.step-done { width:22px;height:22px;background:#16A34A;color:#fff;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:700; }
.step-active { width:22px;height:22px;background:#0047AB;color:#fff;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:700; }
.step-inactive { width:22px;height:22px;background:#E5E8EF;color:#8C95A6;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;font-size:10px;font-weight:700; }
.step-label-a { font-size:12px;color:#1A1D23;font-weight:500; }
.step-label-i { font-size:12px;color:#8C95A6;font-weight:400; }
.step-line { flex:1;height:1px;background:#E5E8EF;max-width:32px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;padding:4px 0 14px 0;">
      <div style="width:32px;height:32px;background:#0047AB;border-radius:6px;
                  display:flex;align-items:center;justify-content:center;
                  color:white;font-size:14px;font-weight:700;">R</div>
      <div>
        <div style="font-size:13px;font-weight:700;color:#1A1D23;">Revenue Analytics</div>
        <div style="font-size:10px;color:#8C95A6;margin-top:1px;">Analytics Engine v2.0</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="section-hdr">User</div>', unsafe_allow_html=True)
    email_input = st.text_input("", placeholder="your@email.com", label_visibility="collapsed",
                                 value=st.session_state.user_email)
    if email_input:
        st.session_state.user_email = email_input

    is_admin = st.session_state.user_email.lower() == ADMIN_EMAIL.lower()
    if is_admin:
        st.markdown('<div style="background:#DCFCE7;color:#15803D;font-size:11px;font-weight:600;padding:5px 10px;border-radius:6px;border:1px solid #BBF7D0;margin-bottom:8px;">✓ Subscription Active</div>', unsafe_allow_html=True)

    if st.button("Sign out", key="signout"):
        st.session_state.authenticated = False
        st.session_state.user_email = ""
        st.rerun()

    st.markdown('<div class="section-hdr">Analytics Modules</div>', unsafe_allow_html=True)
    module = st.radio("", [
        "Cohort Analytics", "Customer Analytics",
        "Product Bundling", "ACV Analysis", "Revenue Concentration",
    ], label_visibility="collapsed")

    st.markdown('<div class="section-hdr" style="margin-top:20px;">Module Status</div>', unsafe_allow_html=True)
    for mn, live in [("Cohort Analytics",True),("Customer Analytics",True),
                     ("Product Bundling",False),("ACV Analysis",False),("Revenue Concentration",False)]:
        badge = '<span class="badge-live">Live</span>' if live else '<span class="badge-soon">Soon</span>'
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;padding:3px 0;">'
            f'<span style="font-size:12px;color:#5A6478;">{mn}</span>{badge}</div>',
            unsafe_allow_html=True)

# Coming soon
if module in ["Product Bundling","ACV Analysis","Revenue Concentration"]:
    st.markdown(f'<div class="page-title">{module}</div>', unsafe_allow_html=True)
    st.markdown('<div class="coming-wrap"><div style="font-size:48px;margin-bottom:14px;">🚀</div><div style="font-size:28px;font-weight:700;color:#0047AB;margin-bottom:8px;">Coming Soon</div><div style="font-size:13px;color:#8C95A6;">This module is under development and will be available in the next release.</div></div>', unsafe_allow_html=True)
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# COHORT ENGINE (original, unchanged)
# ─────────────────────────────────────────────────────────────────────────────
def cohort_engine(df, metric, cols, cohort_type):
    temp = df.groupby(cols)[metric].sum().reset_index().sort_values(metric, ascending=False)
    temp["Rank"] = temp[metric].rank(method="dense", ascending=False)
    max_rank = temp["Rank"].max()
    name = "_".join(cols)
    if cohort_type == "SG":
        def bucket(x):
            if x<=10: return "Top 10"
            elif x<=25: return "11-25"
            elif x<=50: return "26-50"
            else: return "Others"
        temp[f"SG_{name}"] = temp["Rank"].apply(bucket)
    if cohort_type == "PC":
        temp["Pct"] = temp["Rank"] / max_rank
        def bucket(x):
            if x<=.05: return "Top 5%"
            elif x<=.10: return "Top 10%"
            elif x<=.20: return "Top 20%"
            elif x<=.50: return "Top 50%"
            else: return "Bottom 50%"
        temp[f"PC_{name}"] = temp["Pct"].apply(bucket)
    if cohort_type == "RC":
        temp["Cum"] = temp[metric].cumsum()
        total = temp[metric].sum()
        temp["Share"] = temp["Cum"] / total
        def bucket(x):
            if x<=.2: return "Top Drivers"
            elif x<=.5: return "Mid Tier"
            elif x<=.8: return "Long Tail"
            else: return "Bottom Tail"
        temp[f"RC_{name}"] = temp["Share"].apply(bucket)
    return temp

# ─────────────────────────────────────────────────────────────────────────────
# CUSTOMER ANALYTICS ENGINE
# ─────────────────────────────────────────────────────────────────────────────
def run_customer_analytics(df_raw, customer_col, product_col, date_col,
                            metric, qty_col, channel_col, region_col, lookback_months):
    """
    Pixel-perfect Python translation of MRR_Analysis_wf_Latest_Version.yxmd.

    Step 1 — Input & Scope
    Step 2 — Date variables & generate missing months (grid up to Dataset_Max + 12m)
    Step 3 — Lookback × Prior MRR × DTE  (shift by N for N-month lookback)
    Step 4 — Vintage, customer/product min-max dates
    Step 5 — Bridge Classification & all value fields
    """
    # ── Step 1: Prepare & scope ──────────────────────────────────────────
    df = df_raw.copy()
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df[metric]   = pd.to_numeric(df[metric], errors="coerce").fillna(0)

    has_qty  = qty_col     and qty_col     != "None" and qty_col     in df.columns
    has_prod = product_col and product_col != "None" and product_col in df.columns
    has_chan = channel_col and channel_col != "None" and channel_col in df.columns
    has_reg  = region_col  and region_col  != "None" and region_col  in df.columns

    if has_qty:
        df[qty_col] = pd.to_numeric(df[qty_col], errors="coerce").fillna(0)
    else:
        df["_qty"] = 1.0        # Alteryx default: Quantity = 1 when not provided
        qty_col = "_qty"
        has_qty = True

    # Normalise dates to month-end (Alteryx: datetimetrim(Date,'lastofmonth'))
    df[date_col] = df[date_col] + pd.offsets.MonthEnd(0)

    # In-scope filter: MRR > 0 and not null
    df_scope = df[df[metric] > 0].copy()

    # Dimension key columns
    keys = [customer_col]
    if has_prod: keys.append(product_col)
    if has_chan: keys.append(channel_col)
    if has_reg:  keys.append(region_col)

    # ── Step 2: Generate missing months ─────────────────────────────────
    # 2.1  Dataset_Max_Date = max(Date) across all in-scope rows
    dataset_max = df_scope[date_col].max()

    # 2.3  Summarize: Group by keys + Date, sum MRR + Qty
    agg_actual = (
        df_scope.groupby(keys + [date_col], as_index=False)
        .agg(**{metric: (metric, "sum"), qty_col: (qty_col, "sum")})
    )
    agg_actual["Dataset_Max_Date"] = dataset_max

    # 2.5  Per-key lifecycle: min date, max date
    lifecycle = (
        df_scope.groupby(keys, as_index=False)
        .agg(Min_Date=(date_col, "min"), Max_Date=(date_col, "max"))
    )
    lifecycle["Dataset_Max_Date"] = dataset_max

    # 2.7  Generate rows: Initial=[Min_Date], Cond=[Date]<=[Dataset_Max_Date],
    #      Loop=DateTimeTrim(DateTimeAdd(Date,1,'month'),'lastofmonth')
    #      Then filter: Date <= DateTimeTrim(DateTimeAdd(Dataset_Max_Date,12,'months'),'lastofmonth')
    all_months = pd.date_range(
        lifecycle["Min_Date"].min(),
        dataset_max + pd.DateOffset(months=12),
        freq="ME"
    )
    lifecycle["_k"] = 1
    mdf  = pd.DataFrame({"Date_Grid": all_months, "_k": 1})
    grid = lifecycle.merge(mdf, on="_k").drop("_k", axis=1)

    # Filter: Date <= Dataset_Max_Date (generates the active window)
    # Then extended to Dataset_Max + 12m for expiry pool
    grid = grid[
        (grid["Date_Grid"] >= grid["Min_Date"]) &
        (grid["Date_Grid"] <= grid["Dataset_Max_Date"] + pd.DateOffset(months=12))
    ]
    grid = grid.rename(columns={"Date_Grid": date_col})

    # 2.9  Join actual MRR back; missing rows get 0 (Alteryx formula: 0)
    df_grid = grid[keys + [date_col, "Min_Date", "Max_Date", "Dataset_Max_Date"]].merge(
        agg_actual[keys + [date_col, metric, qty_col]],
        on=keys + [date_col], how="left"
    )
    df_grid[metric]  = df_grid[metric].fillna(0)
    df_grid[qty_col] = df_grid[qty_col].fillna(0)

    # Sort for multi-row formula (Step 3): keys + date
    df_grid = df_grid.sort_values(keys + [date_col]).reset_index(drop=True)

    # ── Step 4: Vintage & customer/product date lookups ──────────────────
    # 4.4  Customer min/max date
    cust_dates = (
        df_scope.groupby(customer_col, as_index=False)
        .agg(Customer_Min_Date=(date_col, "min"), Customer_Max_Date=(date_col, "max"))
    )

    # 4.7  Customer-product min/max date
    prod_keys = [customer_col] + ([product_col] if has_prod else [])
    prod_dates = (
        df_scope.groupby(prod_keys, as_index=False)
        .agg(CustProd_Min_Date=(date_col, "min"), CustProd_Max_Date=(date_col, "max"))
    )

    df_grid = df_grid.merge(cust_dates, on=customer_col, how="left")
    df_grid = df_grid.merge(prod_dates, on=prod_keys,    how="left")

    # 4.5 / 4.9  Vintage
    df_grid["Vintage"] = df_grid["Customer_Min_Date"].dt.year

    # Attach extra dimension columns (channel/region) from original data
    for extra_col in ([channel_col] if has_chan else []) + ([region_col] if has_reg else []):
        if extra_col in df_scope.columns:
            emap = df_scope.drop_duplicates(subset=[customer_col])[[customer_col, extra_col]]
            df_grid = df_grid.merge(emap, on=customer_col, how="left", suffixes=("", "_x"))

    # ── Step 3 + 5: Run per lookback window ─────────────────────────────
    # Alteryx runs 3 separate branches (lb=1, lb=3, lb=12) then unions them.
    # Key insight: Prior MRR = shift(N) where N = lookback months.
    # Lookback FILTER: only include rows where
    #   Round(DatetimeDiff(Date, Max_Date, 'days') / 30, 1) <= MonthLookback
    # This means rows more than N months beyond the customer's max date are excluded.

    results = []
    for lb in lookback_months:

        t = df_grid.copy()
        t["Month Lookback"] = lb

        # 3.x.2 Filter: Round(diff(Date, Max_Date, days)/30, 1) <= lb
        days_beyond = (t[date_col] - t["Max_Date"]).dt.days
        t = t[np.round(days_beyond / 30, 1) <= lb].copy()

        # 3.x.3 Expiry Pool Flag & MRR Flag
        t["Expiry Pool Flag"] = np.where(t[date_col] > t["Max_Date"], 1, 0)
        t["MRR Flag"]         = np.where(t[date_col] <= t["Max_Date"], 1, 0)

        # 3.x.4 Multi-Row Formula: Prior MRR = shift(lb) grouped by keys
        # Alteryx: [Row-N:MRR] where N = Month Lookback
        t = t.sort_values(keys + [date_col]).reset_index(drop=True)
        t["Prior MRR or ARR"] = (
            t.groupby(keys)[metric]
            .transform(lambda s: s.shift(lb))
            .fillna(0)
        )
        t["Prior Quantity"] = (
            t.groupby(keys)[qty_col]
            .transform(lambda s: s.shift(lb))
            .fillna(0)
        )

        # 3.x.6 DTE (Due to Expire)
        t["DTE"] = np.where(t["Expiry Pool Flag"] == 1, t["Prior MRR or ARR"], 0)

        # 4.2 Filter FALSE side: remove rows where MRR=0 AND Prior=0 AND DTE=0
        t = t[~((t[metric] == 0) & (t["Prior MRR or ARR"] == 0) & (t["DTE"] == 0))].copy()

        # ── Step 5: Bridge Classification ─────────────────────────────
        # 5.1 pastMRR: days(Date - Min_Date)/30 < lb → "No" else "Yes"
        days_from_first   = (t[date_col] - t["Min_Date"]).dt.days
        t["pastMRR"]      = np.where(np.round(days_from_first / 30, 1) < lb, "No", "Yes")

        # 5.1 futureMRR: Customer_Max_Date > Date → "Yes" else "No"
        t["futureMRR"]    = np.where(t["Customer_Max_Date"] > t[date_col], "Yes", "No")

        # Lookback cutoff date: DateTimeTrim(DateTimeAdd(Date, -lb, 'months'), 'lastofmonth')
        t["Lookback Date"] = (
            t[date_col].apply(lambda d: (d - pd.DateOffset(months=lb)) + pd.offsets.MonthEnd(0))
        )

        # 5.2 Bridge Flag (exact Alteryx logic)
        prior  = t["Prior MRR or ARR"]
        curr   = t[metric]
        past   = t["pastMRR"]
        future = t["futureMRR"]
        dte    = t["DTE"]
        ld     = t["Lookback Date"]          # lookback cutoff
        cust_min = t["Customer_Min_Date"]
        cust_max = t["Customer_Max_Date"]
        prod_min = t["CustProd_Min_Date"]
        prod_max = t["CustProd_Max_Date"]

        conditions = [
            # New Logo / Cross-sell / Other In  (Prior=0, Curr>0, past="No")
            (prior==0) & (curr!=0) & (past=="No") & (prod_min <= ld),             # Other In
            (prior==0) & (curr!=0) & (past=="No") & (cust_min <= ld) & (prod_min > ld),  # Cross-sell
            (prior==0) & (curr!=0) & (past=="No") & (cust_min > ld),              # New Logo
            # Returning  (Prior=0, Curr>0, past="Yes")
            (prior==0) & (curr!=0) & (past=="Yes"),                               # Returning
            # Lapsed  (Curr=0, future="Yes")  — check before Churn
            (curr==0) & (future=="Yes"),                                           # Lapsed
            # Other Out / Churn-Partial / Churn  (Prior≠0, Curr=0, DTE≠0, future="No")
            (prior!=0) & (curr==0) & (dte!=0) & (future=="No") & (prod_max >= t[date_col]),   # Other Out
            (prior!=0) & (curr==0) & (dte!=0) & (future=="No") & (cust_max >= t[date_col]) & (prod_max < t[date_col]),  # Churn-Partial
            (prior!=0) & (curr==0) & (dte!=0) & (future=="No") & (cust_max < t[date_col]) & (prod_max < t[date_col]),  # Churn
            # Upsell / Downsell  (Prior≠0, Curr≠0)
            (prior!=0) & (curr!=0) & (prior <= curr),                             # Upsell
            (prior!=0) & (curr!=0) & (prior > curr),                              # Downsell
        ]
        choices = [
            "Other In", "Cross-sell", "New Logo",
            "Returning",
            "Lapsed",
            "Other Out", "Churn-Partial", "Churn",
            "Upsell", "Downsell",
        ]
        t["Bridge Classification"] = np.select(conditions, choices, default="Unclassified")

        # 5.2 Bridge Value
        t["Bridge Value"]         = curr - prior
        # 5.3 Beginning / Ending
        t["Beginning MRR or ARR"] = prior
        t["Ending MRR or ARR"]    = curr

        # 5.4 Price / Volume decomposition (only for Upsell/Downsell)
        is_upsell_downsell = t["Bridge Classification"].isin(["Upsell", "Downsell"])

        t["Price New"]   = curr  / t[qty_col].replace(0, np.nan)
        t["pPrice New"]  = prior / t["Prior Quantity"].replace(0, np.nan)

        qty_diff   = t[qty_col]         - t["Prior Quantity"]
        price_diff = t["Price New"]     - t["pPrice New"]
        min_qty    = np.minimum(t[qty_col], t["Prior Quantity"])
        min_price  = np.where(t["Price New"] < t["pPrice New"], t["Price New"], t["pPrice New"])

        # Price on Volume (interaction term)
        pov = np.where(
            is_upsell_downsell,
            np.where(
                (t["Price New"] < t["pPrice New"]) & (t[qty_col] < t["Prior Quantity"]),
                ((t["Price New"] - t["pPrice New"]) * (t[qty_col] - t["Prior Quantity"])) * -1,
                np.where(
                    (t["Price New"] > t["pPrice New"]) & (t[qty_col] > t["Prior Quantity"]),
                    (t["Price New"] - t["pPrice New"]) * (t[qty_col] - t["Prior Quantity"]),
                    0
                )
            ),
            0
        )

        # Volume Impact
        vol_impact = np.where(
            is_upsell_downsell,
            qty_diff * np.where(t["Price New"] < t["pPrice New"], t["Price New"], t["pPrice New"]),
            0
        )

        # Price Impact
        pri_impact = np.where(
            is_upsell_downsell,
            price_diff * np.where(t[qty_col] < t["Prior Quantity"], t[qty_col], t["Prior Quantity"]),
            0
        )

        # PV Miscellaneous
        pv_misc = np.where(
            is_upsell_downsell,
            t["Bridge Value"] - (
                np.where(np.isnan(pov), 0, pov) +
                np.where(np.isnan(pri_impact), 0, pri_impact) +
                np.where(np.isnan(vol_impact), 0, vol_impact)
            ),
            0
        )

        t["Price on Volume"] = np.where(is_upsell_downsell, pov, 0)
        t["Price Impact"]    = np.where(is_upsell_downsell, pri_impact, 0)
        # 5.5 Final Volume Impact = Volume Impact + PV Miscellaneous (Alteryx formula 5.5)
        t["Volume Impact"]   = (
            np.where(np.isnan(vol_impact), 0, vol_impact) +
            np.where(np.isnan(pv_misc), 0, pv_misc)
        )

        # 5.5 Lookback Date (already computed above as "Lookback Date")
        # Rename internal columns for consistency
        t = t.rename(columns={
            "Prior MRR or ARR": f"Prior_{metric}",
            "Prior Quantity":   f"Prior_{qty_col}",
        })
        t["Lookback"]    = lb     # keep numeric lookback for filtering
        t["Beginning_ARR"] = t["Beginning MRR or ARR"]
        t["Ending_ARR"]    = t["Ending MRR or ARR"]
        t["Bridge"]        = t["Bridge Classification"]   # alias for existing chart code
        t["Bridge_Value"]  = t["Bridge Value"]

        results.append(t)

    return pd.concat(results, ignore_index=True)


def compute_retention(master, metric, lookback):
    d = master[master["Lookback"]==lookback]
    a = d[d["Beginning_ARR"]>0]
    if a.empty: return {"Beginning ARR":0,"Ending ARR":0,"NRR":0,"GRR":0,"New ARR":0,"Lost ARR":0}
    beg  = a["Beginning_ARR"].sum()
    ch   = a.loc[a["Bridge"].isin(["Churn","Partial Churn"]),"Bridge_Value"].sum()
    dw   = a.loc[a["Bridge"]=="Downsell","Bridge_Value"].sum()
    up   = a.loc[a["Bridge"]=="Upsell","Bridge_Value"].sum()
    cr   = a.loc[a["Bridge"]=="Cross Sell","Bridge_Value"].sum()
    new_arr = d.loc[d["Bridge"]=="New Logo","Ending_ARR"].sum()
    ending  = d["Ending_ARR"].sum()
    return {"Beginning ARR":beg,"Ending ARR":ending,
            "NRR":round((beg+up+cr+ch+dw)/beg*100,1) if beg else 0,
            "GRR":round((beg+ch+dw)/beg*100,1) if beg else 0,
            "New ARR":new_arr,"Lost ARR":ch+dw}


def make_arr_waterfall_table(master, metric, date_col, lookback, year_filter=None):
    """
    Build the ARR waterfall table like the Excel:
    Rows = Bridge Classification (Beginning ARR, New Logo, Upsell, Downsell, Churn, ..., Ending ARR)
    Columns = Date periods
    Values = Bridge Value summed
    """
    df = master[master["Lookback"]==lookback].copy()
    if year_filter and year_filter != "All":
        df = df[df[date_col].dt.year == int(year_filter)]
    if df.empty: return pd.DataFrame()

    # Build Beginning ARR row (= Prior_metric sum where active at start of period)
    agg_bridge = df.groupby([date_col,"Bridge"])["Bridge_Value"].sum().reset_index()
    agg_bridge.columns = [date_col, "Bridge Classification", "Value"]

    # Beginning ARR = sum of Beginning_ARR per period
    beg = df.groupby(date_col)["Beginning_ARR"].sum().reset_index()
    beg["Bridge Classification"] = "Beginning MRR or ARR"
    beg = beg.rename(columns={"Beginning_ARR":"Value"})

    # Ending ARR = sum of Ending_ARR per period
    end = df.groupby(date_col)["Ending_ARR"].sum().reset_index()
    end["Bridge Classification"] = "Ending MRR or ARR"
    end = end.rename(columns={"Ending_ARR":"Value"})

    combined = pd.concat([
        beg[[date_col,"Bridge Classification","Value"]],
        agg_bridge,
        end[[date_col,"Bridge Classification","Value"]],
    ])
    combined = combined[combined["Bridge Classification"] != "No Change"]

    # Pivot: rows = Bridge Classification, columns = Date
    pivot = combined.pivot_table(
        index="Bridge Classification", columns=date_col,
        values="Value", aggfunc="sum"
    ).fillna(0)

    # Sort columns chronologically
    pivot = pivot.reindex(sorted(pivot.columns), axis=1)

    # Sort rows in logical bridge order
    row_order = [r for r in BRIDGE_ORDER if r in pivot.index]
    other_rows = [r for r in pivot.index if r not in BRIDGE_ORDER]
    pivot = pivot.reindex(row_order + other_rows)

    # Format column headers as YYYY-MM
    pivot.columns = [str(c)[:7] for c in pivot.columns]

    return pivot


def make_customer_bridge_table(master, metric, date_col, customer_col, lookback, year_filter=None):
    """
    Customer-level bridge table:
    Rows = Customers, Columns = Bridge Classification + Bridge Value by period
    """
    df = master[master["Lookback"]==lookback].copy()
    if year_filter and year_filter != "All":
        df = df[df[date_col].dt.year == int(year_filter)]
    if df.empty: return pd.DataFrame()

    df["Period"] = df[date_col].dt.strftime("%Y-%m")
    out = df[[customer_col, "Period", "Bridge", "Bridge_Value",
              metric, f"Prior_{metric}"]].copy()
    out = out[out["Bridge"] != "No Change"]
    out.columns = [customer_col, "Period", "Bridge Classification",
                   "Bridge Value", "Ending ARR", "Beginning ARR"]
    out = out.sort_values(["Period", "Bridge Classification", customer_col])
    return out


# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
titles = {
    "Cohort Analytics":   ("Cohort Analytics",   "Segment customers, products and markets into ranked cohorts"),
    "Customer Analytics": ("Customer Analytics",  "ARR bridge, retention trends, top movers and pricing analysis"),
}
pt, ps = titles.get(module, (module,""))
st.markdown(f'<div class="page-title">{pt}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="page-subtitle">{ps}</div>', unsafe_allow_html=True)

left, right = st.columns([1,1.75], gap="large")

# ─────────────────────────────────────────────────────────────────────────────
# LEFT PANEL — Upload & Configure
# ─────────────────────────────────────────────────────────────────────────────
with left:
    data_ok = st.session_state.validated_df is not None
    s1 = "done" if data_ok else "active"
    s2 = "done" if data_ok else "inactive"
    s3 = "active" if data_ok else "inactive"
    st.markdown(f"""
    <div class="step-row">
      <div class="step-{s1}">1</div><span class="step-label-a">Upload</span>
      <div class="step-line"></div>
      <div class="step-{s2}">2</div><span class="step-label-{'a' if data_ok else 'i'}">Map</span>
      <div class="step-line"></div>
      <div class="step-{s3}">3</div><span class="step-label-{'a' if data_ok else 'i'}">Analyse</span>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv","xlsx","xls"],
                                      label_visibility="collapsed")
    if uploaded_file:
        raw_df = load_file(uploaded_file)
        if raw_df is not None:
            raw_df.columns = raw_df.columns.str.strip()
            columns = raw_df.columns.tolist()

            st.markdown('<div class="section-hdr">Dataset Type</div>', unsafe_allow_html=True)
            dataset_type = st.radio("", ["Revenue Dataset","Billing Dataset","Bookings Dataset"],
                                    horizontal=True, label_visibility="collapsed")
            metric_label = ("ACV / TCV Column" if dataset_type=="Bookings Dataset"
                           else "Billing Amount" if dataset_type=="Billing Dataset"
                           else "MRR / ARR Column")

            st.markdown('<div class="section-hdr">Column Mapping</div>', unsafe_allow_html=True)
            metric       = st.selectbox(metric_label, columns)
            customer_col = st.selectbox("Customer Column", columns)
            date_col     = st.selectbox("Date Column", columns)
            product_col  = st.selectbox("Product Column",  ["None"]+columns)
            channel_col  = st.selectbox("Channel Column",  ["None"]+columns)
            region_col   = st.selectbox("Geography / Region Column", ["None"]+columns)
            fiscal_col   = st.selectbox("Fiscal Year Column", ["None"]+columns)
            qty_col      = st.selectbox("Quantity Column (optional)", ["None"]+columns)

            if st.button("✓  Validate Data"):
                raw_df[date_col] = pd.to_datetime(raw_df[date_col], errors="coerce")
                st.session_state.validated_df = raw_df
                st.session_state.mapping = dict(
                    metric=metric, customer_col=customer_col, date_col=date_col,
                    product_col=product_col, channel_col=channel_col,
                    region_col=region_col, fiscal_col=fiscal_col, qty_col=qty_col)
                st.session_state.result = None
                st.success(f"✓  {len(raw_df):,} rows validated")
    st.markdown('</div>', unsafe_allow_html=True)

    # Cohort config
    if data_ok and module == "Cohort Analytics":
        df = st.session_state.validated_df.copy()
        m  = st.session_state.mapping
        metric     = m["metric"]
        fiscal_col = m["fiscal_col"]
        columns    = df.columns.tolist()
        if fiscal_col != "None":
            st.markdown('<div class="section-hdr">Period Filter</div>', unsafe_allow_html=True)
            fy_vals = sorted(df[fiscal_col].dropna().unique())
            logic   = st.selectbox("Period Logic", ["All Periods","Latest Period","Select Fiscal Year"])
            if logic == "Latest Period":         df = df[df[fiscal_col]==fy_vals[-1]]
            elif logic == "Select Fiscal Year":
                fy = st.selectbox("Fiscal Year", fy_vals)
                df = df[df[fiscal_col]==fy]
        st.markdown('<div class="section-hdr">Individual Cohorts</div>', unsafe_allow_html=True)
        individual_cols = st.multiselect("Select Columns", columns)
        st.markdown('<div class="section-hdr">Hierarchical Cohorts</div>', unsafe_allow_html=True)
        hierarchy_count = st.number_input("Number of Hierarchies", 0, 10, 0)
        hierarchies = []
        for i in range(hierarchy_count):
            hc = st.multiselect(f"Hierarchy {i+1}", columns, key=f"h_{i}")
            if hc: hierarchies.append(hc)
        st.markdown('<div class="section-hdr">Cohort Types</div>', unsafe_allow_html=True)
        sg = st.checkbox("Size Group (SG_)")
        pc = st.checkbox("Percentile (PC_)")
        rc = st.checkbox("Revenue Contribution (RC_)")
        if st.button("⚡  Analyse Metrics"):
            result = df.copy()
            for col in individual_cols:
                for flag, ct in [(sg,"SG"),(pc,"PC"),(rc,"RC")]:
                    if flag:
                        t = cohort_engine(df, metric, [col], ct)
                        result = result.merge(t[[col,f"{ct}_{col}"]], on=col, how="left")
            for grp in hierarchies:
                nm = "_".join(grp)
                for flag, ct in [(sg,"SG"),(pc,"PC"),(rc,"RC")]:
                    if flag:
                        t = cohort_engine(df, metric, grp, ct)
                        result = result.merge(t[grp+[f"{ct}_{nm}"]], on=grp, how="left")
            st.session_state.result    = result
            st.session_state._cohort_df = df

    # Customer analytics config
    if data_ok and module == "Customer Analytics":
        st.markdown('<div class="section-hdr">Analytics Settings</div>', unsafe_allow_html=True)
        lb_choices = st.multiselect("Lookback Windows (months)", [1,3,6,12], default=[1,12])
        if st.button("⚡  Run Customer Analytics"):
            m  = st.session_state.mapping
            df = st.session_state.validated_df.copy()
            with st.spinner("Running revenue bridge engine…"):
                master = run_customer_analytics(
                    df_raw=df, customer_col=m["customer_col"],
                    product_col=m["product_col"], date_col=m["date_col"],
                    metric=m["metric"], qty_col=m["qty_col"],
                    channel_col=m["channel_col"], region_col=m["region_col"],
                    lookback_months=lb_choices if lb_choices else [1,12])
            st.session_state.result    = master
            st.session_state.lookbacks = lb_choices if lb_choices else [1,12]
            st.success("✓  Analytics complete")

# ─────────────────────────────────────────────────────────────────────────────
# RIGHT PANEL
# ─────────────────────────────────────────────────────────────────────────────
with right:

    # ══════════════════════════════════════════════════════════════════════
    # COHORT ANALYTICS
    # ══════════════════════════════════════════════════════════════════════
    if module == "Cohort Analytics":
        if st.session_state.result is not None:
            result       = st.session_state.result
            m            = st.session_state.mapping
            metric       = m["metric"]
            fiscal_col   = m["fiscal_col"]
            customer_col = m["customer_col"]
            date_col     = m["date_col"]
            df_used = st.session_state.get("_cohort_df", st.session_state.validated_df)
            cohort_cols = [c for c in result.columns if c.startswith(("SG_","PC_","RC_"))]

            tab1, tab2, tab3 = st.tabs(["Summary","Cohort Analytics","Output"])

            with tab1:
                total_rev = df_used[metric].sum()
                n_cust    = df_used[customer_col].nunique() if customer_col!="None" else 0
                rpc       = total_rev/n_cust if n_cust else 0
                c1,c2,c3  = st.columns(3)
                with c1: st.markdown(f'<div class="metric-card-accent"><div class="metric-label">Total Revenue</div><div class="metric-value-lg">{fmt_currency(total_rev)}</div></div>', unsafe_allow_html=True)
                with c2: st.markdown(f'<div class="metric-card"><div class="metric-label">Customers</div><div class="metric-value">{n_cust:,}</div></div>', unsafe_allow_html=True)
                with c3: st.markdown(f'<div class="metric-card"><div class="metric-label">Revenue / Customer</div><div class="metric-value">{fmt_currency(rpc)}</div></div>', unsafe_allow_html=True)
                st.markdown("")

                if fiscal_col != "None" and customer_col != "None":
                    fy = df_used.groupby(fiscal_col).agg(Revenue=(metric,"sum"), Customers=(customer_col,"nunique")).reset_index()
                    fy["Rev_per_Cust"] = fy["Revenue"]/fy["Customers"]

                    # Summary table by fiscal year
                    st.markdown('<div class="section-hdr">Summary by Fiscal Year</div>', unsafe_allow_html=True)
                    fy_display = fy.copy()
                    fy_display["Revenue"]       = fy_display["Revenue"].apply(fmt_currency)
                    fy_display["Rev_per_Cust"]  = fy_display["Rev_per_Cust"].apply(fmt_currency)
                    fy_display.columns = [fiscal_col, "Revenue", "Unique Customers", "Rev per Customer"]
                    st.dataframe(fy_display, use_container_width=True, hide_index=True)

                    # Revenue combo chart
                    fy_raw = df_used.groupby(fiscal_col).agg(Revenue=(metric,"sum"), Customers=(customer_col,"nunique")).reset_index()
                    fy_raw["Rev_per_Cust"] = fy_raw["Revenue"]/fy_raw["Customers"]
                    fig_fy = go.Figure()
                    fig_fy.add_bar(x=fy_raw[fiscal_col], y=fy_raw["Revenue"], name="Revenue", marker_color=BRAND_BLUE, opacity=0.8)
                    fig_fy.add_scatter(x=fy_raw[fiscal_col], y=fy_raw["Revenue"], mode="lines+markers", name="Trend",
                                       line=dict(color="#E8611A",width=2), marker=dict(size=5,color="#E8611A"))
                    ly = base_layout("Revenue by Fiscal Year"); ly["xaxis"]=LIGHT_AXIS; ly["yaxis"]=LIGHT_AXIS
                    fig_fy.update_layout(**ly); st.plotly_chart(fig_fy, use_container_width=True)

                    c1,c2 = st.columns(2)
                    with c1:
                        fig2 = px.bar(fy_raw, x=fiscal_col, y="Customers", color_discrete_sequence=["#00897B"])
                        ly2  = base_layout("Unique Customers by Fiscal Year"); ly2["xaxis"]=LIGHT_AXIS; ly2["yaxis"]=LIGHT_AXIS
                        fig2.update_layout(**ly2); st.plotly_chart(fig2, use_container_width=True)
                    with c2:
                        fig3 = px.bar(fy_raw, x=fiscal_col, y="Rev_per_Cust", color_discrete_sequence=["#F4A900"])
                        ly3  = base_layout("Revenue per Customer by Fiscal Year"); ly3["xaxis"]=LIGHT_AXIS; ly3["yaxis"]=LIGHT_AXIS
                        fig3.update_layout(**ly3); st.plotly_chart(fig3, use_container_width=True)

                    # Segmentation by fiscal year (stacked bar)
                    st.markdown('<div class="section-hdr">Customer Segmentation by Fiscal Year</div>', unsafe_allow_html=True)
                    seg_fy = df_used.copy()
                    # Rank customers within each fiscal year
                    seg_fy["FY_Rank"] = seg_fy.groupby(fiscal_col)[metric].rank(method="dense", ascending=False)
                    seg_fy["FY_Max"]  = seg_fy.groupby(fiscal_col)[metric].transform("count")
                    seg_fy["Pct"]     = seg_fy["FY_Rank"] / seg_fy["FY_Max"]
                    seg_fy["Segment"] = pd.cut(seg_fy["Pct"], bins=[0,.05,.1,.2,1],
                                               labels=["Top 5%","Top 10%","Top 20%","Long Tail"])
                    seg_agg = seg_fy.groupby([fiscal_col,"Segment"])[metric].sum().reset_index()
                    fig_seg = px.bar(seg_agg, x=fiscal_col, y=metric, color="Segment",
                                     barmode="stack",
                                     color_discrete_map={"Top 5%":BRAND_BLUE,"Top 10%":"#E8611A",
                                                         "Top 20%":"#00897B","Long Tail":"#CBD5E1"})
                    ly_seg = base_layout("Revenue by Segment × Fiscal Year"); ly_seg["xaxis"]=LIGHT_AXIS; ly_seg["yaxis"]=LIGHT_AXIS
                    fig_seg.update_layout(**ly_seg); st.plotly_chart(fig_seg, use_container_width=True)

                elif fiscal_col == "None" and customer_col != "None":
                    # No fiscal col — overall segmentation only
                    seg = df_used.groupby(customer_col)[metric].sum().reset_index()
                    seg["Rank"]    = seg[metric].rank(method="dense", ascending=False)
                    seg["Pct"]     = seg["Rank"]/seg["Rank"].max()
                    seg["Segment"] = pd.cut(seg["Pct"],bins=[0,.05,.1,.2,1],labels=["Top 5%","Top 10%","Top 20%","Long Tail"])
                    pie = seg.groupby("Segment")[metric].sum().reset_index()
                    fig4 = px.pie(pie, names="Segment", values=metric,
                                  color_discrete_sequence=[BRAND_BLUE,"#E8611A","#00897B","#CBD5E1"])
                    ly4 = base_layout("Customer Segmentation"); fig4.update_layout(**ly4)
                    st.plotly_chart(fig4, use_container_width=True)

            with tab2:
                if customer_col!="None" and date_col!="None":
                    try:
                        hdf = st.session_state.validated_df.copy()
                        hdf[date_col] = pd.to_datetime(hdf[date_col])
                        hdf["OrderMonth"]  = hdf[date_col].dt.to_period("M").astype(str)
                        cmap = hdf.groupby(customer_col)["OrderMonth"].min()
                        hdf["CohortMonth"] = hdf[customer_col].map(cmap)
                        hdf["CohortIndex"] = (pd.to_datetime(hdf["OrderMonth"])-pd.to_datetime(hdf["CohortMonth"])).dt.days//30
                        pivot = pd.pivot_table(hdf, values=customer_col, index="CohortMonth", columns="CohortIndex", aggfunc="nunique").fillna(0)
                        # Replace zeros with NaN so cells show blank (colour only, no zero clutter)
                        pivot_display = pivot.replace(0, np.nan)
                        fig_h = px.imshow(pivot_display, text_auto=False, color_continuous_scale="Blues", aspect="auto")
                        fig_h.update_traces(text=None)
                        ly_h  = base_layout("Cohort Heatmap — Customer Count", height=420)
                        ly_h["xaxis"] = dict(**LIGHT_AXIS, title="Month Index")
                        ly_h["yaxis"] = dict(**LIGHT_AXIS, title="Cohort Month")
                        fig_h.update_layout(**ly_h); st.plotly_chart(fig_h, use_container_width=True)

                        # Retention % — zeros become NaN (blank), colour only
                        ret = pivot.divide(pivot.iloc[:,0], axis=0)*100
                        ret_display = ret.replace(0, np.nan)
                        fig_r = px.imshow(ret_display, text_auto=False, color_continuous_scale="RdYlGn",
                                          zmin=0, zmax=100, aspect="auto")
                        fig_r.update_traces(text=None)
                        ly_r  = base_layout("Retention % by Cohort", height=420)
                        ly_r["xaxis"] = dict(**LIGHT_AXIS, title="Month Index")
                        ly_r["yaxis"] = dict(**LIGHT_AXIS, title="Cohort Month")
                        fig_r.update_layout(**ly_r); st.plotly_chart(fig_r, use_container_width=True)
                    except Exception as e:
                        st.warning(f"Cohort heatmap error: {e}")
                else:
                    st.info("Map Customer and Date columns to see the cohort heatmap.")

            with tab3:
                st.markdown(f'<div class="section-hdr">{len(result):,} rows · {len(cohort_cols)} cohort columns</div>', unsafe_allow_html=True)
                st.dataframe(result, use_container_width=True, height=420)
                csv_out = result.to_csv(index=False)
                is_admin = st.session_state.user_email.lower() == ADMIN_EMAIL.lower()
                if is_admin:
                    st.download_button("⬇  Download Output", csv_out, "cohort_output.csv", use_container_width=True)
                else:
                    st.download_button("⬇  Download Output", csv_out, disabled=True, use_container_width=True)
                    st.warning("🔒 Download available for subscribed users. Subscribe for $25/year.")
        else:
            st.markdown('<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:80px 40px;text-align:center;"><div style="font-size:48px;margin-bottom:16px;">📊</div><div style="font-size:18px;font-weight:600;color:#1A1D23;margin-bottom:8px;">Upload your dataset to begin</div><div style="font-size:13px;color:#8C95A6;">Map columns on the left, then configure and run cohort analysis</div></div>', unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════
    # CUSTOMER ANALYTICS
    # ══════════════════════════════════════════════════════════════════════
    elif module == "Customer Analytics":
        master = st.session_state.result
        has_bridge = (master is not None and isinstance(master, pd.DataFrame) and "Bridge" in master.columns)

        if has_bridge:
            m            = st.session_state.mapping
            metric       = m["metric"]
            customer_col = m["customer_col"]
            date_col     = m["date_col"]
            region_col   = m["region_col"]
            lookbacks    = st.session_state.lookbacks
            is_admin     = st.session_state.user_email.lower() == ADMIN_EMAIL.lower()

            # ── Filters row ─────────────────────────────────────────────
            fc1, fc2 = st.columns([1,1])
            with fc1:
                sel_lb = st.selectbox("Lookback Window", lookbacks,
                                      format_func=lambda x: f"{x} Month{'s' if x>1 else ''}")
            with fc2:
                # Year filter from the date column
                available_years = sorted(master[date_col].dt.year.unique())
                year_options    = ["All"] + [str(y) for y in available_years]
                sel_year = st.selectbox("Year Filter", year_options)

            metrics = compute_retention(master, metric, sel_lb)
            df_lb   = master[master["Lookback"]==sel_lb].copy()
            if sel_year != "All":
                df_lb = df_lb[df_lb[date_col].dt.year == int(sel_year)]

            # ── KPI cards ───────────────────────────────────────────────
            kpi_items = [
                ("Total ARR",       fmt_currency(metrics["Ending ARR"]),   "accent"),
                ("New ARR",         fmt_currency(metrics["New ARR"]),       ""),
                ("Lost ARR",        fmt_currency(metrics["Lost ARR"]),      ""),
                ("Net Retention",   f"{metrics['NRR']}%",                   ""),
                ("Gross Retention", f"{metrics['GRR']}%",                   ""),
                ("Beginning ARR",   fmt_currency(metrics["Beginning ARR"]), ""),
            ]
            kpi_cols = st.columns(6)
            for col_obj, (label, val, style) in zip(kpi_cols, kpi_items):
                card_cls = "metric-card-accent" if style=="accent" else "metric-card"
                with col_obj:
                    st.markdown(f'<div class="{card_cls}"><div class="metric-label">{label}</div><div class="metric-value" style="font-size:17px;">{val}</div></div>', unsafe_allow_html=True)

            st.markdown("")

            tab1, tab2, tab3, tab4, tab5 = st.tabs(
                ["Revenue Bridge","Top Customers","Retention Trends","Bridge Table","Output"])

            # ── Tab 1: Revenue Bridge chart ──────────────────────────────
            with tab1:
                ba = df_lb.groupby("Bridge")["Bridge_Value"].sum().reset_index()
                ba = ba[ba["Bridge"]!="No Change"].copy()
                ba["Color"] = ba["Bridge"].map(BRIDGE_COLORS).fillna("#CBD5E1")
                ba = ba.sort_values("Bridge_Value", ascending=False)
                fig_b = go.Figure(go.Bar(
                    x=ba["Bridge"], y=ba["Bridge_Value"],
                    marker_color=ba["Color"].tolist(),
                    text=[fmt_currency(v) for v in ba["Bridge_Value"]],
                    textposition="outside", textfont=dict(color="#5A6478",size=11),
                ))
                ly_b = base_layout(f"Revenue Bridge — {sel_lb}M Lookback{' · ' + sel_year if sel_year!='All' else ''}")
                ly_b["xaxis"] = LIGHT_AXIS; ly_b["yaxis"] = LIGHT_AXIS
                fig_b.update_layout(**ly_b); st.plotly_chart(fig_b, use_container_width=True)

                # Bridge over time
                if date_col in df_lb.columns:
                    bp = df_lb.groupby([date_col,"Bridge"])["Bridge_Value"].sum().reset_index()
                    bp = bp[bp["Bridge"]!="No Change"]
                    top6 = bp.groupby("Bridge")["Bridge_Value"].sum().abs().nlargest(6).index
                    bp   = bp[bp["Bridge"].isin(top6)]
                    fig_bp = px.bar(bp, x=date_col, y="Bridge_Value", color="Bridge",
                                    color_discrete_map=BRIDGE_COLORS, barmode="relative")
                    ly_bp  = base_layout("Revenue Movement Over Time"); ly_bp["xaxis"]=LIGHT_AXIS; ly_bp["yaxis"]=LIGHT_AXIS
                    fig_bp.update_layout(**ly_bp); st.plotly_chart(fig_bp, use_container_width=True)

                if "Price_Impact" in df_lb.columns:
                    pv = {"Price Impact":df_lb["Price_Impact"].fillna(0).sum(),
                          "Volume Impact":df_lb["Volume_Impact"].fillna(0).sum(),
                          "Mix / Other":df_lb["PV_Misc"].fillna(0).sum()}
                    pv_df = pd.DataFrame({"Driver":list(pv.keys()),"Value":list(pv.values())})
                    fig_pv = px.bar(pv_df, x="Driver", y="Value", color="Driver",
                                    color_discrete_sequence=[BRAND_BLUE,"#00897B","#F4A900"])
                    ly_pv  = base_layout("Price vs Volume Decomposition"); ly_pv["xaxis"]=LIGHT_AXIS; ly_pv["yaxis"]=LIGHT_AXIS
                    fig_pv.update_layout(**ly_pv); st.plotly_chart(fig_pv, use_container_width=True)

            # ── Tab 2: Top Customers ─────────────────────────────────────
            with tab2:
                top_df = (df_lb.groupby(customer_col)
                          .agg(Ending_ARR=(metric,"sum"), ARR_Change=("Bridge_Value","sum"))
                          .reset_index().sort_values("Ending_ARR",ascending=False).head(20))
                top10  = top_df.head(10).sort_values("Ending_ARR")
                fig_top = go.Figure(go.Bar(
                    x=top10["Ending_ARR"], y=top10[customer_col], orientation="h",
                    marker_color=BRAND_BLUE,
                    text=[fmt_currency(v) for v in top10["Ending_ARR"]],
                    textposition="outside", textfont=dict(color="#5A6478",size=11),
                ))
                ly_top = base_layout("Top 10 Customers by ARR", height=380)
                ly_top["xaxis"]=LIGHT_AXIS; ly_top["yaxis"]=LIGHT_AXIS_REV
                fig_top.update_layout(**ly_top); st.plotly_chart(fig_top, use_container_width=True)

                mover = df_lb.groupby(customer_col)["Bridge_Value"].sum().reset_index()
                cu, cd = st.columns(2)
                with cu:
                    ups = mover[mover["Bridge_Value"]>0].sort_values("Bridge_Value",ascending=False).head(10).sort_values("Bridge_Value")
                    fig_u = go.Figure(go.Bar(x=ups["Bridge_Value"],y=ups[customer_col],orientation="h",marker_color="#16A34A",text=[fmt_currency(v) for v in ups["Bridge_Value"]],textposition="outside",textfont=dict(color="#5A6478",size=10)))
                    ly_u  = base_layout("Top Upsell Movers",height=320); ly_u["xaxis"]=LIGHT_AXIS; ly_u["yaxis"]=LIGHT_AXIS_REV
                    fig_u.update_layout(**ly_u); st.plotly_chart(fig_u, use_container_width=True)
                with cd:
                    dwn = mover[mover["Bridge_Value"]<0].sort_values("Bridge_Value").head(10).sort_values("Bridge_Value",ascending=False)
                    fig_d = go.Figure(go.Bar(x=dwn["Bridge_Value"],y=dwn[customer_col],orientation="h",marker_color="#EF4444",text=[fmt_currency(v) for v in dwn["Bridge_Value"]],textposition="outside",textfont=dict(color="#5A6478",size=10)))
                    ly_d  = base_layout("Top Churn / Contraction",height=320); ly_d["xaxis"]=LIGHT_AXIS; ly_d["yaxis"]=LIGHT_AXIS_REV
                    fig_d.update_layout(**ly_d); st.plotly_chart(fig_d, use_container_width=True)

                if region_col and region_col!="None" and region_col in df_lb.columns:
                    reg = df_lb.groupby(region_col)[metric].sum().reset_index().sort_values(metric)
                    fig_reg = go.Figure(go.Bar(x=reg[metric],y=reg[region_col],orientation="h",marker_color="#8E24AA",text=[fmt_currency(v) for v in reg[metric]],textposition="outside",textfont=dict(color="#5A6478",size=10)))
                    ly_reg  = base_layout("ARR by Geography",height=320); ly_reg["xaxis"]=LIGHT_AXIS; ly_reg["yaxis"]=LIGHT_AXIS_REV
                    fig_reg.update_layout(**ly_reg); st.plotly_chart(fig_reg, use_container_width=True)

                top_df["Ending ARR"] = top_df["Ending_ARR"].apply(fmt_currency)
                top_df["ARR Change"] = top_df["ARR_Change"].apply(fmt_currency)
                st.dataframe(top_df[[customer_col,"Ending ARR","ARR Change"]], use_container_width=True)

            # ── Tab 3: Retention Trends ──────────────────────────────────
            with tab3:
                nrr_rows = []
                for lb in lookbacks:
                    df_t = master[master["Lookback"]==lb]
                    if date_col not in df_t.columns: continue
                    if sel_year != "All":
                        df_t = df_t[df_t[date_col].dt.year==int(sel_year)]
                    for period, grp in df_t.groupby(date_col):
                        beg = grp["Beginning_ARR"].sum()
                        if beg<=0: continue
                        ch = grp.loc[grp["Bridge"].isin(["Churn","Partial Churn"]),"Bridge_Value"].sum()
                        dw = grp.loc[grp["Bridge"]=="Downsell","Bridge_Value"].sum()
                        up = grp.loc[grp["Bridge"]=="Upsell","Bridge_Value"].sum()
                        cr = grp.loc[grp["Bridge"]=="Cross Sell","Bridge_Value"].sum()
                        nrr_rows.append({"Period":period,"Lookback":f"{lb}M",
                                         "NRR":(beg+up+cr+ch+dw)/beg*100,
                                         "GRR":(beg+ch+dw)/beg*100})
                if nrr_rows:
                    nrr_df  = pd.DataFrame(nrr_rows)
                    fig_nrr = px.line(nrr_df, x="Period", y="NRR", color="Lookback", color_discrete_sequence=BRAND_COLORS)
                    fig_nrr.add_hline(y=100, line_dash="dot", line_color="#8C95A6", annotation_text="100%", annotation_font_color="#8C95A6")
                    ly_nrr  = base_layout("Net Revenue Retention % Over Time"); ly_nrr["xaxis"]=LIGHT_AXIS; ly_nrr["yaxis"]=LIGHT_AXIS
                    fig_nrr.update_layout(**ly_nrr); st.plotly_chart(fig_nrr, use_container_width=True)
                    fig_grr = px.line(nrr_df, x="Period", y="GRR", color="Lookback", color_discrete_sequence=["#EF4444","#F97316","#F59E0B"])
                    ly_grr  = base_layout("Gross Revenue Retention % Over Time"); ly_grr["xaxis"]=LIGHT_AXIS; ly_grr["yaxis"]=LIGHT_AXIS
                    fig_grr.update_layout(**ly_grr); st.plotly_chart(fig_grr, use_container_width=True)
                if "Vintage" in df_lb.columns:
                    vin    = df_lb.groupby("Vintage")[metric].sum().reset_index()
                    fig_v  = px.bar(vin, x="Vintage", y=metric, color_discrete_sequence=[BRAND_BLUE])
                    ly_v   = base_layout("ARR by Customer Vintage (Cohort Year)"); ly_v["xaxis"]=LIGHT_AXIS; ly_v["yaxis"]=LIGHT_AXIS
                    fig_v.update_layout(**ly_v); st.plotly_chart(fig_v, use_container_width=True)

            # ── Tab 4: Bridge Table (Alteryx-style waterfall) ────────────
            with tab4:
                st.markdown(f'<div class="section-hdr">ARR Waterfall Table — {sel_lb}M Lookback{" · " + sel_year if sel_year!="All" else ""}</div>', unsafe_allow_html=True)
                st.markdown("""
                <div style="font-size:12px;color:#5A6478;margin-bottom:12px;line-height:1.5;">
                  Rows = Bridge Classification &nbsp;|&nbsp; Columns = Date period &nbsp;|&nbsp;
                  Values = ARR bridge value (Beginning → movements → Ending).
                  This matches the Alteryx Cross Tab output with Bridge Classification × Date.
                </div>""", unsafe_allow_html=True)

                wtab = make_arr_waterfall_table(master, metric, date_col, sel_lb, sel_year)
                if not wtab.empty:
                    # Style the table: green for positive rows, red for negative
                    def style_bridge_row(row):
                        bridge = row.name
                        if bridge in ["Beginning MRR or ARR","Ending MRR or ARR"]:
                            return ["background-color:#EFF6FF;font-weight:700;color:#1E3A5F"]*len(row)
                        elif bridge in ["New Logo","Cross Sell","Other In","Returning","Upsell"]:
                            return ["background-color:#F0FDF4;color:#15803D"]*len(row)
                        elif bridge in ["Churn","Partial Churn","Downsell","Lapsed"]:
                            return ["background-color:#FEF2F2;color:#B91C1C"]*len(row)
                        return [""]*len(row)

                    # Format numbers
                    def fmt_val(v):
                        if v==0: return "—"
                        return f"{v:,.0f}"

                    display_wtab = wtab.copy()
                    for c in display_wtab.columns:
                        display_wtab[c] = display_wtab[c].apply(fmt_val)

                    styled = display_wtab.style.apply(style_bridge_row, axis=1)
                    st.dataframe(styled, use_container_width=True, height=420)

                    # Also show customer-level bridge detail below
                    st.markdown('<div class="section-hdr" style="margin-top:24px;">Customer-Level Bridge Detail</div>', unsafe_allow_html=True)
                    cust_bridge = make_customer_bridge_table(master, metric, date_col, customer_col, sel_lb, sel_year)
                    if not cust_bridge.empty:
                        # Format currency columns
                        for col_name in ["Bridge Value","Ending ARR","Beginning ARR"]:
                            if col_name in cust_bridge.columns:
                                cust_bridge[col_name] = cust_bridge[col_name].apply(fmt_currency)
                        st.dataframe(cust_bridge, use_container_width=True, height=360)
                else:
                    st.info("No bridge data available for the selected filters.")

            # ── Tab 5: Output (Alteryx-matching schema) ─────────────────
            with tab5:
                is_admin = st.session_state.user_email.lower() == ADMIN_EMAIL.lower()
                m_out    = st.session_state.mapping

                # ── Build the Alteryx-matching output table ──────────────
                # Schema: Customer, Product, Channel, Region, Vintage, Date,
                #         MRR or ARR, Quantity, Month Lookback, DTE,
                #         Lookback Date, Bridge Classification, Bridge Value
                keep_cols_map = {
                    m_out["customer_col"]:  "Customer",
                }
                if m_out["product_col"] != "None":   keep_cols_map[m_out["product_col"]] = "Product"
                if m_out["channel_col"] != "None":   keep_cols_map[m_out["channel_col"]] = "Channel"
                if m_out["region_col"]  != "None":   keep_cols_map[m_out["region_col"]]  = "Region"

                # Columns from the engine — map source name → display name
                # Note: engine produces "Lookback Date" (with space), not "Lookback_Date"
                engine_cols = {
                    "Vintage":              "Vintage",
                    m_out["date_col"]:      "Date",
                    m_out["metric"]:        "MRR or ARR",
                    "Lookback":             "Month Lookback",
                    "DTE":                  "DTE",
                    "Lookback Date":        "Lookback Date",
                    "Bridge Classification":"Bridge Classification",
                    "Bridge Value":         "Bridge Value",
                    "Beginning MRR or ARR": "Beginning MRR or ARR",
                    "Ending MRR or ARR":    "Ending MRR or ARR",
                }
                if m_out["qty_col"] != "None":
                    engine_cols[m_out["qty_col"]] = "Quantity"

                all_map = {**keep_cols_map, **engine_cols}

                # ── Build output: dim cols + engine cols (NO separate Beg/End cols) ──
                # Beginning MRR or ARR and Ending MRR or ARR appear ONLY as rows
                # in Bridge Classification column, not as separate columns.

                avail     = {k: v for k, v in all_map.items() if k in master.columns}
                src = master.copy()
                if sel_year != "All":
                    src = src[src[m_out["date_col"]].dt.year == int(sel_year)]

                # ── Dim cols available in master ───────────────────────
                dim_avail = {k: v for k, v in all_map.items() if k in src.columns}
                dim_keys  = list(dim_avail.keys())

                # ── Movement rows (New Logo, Upsell, Churn etc.) ─────────
                move_df = src[dim_keys].copy().rename(columns=dim_avail).reset_index(drop=True)
                move_df = move_df[move_df["Bridge Classification"] != "No Change"]
                move_df = move_df[~move_df["Bridge Classification"].isin(
                    ["Beginning MRR or ARR", "Ending MRR or ARR"])]

                # ── Beginning MRR or ARR rows ─────────────────────────────
                # Each row where Beginning_ARR > 0 gets a "Beginning MRR or ARR" bridge row.
                # Bridge Value = the Beginning ARR amount for that row.
                beg_src = src[src["Beginning_ARR"] > 0].copy().reset_index(drop=True)
                if not beg_src.empty:
                    beg_df = beg_src[dim_keys].copy().rename(columns=dim_avail).reset_index(drop=True)
                    beg_df["Bridge Classification"] = "Beginning MRR or ARR"
                    beg_df["Bridge Value"]          = beg_src["Beginning_ARR"].values
                else:
                    beg_df = pd.DataFrame(columns=move_df.columns)

                # ── Ending MRR or ARR rows ──────────────────────────────
                # Each row where Ending_ARR > 0 gets an "Ending MRR or ARR" bridge row.
                end_src = src[src["Ending_ARR"] > 0].copy().reset_index(drop=True)
                if not end_src.empty:
                    end_df = end_src[dim_keys].copy().rename(columns=dim_avail).reset_index(drop=True)
                    end_df["Bridge Classification"] = "Ending MRR or ARR"
                    end_df["Bridge Value"]          = end_src["Ending_ARR"].values
                else:
                    end_df = pd.DataFrame(columns=move_df.columns)

                # ── Align all three frames to same columns ────────────────
                final_cols = list(move_df.columns)
                for df_part in [beg_df, end_df]:
                    for c in final_cols:
                        if c not in df_part.columns:
                            df_part[c] = None

                out_df = pd.concat(
                    [beg_df[final_cols], move_df[final_cols], end_df[final_cols]],
                    ignore_index=True
                )

                # Sort: Customer → Date → Month Lookback → bridge order
                bridge_sort_order = {
                    "Beginning MRR or ARR": 0,
                    "New Logo": 1, "Cross Sell": 2, "Other In": 3, "Returning": 4,
                    "Upsell": 5, "Downsell": 6, "Churn": 7, "Partial Churn": 8,
                    "Lapsed": 9, "Ending MRR or ARR": 10,
                }
                out_df["_sort"] = out_df["Bridge Classification"].map(bridge_sort_order).fillna(5)
                sort_cols = [c for c in ["Customer","Date","Month Lookback","_sort"] if c in out_df.columns]
                if sort_cols:
                    out_df = out_df.sort_values(sort_cols).drop(columns=["_sort"])

                total_rows = len(out_df)
                st.markdown(
                    f'<div class="section-hdr">{total_rows:,} rows · Lookback {sel_lb}M{" · " + sel_year if sel_year != "All" else ""} · Beginning & Ending ARR as bridge rows</div>',
                    unsafe_allow_html=True)

                st.markdown("""
                <div style="font-size:12px;color:#5A6478;margin-bottom:10px;line-height:1.5;">
                  Schema matches Alteryx output — <strong>Beginning MRR or ARR</strong> and
                  <strong>Ending MRR or ARR</strong> appear as rows in Bridge Classification,
                  not as separate columns.
                </div>""", unsafe_allow_html=True)

                # Plain st.dataframe — no Styler (avoids StreamlitAPIException in newer versions)
                st.dataframe(out_df, use_container_width=True, height=460)

                csv_out = out_df.to_csv(index=False)
                if is_admin:
                    c_dl1, c_dl2 = st.columns(2)
                    with c_dl1:
                        st.download_button("⬇  Download CSV (Alteryx format)",
                                           csv_out, "arr_bridge_output.csv",
                                           use_container_width=True)
                    with c_dl2:
                        # Excel with 3 sheets: master output, waterfall, customer detail
                        wtab_dl = make_arr_waterfall_table(master, metric, date_col, sel_lb, sel_year)
                        cust_dl = make_customer_bridge_table(master, metric, date_col, customer_col, sel_lb, sel_year)
                        buf = io.BytesIO()
                        with pd.ExcelWriter(buf, engine="openpyxl") as writer:
                            out_df.to_excel(writer, sheet_name="Bridge Output", index=False)
                            if not wtab_dl.empty:
                                wtab_dl.to_excel(writer, sheet_name="ARR Waterfall")
                            if not cust_dl.empty:
                                cust_dl.to_excel(writer, sheet_name="Customer Detail", index=False)
                        buf.seek(0)
                        st.download_button("⬇  Download Excel (3 sheets)",
                                           buf.getvalue(), "arr_bridge_output.xlsx",
                                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                           use_container_width=True)
                else:
                    st.download_button("⬇  Download Output", csv_out, disabled=True, use_container_width=True)
                    st.warning("🔒 Download available for subscribed users. Subscribe for $25/year.")

        elif st.session_state.validated_df is None:
            st.markdown('<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:80px 40px;text-align:center;"><div style="font-size:48px;margin-bottom:16px;">📈</div><div style="font-size:18px;font-weight:600;color:#1A1D23;margin-bottom:8px;">Upload your dataset to begin</div><div style="font-size:13px;color:#8C95A6;">Map columns and click Validate Data</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="display:flex;flex-direction:column;align-items:center;justify-content:center;padding:60px 40px;text-align:center;"><div style="font-size:40px;margin-bottom:16px;">⚡</div><div style="font-size:18px;font-weight:600;color:#1A1D23;margin-bottom:8px;">Ready to run</div><div style="font-size:13px;color:#8C95A6;">Select lookback windows and click Run Customer Analytics</div></div>', unsafe_allow_html=True)
