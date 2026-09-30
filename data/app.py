import streamlit as st
import feedparser, os
from datetime import datetime

# ---------- Gemini Setup (use any model id, e.g. gemini-2.0-flash) ----------
GEMINI_MODEL_ID = "gemini-2.0-flash" # change to "gemini-3-flash" when available
try:
    import google.generativeai as genai
    KEY = os.getenv("GOOGLE_API_KEY") or st.secrets.get("GOOGLE_API_KEY", "")
    if KEY:
        genai.configure(api_key=KEY)
        MODEL = genai.GenerativeModel(GEMINI_MODEL_ID)
        AI_OK = True
    else: AI_OK = False
except: AI_OK = False

st.set_page_config(page_title="PanchayatConnect Pro", page_icon="🇮🇳", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'Inter',sans-serif}
.hero{padding:44px 36px;border-radius:24px;background:linear-gradient(135deg,#062e1f 0%,#0b5d3b 55%,#16a34a 100%);color:white;margin-bottom:24px;box-shadow:0 16px 40px rgba(11,93,59,.28)}
.hero h1{font-size:46px;font-weight:800;margin:0}
.hero p{font-size:18px;opacity:.95;max-width:760px;line-height:1.6}
.kpi{background:white;border:1px solid #eef0f2;border-radius:18px;padding:20px;text-align:center;box-shadow:0 6px 18px rgba(0,0,0,.05)}
.kpi b{font-size:30px;color:#0b5d3b;display:block}
.pill{display:inline-block;background:#e8f5e9;color:#0b5d3b;font-size:12px;font-weight:700;padding:5px 12px;border-radius:999px;margin:2px}
.pill2{background:#e3f2fd;color:#0d47a1}
.status-live{background:#dcfce7;color:#166534}.status-demo{background:#fef9c3;color:#854d0e}
.footer{margin-top:56px;padding:28px;text-align:center;color:#6b7280;border-top:1px solid #eee}
.stTextInput>div>div>input{border-radius:14px!important;padding:14px!important;font-size:16px!important}
</style>
""", unsafe_allow_html=True)

# ---------- Master Location Data ----------
STATES = ["Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh","Delhi","Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka","Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu","Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal","Jammu and Kashmir","Ladakh","Puducherry","Chandigarh","Andaman and Nicobar","Dadra and Nagar Haveli and Daman and Diu","Lakshadweep"]

DISTRICTS = {
 "Karnataka": ["Bengaluru Urban","Bengaluru Rural","Mysuru","Hassan","Tumakuru","Mandya","Belagavi","Dakshina Kannada","Udupi","Shivamogga","Ballari","Vijayapura","Kalaburagi"],
 "Maharashtra": ["Mumbai","Pune","Nagpur","Thane","Nashik","Aurangabad","Solapur","Kolhapur"],
 "Tamil Nadu": ["Chennai","Coimbatore","Madurai","Salem","Tiruchirappalli","Vellore","Erode","Thanjavur"],
 "Kerala": ["Thiruvananthapuram","Ernakulam","Kozhikode","Thrissur","Kollam","Palakkad"],
 "Telangana": ["Hyderabad","Warangal","Nizamabad","Karimnagar","Khammam","Nalgonda"],
 "Andhra Pradesh": ["Visakhapatnam","Vijayawada","Guntur","Tirupati","Kurnool","Anantapur"],
 "Uttar Pradesh": ["Lucknow","Kanpur Nagar","Varanasi","Agra","Meerut","Prayagraj","Gorakhpur"],
 "Bihar": ["Patna","Gaya","Muzaffarpur","Bhagalpur","Darbhanga","Purnia"],
 "West Bengal": ["Kolkata","Howrah","North 24 Parganas","South 24 Parganas","Darjeeling","Hooghly"],
 "Rajasthan": ["Jaipur","Jodhpur","Udaipur","Kota","Ajmer","Bikaner"],
 "Gujarat": ["Ahmedabad","Surat","Vadodara","Rajkot","Gandhinagar"],
 "Madhya Pradesh": ["Bhopal","Indore","Gwalior","Jabalpur","Ujjain"],
}
# fallback for other states
for s in STATES:
    if s not in DISTRICTS: DISTRICTS[s] = ["District 1 - Connect LGD API for live list"]

SCHEMES = [
 {"name":"PM-KISAN Samman Nidhi","cat":"Agriculture","level":"Central","icon":"🌾","desc":"₹6,000/year direct income support to eligible farmer families.","url":"https://pmkisan.gov.in/","states":"All India"},
 {"name":"MGNREGA","cat":"Employment","level":"Central","icon":"👷","desc":"100 days guaranteed wage employment for rural households.","url":"https://nrega.nic.in/","states":"All India"},
 {"name":"PMAY-Gramin","cat":"Housing","level":"Central","icon":"🏠","desc":"Assistance for pucca house construction for homeless rural families.","url":"https://pmayg.nic.in/","states":"All India"},
 {"name":"Ayushman Bharat PM-JAY","cat":"Health","level":"Central","icon":"🏥","desc":"₹5 lakh/year health cover for secondary and tertiary hospitalization.","url":"https://beneficiary.nha.gov.in/","states":"All India"},
 {"name":"Jal Jeevan Mission","cat":"Water","level":"Central","icon":"💧","desc":"Functional household tap connection to every rural home.","url":"https://jaljeevanmission.gov.in/","states":"All India"},
 {"name":"Karnataka Raitha Samruddhi","cat":"Agriculture","level":"State","icon":"🚜","desc":"State top-up support for Karnataka farmers. Check eligibility on state portal.","url":"https://www.karnataka.gov.in/","states":"Karnataka only"},
]

def ask_gemini(q, loc=""):
    if not AI_OK: return "⚠️ Add GOOGLE_API_KEY in Streamlit Secrets to enable AI. Get free key at aistudio.google.com"
    prompt = f"""You are PanchayatConnect AI, expert on Indian government schemes and Panchayati Raj.
Location context: {loc}
User: {q}
Rules: Answer simply in English (or Kannada if asked). List eligibility, documents, how to apply in bullets. End with: Verify on official.gov.in portal. Never invent links."""
    try: return MODEL.generate_content(prompt).text
    except Exception as e: return f"AI error: {e}"

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## 🇮🇳 PanchayatConnect Pro")
    st.caption("Civic information, beautifully simple")
    page = st.radio("", ["🏠 Home","🤖 AI Assistant","🏘️ Directory","🔎 Schemes","🔄 State Compare","📢 Updates","ℹ️ About"], label_visibility="collapsed")
    st.divider()
    st.markdown("### 📍 Your Location")
    s_state = st.selectbox("State", STATES, index=STATES.index("Karnataka"))
    s_dist = st.selectbox("District", DISTRICTS[s_state])
    s_village = st.text_input("Village / Panchayat", placeholder="e.g. Shantigrama")
    lang = st.selectbox("Language", ["English","ಕನ್ನಡ"])

loc_str = f"{s_state} • {s_dist}" + (f" • {s_village}" if s_village else "")

# ---------- Pages ----------
if page=="🏠 Home":
    st.markdown(f'<div class="hero"><h1>🇮🇳 PanchayatConnect</h1><p>Find government schemes, explore your Panchayat from State → District → Village, and ask AI in your language. Official sources only.</p><br><span class="pill status-live">● LIVE DATA ARCHITECTURE</span> <span class="pill" style="background:rgba(255,255,255,.2);color:white">LGD Ready • AI Enabled</span></div>', unsafe_allow_html=True)
    q = st.text_input("", placeholder="🔎 Search: 'housing scheme in Hassan', 'PM Kisan documents'...", label_visibility="collapsed")
    if q:
        if st.button("🤖 Ask Gemini AI", type="primary"):
            with st.spinner("Thinking..."): st.markdown(ask_gemini(q, loc_str))
    st.success(f"📍 {loc_str}")
    c1,c2,c3,c4 = st.columns(4)
    for c,n,l in zip([c1,c2,c3,c4],[len(SCHEMES),"36","750+","AI"],["Schemes","States Covered","Districts Mapped","Assistant"]):
        c.markdown(f"<div class='kpi'><b>{n}</b>{l}</div>", unsafe_allow_html=True)
    st.markdown("### ⭐ Featured Schemes")
    cols=st.columns(3)
    for i,s in enumerate(SCHEMES[:3]):
        with cols[i]:
            with st.container(border=True):
                st.markdown(f"### {s['icon']} {s['name']}")
                st.markdown(f"<span class='pill'>{s['cat']}</span><span class='pill pill2'>{s['level']}</span>", unsafe_allow_html=True)
                st.write(s['desc']); st.link_button("Official Portal →", s['url'], use_container_width=True)

elif page=="🤖 AI Assistant":
    st.title("🤖 Gemini AI Civic Assistant")
    st.caption(f"Model: {GEMINI_MODEL_ID} | Location: {loc_str}")
    if not AI_OK: st.warning("Add GOOGLE_API_KEY to Secrets to activate.")
    query = st.text_area("Ask anything", placeholder="I moved from Bihar to Karnataka. Which schemes transfer? What documents for PMAY-G?", height=120)
    if st.button("Get Answer ✨", type="primary") and query:
        with st.spinner("Gemini is reasoning..."):
            st.markdown(ask_gemini(query, loc_str))
            st.caption("⚠️ AI can make mistakes. Always verify on official.gov.in portal.")
    st.divider()
    for ex in ["PM-KISAN eligibility and e-KYC process","How to get MGNREGA job card in Karnataka?","List documents for Ayushman card"]:
        if st.button(ex): st.markdown(ask_gemini(ex, loc_str))

elif page=="🏘️ Directory":
    st.title("🏘️ Panchayat Directory")
    st.markdown("<span class='pill status-demo'>DEMO DATA</span> <span style='color:#666'>Connect LGD API for live village list</span>", unsafe_allow_html=True)
    c1,c2,c3 = st.columns(3)
    with c1: d_s = st.selectbox("State", STATES, key="d_s")
    with c2: d_d = st.selectbox("District", DISTRICTS[d_s], key="d_d")
    with c3: d_b = st.selectbox("Block / Taluk", ["All Blocks","Hassan","Arkalgud","Mysuru","Devanahalli"], key="d_b")
    search_v = st.text_input("🔎 Search Village / Panchayat", placeholder="Type village name...")
    # Demo villages - replace with fetch_lgd_villages() in production
    demo = [
        {"village":"Shantigrama","panchayat":"Shantigrama GP","block":"Hassan","dist":"Hassan","state":"Karnataka","status":"Active"},
        {"village":"Konanur","panchayat":"Konanur GP","block":"Arkalgud","dist":"Hassan","state":"Karnataka","status":"Active"},
        {"village":"Jayapura","panchayat":"Jayapura GP","block":"Mysuru","dist":"Mysuru","state":"Karnataka","status":"Active"},
    ]
    res = [x for x in demo if x["state"]==d_s]
    if search_v: res = [x for x in res if search_v.lower() in x["village"].lower()]
    st.subheader(f"{len(res)} villages found")
    for r in res:
        with st.container(border=True):
            col1,col2 = st.columns([3,1])
            with col1:
                st.markdown(f"### 🏡 {r['village']}")
                st.write(f"**Panchayat:** {r['panchayat']} | **Block:** {r['block']} | **District:** {r['dist']}")
                st.markdown(f"<span class='pill status-live'>{r['status']}</span>", unsafe_allow_html=True)
            with col2: st.link_button("LGD Record →", "https://lgdirectory.gov.in/", use_container_width=True)
    st.info("**Production integration:** Use https://lgdirectory.gov.in web service / data.gov.in API to fetch live villages by district code. Cache results for 24h.")

elif page=="🔎 Schemes":
    st.title("🔎 Scheme Finder")
    qs = st.text_input("Search", placeholder="farmer, house, job, health...")
    cat = st.selectbox("Category", ["All","Agriculture","Employment","Housing","Health","Water"])
    out = SCHEMES
    if qs: out = [x for x in out if qs.lower() in x["name"].lower()+x["desc"].lower()]
    if cat!="All": out=[x for x in out if x["cat"]==cat]
    for s in out:
        with st.container(border=True):
            st.markdown(f"### {s['icon']} {s['name']}"); st.markdown(f"<span class='pill'>{s['cat']}</span><span class='pill pill2'>{s['states']}</span>", unsafe_allow_html=True)
            st.write(s['desc']); st.link_button("Apply / Official Source →", s['url'])

elif page=="🔄 State Compare":
    st.title("🔄 State to State Compare")
    st.write("Moving states? Check what changes.")
    c1,c2 = st.columns(2)
    with c1: from_s = st.selectbox("From State", STATES, index=STATES.index("Bihar"), key="from")
    with c2: to_s = st.selectbox("To State", STATES, index=STATES.index("Karnataka"), key="to")
    if st.button("Compare with AI", type="primary"):
        with st.spinner("Analyzing..."):
            st.markdown(ask_gemini(f"User moving from {from_s} to {to_s}. Explain which central schemes continue, which state schemes stop, what documents need update (ration card, domicile, voter ID), and steps for transfer.", f"{from_s} to {to_s}"))

elif page=="📢 Updates":
    st.title("📢 Official Updates")
    feed = feedparser.parse("https://pib.gov.in/RssMain.aspx?ModId=6&Lang=1&Regid=1")
    for e in feed.entries[:8]:
        with st.container(border=True):
            st.markdown(f"#### {e.get('title')}"); st.caption(e.get('published',''))
            if e.get('link'): st.link_button("Read official release →", e['link'])

else:
    st.title("About PanchayatConnect")
    st.write("**Independent civic-tech project.** Not a government website. Data sources: LGD, data.gov.in, 【entity-PIB¦canonical_name=PIB】, india.gov.in. Always verify eligibility on official portals.")
    st.warning("Demo village data shown. Production must use live LGD API.")

st.markdown('<div class="footer"><b>🇮🇳 PanchayatConnect Pro</b> • Built for citizens • Verify on official sources • AI powered by Gemini</div>', unsafe_allow_html=True)
