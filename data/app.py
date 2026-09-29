import json
from pathlib import Path
from datetime import datetime

import feedparser
import streamlit as st


# ============================================================
# CONFIG
# ============================================================

APP_NAME = "PanchayatConnect"
APP_VERSION = "0.1.0"

SCHEME_FILE = Path("data/schemes.json")

PIB_RSS = (
    "https://pib.gov.in/"
    "RssMain.aspx?ModId=6&Lang=1&Regid=1"
)


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0;
    }

    .subtitle {
        font-size: 17px;
        opacity: 0.75;
        margin-bottom: 25px;
    }

    .source-box {
        padding: 12px;
        border-radius: 10px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-bottom: 10px;
    }

    .verified {
        font-size: 13px;
        font-weight: 600;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATA
# ============================================================

@st.cache_data
def load_schemes():

    if not SCHEME_FILE.exists():
        return []

    with open(SCHEME_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


schemes = load_schemes()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("🇮🇳 PanchayatConnect")

st.sidebar.caption(
    f"India Civic-Tech Platform v{APP_VERSION}"
)

page = st.sidebar.radio(
    "Navigation",
    [
        "🏠 Dashboard",
        "🔎 Scheme Finder",
        "📢 Government Updates",
        "🏛️ Official Sources",
        "ℹ️ About"
    ]
)


# ============================================================
# LOCATION
# ============================================================

st.sidebar.divider()

st.sidebar.subheader("📍 Your Location")

state = st.sidebar.selectbox(
    "State",
    [
        "Karnataka",
        "Kerala",
        "Tamil Nadu",
        "Maharashtra",
        "Telangana",
        "Andhra Pradesh",
        "Other"
    ]
)

district = st.sidebar.text_input(
    "District",
    placeholder="Example: Hassan"
)

panchayat = st.sidebar.text_input(
    "Gram Panchayat",
    placeholder="Example: Kandali"
)


# ============================================================
# DASHBOARD
# ============================================================

if page == "🏠 Dashboard":

    st.markdown(
        f'<div class="main-title">{APP_NAME}</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="subtitle">'
        "Discover government schemes and official updates "
        "relevant to your location."
        "</div>",
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Scheme Records",
            len(schemes)
        )

    with col2:
        st.metric(
            "Government Sources",
            "3"
        )

    with col3:
        st.metric(
            "Platform",
            "India"
        )

    st.divider()

    st.subheader("🔎 What are you looking for?")

    categories = [
        "🌾 Agriculture",
        "🏠 Housing",
        "💼 Employment",
        "🎓 Education",
        "🏥 Health",
        "💧 Water"
    ]

    cols = st.columns(3)

    for index, category in enumerate(categories):

        with cols[index % 3]:
            if st.button(
                category,
                use_container_width=True
            ):
                st.session_state["selected_category"] = (
                    category.split(" ", 1)[1]
                )
                st.info(
                    f"Searching {category} schemes..."
                )

    st.divider()

    st.subheader("📍 Current Location")

    if district or panchayat:

        location_text = []

        if panchayat:
            location_text.append(panchayat)

        if district:
            location_text.append(district)

        location_text.append(state)

        st.success(
            " → ".join(location_text)
        )

    else:

        st.info(
            "Select your location from the sidebar."
        )


# ============================================================
# SCHEME FINDER
# ============================================================

elif page == "🔎 Scheme Finder":

    st.title("🔎 Scheme Finder")

    st.write(
        "Find schemes using your location, category and "
        "search keywords."
    )

    search = st.text_input(
        "Search",
        placeholder="Example: farmer, housing, employment..."
    )

    category = st.selectbox(
        "Category",
        [
            "All",
            "Agriculture",
            "Housing",
            "Employment",
            "Education",
            "Health",
            "Water"
        ]
    )

    results = schemes

    if search:

        query = search.lower()

        results = [
            scheme
            for scheme in results
            if (
                query in scheme["name"].lower()
                or query in scheme["description"].lower()
                or any(
                    query in keyword.lower()
                    for keyword in scheme.get(
                        "keywords", []
                    )
                )
            )
        ]

    if category != "All":

        results = [
            scheme
            for scheme in results
            if scheme["category"] == category
        ]

    st.write(
        f"### {len(results)} result(s)"
    )

    for scheme in results:

        with st.container(border=True):

            st.subheader(
                f"🇮🇳 {scheme['name']}"
            )

            st.caption(
                f"{scheme['level']} • "
                f"{scheme['category']}"
            )

            st.write(
                scheme["description"]
            )

            st.markdown(
                '<span class="verified">'
                "🟢 Official-source reference"
                "</span>",
                unsafe_allow_html=True
            )

            st.link_button(
                "🔗 Open Official Source",
                scheme["source"]
            )


# ============================================================
# GOVERNMENT UPDATES
# ============================================================

elif page == "📢 Government Updates":

    st.title("📢 Government Updates")

    st.info(
        "Updates shown here come from an official "
        "government publication feed. Always open the "
        "original source before acting on important information."
    )

    if st.button("🔄 Refresh Updates"):

        feed = feedparser.parse(PIB_RSS)

        if feed.entries:

            for entry in feed.entries[:10]:

                with st.container(border=True):

                    st.subheader(
                        entry.get(
                            "title",
                            "Government Update"
                        )
                    )

                    published = entry.get(
                        "published",
                        "Publication date unavailable"
                    )

                    st.caption(
                        f"🟢 PIB • {published}"
                    )

                    link = entry.get(
                        "link",
                        ""
                    )

                    if link:
                        st.link_button(
                            "Read Official Release",
                            link
                        )

        else:

            st.warning(
                "No updates were returned by the official feed."
            )

    st.caption(
        "Last checked: "
        + datetime.now().strftime(
            "%d %b %Y, %I:%M %p"
        )
    )


# ============================================================
# OFFICIAL SOURCES
# ============================================================

elif page == "🏛️ Official Sources":

    st.title("🏛️ Official Government Sources")

    sources = [
        (
            "🇮🇳 National Portal of India",
            "Government schemes and citizen information",
            "https://www.india.gov.in/"
        ),
        (
            "📊 Open Government Data",
            "Government datasets and APIs",
            "https://data.gov.in/"
        ),
        (
            "📰 Press Information Bureau",
            "Official government press releases",
            "https://www.pib.gov.in/"
        ),
        (
            "🔌 API Setu",
            "Government API ecosystem",
            "https://www.apisetu.gov.in/"
        )
    ]

    for name, description, url in sources:

        with st.container(border=True):

            st.subheader(name)

            st.write(description)

            st.link_button(
                "Open Official Source",
                url
            )


# ============================================================
# ABOUT
# ============================================================

elif page == "ℹ️ About":

    st.title("ℹ️ About PanchayatConnect")

    st.write(
        """
        PanchayatConnect is an independent civic-tech project
        designed to help citizens discover and understand
        official government information.
        """
    )

    st.warning(
        """
        PanchayatConnect is NOT a Government of India website.

        Information should always be verified against the
        original official government source.
        """
    )

    st.subheader("Verification principle")

    st.write(
        """
        We aim to show:

        • Where information came from
        • When it was checked
        • The responsible department/source
        • A direct link to the original information
        """
    )

    st.caption(
        f"PanchayatConnect {APP_VERSION}"
    )
