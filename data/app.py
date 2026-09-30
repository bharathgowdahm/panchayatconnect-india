import streamlit as st
import feedparser
import os
from datetime import datetime

# Gemini setup
try:
    import google.generativeai as genai
    GEMINI_KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
    # OR paste directly: GEMINI_KEY = "AIzaSy..."
    if GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
        gemini_model = genai.GenerativeModel("gemini-1.5-flash")
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
except:
    GEMINI_AVAILABLE = False

st.set_page_config(page_title="PanchayatConnect", page_icon="🇮🇳", layout="wide")

# --- CSS ---
st.markdown("""
<style>
.hero{padding:36px;border-radius:20px;background:linear-gradient(135deg,#073b26,#14935a);color:white;margin-bottom:20px}
.stat-card{background:white;border-radius:16px;padding:18px;border:1px solid #eee;text-align:center}
.stat-num{font-size:28px;font-weight:800;color:#0b5d3b}
.tag{display:inline-block;background:#e8f5e9;color:#0b5d3b;font-size:12px;font-weight:700;padding:4px 12px;border-radius:999px;margin-right:6px}
.search-box input{font-size:18px!important;padding:14px!important;border-radius:14px!important}
</style>
""", unsafe_allow_html=True)

# --- STATES & DISTRICTS (Fixed) ---
STATES_DISTRICTS = {
    "Karnataka": ["Bengaluru Urban","Bengaluru Rural","Mysuru","Hassan","Tumakuru","Mandya","Belagavi","Dakshina Kannada","Shivamogga","Ballari"],
    "Kerala": ["Thiruvananthapuram","Kochi","Kozhikode","Thrissur","Kollam","Palakkad"],
    "Tamil Nadu": ["Chennai","Coimbatore","Madurai","Salem","Trichy","Vellore","Erode"],
    "Maharashtra": ["Mumbai","Pune","Nagpur","Nashik","Thane","Aurangabad","Solapur"],
    "Telangana": ["Hyderabad","Warangal","Nizamabad","Karimnagar","Khammam"],
    "Andhra Pradesh": ["Visakhapatnam","Vijayawada","Guntur","Tirupati","Kurnool","Anantapur"],
    "Uttar Pradesh": ["Lucknow","Kanpur","Varanasi","Agra","Meerut","Prayagraj"],
    "Bihar": ["Patna","Gaya","Muzaffarpur","Bhagalpur","Darbhanga"],
    "West Bengal": ["Kolkata","Howrah","Darjeeling","Siliguri","Durgapur"],
    "Rajasthan": ["Jaipur","Jodhpur","Udaipur","Kota","Ajmer"],
    "Gujarat": ["Ahmedabad","Surat","Vadodara","Rajkot"],
    "Madhya Pradesh": ["Bhopal","Indore","Gwalior","Jabalpur"],
    "Odisha": ["Bhubaneswar","Cuttack","Rourkela","Sambalpur"],
    "Punjab": ["Ludhiana","Amritsar","Jalandhar","Patiala"],
    "Haryana": ["Gurugram","Faridabad","Panipat","Ambala"],
    "Delhi": ["New Delhi","North Delhi","South Delhi","East Delhi","West Delhi"],
}

ALL_STATES = sorted(list(STATES_DISTRICTS.keys()))

SCHEMES = [
    {"name":"PM-KISAN","category":"Agriculture","level":"Central","description":"₹6000/year income support to farmer families.","keywords":["farmer","kisan","agriculture"],"url":"https://pmkisan.gov.in/","icon":"🌾"},
    {"name":"MGNREGA","category":"Employment","level":"Central","description":"100 days guaranteed rural wage employment.","keywords":["job","employment","work"],"url":"https://nrega.nic.in/","icon":"👷"},
    {"name":"PMAY-Gramin","category":"Housing","level":"Central","description":"Pucca house assistance for rural families.","keywords":["house","housing","awas"],"url":"https://pmayg.nic.in/","icon":"🏠"},
    {"name":"Ayushman Bharat","category":"Health","level":"Central","description":"₹5 lakh health insurance per family.","keywords":["health","hospital","insurance"],"url":"https://beneficiary.nha.gov.in/","icon":"🏥"},
    {"name":"Jal Jeevan Mission","category":"Water","level":"Central","description":"Tap water to every rural household.","keywords":["water","jal","tap"],"url":"https://jaljeevanmission.gov.in/","icon":"💧"},
]

