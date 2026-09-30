import streamlit as st
import feedparser

# ============================================================
# PANCHAYATCONNECT
# V0.3 — CIVIC INFORMATION PLATFORM
# ============================================================

st.set_page_config(
    page_title="PanchayatConnect",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="auto",
)

# ============================================================
# STYLE
# ============================================================

st.markdown("""
<style>

.hero {
    padding: 30px;
    border-radius: 20px;
    background: linear-gradient(135deg, #0b5d3b, #198754);
    color: white;
    margin-bottom: 25px;
}

.hero h1 {
    font-size: 40px;
    margin-bottom: 5px;
}

.hero p {
    font-size: 17px;
    opacity: .92;
}

.section-title {
    font-size: 25px;
    font-weight: 700;
    margin-top: 25px;
    margin-bottom: 15px;
}

.small-muted {
    opacity: .7;
    font-size: 13px;
}

.footer {
    margin-top: 45px;
    padding: 22px;
    text-align: center;
    border-top: 1px solid #ddd;
    opacity: .7;
}

</style>
""", unsafe_allow_html=True)

# ============================================================
# DEMO DIRECTORY DATA
# ============================================================

panchayats = [
    {
        "state": "Karnataka",
        "district": "Hassan",
        "block": "Hassan",
        "name": "Example Gram Panchayat 1",
        "type": "Village Panchayat",
    },
    {
        "state": "Karnataka",
        "district": "Hassan",
        "block": "Arkalgud",
        "name": "Example Gram Panchayat 2",
        "type": "Village Panchayat",
    },
    {
        "state": "Karnataka",
        "district": "Mysuru",
        "block": "Mysuru",
        "name": "Example Gram Panchayat 3",
        "type": "Village Panchayat",
    },
    {
        "state": "Karnataka",
        "district": "Bengaluru Rural",
        "block": "Devanahalli",
        "name": "Example Gram Panchayat 4",
        "type": "Village Panchayat",
    },
]

# ============================================================
# SCHEME DATA
# ============================================================

schemes = [
    {
        "name": "PM-KISAN",
        "category": "Agriculture",
        "level": "Central",
        "description": "Income support information for eligible farmer families.",
        "keywords": ["farmer", "agriculture", "farm", "kisan"],
        "url": "https://pmkisan.gov.in/",
    },
    {
        "name": "MGNREGA",
        "category": "Employment",
        "level": "Central",
        "description": "Information about rural wage employment under applicable programme rules.",
        "keywords": ["employment", "job", "work", "rural"],
        "url": "https://nrega.nic.in/",
    },
    {
        "name": "PMAY-G",
        "category": "Housing",
        "level": "Central",
        "description": "Information about rural housing assistance for eligible beneficiaries.",
        "keywords": ["house", "housing", "home", "rural"],
        "url": "https://pmayg.nic.in/",
    },
    {
        "name": "Digital India",
        "category": "Digital Services",
        "level": "Central",
        "description": "Government digital-service information and citizen access resources.",
        "keywords": ["digital", "online", "service", "technology"],
        "url": "https://www.digitalindia.gov.in/",
    },
]

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown("## 🇮🇳 PanchayatConnect")

    st.caption(
        "Government information, connected to your Panchayat."
    )

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
            "🏘️ Panchayat Directory",
            "🔎 Find Schemes",
            "📢 Government Updates",
            "🏛️ Official Sources",
            "ℹ️ About",
        ],
    )

    st.divider()

    st.markdown("### 📍 My Location")

    state = st.selectbox(
        "State",
        [
            "Karnataka",
            "Kerala",
            "Tamil Nadu",
            "Maharashtra",
            "Telangana",
            "Andhra Pradesh",
        ],
    )

    district = st.text_input(
        "District",
        placeholder="Example: Hassan",
    )

    panchayat = st.text_input(
        "Panchayat",
        placeholder="Enter Panchayat",
    )

    st.divider()

    language = st.selectbox(
        "Language",
        ["English", "ಕನ್ನಡ"],
    )

# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown("""
    <div class="hero">
        <h1>🇮🇳 PanchayatConnect</h1>
        <p>
        Government information connected to citizens,
        schemes and local Panchayats.
        </p>
    </div>
    """, unsafe_allow_html=True)

    location = state

    if district:
        location += f" • {district}"

    if panchayat:
        location += f" • {panchayat}"

    st.info(f"📍 Selected location: **{location}**")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Schemes", len(schemes))
    c2.metric("Directory", "LGD")
    c3.metric("Languages", "2")
    c4.metric("Version", "0.3")

    st.markdown(
        '<div class="section-title">🚀 Explore</div>',
        unsafe_allow_html=True
    )

    a, b, c = st.columns(3)

    with a:
        st.markdown("### 🏘️ Panchayat Directory")
        st.write(
            "Explore the planned local-government directory."
        )

    with b:
        st.markdown("### 🔎 Scheme Finder")
        st.write(
            "Search schemes by category and citizen need."
        )

    with c:
        st.markdown("### 📢 Updates")
        st.write(
            "Read government releases from official sources."
        )

    st.markdown(
        '<div class="section-title">⭐ Featured Schemes</div>',
        unsafe_allow_html=True
    )

    for scheme in schemes[:3]:

        with st.container(border=True):

            st.markdown(f"### {scheme['name']}")

            st.caption(
                f"{scheme['category']} • {scheme['level']}"
            )

            st.write(scheme["description"])

            st.link_button(
                "🏛️ Official Source",
                scheme["url"]
            )

# ============================================================
# PANCHAYAT DIRECTORY
# ============================================================

elif page == "🏘️ Panchayat Directory":

    st.title("🏘️ Panchayat Directory")

    st.write(
        "Explore local-government information using the "
        "Panchayat hierarchy."
    )

    st.info(
        "🇮🇳 Directory source architecture: "
        "Local Government Directory (LGD), "
        "Ministry of Panchayati Raj."
    )

    st.markdown("### 📍 Select Location")

    col1, col2 = st.columns(2)

    with col1:

        directory_state = st.selectbox(
            "State",
            ["Karnataka"],
            key="directory_state"
        )

    with col2:

        directory_district = st.selectbox(
            "District",
            [
                "All Districts",
                "Hassan",
                "Mysuru",
                "Bengaluru Rural",
            ],
            key="directory_district"
        )

    search_panchayat = st.text_input(
        "🔎 Search Panchayat",
        placeholder="Type Panchayat name..."
    )

    st.divider()

    results = panchayats

    if directory_district != "All Districts":

        results = [
            p
            for p in results
            if p["district"] == directory_district
        ]

    if search_panchayat:

        query = search_panchayat.lower()

        results = [
            p
            for p in results
            if query in p["name"].lower()
        ]

    st.subheader(
        f"Directory Results: {len(results)}"
    )

    for item in results:

        with st.container(border=True):

            st.markdown(
                f"### 🏘️ {item['name']}"
            )

            st.write(
                f"**State:** {item['state']}"
            )

            st.write(
                f"**District:** {item['district']}"
            )

            st.write(
                f"**Block:** {item['block']}"
            )

            st.write(
                f"**Type:** {item['type']}"
            )

            st.caption(
                "⚠️ Prototype directory record — "
                "not yet a live LGD record."
            )

    st.divider()

    st.markdown("### 🏛️ Official LGD")

    st.write(
        "The production version will retrieve verified "
        "Panchayat records and LGD codes from the official "
        "Local Government Directory."
    )

    st.link_button(
        "Open Ministry of Panchayati Raj →",
        "https://panchayat.gov.in/en/lgd/"
    )

# ============================================================
# FIND SCHEMES
# ============================================================

elif page == "🔎 Find Schemes":

    st.title("🔎 Find Government Schemes")

    search = st.text_input(
        "Search",
        placeholder="Example: farmer, housing, employment"
    )

    category = st.selectbox(
        "Category",
        [
            "All",
            "Agriculture",
            "Employment",
            "Housing",
            "Digital Services",
        ]
    )

    results = schemes

    if search:

        query = search.lower()

        results = [
            s
            for s in results
            if (
                query in s["name"].lower()
                or query in s["category"].lower()
                or query in s["description"].lower()
                or any(query in k for k in s["keywords"])
            )
        ]

    if category != "All":

        results = [
            s
            for s in results
            if s["category"] == category
        ]

    st.divider()

    st.subheader(
        f"Results: {len(results)}"
    )

    if not results:

        st.warning("No matching schemes found.")

    for scheme in results:

        with st.container(border=True):

            st.markdown(
                f"### {scheme['name']}"
            )

            st.caption(
                f"{scheme['category']} • {scheme['level']}"
            )

            st.write(
                scheme["description"]
            )

            st.link_button(
                "🏛️ Open Official Source",
                scheme["url"]
            )

# ============================================================
# GOVERNMENT UPDATES
# ============================================================

elif page == "📢 Government Updates":

    st.title("📢 Government Updates")

    st.caption(
        "Official-source update feed"
    )

    PIB_RSS = (
        "https://pib.gov.in/RssMain.aspx"
        "?ModId=6&Lang=1&Regid=1"
    )

    try:

        feed = feedparser.parse(PIB_RSS)

        if feed.entries:

            st.success(
                f"🟢 {len(feed.entries)} updates available"
            )

            for entry in feed.entries[:10]:

                with st.container(border=True):

                    st.markdown(
                        f"### 📰 {entry.get('title', 'Government Update')}"
                    )

                    if entry.get("published"):

                        st.caption(
                            entry.get("published")
                        )

                    summary = entry.get(
                        "summary",
                        "Open the official release for details."
                    )

                    st.write(summary)

                    if entry.get("link"):

                        st.link_button(
                            "Read Official Release →",
                            entry["link"]
                        )

        else:

            st.warning(
                "No updates returned at the moment."
            )

    except Exception:

        st.error(
            "The government update feed is temporarily unavailable."
        )

# ============================================================
# OFFICIAL SOURCES
# ============================================================

elif page == "🏛️ Official Sources":

    st.title("🏛️ Official Government Sources")

    sources = [
        (
            "🇮🇳 India.gov.in",
            "National Portal of India",
            "https://www.india.gov.in/"
        ),
        (
            "📊 data.gov.in",
            "Open Government Data Platform",
            "https://data.gov.in/"
        ),
        (
            "🏘️ Ministry of Panchayati Raj",
            "Official Panchayati Raj information",
            "https://panchayat.gov.in/"
        ),
        (
            "🏛️ LGD",
            "Local Government Directory",
            "https://lgdirectory.gov.in/"
        ),
        (
            "📰 PIB",
            "Press Information Bureau",
            "https://pib.gov.in/"
        ),
    ]

    for i in range(0, len(sources), 2):

        cols = st.columns(2)

        for col, source in zip(
            cols,
            sources[i:i + 2]
        ):

            with col:

                with st.container(border=True):

                    st.markdown(
                        f"### {source[0]}"
                    )

                    st.write(source[1])

                    st.link_button(
                        "Open Official Website",
                        source[2],
                        use_container_width=True
                    )

# ============================================================
# ABOUT
# ============================================================

elif page == "ℹ️ About":

    st.title("ℹ️ About PanchayatConnect")

    st.markdown("""
### 🇮🇳 What is PanchayatConnect?

PanchayatConnect is an independent civic-tech project
designed to make government information easier to discover.

### 🎯 Core Goals

- Panchayat discovery
- Government scheme search
- Official government updates
- Source transparency
- Location-aware information
- Kannada + English support
- Future AI assistance

### 🏗️ Data Architecture

The production platform is designed around official sources
such as the Local Government Directory and Open Government
Data Platform.

### 🔐 Important

PanchayatConnect is **not a government website**.

Information should always be verified against the original
official government source.

The platform does not guarantee scheme eligibility.
""")

# ============================================================
# FOOTER
# ============================================================

st.markdown("""
<div class="footer">
PanchayatConnect • Independent Civic-Tech Project • V0.3
<br>
Official sources are preferred for verification.
</div>
""", unsafe_allow_html=True)
