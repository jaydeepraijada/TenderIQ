CSS = """
<style>
/* ================================================================
   TenderIQ — Professional Theme
   ================================================================ */

/* ── Global ──────────────────────────────────────────────────── */
.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
    max-width: 1200px;
}
h1 { font-weight: 800 !important; color: #0D1B2A !important; letter-spacing: -0.02em; }
h2 { font-weight: 700 !important; color: #0D1B2A !important; }
h3 { font-weight: 600 !important; color: #0D1B2A !important; }
h4 { font-weight: 600 !important; color: #1E3A5F !important; }
p  { color: #374151; line-height: 1.7; }
code {
    background: #EFF6FF !important;
    color: #1E40AF !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
    font-size: 0.85em !important;
    border: 1px solid #DBEAFE;
}
hr { border-color: #E2E8F0 !important; margin: 1.25rem 0 !important; }

/* ── Sidebar ─────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #0D1B2A 0%, #1E3A5F 100%) !important;
    border-right: 1px solid #1E3A5F;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div {
    color: #CBD5E1 !important;
}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] strong {
    color: #F1F5F9 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    color: #E2E8F0 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    width: 100%;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.14) !important;
    border-color: rgba(255,255,255,0.3) !important;
    color: #FFFFFF !important;
}
[data-testid="stSidebar"] [data-testid="stDivider"] { border-color: rgba(255,255,255,0.12) !important; }
[data-testid="stSidebar"] .stAlert {
    background: rgba(245,158,11,0.15) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 8px !important;
}
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color: #94A3B8 !important; }

/* ── Tabs ────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #F1F5F9 !important;
    border-radius: 12px !important;
    padding: 5px !important;
    gap: 2px !important;
    border: 1px solid #E2E8F0;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    padding: 8px 18px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    color: #64748B !important;
    border: none !important;
    background: transparent !important;
    transition: all 0.15s ease !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #1E3A5F !important; background: rgba(255,255,255,0.6) !important; }
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #0D1B2A !important;
    box-shadow: 0 1px 6px rgba(0,0,0,0.1) !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"] { display: none !important; }
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Buttons ─────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    transition: all 0.2s ease !important;
    border: 1px solid #E2E8F0 !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1E3A5F 0%, #2563EB 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 16px rgba(37,99,235,0.45) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"] { color: #374151 !important; }
.stButton > button[kind="secondary"]:hover { background: #F1F5F9 !important; }

/* ── Metric cards ────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 20px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
    transition: box-shadow 0.2s, transform 0.2s;
}
[data-testid="metric-container"]:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.1) !important;
    transform: translateY(-1px);
}
[data-testid="stMetricValue"] { font-size: 2.2rem !important; font-weight: 800 !important; color: #0D1B2A !important; }
[data-testid="stMetricLabel"] { font-size: 0.75rem !important; font-weight: 600 !important; color: #64748B !important; text-transform: uppercase; letter-spacing: 0.06em; }
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* ── Bordered containers (cards) ─────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    overflow: hidden;
    transition: box-shadow 0.2s;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    box-shadow: 0 4px 16px rgba(0,0,0,0.09) !important;
}

/* ── Expanders ───────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    overflow: hidden !important;
    margin-bottom: 4px !important;
}
[data-testid="stExpander"] summary {
    font-weight: 500 !important;
    color: #374151 !important;
    padding: 10px 14px !important;
    background: #F8FAFC;
}
[data-testid="stExpander"] summary:hover { background: #F1F5F9 !important; }

/* ── Alerts ──────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; border: none !important; }
div[data-testid="stAlert"][data-baseweb="notification"][kind="info"] {
    background: #EFF6FF !important; border-left: 4px solid #3B82F6 !important;
}
div[data-testid="stAlert"][data-baseweb="notification"][kind="success"] {
    background: #F0FDF4 !important; border-left: 4px solid #22C55E !important;
}
div[data-testid="stAlert"][data-baseweb="notification"][kind="warning"] {
    background: #FFFBEB !important; border-left: 4px solid #F59E0B !important;
}
div[data-testid="stAlert"][data-baseweb="notification"][kind="error"] {
    background: #FEF2F2 !important; border-left: 4px solid #EF4444 !important;
}

/* ── Progress bar ────────────────────────────────────────────── */
.stProgress > div > div > div { border-radius: 6px !important; }
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #1E3A5F, #2563EB) !important;
    border-radius: 6px !important;
}

/* ── Forms (inputs, selects) ─────────────────────────────────── */
[data-baseweb="input"],
[data-baseweb="select"],
[data-baseweb="textarea"] {
    border-radius: 8px !important;
    border-color: #E2E8F0 !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"]:focus-within {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
}

/* ── Dataframe ───────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #E2E8F0 !important;
}

/* ── Caption ─────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"] p { color: #94A3B8 !important; font-size: 0.8rem !important; }

/* ── Spinner ─────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: #2563EB !important; }

/* ── Hide Streamlit chrome ───────────────────────────────────── */
#MainMenu { visibility: hidden !important; }
footer    { visibility: hidden !important; }
header    { visibility: hidden !important; }

/* ── Verdict badge utility classes ───────────────────────────── */
.tiq-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 4px 12px; border-radius: 20px;
    font-size: 0.8rem; font-weight: 600; white-space: nowrap;
}
.tiq-eligible   { background:#D1FAE5; color:#065F46; border:1px solid #A7F3D0; }
.tiq-not-elig   { background:#FEE2E2; color:#991B1B; border:1px solid #FECACA; }
.tiq-review     { background:#FEF3C7; color:#92400E; border:1px solid #FDE68A; }
.tiq-cat-fin    { background:#DBEAFE; color:#1E40AF; border:1px solid #BFDBFE; }
.tiq-cat-tech   { background:#DCFCE7; color:#166534; border:1px solid #BBF7D0; }
.tiq-cat-comp   { background:#FEF3C7; color:#92400E; border:1px solid #FDE68A; }
.tiq-ocr-text   { background:#F1F5F9; color:#475569; border:1px solid #CBD5E1; }
.tiq-ocr-tess   { background:#FDF4FF; color:#7E22CE; border:1px solid #E9D5FF; }
.tiq-ocr-vision { background:#FFF7ED; color:#C2410C; border:1px solid #FED7AA; }
.tiq-mand       { background:#FEE2E2; color:#991B1B; border:1px solid #FECACA; }
.tiq-optional   { background:#FFFBEB; color:#92400E; border:1px solid #FDE68A; }

/* ── Hero banner ─────────────────────────────────────────────── */
.tiq-hero {
    background: linear-gradient(135deg, #0D1B2A 0%, #1E3A5F 50%, #2563EB 100%);
    border-radius: 16px; padding: 2.5rem 2rem; margin-bottom: 1.5rem;
    color: white;
}
.tiq-hero h1 { color: #FFFFFF !important; margin: 0; font-size: 2rem; }
.tiq-hero p  { color: #CBD5E1 !important; margin: 0.5rem 0 0; font-size: 1.05rem; }

/* ── Kpi strip ───────────────────────────────────────────────── */
.tiq-kpi {
    background: #FFFFFF; border-radius: 12px; padding: 18px 20px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    text-align: center;
}
.tiq-kpi-val { font-size: 2rem; font-weight: 800; color: #0D1B2A; }
.tiq-kpi-lbl { font-size: 0.72rem; font-weight: 600; color: #64748B;
               text-transform: uppercase; letter-spacing: 0.07em; margin-top: 2px; }

/* ── Section header ─────────────────────────────────────────── */
.tiq-section-header {
    border-left: 4px solid #2563EB; padding-left: 12px;
    margin: 1.5rem 0 1rem;
}
</style>
"""
