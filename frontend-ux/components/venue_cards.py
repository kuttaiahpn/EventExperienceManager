import streamlit as st


def get_color_for_occupancy(value: float) -> str:
    if value < 0.5:
        return "#81C784"   # Green
    elif value < 0.8:
        return "#FFB74D"   # Amber
    else:
        return "#EF5350"   # Red


def get_color_for_density(density: str) -> str:
    return {
        "low": "#81C784",
        "medium": "#FFB74D",
        "high": "#FF8A65",
        "critical": "#EF5350",
    }.get(density, "#757575")


def stock_to_float(stock_level: str) -> float:
    """Map stock_level string enum to a 0–1 float for display."""
    return {"optimal": 1.0, "low": 0.4, "depleted": 0.0}.get(stock_level, 0.5)


def render_gate_cards() -> None:
    if "venue_data" not in st.session_state or "gates" not in st.session_state["venue_data"]:
        st.info("No gate data available.")
        return

    gates = st.session_state["venue_data"]["gates"]
    if not gates:
        st.info("No gate data available.")
        return

    # Force 3 columns per row for a clean 3x2 layout
    cols_per_row = 3
    gate_list = sorted(list(gates.items()))
    
    for row_idx in range(0, len(gate_list), cols_per_row):
        cols = st.columns(cols_per_row)
        for i in range(cols_per_row):
            idx = row_idx + i
            if idx < len(gate_list):
                gate_id, gate = gate_list[idx]
                status: str = gate.get("status", "open")
                occupancy: float = float(gate.get("occupancy_rate", 0))
                wait_time: int = gate.get("avg_wait_time_mins", 0)
                anomaly: str = gate.get("anomaly_alert") or ""

                color = get_color_for_occupancy(occupancy) if status == "open" else "#E53935"
                # Removed icon for a cleaner Digital Twin look - status indicated by color glow
                glow_color = f"{color}33" # 20% opacity for glow

                with cols[i]:
                    st.markdown(f"""
                        <div style="background-color:#1A1E2E; padding: 18px; border-radius: 12px;
                                    border: 1px solid {color}44; border-left: 5px solid {color}; 
                                    box-shadow: 0 4px 15px {glow_color}; margin-bottom: 15px;">
                            <h4 style="margin:0; font-size:1.15rem; color:#FAFAFA; font-weight:700;">{gate_id}</h4>
                            <div style="display:flex; justify-content: space-between; margin-top: 12px;">
                                <span style="color:#B0BEC5; font-size:0.9rem; font-weight:500;">{status.upper()}</span>
                                <span style="color:#FAFAFA; font-size:0.9rem; font-weight:600;">⏱️ {wait_time}m</span>
                            </div>
                            <div style="margin-top: 12px; background-color:#0E1117;
                                        border-radius: 6px; height: 10px; width: 100%;">
                                <div style="background-color:{color}; width:{occupancy * 100:.0f}%;
                                            height: 100%; border-radius: 6px; box-shadow: 0 0 8px {color};"></div>
                            </div>
                            {"<div style='color:#FFB74D; font-size:0.85rem; margin-top:10px; font-weight:500;'>🚨 " + anomaly + "</div>" if anomaly else ""}
                        </div>
                    """, unsafe_allow_html=True)


def render_concession_cards() -> None:
    concessions = st.session_state.get("venue_data", {}).get("concessions", {})
    if not concessions:
        return

    # Using 3 columns for concessions
    cols = st.columns(3)
    concession_list = sorted(list(concessions.items()))
    
    for idx, (cid, stall) in enumerate(concession_list):
        prep_time: int = stall.get("avg_prep_time_mins", 0)
        stock_str: str = stall.get("stock_level", "optimal")
        is_active: bool = stall.get("is_active", True)
        
        # Dynamic color based on prep time
        color = get_color_for_occupancy(prep_time / 30.0) if is_active else "#E53935"
        glow_color = f"{color}22"

        with cols[idx % 3]:
            st.markdown(f"""
                <div style="background-color:#1A1E2E; padding: 18px; border-radius: 12px;
                            margin-bottom: 12px; border: 1px solid {color}33; border-top: 4px solid {color};
                            box-shadow: 0 4px 12px {glow_color};">
                    <h5 style="margin:0; color:#FAFAFA; font-size:1.05rem; font-weight:700;">🍔 {cid}</h5>
                    <div style="margin-top: 12px; display:flex; justify-content: space-between; align-items:center;">
                        <span style="font-size: 0.9rem; color:#B0BEC5;">Wait: <strong style="color:{color}; font-size:1rem;">{prep_time}m</strong></span>
                        <span style="font-size: 0.8rem; color:#FAFAFA; background:rgba(255,255,255,0.05); padding:2px 8px; border-radius:4px;">{stock_str.upper()}</span>
                    </div>
                </div>
            """, unsafe_allow_html=True)


