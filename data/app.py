"""
PanchayatConnect — V1.0
=======================
An independent civic-tech platform that makes Indian government
information (schemes, Panchayats, official updates) easier to discover.

Architecture
------------
1. Configuration & constants
2. Design system (CSS)
3. Reusable UI helpers
4. Session state
5. Sidebar (brand, navigation, location, language)
6. Pages (Dashboard, Directory, Schemes, Updates, Sources, About)
7. Footer

Author  : PanchayatConnect
License : Independent civic-tech project (not a government website)
"""

from __future__ import annotations

import html
import re
import time

import streamlit as st

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:  # graceful degradation
    FEEDPARSER_AVAILABLE = False


# ============================================================
# 1. PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="PanchayatConnect — Government Information, Simplified",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "1.0"
APP_YEAR = "2026"


# ============================================================
# 2. CONSTANTS & DATA
# ============================================================

NAV_ITEMS = [
    ("dashboard", "🏠"),
    ("directory", "🏘️"),
    ("schemes", "🔎"),
    ("updates", "📢"),
    ("sources", "🏛️"),
    ("about", "ℹ️"),
]

I18N = {
    "en": {
        "app_name": "PanchayatConnect",
        "tagline": "Government information, connected to your Panchayat.",
        "nav_dashboard": "Dashboard",
        "nav_directory": "Panchayat Directory",
        "nav_schemes": "Find Schemes",
        "nav_updates": "Government Updates",
        "nav_sources": "Official Sources",
        "nav_about": "About",
        "my_location": "My Location",
        "state": "State",
        "district": "District",
        "panchayat": "Panchayat",
        "language": "Language",
        "search": "Search",
        "category": "Category",
        "all": "All",
        "results": "Results",
        "official_source": "Official Source",
        "clear_filters": "Reset filters",
        "no_results": "No matching results found.",
        "type_here": "Type here…",
    },
    "kn": {
        "app_name": "ಪಂಚಾಯತ್ ಕನೆಕ್ಟ್",
        "tagline": "ಸರ್ಕಾರಿ ಮಾಹಿತಿ, ನಿಮ್ಮ ಪಂಚಾಯತ್‌ಗೆ ಸಂಪರ್ಕಿತ.",
        "nav_dashboard": "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "nav_directory": "ಪಂಚಾಯತ್ ಡೈರೆಕ್ಟರಿ",
        "nav_schemes": "ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಿ",
        "nav_updates": "ಸರ್ಕಾರಿ ನವೀಕರಣಗಳು",
        "nav_sources": "ಅಧಿಕೃತ ಮೂಲಗಳು",
        "nav_about": "ನಮ್ಮ ಬಗ್ಗೆ",
        "my_location": "ನನ್ನ ಸ್ಥಳ",
        "state": "ರಾಜ್ಯ",
        "district": "ಜಿಲ್ಲೆ",
        "panchayat": "ಪಂಚಾಯತ್",
        "language": "ಭಾಷೆ",
        "search": "ಹುಡುಕಿ",
        "category": "ವರ್ಗ",
        "all": "ಎಲ್ಲಾ",
        "results": "ಫಲಿತಾಂಶಗಳು",
        "official_source": "ಅಧಿಕೃತ ಮೂಲ",
        "clear_filters": "ಫಿಲ್ಟರ್ ತೆಗೆಯಿರಿ",
        "no_results": "ಯಾವುದೇ ಫಲಿತಾಂಶ ಸಿಗಲಿಲ್ಲ.",
        "type_here": "ಇಲ್ಲಿ ಟೈಪ್ ಮಾಡಿ…",
    },
}

STATES = [
    "Karnataka",
    "Kerala",
    "Tamil Nadu",
    "Maharashtra",
    "Telangana",
    "Andhra Pradesh",
    "Goa",
]

# --- Demo directory (prototype records — not live LGD data) ------------

PANCHAYATS = [
    {"state": "Karnataka", "district": "Hassan", "block": "Hassan",
     "name": "Example Gram Panchayat 1", "type": "Village Panchayat", "code": "DEMO-001"},
    {"state": "Karnataka", "district": "Hassan", "block": "Arkalgud",
     "name": "Example Gram Panchayat 2", "type": "Village Panchayat", "code": "DEMO-002"},
    {"state": "Karnataka", "district": "Hassan", "block": "Belur",
     "name": "Example Gram Panchayat 3", "type": "Village Panchayat", "code": "DEMO-003"},
    {"state": "Karnataka", "district": "Mysuru", "block": "Mysuru",
     "name": "Example Gram Panchayat 4", "type": "Village Panchayat", "code": "DEMO-004"},
    {"state": "Karnataka", "district": "Mysuru", "block": "Hunsur",
     "name": "Example Gram Panchayat 5", "type": "Village Panchayat", "code": "DEMO-005"},
    {"state": "Karnataka", "district": "Bengaluru Rural", "block": "Devanahalli",
     "name": "Example Gram Panchayat 6", "type": "Village Panchayat", "code": "DEMO-006"},
    {"state": "Karnataka", "district": "Bengaluru Rural", "block": "Doddaballapura",
     "name": "Example Gram Panchayat 7", "type": "Village Panchayat", "code": "DEMO-007"},
    {"state": "Karnataka", "district": "Tumakuru", "block": "Tumakuru",
     "name": "Example Gram Panchayat 8", "type": "Village Panchayat", "code": "DEMO-008"},
]