PANCHAYATS = [
    {"state":"Karnataka","district":"Hassan","block":"Hassan","name":"Shantigrama Gram Panchayat","type":"Gram Panchayat"},
    {"state":"Karnataka","district":"Mysuru","block":"Mysuru","name":"Jayapura Gram Panchayat","type":"Gram Panchayat"},
    {"state":"Tamil Nadu","district":"Coimbatore","block":"Pollachi","name":"Kinathukadavu Gram Panchayat","type":"Gram Panchayat"},
]

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("## 🇮🇳 PanchayatConnect")
    page = st.radio("Go to", ["🏠 Dashboard","🤖 AI Search","🏘️ Panchayat Directory","🔎 Find Schemes","📢 Updates","🏛️ Sources","ℹ️ About"], label_visibility="collapsed")
    st.divider()
    st.markdown("### 📍 My Location")
    # FIXED: State -> District cascading
    sel_state = st.selectbox("State", ALL_STATES, index=ALL_STATES.index("Karnataka"))
    sel_district = st.selectbox("District", STATES_DISTRICTS[sel_state])
    sel_panchayat = st.text_input("Panchayat", placeholder="Enter Panchayat name")
    language = st.selectbox("Language", ["English","ಕನ್ನಡ"])

def gemini_ask(prompt):
    if not GEMINI_AVAILABLE:
        return "⚠️ Add your GOOGLE_API_KEY to enable AI Search. Get free key from aistudio.google.com"
    try:
        full_prompt = f"""You are PanchayatConnect AI, a helpful Indian civic assistant.
        Answer about Indian government schemes, panchayats, documents, eligibility in simple language.
        Always mention official source to verify. User question: {prompt}"""
        resp = gemini_model.generate_content(full_prompt)
        return resp.text
    except Exception as e:
        return f"AI temporarily unavailable: {e}"

def scheme_card(s):
    with st.container(border=True):
        st.markdown(f"### {s['icon']} {s['name']}")
        st.markdown(f"<span class='tag'>{s['category']}</span><span class='tag'>{s['level']}</span>", unsafe_allow_html=True)
        st.write(s["description"])
        st.link_button("🏛️ Official Source", s["url"])

# --- DASHBOARD ---
if page == "🏠 Dashboard":
    st.markdown(f'<div class="hero"><h1>🇮🇳 PanchayatConnect</h1><p>Government schemes, Panchayats & official updates — now with AI search.</p></div>', unsafe_allow_html=True)
    
    # GLOBAL SEARCH BAR
    st.markdown("### 🔎 Search anything")
    gq = st.text_input("", placeholder="Try: 'PM Kisan eligibility', 'Hassan panchayat list', 'housing scheme for rural'...", key="global_search", label_visibility="collapsed")
    if gq:
        st.info(f"Showing results for: **{gq}**")
        # quick scheme match
        ql = gq.lower()
        matched = [s for s in SCHEMES if ql in s["name"].lower() or ql in s["description"].lower() or any(ql in k for k in s["keywords"])]
        if matched:
            cols = st.columns(2)
            for i,s in enumerate(matched):
                with cols[i%2]: scheme_card(s)
        # AI button
        if st.button("🤖 Ask Gemini AI about this"):
            with st.spinner("Thinking..."):
                st.markdown(gemini_ask(gq))

    st.success(f"📍 {sel_state} • {sel_district}" + (f" • {sel_panchayat}" if sel_panchayat else ""))
    c1,c2,c3,c4 = st.columns(4)
    for col,n,l in zip([c1,c2,c3,c4],[len(SCHEMES),len(PANCHAYATS),"2","1.0"],["Schemes","Panchayats","Languages","Version"]):
        col.markdown(f"<div class='stat-card'><div class='stat-num'>{n}</div><div>{l}</div></div>", unsafe_allow_html=True)

