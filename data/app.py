"""
PanchayatConnect — V1.1 (complete working build)
"""

from __future__ import annotations
import html, re, time
import streamlit as st

try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="PanchayatConnect",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_VERSION = "1.1"
APP_YEAR = "2026"
GEMINI_MODEL_DEFAULT = "gemini-2.0-flash"


# ============================================================
# STATE → DISTRICT DATASET
# ============================================================
STATES_DISTRICTS = {
    "Karnataka": [
        "Bagalkote","Ballari","Belagavi","Bengaluru Rural","Bengaluru Urban",
        "Bidar","Chamarajanagara","Chikkaballapura","Chikkamagaluru",
        "Chitradurga","Dakshina Kannada","Davanagere","Dharwad","Gadag",
        "Hassan","Haveri","Kalaburagi","Kodagu","Kolar","Koppal","Mandya",
        "Mysuru","Raichur","Ramanagara","Shivamogga","Tumakuru","Udupi",
        "Uttara Kannada","Vijayanagara","Yadgir",
    ],
    "Kerala": [
        "Alappuzha","Ernakulam","Idukki","Kannur","Kasaragod","Kollam",
        "Kottayam","Kozhikode","Malappuram","Palakkad","Pathanamthitta",
        "Thiruvananthapuram","Thrissur","Wayanad",
    ],
    "Tamil Nadu": [
        "Ariyalur","Chengalpattu","Chennai","Coimbatore","Cuddalore",
        "Dharmapuri","Dindigul","Erode","Kallakurichi","Kanchipuram",
        "Kanyakumari","Karur","Krishnagiri","Madurai","Mayiladuthurai",
        "Nagapattinam","Namakkal","Nilgiris","Perambalur","Pudukkottai",
        "Ramanathapuram","Ranipet","Salem","Sivaganga","Tenkasi",
        "Thanjavur","Theni","Thoothukudi","Tiruchirappalli","Tirunelveli",
        "Tirupathur","Tiruppur","Tiruvallur","Tiruvannamalai","Tiruvarur",
        "Vellore","Viluppuram","Virudhunagar",
    ],
    "Maharashtra": [
        "Ahmednagar","Akola","Amravati","Aurangabad","Beed","Bhandara",
        "Buldhana","Chandrapur","Dhule","Gadchiroli","Gondia","Hingoli",
        "Jalgaon","Jalna","Kolhapur","Latur","Mumbai City",
        "Mumbai Suburban","Nagpur","Nanded","Nandurbar","Nashik","Osmanabad",
        "Palghar","Parbhani","Pune","Raigad","Ratnagiri","Sangli","Satara",
        "Sindhudurg","Solapur","Thane","Wardha","Washim","Yavatmal",
    ],
    "Telangana": [
        "Adilabad","Bhadradri Kothagudem","Hanumakonda","Hyderabad",
        "Jagtial","Jangaon","Jayashankar Bhupalpally","Jogulamba Gadwal",
        "Kamareddy","Karimnagar","Khammam","Kumuram Bheem",
        "Mahabubabad","Mahabubnagar","Mancherial","Medak","Medchal-Malkajgiri",
        "Mulugu","Nagarkurnool","Nalgonda","Narayanpet","Nirmal",
        "Nizamabad","Peddapalli","Rajanna Sircilla","Rangareddy","Sangareddy",
        "Siddipet","Suryapet","Vikarabad","Wanaparthy","Warangal","Yadadri",
    ],
    "Andhra Pradesh": [
        "Alluri Sitharama Raju","Anakapalli","Anantapur","Annamayya",
        "Bapatla","Chittoor","Dr. B.R. Ambedkar Konaseema","East Godavari",
        "Eluru","Guntur","Kakinada","Krishna","Kurnool","Nandyal",
        "Nellore","NTR","Palnadu","Parvathipuram Manyam","Prakasam",
        "Srikakulam","Sri Sathya Sai","Tirupati","Visakhapatnam",
        "Vizianagaram","West Godavari","YSR Kadapa",
    ],
    "Goa": ["North Goa", "South Goa"],
    "Uttar Pradesh": [
        "Agra","Aligarh","Ambedkar Nagar","Amethi","Amroha","Auraiya",
        "Ayodhya","Azamgarh","Baghpat","Bahraich","Ballia","Balrampur",
        "Banda","Barabanki","Bareilly","Basti","Bhadohi","Bijnor","Budaun",
        "Bulandshahr","Chandauli","Chitrakoot","Deoria","Etah","Etawah",
        "Farrukhabad","Fatehpur","Firozabad","Gautam Buddha Nagar","Ghaziabad",
        "Ghazipur","Gonda","Gorakhpur","Hamirpur","Hapur","Hardoi","Hathras",
        "Jalaun","Jaunpur","Jhansi","Kannauj","Kanpur Dehat","Kanpur Nagar",
        "Kasganj","Kaushambi","Kushinagar","Lakhimpur Kheri","Lalitpur",
        "Lucknow","Maharajganj","Mahoba","Mainpuri","Mathura","Mau",
        "Meerut","Mirzapur","Moradabad","Muzaffarnagar","Pilibhit",
        "Pratapgarh","Prayagraj","Raebareli","Rampur","Saharanpur",
        "Sambhal","Sant Kabir Nagar","Shahjahanpur","Shamli","Shravasti",
        "Siddharthnagar","Sitapur","Sonbhadra","Sultanpur","Unnao","Varanasi",
    ],
}


