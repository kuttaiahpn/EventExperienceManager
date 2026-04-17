import streamlit as st
from services.api_client import EventFlowAPI


def render_chat_panel() -> None:
    persona: str = st.session_state["user"]["persona"]
    title = "### 💬 AI Concierge" if persona == "attendee" else "### 🧠 AI Orchestration Assistant"
    st.markdown(title)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Render existing chat history
    chat_container = st.container(height=500)
    with chat_container:
        for msg in st.session_state["chat_history"]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("tool_used"):
                    st.caption(f"🔧 {msg['tool_used']}")

    api = EventFlowAPI()
    user_input = st.chat_input("Ask about the event...")

    if user_input:
        # Immediately store and display the user message
        st.session_state["chat_history"].append({"role": "user", "content": user_input})

        with chat_container:
            with st.chat_message("user"):
                st.markdown(user_input)

            context_data: dict = {
                "current_stage": st.session_state.get("venue_data", {}).get("current_stage", "pre_event"),
                "current_location": "General",
            }

            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                tool_placeholder = st.empty()

                full_response: str = ""
                used_tools: list[str] = []

                try:
                    stream = api.chat(
                        persona=persona,
                        session_id=st.session_state.get("_session_id", "default-session"),
                        message=user_input,
                        event_id=st.session_state.get("venue_data", {}).get("event_id", "STADIUM_2026_01"),
                        context=context_data,
                    )

                    for chunk in stream:
                        chunk_type = chunk.get("type")
                        
                        if chunk_type == "token":
                            # Robustly cast to string to avoid "can only concatenate str (not list)" errors
                            token = chunk.get("content", "")
                            if isinstance(token, list):
                                token = " ".join([str(t) for t in token])
                            else:
                                token = str(token)
                                
                            full_response += token
                            message_placeholder.markdown(full_response + "▌")
                            
                        elif chunk_type == "tool_call":
                            tool_name: str = chunk.get("tool_used", "tool")
                            used_tools.append(tool_name)
                            tool_placeholder.caption(f"🔧 Querying: {tool_name}...")

                        elif chunk_type == "final":
                            # "final" is a sentinel (content="done") — do NOT overwrite
                            # the accumulated token stream. Just render it and stop.
                            message_placeholder.markdown(full_response)
                            if used_tools:
                                tool_placeholder.caption(f"🔧 Used: {', '.join(set(used_tools))}")
                            break

                    # Safety net: render whatever was accumulated if stream ends without "final"
                    if full_response:
                        message_placeholder.markdown(full_response)

                except Exception as e:
                    st.error(f"❌ Could not reach AI Assistant: {e}")
                    st.session_state["chat_history"].pop()  # Remove the user message we just added
                    return

                # Persist assistant reply to history
                assistant_msg: dict = {"role": "assistant", "content": full_response}
                if used_tools:
                    assistant_msg["tool_used"] = ", ".join(set(used_tools))
                st.session_state["chat_history"].append(assistant_msg)