# --- AI SEARCH PAGE ---
elif page == "🤖 AI Search":
    st.title("🤖 Gemini AI Civic Assistant")
    st.caption("Ask about schemes, eligibility, documents, panchayat services in English / Kannada")
    if not GEMINI_AVAILABLE:
        st.warning("Add GOOGLE_API_KEY in secrets or env to activate. Get free at aistudio.google.com")
        st.code('GOOGLE_API_KEY = "paste_here"', language="python")
    
    query = st.text_area("Ask your question", placeholder="Example: I am a farmer in Hassan, Karnataka. Which schemes am I eligible for?", height=100)
    col1,col2 = st.columns([1,3])
    with col1:
        ask = st.button("Ask AI ✨", type="primary", use_container_width=True)
    if ask and query:
        with st.spinner("Gemini is thinking..."):
            ans = gemini_ask(f"Location: {sel_state}, {sel_district}. Question: {query}")
            st.markdown("### Answer")
            st.markdown(ans)
            st.caption("⚠️ Verify on official portal. AI can make mistakes.")
    
    st.divider()
    st.markdown("### 💡 Try these")
    for ex in ["What documents needed for PMAY-G?", "PM-KISAN eligibility criteria", "How to apply for MGNREGA job card?"]:
        if st.button(ex, key=ex):
            with st.spinner("..."):
                st.markdown(gemini_ask(ex))

# --- DIRECTORY (FIXED) ---
elif page == "🏘️ Panchayat Directory":
    st.title("🏘️ Panchayat Directory")
    c1,c2,c3 = st.columns(3)
    with c1:
        f_state = st.selectbox("State", ALL_STATES, key="f_state")
    with c2:
        # District list updates automatically based on state - THIS WAS THE BUG
        f_dist = st.selectbox("District", ["All Districts"] + STATES_DISTRICTS[f_state], key="f_dist")
    with c3:
        f_q = st.text_input("Search Panchayat", placeholder="Type name...")
    
    results = [p for p in PANCHAYATS if p["state"]==f_state]
    if f_dist != "All Districts":
        results = [p for p in results if p["district"]==f_dist]
    if f_q:
        results = [p for p in results if f_q.lower() in p["name"].lower()]
    
    st.subheader(f"Found {len(results)}")
    for p in results:
        with st.container(border=True):
            st.markdown(f"### 🏘️ {p['name']}")
            st.write(f"{p['block']} Block, {p['district']}, {p['state']}")

# --- Other pages (schemes, updates, sources, about) keep same as before ---
elif page == "🔎 Find Schemes":
    st.title("🔎 Find Schemes")
    s = st.text_input("Search schemes", placeholder="farmer, housing, job...")
    cat = st.selectbox("Category", ["All"]+sorted(set(x["category"] for x in SCHEMES)))
    res = SCHEMES
    if s:
        ql=s.lower(); res=[x for x in res if ql in x["name"].lower() or ql in x["description"].lower()]
    if cat!="All": res=[x for x in res if x["category"]==cat]
    for x in res: scheme_card(x)

elif page == "📢 Updates":
    st.title("📢 Government Updates")
    feed = feedparser.parse("https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1")
    for e in feed.entries[:10]:
        with st.container(border=True):
            st.markdown(f"#### {e.get('title')}")
            st.caption(e.get('published',''))
            if e.get('link'): st.link_button("Read →", e.get('link'))

elif page == "🏛️ Sources":
    st.title("🏛️ Official Sources")
    for name,url in [("India.gov.in","https://www.india.gov.in/"),("data.gov.in","https://data.gov.in/"),("MoPR","https://panchayat.gov.in/"),("PIB","https://pib.gov.in/")]:
        with st.container(border=True):
            st.markdown(f"### {name}"); st.link_button("Open →", url)

elif page == "ℹ️ About":
    st.title("About")
    st.write("PanchayatConnect is an independent civic-tech project. Not a government website. Verify on official portals.")