# --- Scheme repository -------------------------------------------------

SCHEMES = [
    {
        "name": "PM-KISAN",
        "full_name": "Pradhan Mantri Kisan Samman Nidhi",
        "category": "Agriculture",
        "level": "Central",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": (
            "Income support for eligible landholding farmer families, released in "
            "periodic instalments directly into the beneficiary's bank account."
        ),
        "keywords": ["farmer", "agriculture", "farm", "kisan", "income", "land", "crop"],
        "url": "https://pmkisan.gov.in/",
    },
    {
        "name": "Pradhan Mantri Fasal Bima Yojana",
        "full_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "category": "Agriculture",
        "level": "Central",
        "ministry": "Ministry of Agriculture & Farmers Welfare",
        "description": (
            "Crop insurance cover against yield losses arising from natural calamities, "
            "pests and diseases for notified crops and areas."
        ),
        "keywords": ["crop", "insurance", "farmer", "agriculture", "bima", "yield"],
        "url": "https://pmfby.gov.in/",
    },
    {
        "name": "MGNREGA",
        "full_name": "Mahatma Gandhi National Rural Employment Guarantee Act",
        "category": "Employment",
        "level": "Central",
        "ministry": "Ministry of Rural Development",
        "description": (
            "Guarantees a minimum number of days of unskilled wage employment in a "
            "financial year to rural households, subject to programme rules."
        ),
        "keywords": ["employment", "job", "work", "rural", "wages", "nrega", "labour"],
        "url": "https://nrega.nic.in/",
    },
    {
        "name": "e-Shram",
        "full_name": "e-Shram National Database of Unorganised Workers",
        "category": "Employment",
        "level": "Central",
        "ministry": "Ministry of Labour & Employment",
        "description": (
            "National registry for unorganised workers, linking them to social "
            "security benefits and welfare schemes."
        ),
        "keywords": ["worker", "labour", "unorganised", "shram", "registration", "employment"],
        "url": "https://eshram.gov.in/",
    },
    {
        "name": "PMAY-G",
        "full_name": "Pradhan Mantri Awaas Yojana — Gramin",
        "category": "Housing",
        "level": "Central",
        "ministry": "Ministry of Rural Development",
        "description": (
            "Assistance for construction of pucca houses for eligible rural "
            "households, including basic amenities support."
        ),
        "keywords": ["house", "housing", "home", "rural", "awas", "construction"],
        "url": "https://pmayg.nic.in/",
    },
    {
        "name": "Ayushman Bharat PM-JAY",
        "full_name": "Pradhan Mantri Jan Arogya Yojana",
        "category": "Health",
        "level": "Central",
        "ministry": "Ministry of Health & Family Welfare",
        "description": (
            "Health assurance cover for eligible families for secondary and tertiary "
            "care hospitalisation at empanelled hospitals."
        ),
        "keywords": ["health", "hospital", "insurance", "medical", "ayushman", "treatment"],
        "url": "https://pmjay.gov.in/",
    },
    {
        "name": "Pradhan Mantri Ujjwala Yojana",
        "full_name": "Pradhan Mantri Ujjwala Yojana (PMUY)",
        "category": "Welfare",
        "level": "Central",
        "ministry": "Ministry of Petroleum & Natural Gas",
        "description": (
            "Provides clean cooking fuel connections to eligible women from "
            "below-poverty-line households."
        ),
        "keywords": ["lpg", "gas", "women", "cooking", "ujjwala", "household"],
        "url": "https://www.pmuy.gov.in/",
    },
    {
        "name": "Sukanya Samriddhi Yojana",
        "full_name": "Sukanya Samriddhi Yojana (SSY)",
        "category": "Women & Child",
        "level": "Central",
        "ministry": "Ministry of Finance",
        "description": (
            "Small savings scheme for a girl child, offering attractive interest and "
            "tax benefits to encourage long-term savings for education and marriage."
        ),
        "keywords": ["girl", "child", "savings", "women", "sukanya", "education"],
        "url": "https://www.india.gov.in/spotlight/sukanya-samriddhi-yojana",
    },
    {
        "name": "Atal Pension Yojana",
        "full_name": "Atal Pension Yojana (APY)",
        "category": "Social Security",
        "level": "Central",
        "ministry": "Ministry of Finance",
        "description": (
            "Guaranteed minimum pension scheme for citizens in the unorganised "
            "sector, with government co-contribution for eligible subscribers."
        ),
        "keywords": ["pension", "retirement", "atal", "social security", "savings"],
        "url": "https://www.npscra.nsdl.co.in/scheme-details.php",
    },
    {
        "name": "Swachh Bharat Mission (Grameen)",
        "full_name": "Swachh Bharat Mission — Gramin, Phase II",
        "category": "Sanitation",
        "level": "Central",
        "ministry": "Ministry of Jal Shakti",
        "description": (
            "Focuses on sustaining open-defecation-free status and improving solid "
            "and liquid waste management in rural areas."
        ),
        "keywords": ["sanitation", "toilet", "swachh", "waste", "rural", "cleanliness"],
        "url": "https://swachhbharatmission.ddws.gov.in/",
    },
    {
        "name": "Digital India",
        "full_name": "Digital India Programme",
        "category": "Digital Services",
        "level": "Central",
        "ministry": "Ministry of Electronics & IT",
        "description": (
            "Umbrella programme for delivering government services digitally, "
            "expanding rural broadband and promoting digital literacy."
        ),
        "keywords": ["digital", "online", "service", "technology", "internet", "egovernance"],
        "url": "https://www.digitalindia.gov.in/",
    },
    {
        "name": "PM Vishwakarma",
        "full_name": "PM Vishwakarma Scheme",
        "category": "Skill Development",
        "level": "Central",
        "ministry": "Ministry of Micro, Small & Medium Enterprises",
        "description": (
            "End-to-end support to traditional artisans and craftspeople, including "
            "skill training, toolkit incentives and collateral-free credit."
        ),
        "keywords": ["artisan", "craft", "skill", "training", "loan", "vishwakarma"],
        "url": "https://pmvishwakarma.gov.in/",
    },
]

