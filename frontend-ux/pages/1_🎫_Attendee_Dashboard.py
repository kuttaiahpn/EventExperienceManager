import streamlit as st
from components.stage_indicator import show_stage_indicator
from components.venue_cards import (
    render_gate_cards,
    render_concession_cards,
    render_facility_cards,
    render_parking_cards,
    render_zone_summary_cards,
)
from components.chat_panel import render_chat_panel

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

if st.session_state["user"]["persona"] != "attendee":
    st.error("Access Denied.")
    st.stop()

st.markdown("""
<style>
    @media (max-width: 768px) {
        .block-container { padding: 1rem !important; }
    }
</style>
""", unsafe_allow_html=True)

show_stage_indicator()

# ── Header & Modern Chat Toggle ────────────────────────────────────────────────
header_col, chat_toggle_col, refresh_col = st.columns([4, 1, 1])
with header_col:
    st.title("🎫 Attendee Dashboard")

with chat_toggle_col:
    st.markdown("<br>", unsafe_allow_html=True)
    show_chat = st.toggle("💬 AI Panel", value=False, help="Show AI Concierge on the right")

with refresh_col:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ── Layout Engine: Optional 7:3 split ──────────────────────────────────────────
main_area, chat_area = st.columns([7, 3]) if show_chat else (st.container(), None)

with main_area:
    # ── Section 1: Entry Gates ────────────────────────────────────────────────
    st.subheader("🚪 Entry Gates")
    @st.fragment
    def gate_fragment() -> None:
        render_gate_cards()
    gate_fragment()

    st.markdown("---")

    # ── Section 2: Concessions ────────────────────────────────────────────────
    st.subheader("🍔 Food & Drinks")
    @st.fragment
    def concession_fragment() -> None:
        render_concession_cards()
    concession_fragment()

    st.markdown("---")

    # ── Section 3: Facilities & Amenities ────────────────────────────────────
    st.subheader("🚻 Facilities")
    @st.fragment
    def facility_fragment() -> None:
        render_facility_cards()
    facility_fragment()

    st.markdown("---")

    # ── Section 4: Crowd Density ─────────────────────────────────────────────
    st.subheader("📍 Live Crowd Density")
    @st.fragment
    def zone_fragment() -> None:
        render_zone_summary_cards()
    zone_fragment()

    st.markdown("---")

    # ── Section 5: Parking ────────────────────────────────────────────────────
    st.subheader("🅿️ Parking Status")
    @st.fragment
    def parking_fragment() -> None:
        render_parking_cards()
    parking_fragment()

if chat_area:
    with chat_area:
        st.markdown(f"""
            <div style="background-color:#1E2235; padding:20px; border-radius:15px; border:1px solid #4FC3F733;">
                <h4 style="margin-top:0; color:#4FC3F7;">💬 AI Concierge</h4>
                <p style="font-size:0.85rem; color:#B0BEC5;">Real-time event guidance</p>
            </div>
        """, unsafe_allow_html=True)
        render_chat_panel()
