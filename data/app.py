import streamlit as st

# ============================================================
# PANCHAYATCONNECT
# V0.2 PROFESSIONAL DASHBOARD
# ============================================================

st.set_page_config(
    page_title="PanchayatConnect",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="auto",
)

# ============================================================
# CUSTOM STYLE
# ============================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .hero {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #0f5132,
            #198754
        );
        color: white;
        margin-bottom: 24px;
    }

    .hero h1 {
        font-size: 38px;
        margin-bottom: 5px;
    }

    .hero p {
        font-size: 17px;
        opacity: 0.92;
    }

    .section-title {
        font-size: 25px;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 12px;
    }

    .scheme-card {
        padding: 20px;
        border: 1px solid #dddddd;
        border-radius: 16px;
        margin-bottom: 12px;
        background: rgba(255,255,255,0.03);
    }

    .scheme-title {
        font-size: 20px;
        font-weight: 700;
    }

    .scheme-category {
        font-size: 14px;
        opacity: 0.75;
        margin-bottom: 8px;
    }

    .source-card {
        padding: 18px;
        border: 1px solid #dddddd;
        border-radius: 14px;
        height: 100%;
    }

    .footer {
        margin-top: 40px;
        padding: 20px;
        border-top: 1px solid #dddddd;
        text-align: center;
        opacity: 0.7;
        font-size: 13px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# SAMPLE VERIFIED-STYLE DATA
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
        "description": "Information about rural wage employment under the applicable programme rules.",
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

    st.caption("Government information, connected to your Panchayat.")

    st.divider()

    page = st.radio(
        "Navigation",
        [
            "🏠 Dashboard",
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
        placeholder="Enter Panchayat name",
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

    st.markdown(
        """
        <div class="hero">
            <h1>🇮🇳 PanchayatConnect</h1>
            <p>
            Discover government schemes, official information
            and important public-service updates in one place.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if district:
        location_text = district
        if panchayat:
            location_text += f" • {panchayat}"
        location_text += f" • {state}"
    else:
        location_text = state

    st.info(f"📍 Current search location: **{location_text}**")

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Available Schemes",
        len(schemes),
    )

    col2.metric(
        "Government Sources",
        "4",
    )

    col3.metric(
        "Languages",
        "2",
    )

    col4.metric(
        "Platform",
        "V0.2",
    )

    st.markdown(
        '<div class="section-title">⚡ Explore PanchayatConnect</div>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("### 🔎 Find Schemes")
        st.write(
            "Search government schemes using your location "
            "and citizen needs."
        )

        if st.button(
            "Search Schemes →",
            key="dashboard_scheme",
            use_container_width=True,
        ):
            st.info("Use **Find Schemes** from the sidebar.")

    with c2:
        st.markdown("### 📢 Government Updates")
        st.write(
            "A future section for verified government "
            "announcements and public updates."
        )

        st.info("Live update integration coming next.")

    with c3:
        st.markdown("### 🏛️ Official Sources")
        st.write(
            "Access original government portals instead of "
            "relying on unverified information."
        )

        if st.button(
            "View Sources →",
            key="dashboard_sources",
            use_container_width=True,
        ):
            st.info("Open **Official Sources** from the sidebar.")

    # Featured schemes
    st.markdown(
        '<div class="section-title">⭐ Featured Schemes</div>',
        unsafe_allow_html=True,
    )

    for scheme in schemes[:3]:

        st.markdown(
            f"""
            <div class="scheme-card">
                <div class="scheme-title">
                    {scheme["name"]}
                </div>

                <div class="scheme-category">
                    {scheme["category"]} • {scheme["level"]}
                </div>

                <div>
                    {scheme["description"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.link_button(
            "Open Official Source",
            scheme["url"],
            use_container_width=False,
        )

# ============================================================
# FIND SCHEMES
# ============================================================

elif page == "🔎 Find Schemes":

    st.title("🔎 Find Government Schemes")

    st.write(
        "Search the current PanchayatConnect demonstration "
        "catalogue."
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        search = st.text_input(
            "Search",
            placeholder="Example: farmer, housing, employment",
        )

    with col2:
        category = st.selectbox(
            "Category",
            [
                "All",
                "Agriculture",
                "Employment",
                "Housing",
                "Digital Services",
            ],
        )

    st.divider()

    results = schemes

    if search:
        search_lower = search.lower()

        results = [
            scheme
            for scheme in results
            if (
                search_lower in scheme["name"].lower()
                or search_lower in scheme["category"].lower()
                or search_lower in scheme["description"].lower()
                or any(
                    search_lower in keyword
                    for keyword in scheme["keywords"]
                )
            )
        ]

    if category != "All":
        results = [
            scheme
            for scheme in results
            if scheme["category"] == category
        ]

    st.subheader(f"Results: {len(results)}")

    if not results:

        st.warning(
            "No matching schemes found in the current catalogue."
        )

    else:

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
                    "🏛️ Open Official Government Source",
                    scheme["url"],
                )

# ============================================================
# GOVERNMENT UPDATES
# ============================================================

elif page == "📢 Government Updates":

    st.title("📢 Government Updates")

    st.info(
        "Live government update integration is planned for "
        "the next version."
    )

    st.markdown("### Planned Update System")

    updates = [
        "Official government announcements",
        "Scheme deadline changes",
        "New scheme notifications",
        "Important citizen-service notices",
        "Panchayat-level public information",
    ]

    for item in updates:
        st.write(f"• {item}")

    st.warning(
        "PanchayatConnect will show the original source and "
        "verification timestamp when live data is introduced."
    )

# ============================================================
# OFFICIAL SOURCES
# ============================================================

elif page == "🏛️ Official Sources":

    st.title("🏛️ Official Government Sources")

    st.write(
        "Use the original government portals for authoritative "
        "information."
    )

    sources = [
        (
            "🇮🇳 India.gov.in",
            "National Portal of India",
            "https://www.india.gov.in/",
        ),
        (
            "📊 data.gov.in",
            "Open Government Data Platform",
            "https://www.data.gov.in/",
        ),
        (
            "📰 PIB",
            "Press Information Bureau",
            "https://pib.gov.in/",
        ),
        (
            "🌾 PM-KISAN",
            "Official PM-KISAN portal",
            "https://pmkisan.gov.in/",
        ),
        (
            "🏠 PMAY-G",
            "Pradhan Mantri Awaas Yojana – Gramin",
            "https://pmayg.nic.in/",
        ),
    ]

    for i in range(0, len(sources), 2):

        cols = st.columns(2)

        for col, source in zip(cols, sources[i:i + 2]):

            with col:

                st.markdown(
                    f"""
                    <div class="source-card">
                        <h3>{source[0]}</h3>
                        <p>{source[1]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.link_button(
                    "Visit Official Website",
                    source[2],
                    use_container_width=True,
                )

# ============================================================
# ABOUT
# ============================================================

elif page == "ℹ️ About":

    st.title("ℹ️ About PanchayatConnect")

    st.markdown(
        """
        ### What is PanchayatConnect?

        PanchayatConnect is an independent civic-tech project
        designed to make government information easier for
        citizens to discover.

        ### 🎯 Vision

        Connect citizens with relevant government information
        through a simple, location-aware platform.

        ### 🧩 Planned Technology

        - Streamlit prototype
        - Government data sources
        - PostgreSQL database
        - FastAPI backend
        - Search and filtering
        - Transparent scheme matching
        - AI/RAG assistant
        - Kannada + English support
        - Verification and source tracking

        ### 🔐 Important

        PanchayatConnect is **not a government website**.

        Government information should always be verified against
        the original official source.

        The project does not guarantee eligibility for any
        government scheme.
        """
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        PanchayatConnect • Independent Civic-Tech Project • V0.2
        <br>
        Government information should be verified with the
        original official source.
    </div>
    """,
    unsafe_allow_html=True,
)