SCHEME_CATEGORIES = sorted({s["category"] for s in SCHEMES})

SOURCES = [
    {"icon": "🇮🇳", "name": "India.gov.in", "desc": "National Portal of India — single window to government services.",
     "url": "https://www.india.gov.in/", "group": "National"},
    {"icon": "📊", "name": "data.gov.in", "desc": "Open Government Data Platform of India.",
     "url": "https://data.gov.in/", "group": "National"},
    {"icon": "🏘️", "name": "Ministry of Panchayati Raj", "desc": "Nodal ministry for Panchayati Raj institutions.",
     "url": "https://panchayat.gov.in/", "group": "Panchayati Raj"},
    {"icon": "🗂️", "name": "Local Government Directory (LGD)", "desc": "Official registry of Panchayats and local bodies.",
     "url": "https://lgdirectory.gov.in/", "group": "Panchayati Raj"},
    {"icon": "📰", "name": "Press Information Bureau", "desc": "Official government press releases and updates.",
     "url": "https://pib.gov.in/", "group": "Updates"},
    {"icon": "💰", "name": "MyScheme", "desc": "National platform to discover government schemes.",
     "url": "https://www.myscheme.gov.in/", "group": "Schemes"},
    {"icon": "🛡️", "name": "myGov", "desc": "Citizen engagement and participation platform.",
     "url": "https://www.mygov.in/", "group": "Citizen Engagement"},
    {"icon": "📈", "name": "NITI Aayog", "desc": "Policy think tank of the Government of India.",
     "url": "https://www.niti.gov.in/", "group": "National"},
]

PIB_RSS = "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1"


# ============================================================
# 3. DESIGN SYSTEM
# ============================================================

