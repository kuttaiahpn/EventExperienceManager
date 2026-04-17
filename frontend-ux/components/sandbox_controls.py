import streamlit as st
import time
from services.api_client import EventFlowAPI

def render_sandbox_controls():
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎛️ Simulation Sandbox")
    
    api = EventFlowAPI()
    event_id = st.session_state["venue_data"].get("event_id", "STADIUM_2026_01")
    
    with st.sidebar.expander("⏱️ Stage Transition", expanded=True):
        stages = ["pre_event", "entry", "during", "exit"]
        current = st.session_state["venue_data"].get("current_stage", "pre_event")
        try:
            curr_idx = stages.index(current)
        except ValueError:
            curr_idx = 0
            
        new_stage = st.selectbox("Force Event Stage", stages, index=curr_idx)
        if new_stage != current:
            api.simulate(event_id, "stage_transition", 100, new_stage)
            st.session_state["last_injection"] = time.strftime("%H:%M:%S")
            st.session_state["last_anomaly_type"] = "stage_transition"
            st.session_state["last_target"] = new_stage

    with st.sidebar.expander("🚪 Gate Controls", expanded=False):
        gates = st.session_state["venue_data"].get("gates", {})
        if gates:
            gate_options = {g.get("name", k): k for k, g in gates.items()}
            target_gate_name = st.selectbox("Select Gate", list(gate_options.keys()))
            target_gate_id = gate_options.get(target_gate_name)
            
            gate_status = gates.get(target_gate_id, {}).get("status", "open")
            action = "Close" if gate_status == "open" else "Open"
            
            if st.button(f"{action} {target_gate_name}", use_container_width=True):
                anomaly = "gate_failure" if action == "Close" else "gate_recovery"
                with st.spinner("Simulating..."):
                    api.simulate(event_id, anomaly, 100, target_gate_id)
                st.session_state["last_injection"] = time.strftime("%H:%M:%S")
                st.session_state["last_anomaly_type"] = anomaly
                st.session_state["last_target"] = target_gate_id
                st.toast(f"{target_gate_name} simulation triggered")

    with st.sidebar.expander("🌊 Crowd Surge", expanded=False):
        zones = st.session_state["venue_data"].get("zones", {})
        if zones:
            zone_options = {z.get("name", k): k for k, z in zones.items()}
            target_zone_name = st.selectbox("Select Zone", list(zone_options.keys()))
            target_zone_id = zone_options.get(target_zone_name)
            
            surge_severity = st.slider("Severity", 0, 100, 85, key="surge_sev")
            if st.button("Simulate Surge", use_container_width=True):
                with st.spinner("Injecting surge..."):
                    api.simulate(event_id, "surge", surge_severity, target_zone_id)
                st.session_state["last_injection"] = time.strftime("%H:%M:%S")
                st.session_state["last_anomaly_type"] = "surge"
                st.session_state["last_target"] = target_zone_id
                st.toast("Surge simulation triggered")

    with st.sidebar.expander("🍔 Vendor Slowdown", expanded=False):
        concessions = st.session_state["venue_data"].get("concessions", {})
        if concessions:
            stall_options = {c.get("name", k): k for k, c in concessions.items()}
            target_stall_name = st.selectbox("Select Concession", list(stall_options.keys()))
            target_stall_id = stall_options.get(target_stall_name)
            
            prep_severity = st.slider("Added Wait (mins)", 1, 30, 15, key="vendor_sev")
            if st.button("Trigger Slowdown", use_container_width=True):
                with st.spinner("Simulating slowdown..."):
                    api.simulate(event_id, "vendor_slowdown", prep_severity, target_stall_id)
                st.session_state["last_injection"] = time.strftime("%H:%M:%S")
                st.session_state["last_anomaly_type"] = "vendor_slowdown"
                st.session_state["last_target"] = target_stall_id
                st.toast("Vendor slowdown triggered")

    with st.sidebar.expander("⛈️ Extreme Weather", expanded=False):
        weather_on = st.toggle("Enable Weather Delay")
        if weather_on != st.session_state.get("_weather_active", False):
            st.session_state["_weather_active"] = weather_on
            severity = 100 if weather_on else 0
            api.simulate(event_id, "weather_delay", severity, "GLOBAL")
            st.session_state["last_injection"] = time.strftime("%H:%M:%S")
            st.session_state["last_anomaly_type"] = "weather_delay"
            st.session_state["last_target"] = "GLOBAL"

    last_inj = st.session_state.get("last_injection", "None")
    st.sidebar.caption(f"Last injection: {last_inj}")