# ============================================================
# SCHEMES, PANCHAYATS, SOURCES (same as before)
# ============================================================
SCHEMES = [
    {"name":"PM-KISAN","full_name":"Pradhan Mantri Kisan Samman Nidhi",
     "category":"Agriculture","level":"Central",
     "ministry":"Ministry of Agriculture & Farmers Welfare",
     "description":"Income support for eligible landholding farmer families, released in periodic instalments directly into the beneficiary's bank account.",
     "keywords":["farmer","agriculture","farm","kisan","income","land","crop"],
     "url":"https://pmkisan.gov.in/"},
    {"name":"MGNREGA","full_name":"Mahatma Gandhi National Rural Employment Guarantee Act",
     "category":"Employment","level":"Central",
     "ministry":"Ministry of Rural Development",
     "description":"Guarantees a minimum number of days of unskilled wage employment in a financial year to rural households, subject to programme rules.",
     "keywords":["employment","job","work","rural","wages","nrega","labour"],
     "url":"https://nrega.nic.in/"},
    {"name":"PMAY-G","full_name":"Pradhan Mantri Awaas Yojana — Gramin",
     "category":"Housing","level":"Central",
     "ministry":"Ministry of Rural Development",
     "description":"Assistance for construction of pucca houses for eligible rural households, including basic amenities support.",
     "keywords":["house","housing","home","rural","awas","construction"],
     "url":"https://pmayg.nic.in/"},
    {"name":"Ayushman Bharat PM-JAY","full_name":"Pradhan Mantri Jan Arogya Yojana",
     "category":"Health","level":"Central",
     "ministry":"Ministry of Health & Family Welfare",
     "description":"Health assurance cover for eligible families for secondary and tertiary care hospitalisation at empanelled hospitals.",
     "keywords":["health","hospital","insurance","medical","ayushman","treatment"],
     "url":"https://pmjay.gov.in/"},
    {"name":"Pradhan Mantri Ujjwala Yojana","full_name":"Pradhan Mantri Ujjwala Yojana (PMUY)",
     "category":"Welfare","level":"Central",
     "ministry":"Ministry of Petroleum & Natural Gas",
     "description":"Provides clean cooking fuel connections to eligible women from below-poverty-line households.",
     "keywords":["lpg","gas","women","cooking","ujjwala","household"],
     "url":"https://www.pmuy.gov.in/"},
    {"name":"Atal Pension Yojana","full_name":"Atal Pension Yojana (APY)",
     "category":"Social Security","level":"Central",
     "ministry":"Ministry of Finance",
     "description":"Guaranteed minimum pension scheme for citizens in the unorganised sector, with government co-contribution for eligible subscribers.",
     "keywords":["pension","retirement","atal","social security","savings"],
     "url":"https://www.npscra.nsdl.co.in/scheme-details.php"},
    {"name":"Digital India","full_name":"Digital India Programme",
     "category":"Digital Services","level":"Central",
     "ministry":"Ministry of Electronics & IT",
     "description":"Umbrella programme for delivering government services digitally, expanding rural broadband and promoting digital literacy.",
     "keywords":["digital","online","service","technology","internet","egovernance"],
     "url":"https://www.digitalindia.gov.in/"},
    {"name":"PM Vishwakarma","full_name":"PM Vishwakarma Scheme",
     "category":"Skill Development","level":"Central",
     "ministry":"Ministry of Micro, Small & Medium Enterprises",
     "description":"End-to-end support to traditional artisans and craftspeople, including skill training, toolkit incentives and collateral-free credit.",
     "keywords":["artisan","craft","skill","training","loan","vishwakarma"],
     "url":"https://pmvishwakarma.gov.in/"},
]

SCHEME_CATEGORIES = sorted({s["category"] for s in SCHEMES})

PANCHAYATS = [
    {"state":"Karnataka","district":"Hassan","block":"Hassan","name":"Example Gram Panchayat 1","type":"Village Panchayat","code":"DEMO-001"},
    {"state":"Karnataka","district":"Hassan","block":"Arkalgud","name":"Example Gram Panchayat 2","type":"Village Panchayat","code":"DEMO-002"},
    {"state":"Karnataka","district":"Mysuru","block":"Mysuru","name":"Example Gram Panchayat 3","type":"Village Panchayat","code":"DEMO-003"},
    {"state":"Karnataka","district":"Bengaluru Rural","block":"Devanahalli","name":"Example Gram Panchayat 4","type":"Village Panchayat","code":"DEMO-004"},
    {"state":"Karnataka","district":"Tumakuru","block":"Tumakuru","name":"Example Gram Panchayat 5","type":"Village Panchayat","code":"DEMO-005"},
]

SOURCES = [
    {"icon":"🇮🇳","name":"India.gov.in","desc":"National Portal of India.","url":"https://www.india.gov.in/","group":"National"},
    {"icon":"📊","name":"data.gov.in","desc":"Open Government Data Platform.","url":"https://data.gov.in/","group":"National"},
    {"icon":"🏘️","name":"Ministry of Panchayati Raj","desc":"Nodal ministry for Panchayati Raj.","url":"https://panchayat.gov.in/","group":"Panchayati Raj"},
    {"icon":"🗂️","name":"LGD","desc":"Local Government Directory.","url":"https://lgdirectory.gov.in/","group":"Panchayati Raj"},
    {"icon":"📰","name":"PIB","desc":"Press Information Bureau.","url":"https://pib.gov.in/","group":"Updates"},
    {"icon":"💰","name":"MyScheme","desc":"Discover government schemes.","url":"https://www.myscheme.gov.in/","group":"Schemes"},
]

