import streamlit as st

def show_stage_indicator():
    # Defensive check
    if "venue_data" not in st.session_state:
        return
        
    current_stage = st.session_state["venue_data"].get("current_stage", "pre_event")
    
    stages = {
        "pre_event": {"color": "#4FC3F7", "label": "Pre-Event", "icon": "⏳"},
        "entry": {"color": "#FFB74D", "label": "Entry Flow", "icon": "🚪"},
        "during": {"color": "#81C784", "label": "In Progress", "icon": "🏟️"},
        "exit": {"color": "#BA68C8", "label": "Exit Flow", "icon": "👋"}
    }
    
    stage_info = stages.get(current_stage, stages["pre_event"])
    
    st.markdown(f"""
        <div style="
            display: inline-flex;
            align-items: center;
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.05);
            border: 1px solid {stage_info['color']}66;
            border-radius: 50px;
            margin-bottom: 1rem;
            color: #FAFAFA;
            font-weight: 600;
            box-shadow: 0 0 10px {stage_info['color']}33;
        ">
            <span style="margin-right: 8px;">{stage_info['icon']}</span>
            <span style="color: {stage_info['color']}; margin-right: 8px;">●</span>
            Event Stage: {stage_info['label']}
        </div>
    """, unsafe_allow_html=True)
