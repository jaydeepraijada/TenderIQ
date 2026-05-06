CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ── Font ──────────────────────────────────────────────────── */
html, body, [class*="css"], .stMarkdown, .stText, button, input, select {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ── Page chrome ───────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.main .block-container { max-width: 1140px; padding-top: 1.2rem !important; }

/* ── Sidebar ───────────────────────────────────────────────── */
section[data-testid="stSidebar"] > div:first-child {
    background: #0A1628 !important;
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span:not(.st-emotion-cache-hidden),
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] label { color: #CBD5E1 !important; }
[data-testid="stSidebar"] strong  { color: #F1F5F9 !important; }
[data-testid="stSidebar"] hr     { border-color: rgba(255,255,255,0.1) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #CBD5E1 !important;
    transition: background 0.15s;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.13) !important;
    color: #fff !important;
}
[data-testid="stSidebar"] .stAlert { border-radius: 8px !important; }

/* ── Tabs ──────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #F0F4F8;
    padding: 4px;
    border-radius: 10px;
    gap: 2px;
    border: 1px solid #E2E8F0;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 7px !important;
    padding: 7px 16px !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #64748B !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: #FFFFFF !important;
    color: #0D1B2A !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.1) !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ── Buttons ───────────────────────────────────────────────── */
.stButton > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    transition: all 0.18s ease !important;
    letter-spacing: 0.01em;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1E40AF, #2563EB) !important;
    border: none !important;
    color: #fff !important;
    box-shadow: 0 2px 8px rgba(37,99,235,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 4px 16px rgba(37,99,235,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ── Metrics ───────────────────────────────────────────────── */
[data-testid="metric-container"] {
    background: #fff !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 18px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
}
[data-testid="stMetricValue"] { font-size: 2rem !important; font-weight: 800 !important; }
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; font-weight: 600 !important;
    text-transform: uppercase; letter-spacing: 0.07em; color: #64748B !important; }

/* ── Bordered containers ───────────────────────────────────── */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 12px !important;
    border-color: #E2E8F0 !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}

/* ── Expanders ─────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary { font-weight: 500 !important; font-size: 0.875rem !important; }

/* ── Alerts ────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Progress ──────────────────────────────────────────────── */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #1E40AF, #2563EB) !important;
    border-radius: 6px !important;
}

/* ── Inputs ────────────────────────────────────────────────── */
[data-baseweb="input"] > div,
[data-baseweb="select"] > div:first-child {
    border-radius: 8px !important;
    border-color: #E2E8F0 !important;
}
</style>
"""
