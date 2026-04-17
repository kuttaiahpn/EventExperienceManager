import streamlit as st
import plotly.express as px
import pandas as pd

def render_zone_heatmap():
    if "venue_data" not in st.session_state or "zones" not in st.session_state["venue_data"]:
        st.info("No zone data available for heatmap.")
        return
        
    zones = st.session_state["venue_data"]["zones"]
    if not zones:
        st.info("No zone data available for heatmap.")
        return
        
    data = []
    # Map categorical density to numeric for Plotly
    density_map = {
        "low": 0.2,
        "medium": 0.5,
        "high": 0.8,
        "critical": 1.0
    }
    
    for zid, zdata in zones.items():
        raw_density = zdata.get("crowd_density", "low")
        # Handle cases where it's already a float or a string enum
        if isinstance(raw_density, (int, float)):
            density = float(raw_density)
        else:
            density = density_map.get(str(raw_density).lower(), 0.2)

        data.append({
            "Zone": zdata.get("name", zid),
            "Density": density,
            "Capacity": zdata.get("capacity", 100) or 100,
            "Status": str(raw_density).title(),
            "Root": "Zones"
        })
        
    if not data:
        return
        
    df = pd.DataFrame(data)
    
    fig = px.treemap(
        df, 
        path=['Root', 'Zone'], 
        values='Capacity',
        color='Density',
        color_continuous_scale=["#81C784", "#FFB74D", "#EF5350"],
        range_color=[0, 1.0],
        custom_data=['Density', 'Status']
    )
    
    fig.update_traces(
        hovertemplate="<br>".join([
            "Zone: %{label}",
            "Density: %{customdata[0]:.0%}",
            "Status: %{customdata[1]}"
        ])
    )
    
    fig.update_layout(
        margin=dict(t=0, l=0, r=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=400,
        font=dict(color="#FAFAFA")
    )
    
    st.plotly_chart(fig, use_container_width=True)