CSS = """
<style>
/* ---------------- Tokens ---------------- */
:root{
  --pc-primary:#0B6E4F;
  --pc-primary-600:#0E7C59;
  --pc-primary-050:#EAF5F0;
  --pc-ink:#0F172A;
  --pc-body:#475569;
  --pc-muted:#64748B;
  --pc-border:#E6EAF0;
  --pc-surface:#FFFFFF;
  --pc-bg:#F6F8FB;
  --pc-radius:16px;
}

/* ---------------- App shell ---------------- */
.stApp{ background:var(--pc-bg); }
header[data-testid="stHeader"]{ background:transparent; }
#MainMenu{ visibility:hidden; }
footer{ visibility:hidden; }

.block-container{
  padding-top:1.6rem;
  padding-bottom:3rem;
  max-width:1180px;
}

/* ---------------- Sidebar ---------------- */
section[data-testid="stSidebar"]{
  background:var(--pc-surface);
  border-right:1px solid var(--pc-border);
}
section[data-testid="stSidebar"] .block-container{ padding-top:1rem; }

.pc-brand{
  display:flex; align-items:center; gap:12px;
  padding:6px 4px 14px 4px;
}
.pc-brand-logo{
  width:44px; height:44px; border-radius:13px;
  display:flex; align-items:center; justify-content:center;
  font-size:22px;
  background:linear-gradient(135deg,#0B6E4F,#16A34A);
  box-shadow:0 8px 18px -8px rgba(11,110,79,.75);
}
.pc-brand-name{
  font-size:1.02rem; font-weight:800; color:var(--pc-ink);
  letter-spacing:-.02em; line-height:1.15;
}
.pc-brand-sub{
  font-size:.72rem; color:var(--pc-muted); font-weight:500;
}

.pc-side-label{
  font-size:.7rem; font-weight:700; letter-spacing:.09em;
  text-transform:uppercase; color:#94A3B8;
  margin:16px 0 8px 4px;
}

/* Sidebar buttons = navigation */
section[data-testid="stSidebar"] .stButton > button{
  width:100%;
  justify-content:flex-start;
  text-align:left;
  padding:9px 14px;
  border-radius:11px;
  font-size:.9rem;
  font-weight:600;
  border:1px solid transparent;
  background:transparent;
  color:var(--pc-body);
  box-shadow:none;
}
section[data-testid="stSidebar"] .stButton > button:hover{
  background:var(--pc-primary-050);
  color:var(--pc-primary);
  border-color:transparent;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]{
  background:linear-gradient(135deg,#0B6E4F,#12905F);
  color:#fff;
  box-shadow:0 10px 20px -12px rgba(11,110,79,.9);
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover{
  color:#fff;
  filter:brightness(1.05);
}

/* ---------------- Hero ---------------- */
.pc-hero{
  position:relative;
  display:flex; align-items:center; gap:22px;
  padding:30px 32px;
  border-radius:22px;
  background:linear-gradient(135deg,#08402E 0%,#0B6E4F 45%,#159A6A 100%);
  color:#fff;
  overflow:hidden;
  box-shadow:0 24px 48px -26px rgba(8,64,46,.85);
  margin-bottom:8px;
}
.pc-hero::after{
  content:""; position:absolute; right:-70px; top:-80px;
  width:260px; height:260px; border-radius:50%;
  background:rgba(255,255,255,.09);
}
.pc-hero::before{
  content:""; position:absolute; right:90px; bottom:-110px;
  width:200px; height:200px; border-radius:50%;
  background:rgba(255,255,255,.06);
}
.pc-hero-icon{
  position:relative; z-index:1;
  font-size:38px; line-height:1;
  padding:15px; border-radius:18px;
  background:rgba(255,255,255,.15);
  border:1px solid rgba(255,255,255,.22);
  backdrop-filter:blur(6px);
  flex-shrink:0;
}
.pc-hero-text{ position:relative; z-index:1; }
.pc-hero h1{
  font-size:1.95rem !important;
  font-weight:800 !important;
  color:#fff !important;
  margin:0 0 6px 0 !important;
  letter-spacing:-.025em;
  line-height:1.15;
}
.pc-hero p{
  margin:0; font-size:.98rem; color:rgba(255,255,255,.9);
  max-width:760px; line-height:1.55;
}
.pc-hero-chips{ margin-top:14px; display:flex; gap:8px; flex-wrap:wrap; }
.pc-hero-chip{
  background:rgba(255,255,255,.16);
  border:1px solid rgba(255,255,255,.26);
  color:#fff; padding:4px 12px; border-radius:999px;
  font-size:.74rem; font-weight:600;
  backdrop-filter:blur(4px);
}

/* ---------------- Section headers ---------------- */
.pc-section{
  display:flex; align-items:center; gap:9px;
  font-size:1.16rem; font-weight:800; color:var(--pc-ink);
  letter-spacing:-.02em;
  margin:30px 0 4px 0;
}
.pc-section-sub{
  font-size:.86rem; color:var(--pc-muted);
  margin:0 0 14px 0;
}

/* ---------------- Cards ---------------- */
div[data-testid="stVerticalBlockBorderWrapper"]{
  border-radius:var(--pc-radius) !important;
  border:1px solid var(--pc-border) !important;
  background:var(--pc-surface) !important;
  box-shadow:0 1px 2px rgba(16,24,40,.04),
             0 14px 30px -22px rgba(16,24,40,.30);
  transition:box-shadow .2s ease, transform .2s ease, border-color .2s ease;
  padding:4px 2px;
}
div[data-testid="stVerticalBlockBorderWrapper"]:has(.pc-hoverable):hover{
  transform:translateY(-3px);
  border-color:#CFE7DC !important;
  box-shadow:0 4px 10px rgba(16,24,40,.06),
             0 26px 44px -26px rgba(11,110,79,.45);
}

.pc-card-title{
  font-size:1.04rem; font-weight:750; color:var(--pc-ink);
  margin:0 0 3px 0; letter-spacing:-.015em; line-height:1.3;
}
.pc-card-sub{
  font-size:.8rem; color:var(--pc-muted);
  margin:0 0 12px 0; line-height:1.4;
}
.pc-card-body{
  font-size:.88rem; color:var(--pc-body);
  line-height:1.6; margin:10px 0 12px 0;
}
.pc-chip-row{ display:flex; gap:6px; flex-wrap:wrap; margin-bottom:2px; }
.pc-chip{
  display:inline-block; padding:3px 10px; border-radius:999px;
  font-size:.7rem; font-weight:700; letter-spacing:.02em;
  background:var(--pc-primary-050); color:var(--pc-primary);
  border:1px solid #CFE7DC;
}
.pc-chip.blue{ background:#EAF2FE; color:#1D4ED8; border-color:#D3E2FD; }
.pc-chip.amber{ background:#FFF6E8; color:#B45309; border-color:#FBE0B4; }
.pc-chip.grey{ background:#F1F5F9; color:#475569; border-color:#E2E8F0; }

/* ---------------- Metrics ---------------- */
div[data-testid="stMetric"]{
  background:var(--pc-surface);
  border:1px solid var(--pc-border);
  border-radius:var(--pc-radius);
  padding:16px 18px;
  box-shadow:0 1px 2px rgba(16,24,40,.04),
             0 14px 30px -22px rgba(16,24,40,.30);
}
div[data-testid="stMetricValue"]{
  font-size:1.55rem; font-weight:800; color:var(--pc-primary);
  letter-spacing:-.02em;
}
div[data-testid="stMetricLabel"]{
  font-size:.78rem; font-weight:700; color:var(--pc-muted);
  text-transform:uppercase; letter-spacing:.05em;
}

/* ---------------- Buttons ---------------- */
.stButton > button{
  border-radius:11px;
  font-weight:650;
  border:1px solid #DCE4ED;
  transition:all .15s ease;
}
.stButton > button:hover{
  border-color:var(--pc-primary);
  color:var(--pc-primary);
  background:var(--pc-primary-050);
}
.stLinkButton > a{
  border-radius:11px !important;
  font-weight:650 !important;
  border:1px solid #DCE4ED !important;
  transition:all .15s ease;
}
.stLinkButton > a:hover{
  border-color:var(--pc-primary) !important;
  color:var(--pc-primary) !important;
  background:var(--pc-primary-050) !important;
}

/* ---------------- Inputs ---------------- */
.stTextInput input, .stSelectbox div[data-baseweb="select"] > div,
.stMultiSelect div[data-baseweb="select"] > div{
  border-radius:11px !important;
}

/* ---------------- Misc ---------------- */
.pc-loc-box{
  background:var(--pc-primary-050);
  border:1px solid #CFE7DC;
  border-radius:14px;
  padding:12px 16px;
  font-size:.87rem;
  color:#0B5D3B;
  font-weight:600;
  margin-bottom:6px;
}
.pc-note{
  font-size:.8rem; color:var(--pc-muted); line-height:1.6;
}
.pc-footer{
  margin-top:52px; padding:26px 20px 12px 20px;
  border-top:1px solid var(--pc-border);
  text-align:center; color:var(--pc-muted); font-size:.8rem; line-height:1.8;
}
.pc-footer strong{ color:var(--pc-ink); }
.pc-divider{ height:1px; background:var(--pc-border); margin:26px 0 0 0; }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# 4. HELPERS
# ============================================================

def t(key: str) -> str:
    """Translate a key using the active language."""
    lang = st.session_state.get("lang_code", "en")
    return I18N.get(lang, I18N["en"]).get(key, I18N["en"].get(key, key))


def nav_label(key: str) -> str:
    return t(f"nav_{key}")


def render_hero(icon: str, title: str, subtitle: str, chips: list[str] | None = None) -> None:
    chips_html = ""
    if chips:
        chips_html = '<div class="pc-hero-chips">' + "".join(
            f'<span class="pc-hero-chip">{html.escape(c)}</span>' for c in chips
        ) + "</div>"

    st.markdown(
        f"""
        <div class="pc-hero">
            <div class="pc-hero-icon">{icon}</div>
            <div class="pc-hero-text">
                <h1>{html.escape(title)}</h1>
                <p>{html.escape(subtitle)}</p>
                {chips_html}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section(title: str, subtitle: str | None = None) -> None:
    st.markdown(f'<div class="pc-section">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="pc-section-sub">{subtitle}</div>', unsafe_allow_html=True)


