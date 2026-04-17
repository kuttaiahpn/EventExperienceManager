import streamlit as st
from components.chat_panel import render_chat_panel

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

if st.session_state["user"]["persona"] != "manager":
    st.error("Access Denied.")
    st.stop()

st.title("🧠 AI Orchestration")
st.markdown("Query event anomalies, command gate closures, and pull root-cause analyses across all venue telemetry.")

render_chat_panel()
