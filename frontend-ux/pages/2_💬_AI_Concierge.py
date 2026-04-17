import streamlit as st
from components.chat_panel import render_chat_panel

if not st.session_state.get("authenticated"):
    st.switch_page("app.py")

if st.session_state["user"]["persona"] != "attendee":
    st.error("Access Denied.")
    st.stop()

st.title("💬 AI Concierge")
st.markdown("Ask regarding event hours, washroom wait times, bag policy, and food locations.")

render_chat_panel()
