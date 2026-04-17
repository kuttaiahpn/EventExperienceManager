import streamlit as st
from components.login_page import show_login_page
from services.firestore_listener import start_firestore_listener

st.set_page_config(
    page_title="EventFlow AI",
    page_icon="🏟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Global CSS
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }
    .st-emotion-cache-1kyxreq {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .sidebar-content {
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if "_session_id" not in st.session_state:
    import uuid
    st.session_state["_session_id"] = str(uuid.uuid4())

if not st.session_state["authenticated"]:
    # Hide sidebar while unauthenticated
    st.markdown("""
    <style>
        [data-testid="stSidebar"] { display: none; }
        [data-testid="stHeader"] { display: none; }
    </style>
    """, unsafe_allow_html=True)
    show_login_page()
    st.stop()

# Ensure we always try to start the listener once authenticated
start_firestore_listener(st.session_state.get("event_id_to_track", "STADIUM_2026_01"))

# Define Pages for Navigation
def get_pages():
    persona = st.session_state.get("user", {}).get("persona", "attendee")
    
    if persona == "attendee":
        return [
            st.Page("pages/1_🎫_Attendee_Dashboard.py", title="Attendee Dashboard", icon="🎫", default=True),
            st.Page("pages/2_💬_AI_Concierge.py", title="AI Concierge", icon="💬"),
        ]
    else: # Manager
        return [
            st.Page("pages/3_📊_Manager_Dashboard.py", title="Manager Dashboard", icon="📊", default=True),
            st.Page("pages/4_🧠_AI_Orchestration.py", title="AI Orchestration", icon="🧠"),
        ]

# Authenticated Navigation
pg = st.navigation(get_pages())

# Authenticated Sidebar Header
with st.sidebar:
    st.markdown("## 🏟️ EventFlow AI")
    st.markdown(f"**{st.session_state['user']['name']}**")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        st.caption(f"Role: {st.session_state['user']['persona'].title()}")
    with col2:
        if st.button("Logout"):
            keys = list(st.session_state.keys())
            for key in keys:
                del st.session_state[key]
            st.rerun()

# Run the selected page
pg.run()