def chips(items: list[tuple[str, str]]) -> None:
    """items = [(text, variant)] where variant ∈ {'', 'blue', 'amber', 'grey'}"""
    html_parts = "".join(
        f'<span class="pc-chip {variant}">{html.escape(text)}</span>'
        for text, variant in items
    )
    st.markdown(f'<div class="pc-chip-row">{html_parts}</div>', unsafe_allow_html=True)


def clean_html_text(raw: str, limit: int = 260) -> str:
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "…"
    return text


@st.cache_data(ttl=900, show_spinner=False)
def load_pib_updates(feed_url: str, limit: int = 12) -> list[dict]:
    """Fetch and normalise the official PIB RSS feed (cached for 15 minutes)."""
    if not FEEDPARSER_AVAILABLE:
        return []

    feed = feedparser.parse(feed_url)
    items: list[dict] = []

    for entry in feed.entries[:limit]:
        published = entry.get("published", "")
        if entry.get("published_parsed"):
            try:
                published = time.strftime("%d %b %Y · %H:%M", entry.published_parsed)
            except Exception:
                pass

        items.append(
            {
                "title": clean_html_text(entry.get("title", "Government Update"), 160),
                "link": entry.get("link", ""),
                "published": published,
                "summary": clean_html_text(entry.get("summary", ""), 280),
            }
        )
    return items


def scheme_card(scheme: dict) -> None:
    with st.container(border=True):
        st.markdown('<span class="pc-hoverable"></span>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="pc-card-title">{html.escape(scheme["name"])}</div>'
            f'<div class="pc-card-sub">{html.escape(scheme["full_name"])}</div>',
            unsafe_allow_html=True,
        )
        chips(
            [
                (scheme["category"], ""),
                (scheme["level"], "blue"),
            ]
        )
        st.markdown(
            f'<div class="pc-card-body">{html.escape(scheme["description"])}</div>',
            unsafe_allow_html=True,
        )
        st.caption(f"🏛️ {scheme['ministry']}")
        st.link_button(
            f"{t('official_source')} →",
            scheme["url"],
            use_container_width=True,
        )


# ============================================================
# 5. SESSION STATE
# ============================================================

if "page" not in st.session_state:
    st.session_state.page = "dashboard"

if "lang_choice" not in st.session_state:
    st.session_state.lang_choice = "English"

st.session_state.lang_code = "kn" if st.session_state.lang_choice == "ಕನ್ನಡ" else "en"


# ============================================================
# 6. SIDEBAR
# ============================================================