def render_facility_cards() -> None:
    facilities = st.session_state.get("venue_data", {}).get("facilities", {})
    if not facilities:
        return

    cols = st.columns(4)
    facility_list = sorted(list(facilities.items()))
    
    for idx, (fid, fac) in enumerate(facility_list):
        wait_time: int = fac.get("wait_time_mins", 0)
        status: str = fac.get("status", "open")
        fac_type: str = fac.get("type", "restroom")
        icon = "🚻" if fac_type == "restroom" else ("⚕️" if fac_type == "medical" else "ℹ️")
        color = get_color_for_occupancy(wait_time / 15.0) if status == "open" else "#E53935"
        glow_color = f"{color}22"

        with cols[idx % 4]:
            st.markdown(f"""
                <div style="background-color:#1A1E2E; padding: 15px; border-radius: 12px;
                            margin-bottom: 15px; text-align: center; border: 1px solid {color}33; 
                            border-bottom: 4px solid {color}; box-shadow: 0 4px 12px {glow_color};">
                    <div style="font-size: 1.6rem; margin-bottom: 8px;">{icon}</div>
                    <div style="font-size: 0.95rem; font-weight:700; color:#FAFAFA; margin-bottom:4px;">{fid}</div>
                    <div style="font-size: 0.85rem; color:{color}; font-weight:600;">{wait_time}m · {status.upper()}</div>
                </div>
            """, unsafe_allow_html=True)


def render_parking_cards() -> None:
    parking = st.session_state.get("venue_data", {}).get("parking", {})
    if not parking:
        return

    cols = st.columns(2)
    parking_list = sorted(list(parking.items()))
    
    for idx, (pid, lot) in enumerate(parking_list):
        occ: float = float(lot.get("occupancy_rate", 0))
        status: str = lot.get("status", "filling")
        color = get_color_for_occupancy(occ)

        with cols[idx % 2]:
            st.markdown(f"""
                <div style="background-color:#1A1E2E; padding: 15px; border-radius: 10px; margin-bottom: 12px;">
                    <div style="display:flex; justify-content: space-between; align-items:center;">
                        <strong style="color:#FAFAFA; font-size:1rem;">🅿️ {pid}</strong>
                        <span style="color:#B0BEC5; font-size:0.85rem;">{occ * 100:.0f}% · {status.title()}</span>
                    </div>
                    <div style="margin-top: 12px; background-color:#0E1117; border-radius: 5px; height: 8px; width: 100%;">
                        <div style="background-color:{color}; width:{occ * 100:.0f}%; height: 100%; border-radius: 5px;"></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)


def render_zone_summary_cards() -> None:
    """Compact zone density badges — usable anywhere in Attendee or Manager views."""
    zones = st.session_state.get("venue_data", {}).get("zones", {})
    if not zones:
        return

    cols = st.columns(4)
    zone_list = sorted(list(zones.items()))
    
    for idx, (zid, zone) in enumerate(zone_list):
        density: str = zone.get("crowd_density", "low")
        washroom: int = zone.get("washroom_wait_mins", 0)
        color = get_color_for_density(density)
        glow_color = f"{color}22"
        
        with cols[idx % 4]:
            st.markdown(f"""
                <div style="background-color:#1A1E2E; padding: 15px; border-radius: 10px;
                            margin-bottom: 12px; border: 1px solid {color}33; border-top: 4px solid {color}; 
                            box-shadow: 0 4px 10px {glow_color}; text-align:center;">
                    <div style="font-size:0.95rem; font-weight:700; color:#FAFAFA; margin-bottom:4px;">{zid}</div>
                    <div style="color:{color}; font-size:0.85rem; font-weight:800; letter-spacing:1px; margin-bottom:6px;">{density.upper()}</div>
                    <div style="color:#B0BEC5; font-size:0.8rem; background:rgba(0,0,0,0.2); padding:4px; border-radius:4px;">🚻 {washroom}m wait</div>
                </div>
            """, unsafe_allow_html=True)
