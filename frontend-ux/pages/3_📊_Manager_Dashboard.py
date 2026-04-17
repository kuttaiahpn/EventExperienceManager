import streamlit as st
from components.stage_indicator import show_stage_indicator
from components.heatmap import render_zone_heatmap
from components.venue_cards import render_gate_cards
from components.sandbox_controls import render_sandbox_controls

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

if st.session_state["user"]["persona"] != "manager":
    st.error("Access Denied.")
    st.stop()

st.markdown("""
<style>
    .streamlit-expanderHeader { font-weight: 600; color: #4FC3F7; }
</style>
""", unsafe_allow_html=True)

# ── Header & Modern Chat Toggle ────────────────────────────────────────────────
header_col, chat_toggle_col, refresh_col = st.columns([5, 1, 1])
with header_col:
    st.title("📊 Orchestration Dashboard")
    
with chat_toggle_col:
    st.markdown("<br>", unsafe_allow_html=True)
    show_chat = st.toggle("🧠 AI Panel", value=False, help="Show AI Orchestrator on the right")
            
with refresh_col:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ── Layout Engine: Optional 7:3 split ──────────────────────────────────────────
main_area, chat_area = st.columns([7, 3]) if show_chat else (st.container(), None)

with main_area:
    # ── Critical Alert Banner ─────────────────────────────────────────────────────
    @st.fragment
    def alert_banner() -> None:
        if "venue_data" in st.session_state and "zones" in st.session_state["venue_data"]:
            alerts_found = False
            for zid, z in st.session_state["venue_data"]["zones"].items():
                if z.get("crowd_density") in ("high", "critical"):
                    st.error(f"🚨 HIGH CROWD DENSITY detected in **{zid}**")
                    alerts_found = True
            if not alerts_found:
                st.success("✅ All zones nominal — no critical alerts")
    alert_banner()

    # ── Section 1: Heatmap ────────────────────────────────────────────────────────
    @st.fragment
    def heatmap_layer() -> None:
        st.subheader("📍 Zone Density Live Map")
        render_zone_heatmap()
    heatmap_layer()

    st.markdown("---")

    # ── Section 2: Gates ──────────────────────────────────────────────────────────
    @st.fragment
    def gate_layer() -> None:
        st.subheader("🚪 Global Gate Overview")
        render_gate_cards()
    gate_layer()

    # ── Section 3: Simulation Sandbox ─────────────────────────────────────────────
    # Not inside @st.fragment to allow sidebar operations
    render_sandbox_controls()

    # ── Section 4: Event Log Feed ─────────────────────────────────────────────────
    st.markdown("---")
    st.subheader("📋 Event Log Feed")
    st.caption("Simulation injections and telemetry events")
    if "last_injection" in st.session_state:
        ts = st.session_state["last_injection"]
        atype = st.session_state.get("last_anomaly_type", "simulation")
        target = st.session_state.get("last_target", "GLOBAL")
        st.code(f"[{ts}] Manager sandbox → anomaly_type={atype} target={target} · status=published")
    else:
        st.code("Listening for stadium telemetry...")

if chat_area:
    with chat_area:
        st.markdown(f"""
            <div style="background-color:#1E2235; padding:20px; border-radius:15px; border:1px solid #4FC3F733;">
                <h4 style="margin-top:0; color:#4FC3F7;">🧠 AI Orchestrator</h4>
                <p style="font-size:0.85rem; color:#B0BEC5;">Direct stadium command</p>
            </div>
        """, unsafe_allow_html=True)
        from components.chat_panel import render_chat_panel
        render_chat_panel()