with st.sidebar:

    # ---- Brand ----
    st.markdown(
        """
        <div class="pc-brand">
            <div class="pc-brand-logo">🇮🇳</div>
            <div>
                <div class="pc-brand-name">PanchayatConnect</div>
                <div class="pc-brand-sub">Civic Information Platform</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Navigation ----
    st.markdown('<div class="pc-side-label">Navigation</div>', unsafe_allow_html=True)

    for key, icon in NAV_ITEMS:
        is_active = st.session_state.page == key
        if st.button(
            f"{icon}  {nav_label(key)}",
            key=f"nav_btn_{key}",
            use_container_width=True,
            type="primary" if is_active else "secondary",
        ):
            st.session_state.page = key
            st.rerun()

    st.divider()

    # ---- Location ----
    st.markdown(
        f'<div class="pc-side-label">📍 {t("my_location")}</div>',
        unsafe_allow_html=True,
    )

    sel_state = st.selectbox(t("state"), STATES, key="loc_state")
    sel_district = st.text_input(
        t("district"), placeholder="e.g. Hassan", key="loc_district"
    )
    sel_panchayat = st.text_input(
        t("panchayat"), placeholder="e.g. Example Gram Panchayat 1", key="loc_panchayat"
    )

    st.divider()

    # ---- Language ----
    st.selectbox(
        f"🌐 {t('language')}",
        ["English", "ಕನ್ನಡ"],
        key="lang_choice",
    )

    st.markdown(
        f"""
        <div style="margin-top:22px;padding:12px 14px;border-radius:12px;
                    background:#F8FAFC;border:1px solid #E6EAF0;">
            <div style="font-size:.7rem;font-weight:700;letter-spacing:.08em;
                        text-transform:uppercase;color:#94A3B8;">Status</div>
            <div style="font-size:.8rem;color:#475569;margin-top:4px;line-height:1.6;">
                Prototype build · v{APP_VERSION}<br>
                Independent civic-tech project
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# 7. PAGES
# ============================================================

page = st.session_state.page

# ------------------------------------------------------------
# 7.1 DASHBOARD
# ------------------------------------------------------------
if page == "dashboard":

    render_hero(
        "🇮🇳",
        "PanchayatConnect",
        "One place to discover Panchayats, government schemes and official "
        "updates — with clear links back to the original source.",
        chips=["Verified sources", "English + ಕನ್ನಡ", "Location aware"],
    )

    st.write("")

    # ---- Active location strip ----
    location_parts = [sel_state]
    if sel_district:
        location_parts.append(sel_district)
    if sel_panchayat:
        location_parts.append(sel_panchayat)

    st.markdown(
        f'<div class="pc-loc-box">📍 {t("my_location")}: '
        f'{" • ".join(html.escape(p) for p in location_parts)}</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    # ---- KPI row ----
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Schemes Listed", len(SCHEMES))
    c2.metric("Directory Source", "LGD")
    c3.metric("Languages", "2")
    c4.metric("Version", APP_VERSION)

    # ---- Quick actions ----
    section("🚀 Quick actions", "Jump straight to what you need.")

    qa1, qa2, qa3 = st.columns(3)

    with qa1:
        with st.container(border=True):
            st.markdown('<span class="pc-hoverable"></span>', unsafe_allow_html=True)
            st.markdown('<div class="pc-card-title">🏘️ Panchayat Directory</div>',
                        unsafe_allow_html=True)
            st.markdown(
                '<div class="pc-card-body">Browse the local-government hierarchy '
                'from State down to Gram Panchayat.</div>',
                unsafe_allow_html=True,
            )
            if st.button("Open directory", key="qa_dir", use_container_width=True):
                st.session_state.page = "directory"
                st.rerun()

    with qa2:
        with st.container(border=True):
            st.markdown('<span class="pc-hoverable"></span>', unsafe_allow_html=True)
            st.markdown('<div class="pc-card-title">🔎 Scheme Finder</div>',
                        unsafe_allow_html=True)
            st.markdown(
                '<div class="pc-card-body">Search central schemes by need, '
                'category or keyword.</div>',
                unsafe_allow_html=True,
            )
            if st.button("Find schemes", key="qa_sch", use_container_width=True):
                st.session_state.page = "schemes"
                st.rerun()

    with qa3:
        with st.container(border=True):
            st.markdown('<span class="pc-hoverable"></span>', unsafe_allow_html=True)
            st.markdown('<div class="pc-card-title">📢 Official Updates</div>',
                        unsafe_allow_html=True)
            st.markdown(
                '<div class="pc-card-body">Live releases pulled from the '
                'Press Information Bureau feed.</div>',
                unsafe_allow_html=True,
            )
            if st.button("View updates", key="qa_upd", use_container_width=True):
                st.session_state.page = "updates"
                st.rerun()

    # ---- Featured schemes ----
    section("⭐ Featured schemes", "A few widely accessed central schemes.")

    featured = SCHEMES[:3]
    cols = st.columns(3)
    for col, scheme in zip(cols, featured):
        with col:
            scheme_card(scheme)

    # ---- Trust note ----
    st.write("")
    st.info(
        "🔐 **Source transparency.** PanchayatConnect is an independent project and "
        "is **not** a government website. Always verify details on the linked official "
        "portal before acting on them.",
        icon="ℹ️",
    )


# ------------------------------------------------------------
# 7.2 PANCHAYAT DIRECTORY
# ------------------------------------------------------------
elif page == "directory":

    render_hero(
        "🏘️",
        t("nav_directory"),
        "Explore the local-government hierarchy using official directory "
        "architecture (State → District → Block → Gram Panchayat).",
        chips=["LGD-aligned", "Prototype data"],
    )

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="pc-card-title">📍 Filter directory</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="pc-card-sub">Narrow results by district, block or name.</div>',
            unsafe_allow_html=True,
        )

        f1, f2, f3 = st.columns([1, 1, 2])

        with f1:
            dir_state = st.selectbox(
                t("state"), ["Karnataka"], key="dir_state"
            )
        with f2:
            dir_district = st.selectbox(
                t("district"),
                ["All Districts"] + sorted({p["district"] for p in PANCHAYATS}),
                key="dir_district",
            )
        with f3:
            dir_search = st.text_input(
                f"🔎 {t('search')}",
                placeholder=t("type_here"),
                key="dir_search",
            )

        b1, b2 = st.columns([1, 1])
        with b1:
            dir_block = st.selectbox(
                "Block",
                ["All Blocks"] + sorted({p["block"] for p in PANCHAYATS}),
                key="dir_block",
            )
        with b2:
            if st.button(t("clear_filters"), key="dir_reset", use_container_width=True):
                st.session_state.dir_district = "All Districts"
                st.session_state.dir_block = "All Blocks"
                st.session_state.dir_search = ""
                st.rerun()

    # ---- Apply filters ----
    results = [p for p in PANCHAYATS if p["state"] == dir_state]

    if dir_district != "All Districts":
        results = [p for p in results if p["district"] == dir_district]

    if dir_block != "All Blocks":
        results = [p for p in results if p["block"] == dir_block]

    if dir_search:
        q = dir_search.strip().lower()
        results = [p for p in results if q in p["name"].lower()]

    section(
        f"📋 {t('results')}: {len(results)}",
        "Prototype records shown for demonstration purposes.",
    )

    if not results:
        st.warning(t("no_results"))
    else:
        cols = st.columns(2)
        for i, item in enumerate(results):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown('<span class="pc-hoverable"></span>', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="pc-card-title">🏘️ {html.escape(item["name"])}</div>',
                        unsafe_allow_html=True,
                    )
                    chips([(item["type"], ""), (item["code"], "grey")])
                    st.markdown(
                        f'<div class="pc-card-body">'
                        f'<b>State:</b> {html.escape(item["state"])}<br>'
                        f'<b>District:</b> {html.escape(item["district"])}<br>'
                        f'<b>Block:</b> {html.escape(item["block"])}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    st.caption("⚠️ Prototype record — not yet a live LGD entry.")

    st.write("")
    with st.container(border=True):
        st.markdown('<div class="pc-card-title">🏛️ About the Local Government Directory</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="pc-card-body">The production version of PanchayatConnect will '
            'retrieve verified Panchayat records and LGD codes directly from the '
            'official Local Government Directory maintained by the Ministry of '
            'Panchayati Raj.</div>',
            unsafe_allow_html=True,
        )
        st.link_button(
            "Open Ministry of Panchayati Raj →",
            "https://panchayat.gov.in/en/lgd/",
            use_container_width=True,
        )


# ------------------------------------------------------------
# 7.3 FIND SCHEMES
# ------------------------------------------------------------
elif page == "schemes":

    render_hero(
        "🔎",
        t("nav_schemes"),
        "Search central government schemes by keyword, category or level — "
        "every result links to its official portal.",
        chips=[f"{len(SCHEMES)} schemes", "Official links", "Keyword search"],
    )

    st.write("")

    with st.container(border=True):
        st.markdown('<div class="pc-card-title">🔍 Search & filter</div>',
                    unsafe_allow_html=True)
        st.markdown(
            '<div class="pc-card-sub">Try “farmer”, “housing”, “pension” or “health”.</div>',
            unsafe_allow_html=True,
        )

        s1, s2 = st.columns([2, 1])
        with s1:
            query = st.text_input(
                t("search"),
                placeholder="e.g. farmer, housing, employment",
                key="sch_query",
            )
        with s2:
            level = st.selectbox("Level", ["All", "Central", "State"], key="sch_level")

        s3, s4 = st.columns([2, 1])
        with s3:
            cats = st.multiselect(
                t("category"),
                SCHEME_CATEGORIES,
                default=[],
                key="sch_cats",
                placeholder="All categories",
            )
        with s4:
            sort_by = st.selectbox(
                "Sort by", ["Name (A–Z)", "Category"], key="sch_sort"
            )

        if st.button(t("clear_filters"), key="sch_reset", use_container_width=False):
            st.session_state.sch_query = ""
            st.session_state.sch_cats = []
            st.session_state.sch_level = "All"
            st.rerun()

    # ---- Filtering ----
    results = list(SCHEMES)

    if query:
        q = query.strip().lower()
        results = [
            s for s in results
            if q in s["name"].lower()
            or q in s["full_name"].lower()
            or q in s["category"].lower()
            or q in s["description"].lower()
            or any(q in k for k in s["keywords"])
        ]

    if cats:
        results = [s for s in results if s["category"] in cats]

    if level != "All":
        results = [s for s in results if s["level"] == level]

    if sort_by == "Name (A–Z)":
        results = sorted(results, key=lambda s: s["name"].lower())
    else:
        results = sorted(results, key=lambda s: (s["category"], s["name"].lower()))

    section(f"📦 {t('results')}: {len(results)}")

    if not results:
        st.warning(t("no_results"))
        st.caption("Try removing a filter or using a broader keyword.")
    else:
        cols = st.columns(2)
        for i, scheme in enumerate(results):
            with cols[i % 2]:
                scheme_card(scheme)


# ------------------------------------------------------------
# 7.4 GOVERNMENT UPDATES
# ------------------------------------------------------------
elif page == "updates":

    render_hero(
        "📢",
        t("nav_updates"),
        "Official releases aggregated from the Press Information Bureau RSS feed.",
        chips=["Live feed", "Cached 15 min"],
    )

    st.write("")

    top_l, top_r = st.columns([3, 1])
    with top_r:
        if st.button("🔄 Refresh feed", use_container_width=True):
            load_pib_updates.clear()
            st.rerun()

    if not FEEDPARSER_AVAILABLE:
        st.error(
            "The `feedparser` package is not installed. Run "
            "`pip install feedparser` to enable live updates."
        )
    else:
        with st.spinner("Fetching the latest official releases…"):
            try:
                updates = load_pib_updates(PIB_RSS, 12)
                error = None
            except Exception as exc:  # noqa: BLE001
                updates, error = [], str(exc)

        if error:
            st.error("The government update feed is temporarily unavailable.")
            st.caption(f"Technical detail: {error}")
        elif not updates:
            st.warning("No updates were returned at the moment. Please try again later.")
        else:
            st.success(f"🟢 {len(updates)} official updates available")
            st.caption(
                "Source: Press Information Bureau (pib.gov.in). "
                "Content is reproduced from the official feed."
            )

            for item in updates:
                with st.container(border=True):
                    st.markdown('<span class="pc-hoverable"></span>', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="pc-card-title">📰 {html.escape(item["title"])}</div>',
                        unsafe_allow_html=True,
                    )
                    if item["published"]:
                        st.markdown(
                            f'<div class="pc-card-sub">🕒 {html.escape(item["published"])}</div>',
                            unsafe_allow_html=True,
                        )
                    if item["summary"]:
                        st.markdown(
                            f'<div class="pc-card-body">{html.escape(item["summary"])}</div>',
                            unsafe_allow_html=True,
                        )
                    if item["link"]:
                        st.link_button(
                            "Read official release →",
                            item["link"],
                            use_container_width=True,
                        )


# ------------------------------------------------------------
# 7.5 OFFICIAL SOURCES
# ------------------------------------------------------------
elif page == "sources":

    render_hero(
        "🏛️",
        t("nav_sources"),
        "A curated set of official Government of India portals for verification "
        "and further reading.",
        chips=["Government of India", "Verified links"],
    )

    st.write("")

    groups: dict[str, list[dict]] = {}
    for source in SOURCES:
        groups.setdefault(source["group"], []).append(source)

    for group_name, items in groups.items():
        section(f"• {group_name}")
        cols = st.columns(2)
        for i, source in enumerate(items):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown('<span class="pc-hoverable"></span>', unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="pc-card-title">{source["icon"]} '
                        f'{html.escape(source["name"])}</div>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f'<div class="pc-card-body">{html.escape(source["desc"])}</div>',
                        unsafe_allow_html=True,
                    )
                    st.link_button(
                        "Open official website →",
                        source["url"],
                        use_container_width=True,
                    )


# ------------------------------------------------------------
# 7.6 ABOUT
# ------------------------------------------------------------
elif page == "about":

    render_hero(
        "ℹ️",
        f"About PanchayatConnect",
        "An independent civic-tech initiative focused on making government "
        "information easier to find, understand and verify.",
        chips=[f"Version {APP_VERSION}", "Open architecture"],
    )

    st.write("")

    a1, a2 = st.columns([3, 2])

    with a1:
        with st.container(border=True):
            st.markdown('<div class="pc-card-title">🎯 What we are building</div>',
                        unsafe_allow_html=True)
            st.markdown(
                """
                <div class="pc-card-body">
                PanchayatConnect connects citizens to three things that are usually
                scattered across dozens of websites:
                <br><br>
                <b>1. Local discovery</b> — find your Gram Panchayat within the
                official administrative hierarchy.<br>
                <b>2. Scheme discovery</b> — search central schemes by need,
                category or keyword.<br>
                <b>3. Official updates</b> — read government releases from the
                original source, not a re-written copy.
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")

        with st.container(border=True):
            st.markdown('<div class="pc-card-title">🏗️ Data architecture</div>',
                        unsafe_allow_html=True)
            st.markdown(
                """
                <div class="pc-card-body">
                The production platform is designed around authoritative public
                sources — the <b>Local Government Directory (LGD)</b> for Panchayat
                records, <b>data.gov.in</b> for open datasets, and ministry portals
                for scheme rules and eligibility.
                </div>
                """,
                unsafe_allow_html=True,
            )

    with a2:
        with st.container(border=True):
            st.markdown('<div class="pc-card-title">🔐 Important disclaimer</div>',
                        unsafe_allow_html=True)
            st.markdown(
                """
                <div class="pc-card-body">
                PanchayatConnect is <b>not a government website</b> and is not
                affiliated with any government body.
                <br><br>
                Information shown here is for general awareness only. It does not
                constitute eligibility advice, and the platform does not guarantee
                scheme approval.
                <br><br>
                <b>Always verify against the original official source</b> before
                applying for any scheme or acting on any information.
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")

        with st.container(border=True):
            st.markdown('<div class="pc-card-title">🗺️ Roadmap</div>',
                        unsafe_allow_html=True)
            chips([
                ("Live LGD integration", "amber"),
                ("Kannada full UI", "amber"),
                ("AI scheme assistant", "amber"),
                ("Offline mode", "grey"),
                ("State schemes", "grey"),
            ])
            st.markdown(
                '<div class="pc-card-body" style="margin-top:12px;">'
                'Upcoming releases will focus on verified data pipelines and '
                'vernacular access.</div>',
                unsafe_allow_html=True,
            )


# ============================================================
# 8. FOOTER
# ============================================================

st.markdown(
    f"""
    <div class="pc-footer">
        <strong>PanchayatConnect</strong> · Independent Civic-Tech Project · v{APP_VERSION}
        <br>
        Not a government website. Always verify information on the original official source.
        <br>
        © {APP_YEAR} PanchayatConnect
    </div>
    """,
    unsafe_allow_html=True,
)
