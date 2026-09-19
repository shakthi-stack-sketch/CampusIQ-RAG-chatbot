import os
import streamlit as st

from src.rag_engine import ask_question


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="CampusIQ | Prathyusha Engineering College",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# PATHS
# =========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGO_PATH = os.path.join(
    BASE_DIR,
    "assets",
    "college_logo.jpeg"
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "theme" not in st.session_state:
    st.session_state.theme = "Light"


# =========================================================
# COLORS
# =========================================================

if st.session_state.theme == "Light":

    BG = "#F7F0E7"
    CARD = "#FFFDF9"
    TEXT = "#171717"
    MUTED = "#665B54"
    MAROON = "#7A1111"
    BORDER = "#E6D4C3"

else:

    BG = "#12100F"
    CARD = "#211B19"
    TEXT = "#F8F1EA"
    MUTED = "#CDBFB5"
    MAROON = "#C23A3A"
    BORDER = "#4A3934"


# =========================================================
# PREMIUM CSS
# =========================================================

st.markdown(
    f"""
<style>

/* ================= GLOBAL ================= */

.stApp {{
    background:
        radial-gradient(
            circle at 0% 0%,
            rgba(122, 17, 17, 0.12),
            transparent 28%
        ),
        radial-gradient(
            circle at 100% 10%,
            rgba(190, 130, 70, 0.10),
            transparent 25%
        ),
        {BG};
}}

#MainMenu {{
    visibility: hidden;
}}

footer {{
    visibility: hidden;
}}

header {{
    background: transparent !important;
}}

.block-container {{
    max-width: 1200px;
    padding-top: 2.5rem;
    padding-bottom: 5rem;
}}


/* ================= SIDEBAR ================= */

section[data-testid="stSidebar"] {{
    background:
        linear-gradient(
            180deg,
            #360606 0%,
            #681010 50%,
            #8B1B1B 100%
        );
}}

section[data-testid="stSidebar"] * {{
    color: #FFF9F3 !important;
}}

section[data-testid="stSidebar"] img {{
    border-radius: 18px;
    background: #FFFFFF;
    padding: 5px;
    transition: transform 0.35s ease;
}}

section[data-testid="stSidebar"] img:hover {{
    transform: rotate(-2deg) scale(1.05);
}}


/* ================= TEXT ================= */

h1 {{
    color: {MAROON} !important;
    font-weight: 800 !important;
    letter-spacing: -1px !important;
}}

h2, h3 {{
    color: {TEXT} !important;
}}

p, span {{
    color: {TEXT};
}}


/* ================= HERO ================= */

.hero-title {{
    font-size: 3rem;
    font-weight: 800;
    color: {MAROON};
    margin-bottom: 0.3rem;
}}

.hero-subtitle {{
    font-size: 1.15rem;
    color: {MUTED};
    margin-bottom: 2rem;
}}


/* ================= PREMIUM FEATURE CARDS ================= */

.feature-card {{
    background: {CARD};

    border: 1px solid {BORDER};

    border-radius: 24px;

    padding: 28px 22px;

    min-height: 250px;

    position: relative;

    overflow: hidden;

    box-shadow:
        0px 8px 30px rgba(60,20,20,0.08);

    transition:
        transform 0.35s cubic-bezier(.2,.8,.2,1),
        box-shadow 0.35s ease,
        border-color 0.35s ease;

    cursor: default;
}}


/* CARD TOP GLOW */

.feature-card::before {{
    content: "";

    position: absolute;

    width: 180px;
    height: 180px;

    background:
        radial-gradient(
            circle,
            rgba(122,17,17,0.14),
            transparent 70%
        );

    top: -90px;
    right: -70px;

    transition:
        transform 0.5s ease;
}}


/* REAL HOVER EFFECT */

.feature-card:hover {{
    transform:
        translateY(-12px)
        scale(1.02);

    border-color: {MAROON};

    box-shadow:
        0px 25px 50px
        rgba(100,20,20,0.20);
}}

.feature-card:hover::before {{
    transform: scale(1.8);
}}


/* ICON */

.feature-icon {{
    font-size: 3rem;

    display: inline-block;

    transition:
        transform 0.35s ease;

    margin-bottom: 12px;
}}

.feature-card:hover .feature-icon {{
    transform:
        translateY(-6px)
        scale(1.18)
        rotate(-5deg);
}}


/* CARD TITLE */

.feature-title {{
    font-size: 1.3rem;

    font-weight: 700;

    color: {MAROON};

    margin-bottom: 10px;
}}


/* CARD TEXT */

.feature-text {{
    color: {MUTED};

    line-height: 1.6;
}}


/* ================= BUTTONS ================= */

.stButton button {{
    background:
        linear-gradient(
            135deg,
            #701010,
            #A72B2B
        ) !important;

    color: white !important;

    border: none !important;

    border-radius: 14px !important;

    font-weight: 600 !important;

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease !important;

    box-shadow:
        0px 7px 18px
        rgba(110,20,20,0.20);
}}

.stButton button:hover {{
    transform:
        translateY(-4px)
        scale(1.03);

    box-shadow:
        0px 16px 30px
        rgba(110,20,20,0.35);
}}


/* ================= CHAT ================= */

div[data-testid="stChatMessage"] {{
    background: {CARD} !important;

    border: 1px solid {BORDER};

    border-radius: 20px;

    padding: 16px;

    margin-bottom: 15px;

    animation:
        chatAppear 0.4s ease;

    box-shadow:
        0px 8px 25px
        rgba(50,20,20,0.07);
}}

div[data-testid="stChatMessage"]:hover {{
    border-color: {MAROON};

    box-shadow:
        0px 14px 35px
        rgba(100,20,20,0.13);
}}

div[data-testid="stChatMessage"] * {{
    color: {TEXT} !important;
}}


/* =========================================================
   CHAT INPUT - FIXED FOR CLEAR TYPING
========================================================= */

div[data-testid="stChatInput"] {{
    background-color: #FFFFFF !important;

    border: 2px solid {BORDER} !important;

    border-radius: 20px !important;

    transition: all 0.3s ease;

    box-shadow:
        0px 10px 28px
        rgba(60,20,20,0.10);
}}


/* HOVER EFFECT */

div[data-testid="stChatInput"]:hover {{
    border-color: {MAROON} !important;

    box-shadow:
        0px 14px 32px
        rgba(100,20,20,0.15);
}}


/* FOCUS EFFECT */

div[data-testid="stChatInput"]:focus-within {{
    border-color: {MAROON} !important;

    transform: translateY(-2px);

    box-shadow:
        0px 16px 35px
        rgba(100,20,20,0.18);
}}


/* THE TEXT AREA */

div[data-testid="stChatInput"] textarea {{
    color: #171717 !important;

    background-color: #FFFFFF !important;

    caret-color: #7A1111 !important;

    -webkit-text-fill-color: #171717 !important;

    opacity: 1 !important;
}}


/* PLACEHOLDER */

div[data-testid="stChatInput"] textarea::placeholder {{
    color: #6B625C !important;

    opacity: 1 !important;

    -webkit-text-fill-color: #6B625C !important;
}}


/* ADDITIONAL STREAMLIT INPUT FIX */

div[data-testid="stChatInput"] textarea:focus {{
    color: #171717 !important;

    background-color: #FFFFFF !important;

    -webkit-text-fill-color: #171717 !important;
}}


/* ================= ANIMATION ================= */

@keyframes chatAppear {{

    from {{
        opacity: 0;
        transform: translateY(20px);
    }}

    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

</style>
""",
    unsafe_allow_html=True
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    if os.path.exists(LOGO_PATH):

        st.image(
            LOGO_PATH,
            use_container_width=True
        )

    st.title("CampusIQ")

    st.caption(
        "Prathyusha Engineering College"
    )

    st.divider()

    st.subheader("Explore Campus")

    st.write("🚌 Bus Timings")
    st.write("🍽️ Mess Menu")
    st.write("📚 Academics")
    st.write("👔 Dress Code")
    st.write("🏠 Hostel Facilities")
    st.write("🤝 Student Clubs")
    st.write("🚀 Innovation Domains")

    st.divider()

    selected_theme = st.radio(
        "🎨 Appearance",
        ["Light", "Dark"],
        index=0 if st.session_state.theme == "Light" else 1
    )

    if selected_theme != st.session_state.theme:

        st.session_state.theme = selected_theme
        st.rerun()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.rerun()


# =========================================================
# MAIN PAGE
# =========================================================

st.markdown(
    """
    <div class="hero-title">
        Welcome to CampusIQ 🎓
    </div>

    <div class="hero-subtitle">
        Your intelligent AI-powered college information assistant for
        Prathyusha Engineering College.
    </div>
    """,
    unsafe_allow_html=True
)


st.divider()


# =========================================================
# FEATURE CARDS
# =========================================================

st.markdown("## 🌟 Explore Your Campus")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🚌</div>
            <div class="feature-title">Transport</div>
            <div class="feature-text">
                Find bus timings and transportation information.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🍽️</div>
            <div class="feature-title">Mess Menu</div>
            <div class="feature-text">
                Explore breakfast, lunch, snacks and dinner menus.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-title">Academics</div>
            <div class="feature-text">
                Learn about semesters, examinations and academics.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


with col4:

    st.markdown(
        """
        <div class="feature-card">
            <div class="feature-icon">🚀</div>
            <div class="feature-title">Campus Life</div>
            <div class="feature-text">
                Discover clubs, hostel facilities and opportunities.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


st.divider()


# =========================================================
# CHAT
# =========================================================

st.markdown("## 💬 Ask CampusIQ")

st.caption(
    "Ask anything specifically about Prathyusha Engineering College."
)


# DISPLAY CHAT HISTORY

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# USER INPUT

question = st.chat_input(
    "Ask anything about Prathyusha Engineering College..."
)


if question:

    with st.chat_message("user"):

        st.markdown(question)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    with st.chat_message("assistant"):

        with st.spinner(
            "🔍 CampusIQ is searching..."
        ):

            try:

                answer, sources = ask_question(question)

            except Exception:

                answer = (
                    "⚠️ Sorry, something went wrong. "
                    "Please try again."
                )

                sources = []

        st.markdown(answer)


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    # SOURCES

    if sources:

        with st.expander("📄 View Information Sources"):

            displayed_sources = set()

            for source in sources:

                filename = source.metadata.get(
                    "source",
                    "Unknown Document"
                )

                if filename not in displayed_sources:

                    st.write(f"📌 {filename}")

                    displayed_sources.add(filename)