PIB_RSS = "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1"


# ============================================================
# CSS
# ============================================================
CSS = """
<style>
:root{
  --pc-primary:#0B6E4F;
  --pc-primary-050:#EAF5F0;
  --pc-ink:#0F172A;
  --pc-body:#475569;
  --pc-muted:#64748B;
  --pc-border:#E6EAF0;
  --pc-surface:#FFFFFF;
  --pc-bg:#F6F8FB;
}
.stApp{ background:var(--pc-bg); }
#MainMenu, footer, header[data-testid="stHeader"]{ visibility:hidden; }
.block-container{ padding-top:1.2rem; padding-bottom:3rem; max-width:1180px; }

section[data-testid="stSidebar"]{ background:var(--pc-surface); border-right:1px solid var(--pc-border); }

.pc-brand{ display:flex; align-items:center; gap:12px; padding:6px 4px 14px 4px; }
.pc-brand-logo{
  width:44px; height:44px; border-radius:13px; display:flex;
  align-items:center; justify-content:center; font-size:22px;
  background:linear-gradient(135deg,#0B6E4F,#16A34A);
  box-shadow:0 8px 18px -8px rgba(11,110,79,.75);
}
.pc-brand-name{ font-size:1.02rem; font-weight:800; color:var(--pc-ink); line-height:1.15; }
.pc-brand-sub{ font-size:.72rem; color:var(--pc-muted); }

.pc-side-label{
  font-size:.7rem; font-weight:700; letter-spacing:.09em;
  text-transform:uppercase; color:#94A3B8; margin:16px 0 8px 4px;
}

section[data-testid="stSidebar"] .stButton > button{
  width:100%; justify-content:flex-start; text-align:left;
  padding:9px 14px; border-radius:11px; font-size:.9rem; font-weight:600;
  border:1px solid transparent; background:transparent; color:var(--pc-body);
}
section[data-testid="stSidebar"] .stButton > button:hover{
  background:var(--pc-primary-050); color:var(--pc-primary);
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]{
  background:linear-gradient(135deg,#0B6E4F,#12905F); color:#fff;
}

.pc-hero{
  position:relative; display:flex; align-items:center; gap:22px;
  padding:30px 32px; border-radius:22px;
  background:linear-gradient(135deg,#08402E 0%,#0B6E4F 45%,#159A6A 100%);
  color:#fff; overflow:hidden;
  box-shadow:0 24px 48px -26px rgba(8,64,46,.85); margin-bottom:8px;
}
.pc-hero::after{
  content:""; position:absolute; right:-70px; top:-80px;
  width:260px; height:260px; border-radius:50%;
  background:rgba(255,255,255,.09);
}
.pc-hero-icon{
  font-size:38px; padding:15px; border-radius:18px;
  background:rgba(255,255,255,.15);
  border:1px solid rgba(255,255,255,.22); flex-shrink:0;
}
.pc-hero h1{ font-size:1.95rem !important; font-weight:800 !important;
             color:#fff !important; margin:0 0 6px 0 !important; }
.pc-hero p{ margin:0; font-size:.98rem; color:rgba(255,255,255,.9); }

.pc-section{ display:flex; align-items:center; gap:9px;
  font-size:1.16rem; font-weight:800; color:var(--pc-ink);
  margin:26px 0 4px 0; }
.pc-section-sub{ font-size:.86rem; color:var(--pc-muted); margin:0 0 14px 0; }

div[data-testid="stVerticalBlockBorderWrapper"]{
  border-radius:16px !important; border:1px solid var(--pc-border) !important;
  background:var(--pc-surface) !important;
  box-shadow:0 1px 2px rgba(16,24,40,.04), 0 14px 30px -22px rgba(16,24,40,.30);
  padding:4px 2px;
}

.pc-card-title{ font-size:1.04rem; font-weight:750; color:var(--pc-ink);
  margin:0 0 3px 0; line-height:1.3; }
.pc-card-sub{ font-size:.8rem; color:var(--pc-muted); margin:0 0 12px 0; }
.pc-card-body{ font-size:.88rem; color:var(--pc-body); line-height:1.6; margin:10px 0 12px 0; }

.pc-chip{
  display:inline-block; padding:3px 10px; border-radius:999px;
  font-size:.7rem; font-weight:700;
  background:var(--pc-primary-050); color:var(--pc-primary);
  border:1px solid #CFE7DC; margin-right:5px;
}
.pc-chip.blue{ background:#EAF2FE; color:#1D4ED8; border-color:#D3E2FD; }
.pc-chip.amber{ background:#FFF6E8; color:#B45309; border-color:#FBE0B4; }
.pc-chip.grey{ background:#F1F5F9; color:#475569; border-color:#E2E8F0; }

div[data-testid="stMetric"]{
  background:var(--pc-surface); border:1px solid var(--pc-border);
  border-radius:16px; padding:16px 18px;
}
div[data-testid="stMetricValue"]{ font-size:1.55rem; font-weight:800; color:var(--pc-primary); }
div[data-testid="stMetricLabel"]{ font-size:.78rem; font-weight:700; color:var(--pc-muted);
  text-transform:uppercase; letter-spacing:.05em; }

.pc-loc-box{
  background:var(--pc-primary-050); border:1px solid #CFE7DC;
  border-radius:14px; padding:12px 16px; font-size:.87rem;
  color:#0B5D3B; font-weight:600;
}
.pc-footer{
  margin-top:52px; padding:26px 20px 12px 20px;
  border-top:1px solid var(--pc-border);
  text-align:center; color:var(--pc-muted); font-size:.8rem; line-height:1.8;
}
.pc-footer strong{ color:var(--pc-ink); }

/* Global search bar */
.pc-search-wrap{
  background:var(--pc-surface); border:1px solid var(--pc-border);
  border-radius:18px; padding:18px 20px; margin:14px 0 6px 0;
  box-shadow:0 1px 2px rgba(16,24,40,.04), 0 14px 30px -22px rgba(16,24,40,.30);
}
.pc-search-title{
  display:flex; align-items:center; gap:8px;
  font-size:.95rem; font-weight:750; color:var(--pc-ink); margin-bottom:8px;
}

/* AI chat bubbles */
.pc-chat-user{
  background:#EAF2FE; border:1px solid #D3E2FD;
  border-radius:14px 14px 4px 14px; padding:10px 14px;
  font-size:.9rem; color:#0F172A; margin:6px 0; margin-left:14%;
}
.pc-chat-ai{
  background:#EAF5F0; border:1px solid #CFE7DC;
  border-radius:14px 14px 14px 4px; padding:12px 16px;
  font-size:.9rem; color:#0F172A; margin:6px 0; margin-right:14%;
  white-space:pre-wrap; line-height:1.6;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================
def section(title, subtitle=None):
    st.markdown(f'<div class="pc-section">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="pc-section-sub">{subtitle}</div>', unsafe_allow_html=True)


def render_hero(icon, title, subtitle):
    st.markdown(
        f"""<div class="pc-hero">
            <div class="pc-hero-icon">{icon}</div>
            <div><h1>{html.escape(title)}</h1><p>{html.escape(subtitle)}</p></div>
        </div>""",
        unsafe_allow_html=True,
    )


def chips(items):
    html_parts = "".join(
        f'<span class="pc-chip {v}">{html.escape(t)}</span>' for t, v in items
    )
    st.markdown(html_parts, unsafe_allow_html=True)


def clean_html_text(raw, limit=260):
    if not raw:
        return ""
    text = re.sub(r"<[^>]+>", " ", raw)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0] + "…"
    return text


def highlight(text, query):
    """Return HTML with query terms wrapped in a <mark>."""
    if not query:
        return html.escape(text)
    pattern = re.compile(re.escape(query), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark>{html.escape(m.group(0))}</mark>",
                       html.escape(text))


@st.cache_data(ttl=900, show_spinner=False)
def load_pib_updates(feed_url, limit=12):
    if not FEEDPARSER_AVAILABLE:
        return []
    feed = feedparser.parse(feed_url)
    items = []
    for entry in feed.entries[:limit]:
        published = entry.get("published", "")
        if entry.get("published_parsed"):
            try:
                published = time.strftime("%d %b %Y · %H:%M", entry.published_parsed)
            except Exception:
                pass
        items.append({
            "title": clean_html_text(entry.get("title", "Government Update"), 160),
            "link": entry.get("link", ""),
            "published": published,
            "summary": clean_html_text(entry.get("summary", ""), 280),
        })
    return items


# ---- Global search across all local data -------------------
def global_search(query: str):
    """Return dict with matched schemes, panchayats, sources."""
    if not query or not query.strip():
        return {"schemes": [], "panchayats": [], "sources": []}
    q = query.strip().lower()

    schemes = [
        s for s in SCHEMES
        if q in s["name"].lower()
        or q in s["full_name"].lower()
        or q in s["category"].lower()
        or q in s["description"].lower()
        or any(q in k for k in s["keywords"])
    ]
    panchayats = [
        p for p in PANCHAYATS
        if q in p["name"].lower()
        or q in p["district"].lower()
        or q in p["state"].lower()
        or q in p["block"].lower()
    ]
    sources = [
        s for s in SOURCES
        if q in s["name"].lower() or q in s["desc"].lower()
    ]
    return {"schemes": schemes, "panchayats": panchayats, "sources": sources}


# ---- Gemini helpers ----------------------------------------
def get_gemini_client():
    """Configure and return a Gemini model, using st.secrets or sidebar key."""
    if not GEMINI_AVAILABLE:
        return None
    api_key = st.session_state.get("gemini_api_key", "").strip()
    if not api_key:
        try:
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            api_key = ""
    if not api_key:
        return None
    try:
        genai.configure(api_key=api_key)
        model_name = st.session_state.get("gemini_model", GEMINI_MODEL_DEFAULT)
        return genai.GenerativeModel(model_name)
    except Exception:
        return None


CIVIC_SYSTEM_PROMPT = """You are PanchayatConnect Assistant, a helpful civic-tech AI for Indian citizens.

