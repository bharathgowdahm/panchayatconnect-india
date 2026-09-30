import streamlit as st
import feedparser
from datetime import datetime

# ============================================================
# PanchayatConnect — V1.0 Professional
# ============================================================

st.set_page_config(
    page_title="PanchayatConnect | Civic Information Platform",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# THEME / CSS
# ============================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
    padding: 42px 36px;
    border-radius: 24px;
    background: linear-gradient(135deg, #073b26 0%, #0b5d3b 45%, #14935a 100%);
    color: white;
    margin-bottom: 28px;
    box-shadow: 0 12px 32px rgba(11,93,59,.25);
}
.hero h1 { font-size: 44px; font-weight: 800; margin: 0 0 8px 0; }
.hero p { font-size: 18px; opacity:.95; margin: 0; max-width: 720px; line-height: 1.6; }
.hero-badge {
    display: inline-block; background: rgba(255,255,255,.18);
    padding: 6px 14px; border-radius: 999px;
    font-size: 13px; font-weight: 600; margin-bottom: 14px;
}

.stat-card {
    background: white; border-radius: 18px; padding: 20px;
    border: 1px solid #e9ecef; text-align: center;
    box-shadow: 0 4px 14px rgba(0,0,0,.04);
}
.stat-num { font-size: 30px; font-weight: 800; color: #0b5d3b; }
.stat-label { font-size: 13px; color: #6c757d; font-weight: 600; text-transform: uppercase; letter-spacing:.5px; }

.section-title { font-size: 24px; font-weight: 800; margin: 32px 0 16px 0; color: #1a1a1a; }
.section-sub { color: #6c757d; margin-top: -10px; margin-bottom: 18px; }

.scheme-card { border-radius: 18px!important; padding: 8px 4px!important; }
.tag {
    display:inline-block; background:#e8f5e9; color:#0b5d3b;
    font-size:12px; font-weight:700; padding:4px 12px; border-radius:999px; margin-right:6px;
}
.tag-blue { background:#e3f2fd; color:#0d47a1; }

.footer {
    margin-top: 60px; padding: 28px; text-align: center;
    border-top: 1px solid #e9ecef; color: #6c757d; font-size: 14px;
}
a { text-decoration: none; }
.stButton>button,.stLinkButton>a {
    border-radius: 12px!important; font-weight: 600!important;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA
# ============================================================

SCHEMES = [
    {"name": "PM-KISAN Samman Nidhi", "category": "Agriculture", "level": "Central",
     "description": "Direct income support of ₹6,000/year to eligible farmer families in three instalments.",
     "keywords": ["farmer","agriculture","farm","kisan","crop"],
     "url": "https://pmkisan.gov.in/", "icon": "🌾"},
    {"name": "MGNREGA", "category": "Employment", "level": "Central",
     "description": "Guaranteed 100 days of wage employment per year to rural households.",
     "keywords": ["employment","job","work","rural","wage"],
     "url": "https://nrega.nic.in/", "icon": "👷"},
    {"name": "PMAY-Gramin", "category": "Housing", "level": "Central",
     "description": "Financial assistance for construction of pucca houses for rural homeless families.",
     "keywords": ["house","housing","home","rural","awas"],
     "url": "https://pmayg.nic.in/", "icon": "🏠"},
    {"name": "Jal Jeevan Mission", "category": "Water", "level": "Central",
     "description": "Functional household tap water connection to every rural household.",
     "keywords": ["water","tap","jal","drinking"],
     "url": "https://jaljeevanmission.gov.in/", "icon": "💧"},
    {"name": "Ayushman Bharat PM-JAY", "category": "Health", "level": "Central",
     "description": "Health insurance cover of ₹5 lakh per family per year for secondary & tertiary care.",
     "keywords": ["health","hospital","insurance","medical","ayushman"],
     "url": "https://beneficiary.nha.gov.in/", "icon": "🏥"},
    {"name": "【entity-Digital India¦canonical_name=Digital India】", "category": "Digital Services", "level": "Central",
     "description": "Digital infrastructure, digital literacy and digital delivery of government services.",
     "keywords": ["digital","online","service","technology","internet"],
     "url": "https://www.digitalindia.gov.in/", "icon": "💻"},
]

PANCHAYATS = [
    {"state":"Karnataka","district":"Hassan","block":"Hassan","name":"Shantigrama Gram Panchayat","type":"Gram Panchayat","population":"8,240"},
    {"state":"Karnataka","district":"Hassan","block":"Arkalgud","name":"Konanur Gram Panchayat","type":"Gram Panchayat","population":"6,150"},
    {"state":"Karnataka","district":"Mysuru","block":"Mysuru","name":"Jayapura Gram Panchayat","type":"Gram Panchayat","population":"9,800"},
    {"state":"Karnataka","district":"Bengaluru Rural","block":"Devanahalli","name":"Vijayapura Gram Panchayat","type":"Gram Panchayat","population":"12,400"},
]

CATEGORIES = ["All"] + sorted(set(s["category"] for s in SCHEMES))

TEXT = {
    "English": {
        "tagline": "Government information, connected to your Panchayat.",
        "hero_badge": "● LIVE CIVIC PLATFORM • V1.0",
        "hero_sub": "Discover government schemes, explore your local Panchayat, and stay updated with official releases — all in one trusted place.",
        "explore": "Quick Access", "featured": "Featured Schemes",
    },
    "ಕನ್ನಡ": {
        "tagline": "ಸರ್ಕಾರಿ ಮಾಹಿತಿ, ನಿಮ್ಮ ಪಂಚಾಯತಿಗೆ ಸಂಪರ್ಕ.",
        "hero_badge": "● ಲೈವ್ ನಾಗರಿಕ ವೇದಿಕೆ • V1.0",
        "hero_sub": "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳನ್ನು ಹುಡುಕಿ, ನಿಮ್ಮ ಸ್ಥಳೀಯ ಪಂಚಾಯತಿಯನ್ನು ಅನ್ವೇಷಿಸಿ, ಅಧಿಕೃತ ಪ್ರಕಟಣೆಗಳೊಂದಿಗೆ ನವೀಕೃತವಾಗಿರಿ.",
        "explore": "ತ್ವರಿತ ಪ್ರವೇಶ", "featured": "ಪ್ರಮುಖ ಯೋಜನೆಗಳು",
    }
}

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown("## 🇮🇳 PanchayatConnect")
    language = st.selectbox("🌐 Language / ಭಾಷೆ", ["English", "ಕನ್ನಡ"])
    t = TEXT[language]
    st.caption(t["tagline"])
    st.divider()

    page = st.radio("Navigation", ["🏠 Dashboard","🏘️ Panchayat Directory","🔎 Find Schemes","📢 Government Updates","🏛️ Official Sources","ℹ️ About"],
                    label_visibility="collapsed")

    st.divider()
    st.markdown("### 📍 My Location")
    state = st.selectbox("State", ["Karnataka","Kerala","Tamil Nadu","Maharashtra","Telangana","Andhra Pradesh"])
    district = st.text_input("District", placeholder="e.g. Hassan")
    panchayat_input = st.text_input("Panchayat", placeholder="Enter Panchayat name")

    st.divider()
    st.caption("🔐 Independent civic-tech project. Always verify with official sources.")

# ============================================================
# HELPERS
# ============================================================

def scheme_card(s):
    with st.container(border=True):
        st.markdown(f"### {s['icon']} {s['name']}")
        st.markdown(f"<span class='tag'>{s['category']}</span><span class='tag tag-blue'>{s['level']}</span>", unsafe_allow_html=True)
        st.write("")
        st.write(s["description"])
        st.link_button("🏛️ Official Source →", s["url"], use_container_width=True)

def location_str():
    loc = state
    if district: loc += f" • {district}"
    if panchayat_input: loc += f" • {panchayat_input}"
    return loc

# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":
    st.markdown(f"""
    <div class="hero">
        <div class="hero-badge">{t['hero_badge']}</div>
        <h1>🇮🇳 PanchayatConnect</h1>
        <p>{t['hero_sub']}</p>
    </div>
    """, unsafe_allow_html=True)

    st.success(f"📍 **Selected location:** {location_str()}")

    c1,c2,c3,c4 = st.columns(4)
    for col, num, label in zip([c1,c2,c3,c4],
        [len(SCHEMES), len(PANCHAYATS), "2", "1.0"],
        ["Schemes Listed","Panchayats","Languages","Version"]):
        col.markdown(f"<div class='stat-card'><div class='stat-num'>{num}</div><div class='stat-label'>{label}</div></div>", unsafe_allow_html=True)

    st.markdown(f"<div class='section-title'>🚀 {t['explore']}</div>", unsafe_allow_html=True)
    a,b,c = st.columns(3)
    with a:
        with st.container(border=True):
            st.markdown("### 🏘️ Directory")
            st.write("Find your Gram Panchayat by district and block.")
            if st.button("Open Directory →", key="g1", use_container_width=True):
                st.switch_page("app.py")
    with b:
        with st.container(border=True):
            st.markdown("### 🔎 Scheme Finder")
            st.write("Search 6+ schemes by need, keyword or category.")
    with c:
        with st.container(border=True):
            st.markdown("### 📢 Live Updates")
            st.write("Official 【entity-PIB¦canonical_name=PIB】 press releases, auto-updated.")

    st.markdown(f"<div class='section-title'>⭐ {t['featured']}</div><div class='section-sub'>Most accessed citizen schemes</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for col, s in zip(cols, SCHEMES[:3]):
        with col: scheme_card(s)

# ============================================================
# DIRECTORY
# ============================================================

elif page == "🏘️ Panchayat Directory":
    st.title("🏘️ Panchayat Directory")
    st.caption("Powered by Local Government Directory (LGD) architecture • Ministry of Panchayati Raj")
    st.divider()

    col1, col2, col3 = st.columns([2,2,3])
    with col1:
        d_state = st.selectbox("State", ["Karnataka"], key="ds")
    with col2:
        d_dist = st.selectbox("District", ["All Districts","Hassan","Mysuru","Bengaluru Rural"], key="dd")
    with col3:
        q = st.text_input("🔎 Search Panchayat", placeholder="Type name, block...")

    results = PANCHAYATS
    if d_dist!= "All Districts":
        results = [p for p in results if p["district"]==d_dist]
    if q:
        ql = q.lower()
        results = [p for p in results if ql in p["name"].lower() or ql in p["block"].lower()]

    st.subheader(f"Results: {len(results)} Panchayats")
    for p in results:
        with st.container(border=True):
            c1,c2 = st.columns([3,1])
            with c1:
                st.markdown(f"### 🏘️ {p['name']}")
                st.caption(f"{p['type']} • LGD Linked")
                st.write(f"📍 {p['block']} Block, {p['district']} District, {p['state']}")
                st.write(f"👥 Population: ~{p['population']}")
            with c2:
                st.link_button("View LGD →", "https://lgdirectory.gov.in/", use_container_width=True)
            st.caption("⚠️ Demo record — production will fetch live LGD codes.")

# ============================================================
# SCHEMES
# ============================================================

elif page == "🔎 Find Schemes":
    st.title("🔎 Find Government Schemes")
    st.caption("Search by need — farmer, housing, job, water, health...")
    st.divider()

    c1,c2 = st.columns([3,1])
    with c1:
        search = st.text_input("Search", placeholder="Try: farmer, housing, employment, water", label_visibility="collapsed")
    with c2:
        cat = st.selectbox("Category", CATEGORIES, label_visibility="collapsed")

    results = SCHEMES
    if search:
        ql = search.lower()
        results = [s for s in results if ql in s["name"].lower() or ql in s["description"].lower()
                   or ql in s["category"].lower() or any(ql in k for k in s["keywords"])]
    if cat!= "All":
        results = [s for s in results if s["category"]==cat]

    st.subheader(f"Found {len(results)} schemes")
    if not results:
        st.warning("No schemes match. Try 'farmer', 'house', 'job'.")
    cols = st.columns(2)
    for i,s in enumerate(results):
        with cols[i%2]: scheme_card(s)

# ============================================================
# UPDATES
# ============================================================

elif page == "📢 Government Updates":
    st.title("📢 Government Updates")
    st.caption(f"Official 【entity-PIB¦canonical_name=PIB】 feed • Last checked {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
    st.divider()

    PIB_RSS = "https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1"
    with st.spinner("Fetching official releases..."):
        try:
            feed = feedparser.parse(PIB_RSS)
            if feed.entries:
                st.success(f"🟢 {len(feed.entries)} live updates from 【entity-PIB¦canonical_name=PIB】")
                for e in feed.entries[:12]:
                    with st.container(border=True):
                        st.markdown(f"#### 📰 {e.get('title','Government Update')}")
                        if e.get("published"): st.caption(f"📅 {e.get('published')}")
                        st.write(e.get("summary","Open official release for full details.")[:350]+"...")
                        if e.get("link"):
                            st.link_button("Read Official Release →", e["link"])
            else:
                st.warning("No updates at the moment. Please try again later.")
        except Exception:
            st.error("Feed temporarily unavailable. Visit 【entity-pib¦canonical_name=PIB】.gov.in directly.")
            st.link_button("Open 【entity-PIB¦canonical_name=PIB】 Website →", "https://pib.gov.in/")

# ============================================================
# SOURCES
# ============================================================

elif page == "🏛️ Official Sources":
    st.title("🏛️ Official Government Sources")
    st.caption("Always verify information on the original government portal.")
    st.divider()
    sources = [
        ("🇮🇳 National Portal","india.gov.in","Single window for all government services.","https://www.india.gov.in/","🔵"),
        ("📊 Open Data","data.gov.in","Datasets, APIs and visualizations from ministries.","https://data.gov.in/","🟢"),
        ("🏘️ Panchayati Raj","panchayat.gov.in","Ministry schemes, circulars and LGD access.","https://panchayat.gov.in/","🟠"),
        ("🏛️ LGD Directory","lgdirectory.gov.in","Official codes for States, Districts, Blocks, Panchayats.","https://lgdirectory.gov.in/","🟣"),
        ("📰 Press Bureau","【entity-pib¦canonical_name=PIB】.gov.in","Official press releases and announcements.","https://pib.gov.in/","🔴"),
        ("💻 MyGov","mygov.in","Citizen engagement and participatory governance.","https://www.mygov.in/","🟡"),
    ]
    cols = st.columns(3)
    for i,(title,domain,desc,url,color) in enumerate(sources):
        with cols[i%3]:
            with st.container(border=True):
                st.markdown(f"### {title}")
                st.caption(domain)
                st.write(desc)
                st.link_button("Visit Official Site →", url, use_container_width=True)

# ============================================================
# ABOUT
# ============================================================

elif page == "ℹ️ About":
    st.title("ℹ️ About PanchayatConnect")
    c1,c2 = st.columns(2)
    with c1:
        with st.container(border=True):
            st.markdown("### 🎯 Mission")
            st.write("Make every government scheme, Panchayat office, and official update discoverable for every rural citizen — in their language.")
            st.markdown("### ✨ Features")
            st.write("- Panchayat discovery (LGD-ready)\n- Smart scheme search\n- Live 【entity-PIB¦canonical_name=PIB】 updates\n- Kannada + English\n- 100% source-transparent")
    with c2:
        with st.container(border=True):
            st.markdown("### 🏗️ Data Architecture")
            st.write("**Sources:** LGD, data.gov.in, 【entity-PIB¦canonical_name=PIB】, india.gov.in\n\n**Stack:** Streamlit, Feedparser, Open APIs\n\n**Roadmap:** AI assistant, offline mode, voice search in Kannada.")
            st.markdown("### 🔐 Disclaimer")
            st.warning("PanchayatConnect is **not a government website**. Always verify eligibility and details on official portals.")

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
<b>🇮🇳 PanchayatConnect</b> • Independent Civic-Tech Project • V1.0<br>
Built for citizens • Powered by official open data • Verify on official sources
</div>
""", unsafe_allow_html=True)
