import os
import time
import streamlit as st
from google.cloud import firestore
from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx

def start_firestore_listener(event_id: str):
    """
    Initializes and starts the Firestore listeners for the real-time venue state.
    Must be called from a Streamlit executing thread.
    """
    if st.session_state.get("firestore_listener_active"):
        return
        
    st.session_state["firestore_listener_active"] = True
    
    if "venue_data" not in st.session_state:
         # Initialize default structures so the UI doesn't crash before first load
        st.session_state["venue_data"] = {
             "gates": {},
             "zones": {},
             "concessions": {},
             "facilities": {},
             "parking": {},
             "current_stage": "pre_event",
             "event_id": event_id
        }

    ctx = get_script_run_ctx()
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT", "promptwars-virtual2026")
    db_name = os.environ.get("FIRESTORE_DATABASE", "(default)")
    
    # Wait to instantiate DB inside to prevent pickling issues, though it should be fine here.
    try:
        db = firestore.Client(project=project_id, database=db_name)
    except Exception as e:
        print(f"Error initializing Firestore Client: {e}")
        return
        
    doc_ref = db.collection("venue_state").document(event_id)

    def on_doc_snapshot(doc_snapshot, changes, read_time):
        if ctx:
            add_script_run_ctx(ctx=ctx)
        
        for doc in doc_snapshot:
            if doc.exists:
                data = doc.to_dict() or {}
                st.session_state["venue_data"].update(data)
                # Flatten event_metadata fields to top level so all components
                # can read current_stage, event_id etc. without knowing the nesting
                event_meta = data.get("event_metadata", {})
                if event_meta:
                    st.session_state["venue_data"]["current_stage"] = event_meta.get(
                        "current_stage",
                        st.session_state["venue_data"].get("current_stage", "pre_event")
                    )
                    st.session_state["venue_data"]["event_id"] = event_meta.get(
                        "event_id", event_id
                    )
                
    doc_ref.on_snapshot(on_doc_snapshot)

    def get_col_handler(col_name: str):
        def on_col_snapshot(col_snapshot, changes, read_time):
            if ctx:
                add_script_run_ctx(ctx=ctx)
                
            if "venue_data" not in st.session_state:
                 st.session_state["venue_data"] = {}
            if col_name not in st.session_state["venue_data"]:
                 st.session_state["venue_data"][col_name] = {}
                 
            for doc in col_snapshot:
                if doc.exists:
                    st.session_state["venue_data"][col_name][doc.id] = doc.to_dict()
                    
        return on_col_snapshot

    for sub_col in ["gates", "zones", "concessions", "facilities", "parking"]:
        doc_ref.collection(sub_col).on_snapshot(get_col_handler(sub_col))