Guidelines:
- Answer questions about Indian government schemes, Panchayati Raj, LGD, and rural welfare.
- When discussing a scheme, mention: purpose, likely eligibility, how to apply, official portal.
- Be factual and concise. If unsure, say so — never invent scheme names, amounts, or URLs.
- Always remind users to verify details on the official government portal.
- Use simple language suitable for rural citizens. Use short paragraphs and bullet points.
- You are NOT a government representative."""


def ask_gemini(prompt: str, history=None):
    model = get_gemini_client()
    if not model:
        return None, "Gemini is not configured. Add your API key in the sidebar."
    try:
        full_prompt = f"{CIVIC_SYSTEM_PROMPT}\n\nUser question: {prompt}"
        resp = model.generate_content(full_prompt)
        text = getattr(resp, "text", None) or "_(no response)_"
        return text, None
    except Exception as exc:
        return None, f"Gemini error: {exc}"


# ============================================================
# SESSION STATE
# ============================================================
st.session_state.setdefault("page", "dashboard")
st.session_state.setdefault("global_query", "")
st.session_state.setdefault("ai_chat", [])
st.session_state.setdefault("gemini_api_key", "")
st.session_state.setdefault("gemini_model", GEMINI_MODEL_DEFAULT)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:

    st.markdown("""
        <div class="pc-brand">
            <div class="pc-brand-logo">🇮🇳</div>
            <div>
                <div class="pc-brand-name">PanchayatConnect</div>
                <div class="pc-brand-sub">Civic Information Platform</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="pc-side-label">Navigation</div>', unsafe_allow_html=True)

    NAV_ITEMS = [
        ("dashboard", "🏠", "Dashboard"),
        ("directory", "🏘️", "Panchayat Directory"),
        ("schemes",   "🔎", "Find Schemes"),
        ("ai",        "✨", "AI Assistant"),
        ("updates",   "📢", "Government Updates"),
        ("sources",   "🏛️", "Official Sources"),
        ("about",     "ℹ️", "About"),
    ]
    for key, icon, label in NAV_ITEMS:
        active = st.session_state.page == key
        if st.button(f"{icon}  {label}", key=f"nav_{key}",
                     use_container_width=True,
                     type="primary" if active else "secondary"):
            st.session_state.page = key
            st.rerun()

    st.divider()

    # -------- Location: State → District cascade --------
    st.markdown('<div class="pc-side-label">📍 My Location</div>',
                unsafe_allow_html=True)

    # Ensure state persists between reruns
    st.session_state.setdefault("loc_state", "Karnataka")
    st.session_state.setdefault("loc_district", "")

    # State dropdown
    selected_state = st.selectbox(
        "State",
        list(STATES_DISTRICTS.keys()),
        key="loc_state",
    )

    # District depends on selected state — recomputed every run
    district_options = ["— Select district —"] + STATES_DISTRICTS.get(selected_state, [])

    # If previously selected district is not in new state, reset it
    current_d = st.session_state.get("loc_district", "")
    if current_d not in district_options:
        st.session_state.loc_district = "— Select district —"

    selected_district = st.selectbox(
        "District",
        district_options,
        key="loc_district",
    )

    selected_panchayat = st.text_input(
        "Panchayat", placeholder="e.g. Example Gram Panchayat 1", key="loc_panchayat"
    )

    st.divider()

    # -------- Gemini API key --------
    st.markdown('<div class="pc-side-label">✨ Gemini AI</div>',
                unsafe_allow_html=True)

    if not GEMINI_AVAILABLE:
        st.caption("⚠️ `google-generativeai` not installed.")
        st.code("pip install google-generativeai", language="bash")
    else:
        st.text_input(
            "API Key",
            type="password",
            placeholder="Paste your Gemini API key",
            key="gemini_api_key",
            help="Get a free key at aistudio.google.com/app/apikey",
        )
        st.selectbox(
            "Model",
            GEMINI_MODELS,
            key="gemini_model",
        )
        if st.session_state.gemini_api_key or (lambda: (
            st.secrets.get("GEMINI_API_KEY", "") if hasattr(st, "secrets") else ""
        ))():
            st.success("Gemini ready", icon="✅")
        else:
            st.caption("Add an API key to enable AI answers.")

    st.divider()

    st.caption(f"Independent civic-tech project · v{APP_VERSION}")


# ============================================================
# GLOBAL SEARCH BAR (visible on all pages except AI page)
# ============================================================
def render_global_search():
    st.markdown('<div class="pc-search-wrap">'
                '<div class="pc-search-title">🔍 Search PanchayatConnect</div>'
                '</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([5, 1])
    with col1:
        q = st.text_input(
            "Search",
            value=st.session_state.global_query,
            placeholder="Search schemes, panchayats, sources…",
            key="global_search_input",
            label_visibility="collapsed",
        )
    with col2:
        do_search = st.button("Search", use_container_width=True, type="primary")

    if do_search:
        st.session_state.global_query = q
        # Optionally also ping Gemini for a summary if key set
        if q.strip():
            model = get_gemini_client()
            if model:
                with st.spinner("Asking Gemini…"):
                    answer, err = ask_gemini(q)
                    st.session_state["last_ai_answer"] = answer if answer else err
            else:
                st.session_state.pop("last_ai_answer", None)

    q = st.session_state.global_query.strip()
    if not q:
        return

    results = global_search(q)
    total = len(results["schemes"]) + len(results["panchayats"]) + len(results["sources"])

    st.markdown(
        f"<div style='margin:10px 0 4px 0;color:#64748B;font-size:.85rem;'>"
        f"Found <b>{total}</b> local matches for <b>{html.escape(q)}</b></div>",
        unsafe_allow_html=True,
    )

    # -------- Optional AI summary --------
    ai_ans = st.session_state.get("last_ai_answer")
    if ai_ans:
        with st.container(border=True):
            st.markdown('<div class="pc-card-title">✨ Gemini answer</div>',
                        unsafe_allow_html=True)
            st.markdown(f'<div class="pc-chat-ai">{html.escape(ai_ans)}</div>',
                        unsafe_allow_html=True)
            st.caption("AI-generated. Verify on the official portal.")

    # -------- Local matches --------
    if total == 0:
        st.info("No local matches. Try the AI Assistant page for a broader answer.")
        return

    # Schemes
    if results["schemes"]:
        st.markdown("##### 🎯 Schemes")
        for s in results["schemes"][:4]:
            with st.container(border=True):
                st.markdown(
                    f'<div class="pc-card-title">{highlight(s["name"], q)}</div>'
                    f'<div class="pc-card-sub">{html.escape(s["full_name"])}</div>',
                    unsafe_allow_html=True,
                )
                chips([(s["category"], ""), (s["level"], "blue")])
                st.markdown(f'<div class="pc-card-body">{highlight(s["description"], q)}</div>',
                            unsafe_allow_html=True)
                st.link_button("Open official source →", s["url"],
                               use_container_width=True)

    # Panchayats
    if results["panchayats"]:
        st.markdown("##### 🏘️ Panchayats")
        for p in results["panchayats"][:4]:
            with st.container(border=True):
                st.markdown(
                    f'<div class="pc-card-title">{highlight(p["name"], q)}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div class="pc-card-sub">{html.escape(p["district"])} · '
                    f'{html.escape(p["state"])} · {html.escape(p["block"])}</div>',
                    unsafe_allow_html=True,
                )
                chips([(p["type"], ""), (p["code"], "grey")])

    # Sources
    if results["sources"]:
        st.markdown("##### 🏛️ Official Sources")
        for s in results["sources"][:4]:
            with st.container(border=True):
                st.markdown(
                    f'<div class="pc-card-title">{s["icon"]} {highlight(s["name"], q)}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(f'<div class="pc-card-body">{highlight(s["desc"], q)}</div>',
                            unsafe_allow_html=True)
                st.link_button("Open →", s["url"], use_container_width=True)


# ============================================================
# PAGES
# ============================================================
page = st.session_state.page

# ---- DASHBOARD ----
if page == "dashboard":
    render_hero("🇮🇳", "PanchayatConnect",
                "Discover Panchayats, government schemes and official updates — "
                "with AI help and links back to the source.")

    render_global_search()

    st.write("")

    # Location strip
    parts = [st.session_state.loc_state]
    if st.session_state.loc_district and st.session_state.loc_district != "— Select district —":
        parts.append(st.session_state.loc_district)
    if st.session_state.get("loc_panchayat"):
        parts.append(st.session_state.loc_panchayat)
    st.markdown(
        f'<div class="pc-loc-box">📍 My Location: '
        f'{" • ".join(html.escape(p) for p in parts)}</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Schemes Listed", len(SCHEMES))
    c2.metric("Panchayat Records", len(PANCHAYATS))
    c3.metric("States Covered", len(STATES_DISTRICTS))
    c4.metric("Version", APP_VERSION)

    section("🚀 Quick actions", "Jump straight to what you need.")
    a, b, c = st.columns(3)
    with a:
        with st.container(border=True):
            st.markdown('<div class="pc-card-title">🏘️ Panchayat Directory</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="pc-card-body">Browse State → District → Block → Gram Panchayat.</div>',
                        unsafe_allow_html=True)
            if st.button("Open Directory", key="qa_dir", use_container_width=True):
                st.session_state.page = "directory"; st.rerun()
    with b:
        with st.container(border=True):
            st.markdown('<div class="pc-card-title">🔎 Scheme Finder</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="pc-card-body">Search schemes by need, category or keyword.</div>',
                        unsafe_allow_html=True)
            if st.button("Find Schemes", key="qa_sch", use_container_width=True):
                st.session_state.page = "schemes"; st.rerun()
    with c:
        with st.container(border=True):
            st.markdown('<div class="pc-card-title">✨ AI Assistant</div>',
                        unsafe_allow_html=True)
            st.markdown('<div class="pc-card-body">Ask Gemini about schemes, Panchayats, welfare.</div>',
                        unsafe_allow_html=True)
            if st.button("Ask AI", key="qa_ai", use_container_width=True):
                st.session_state.page = "ai"; st.rerun()

    section("⭐ Featured schemes", "Widely-used central schemes.")
    cols = st.columns(3)
    for col, s in zip(cols, SCHEMES[:3]):
        with col:
            with st.container(border=True):
                st.markdown(f'<div class="pc-card-title">{html.escape(s["name"])}</div>'
                            f'<div class="pc-card-sub">{html.escape(s["full_name"])}</div>',
                            unsafe_allow_html=True)
                chips([(s["category"], ""), (s["level"], "blue")])
                st.markdown(f'<div class="pc-card-body">{html.escape(s["description"])}</div>',
                            unsafe_allow_html=True)
                st.link_button("Official Source →", s["url"], use_container_width=True)

    st.info("🔐 PanchayatConnect is **not** a government website. Always verify on the "
            "official portal before acting.", icon="ℹ️")


# ---- DIRECTORY ----
elif page == "directory":
    render_hero("🏘️", "Panchayat Directory",
                "Explore the local-government hierarchy: State → District → Block → Gram Panchayat.")

    render_global_search()

    st.write("")

    with st.container(border=True):
        f1, f2, f3 = st.columns([1, 1, 2])
        with f1:
            dir_state = st.selectbox("State", list(STATES_DISTRICTS.keys()),
                                     key="dir_state")
        with f2:
            dist_opts = ["All Districts"] + STATES_DISTRICTS.get(dir_state, [])
            # reset if previous district not in list
            if st.session_state.get("dir_district") not in dist_opts:
                st.session_state.dir_district = "All Districts"
            dir_district = st.selectbox("District", dist_opts, key="dir_district")
        with f3:
            dir_search = st.text_input("🔎 Search Panchayat",
                                       placeholder="Type Panchayat name…",
                                       key="dir_search")

    results = [p for p in PANCHAYATS if p["state"] == dir_state]
    if dir_district != "All Districts":
        results = [p for p in results if p["district"] == dir_district]
    if dir_search:
        q = dir_search.lower()
        results = [p for p in results if q in p["name"].lower()]

    section(f"📋 Results: {len(results)}",
            "Prototype records — not yet live LGD entries.")

    if not results:
        st.warning("No Panchayats found for this filter. Try relaxing district or search.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(results):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f'<div class="pc-card-title">🏘️ {html.escape(item["name"])}</div>',
                                unsafe_allow_html=True)
                    chips([(item["type"], ""), (item["code"], "grey")])
                    st.markdown(
                        f'<div class="pc-card-body">'
                        f'<b>State:</b> {html.escape(item["state"])}<br>'
                        f'<b>District:</b> {html.escape(item["district"])}<br>'
                        f'<b>Block:</b> {html.escape(item["block"])}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    st.caption("⚠️ Prototype record.")

    st.link_button("Open Ministry of Panchayati Raj — LGD →",
                   "https://panchayat.gov.in/en/lgd/",
                   use_container_width=True)


# ---- SCHEMES ----
elif page == "schemes":
    render_hero("🔎", "Find Government Schemes",
                "Search central schemes by keyword or category. Every result links to its official portal.")

    render_global_search()

    st.write("")

    with st.container(border=True):
        s1, s2 = st.columns([2, 1])
        with s1:
            query = st.text_input("Search", placeholder="e.g. farmer, housing, pension",
                                  key="sch_query")
        with s2:
            cats = st.multiselect("Category", SCHEME_CATEGORIES,
                                  default=[], key="sch_cats",
                                  placeholder="All categories")

    results = list(SCHEMES)
    if query:
        q = query.lower()
        results = [s for s in results
                   if q in s["name"].lower()
                   or q in s["full_name"].lower()
                   or q in s["description"].lower()
                   or any(q in k for k in s["keywords"])]
    if cats:
        results = [s for s in results if s["category"] in cats]

    section(f"📦 Results: {len(results)}")

    if not results:
        st.warning("No matching schemes.")
    else:
        cols = st.columns(2)
        for i, s in enumerate(results):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f'<div class="pc-card-title">{html.escape(s["name"])}</div>'
                                f'<div class="pc-card-sub">{html.escape(s["full_name"])}</div>',
                                unsafe_allow_html=True)
                    chips([(s["category"], ""), (s["level"], "blue")])
                    st.markdown(f'<div class="pc-card-body">{html.escape(s["description"])}</div>',
                                unsafe_allow_html=True)
                    st.caption(f"🏛️ {s['ministry']}")
                    st.link_button("Official Source →", s["url"],
                                   use_container_width=True)


# ---- AI ASSISTANT ----
elif page == "ai":
    render_hero("✨", "AI Assistant",
                "Ask Gemini about Indian government schemes, Panchayati Raj, welfare "
                "programmes and civic topics.")

    st.write("")

    if not GEMINI_AVAILABLE:
        st.error("The `google-generativeai` package is not installed. "
                 "Run `pip install google-generativeai` and restart.")
    elif not st.session_state.gemini_api_key and not (
        hasattr(st, "secrets") and st.secrets.get("GEMINI_API_KEY", "")
    ):
        st.warning("🔑 Add your Gemini API key in the sidebar to enable the AI assistant.")
        st.markdown(
            "Don't have a key? Get one free at "
            "[aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)."
        )
    else:
        # Chat history
        for turn in st.session_state.ai_chat:
            role = turn["role"]
            content = html.escape(turn["content"])
            if role == "user":
                st.markdown(f'<div class="pc-chat-user">🧑 {content}</div>',
                            unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="pc-chat-ai">✨ {content}</div>',
                            unsafe_allow_html=True)

        # Suggestion chips (only when empty)
        if not st.session_state.ai_chat:
            st.caption("Try one of these:")
            sugg = st.columns(3)
            suggestions = [
                "What is PM-KISAN and who is eligible?",
                "Explain how MGNREGA works.",
                "How do I find my Gram Panchayat?",
            ]
            for col, s in zip(sugg, suggestions):
                with col:
                    if st.button(s, key=f"sug_{s[:12]}", use_container_width=True):
                        st.session_state.ai_chat.append({"role": "user", "content": s})
                        with st.spinner("Thinking…"):
                            ans, err = ask_gemini(s)
                        st.session_state.ai_chat.append({
                            "role": "assistant",
                            "content": ans if ans else f"⚠️ {err}"
                        })
                        st.rerun()

        # Chat input
        user_msg = st.chat_input("Ask anything about government schemes…")
        if user_msg:
            st.session_state.ai_chat.append({"role": "user", "content": user_msg})
            with st.spinner("Gemini is thinking…"):
                ans, err = ask_gemini(user_msg)
            st.session_state.ai_chat.append({
                "role": "assistant",
                "content": ans if ans else f"⚠️ {err}"
            })
            st.rerun()

        if st.session_state.ai_chat:
            if st.button("🗑️ Clear chat"):
                st.session_state.ai_chat = []
                st.rerun()

        st.caption("⚠️ AI responses may be inaccurate. Always verify on the official portal.")


# ---- UPDATES ----
elif page == "updates":
    render_hero("📢", "Government Updates",
                "Official releases from the Press Information Bureau RSS feed.")

    st.write("")

    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🔄 Refresh", use_container_width=True):
            load_pib_updates.clear()
            st.rerun()

    if not FEEDPARSER_AVAILABLE:
        st.error("Install `feedparser`: `pip install feedparser`")
    else:
        with st.spinner("Fetching latest releases…"):
            try:
                updates = load_pib_updates(PIB_RSS, 12)
                error = None
            except Exception as e:
                updates, error = [], str(e)

        if error:
            st.error("The updates feed is temporarily unavailable.")
            st.caption(f"Detail: {error}")
        elif not updates:
            st.warning("No updates returned.")
        else:
            st.success(f"🟢 {len(updates)} official updates available")
            st.caption("Source: pib.gov.in")
            for item in updates:
                with st.container(border=True):
                    st.markdown(f'<div class="pc-card-title">📰 {html.escape(item["title"])}</div>',
                                unsafe_allow_html=True)
                    if item["published"]:
                        st.caption(f"🕒 {item['published']}")
                    if item["summary"]:
                        st.markdown(f'<div class="pc-card-body">{html.escape(item["summary"])}</div>',
                                    unsafe_allow_html=True)
                    if item["link"]:
                        st.link_button("Read official release →",
                                       item["link"], use_container_width=True)


# ---- SOURCES ----
elif page == "sources":
    render_hero("🏛️", "Official Government Sources",
                "Verified Government of India portals for further reading.")

    st.write("")

    groups = {}
    for s in SOURCES:
        groups.setdefault(s["group"], []).append(s)

    for gname, items in groups.items():
        section(f"• {gname}")
        cols = st.columns(2)
        for i, s in enumerate(items):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f'<div class="pc-card-title">{s["icon"]} {html.escape(s["name"])}</div>',
                                unsafe_allow_html=True)
                    st.markdown(f'<div class="pc-card-body">{html.escape(s["desc"])}</div>',
                                unsafe_allow_html=True)
                    st.link_button("Open official website →", s["url"],
                                   use_container_width=True)


# ---- ABOUT ----
elif page == "about":
    render_hero("ℹ️", "About PanchayatConnect",
                "An independent civic-tech initiative for easier access to "
                "Indian government information.")

    st.write("")

    a, b = st.columns([3, 2])
    with a:
        with st.container(border=True):
            st.markdown('<div class="pc-card-title">🎯 What we are building</div>',
                        unsafe_allow_html=True)
            st.markdown("""
                <div class="pc-card-body">
                <b>1. Local discovery</b> — find your Gram Panchayat in the official hierarchy.<br>
                <b>2. Scheme discovery</b> — search central schemes by need, category or keyword.<br>
                <b>3. Official updates</b> — read releases from the original source.<br>
                <b>4. AI assistance</b> — Gemini-powered answers about civic topics.
                </div>
            """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="pc-card-title">🏗️ Data architecture</div>',
                        unsafe_allow_html=True)
            st.markdown("""
                <div class="pc-card-body">
                Built on authoritative public sources: <b>LGD</b>, <b>data.gov.in</b>,
                <b>MyScheme</b>, and ministry portals. AI responses are grounded
                with a civic-focused system prompt.
                </div>
            """, unsafe_allow_html=True)

    with b:
        with st.container(border=True):
            st.markdown('<div class="pc-card-title">🔐 Disclaimer</div>',
                        unsafe_allow_html=True)
            st.markdown("""
                <div class="pc-card-body">
                PanchayatConnect is <b>not a government website</b>. Information is
                for general awareness. Always verify on the original official source.
                AI answers may be inaccurate and are not scheme eligibility advice.
                </div>
            """, unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown('<div class="pc-card-title">🗺️ Roadmap</div>',
                        unsafe_allow_html=True)
            chips([("Live LGD sync", "amber"),
                   ("Kannada full UI", "amber"),
                   ("RAG on scheme docs", "amber"),
                   ("Offline mode", "grey")])


# ============================================================
# FOOTER
# ============================================================
st.markdown(
    f"""<div class="pc-footer">
        <strong>PanchayatConnect</strong> · Independent Civic-Tech Project · v{APP_VERSION}
        <br>
        Not a government website. Verify information on the original official source.
        <br>
        © {APP_YEAR} PanchayatConnect
    </div>""",
    unsafe_allow_html=True,
)
