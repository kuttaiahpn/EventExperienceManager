import streamlit as st

def show_login_page():
    st.markdown("""
        <style>
        /* Modern Portal Styles */
        .main-container {
            padding-top: 1rem !important;
        }
        .header-icons {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            letter-spacing: 15px;
            color: #4FC3F7;
        }
        .feature-card {
            background: rgba(26, 30, 46, 0.4);
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 4px solid #4FC3F7;
            margin-bottom: 1.5rem;
            transition: transform 0.2s;
        }
        .feature-card:hover {
            transform: translateX(10px);
            background: rgba(26, 30, 46, 0.6);
        }
        .feature-title {
            color: #FAFAFA;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }
        .feature-tagline {
            color: #4FC3F7;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        .feature-desc {
            color: #B0BEC5;
            font-size: 0.85rem;
            line-height: 1.4;
        }
        
        .login-card {
            padding: 2.5rem;
            background: linear-gradient(145deg, #1A1E2E, #111420);
            border-radius: 20px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.05);
            margin-top: 2rem;
        }
        .login-title {
            background: -webkit-linear-gradient(45deg, #4FC3F7, #00C853);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.8rem;
            font-weight: 800;
            margin-bottom: 0.5rem;
        }
        .login-tagline {
            color: #B0BEC5;
            font-size: 1rem;
            margin-bottom: 2rem;
        }
        .demo-badge {
            font-size: 0.75rem;
            color: #FFB74D;
            background: rgba(255,183,77,0.1);
            padding: 4px 12px;
            border-radius: 20px;
            display: inline-block;
            margin-top: 1.5rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Creative Header Section
    st.markdown('<div style="text-align: center;" class="main-container">', unsafe_allow_html=True)
    st.markdown('<div class="header-icons">🏟️ 📍 🍔 🥳 🚀</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-title">EventFlow AI</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 2], gap="large")

    with col1:
        st.markdown("<br>", unsafe_allow_html=True)
        # Point 1
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🏛️ 1. The Digital Twin Engine</div>
            <div class="feature-tagline">Real-time venue orchestration at your fingertips.</div>
            <div class="feature-desc">Experience a live "Digital Twin" of your venue that synchronizes stadium telemetry with AI reasoning, ensuring every gate, stall, and zone is monitored in real-time.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Point 2
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🎭 2. Dual-Persona Intelligence</div>
            <div class="feature-tagline">Tailored experiences for Fans and Fixers.</div>
            <div class="feature-desc">Whether providing wayfinding for an Attendee or risk-bottleneck analysis for a Manager, our multi-agent system adapts its reasoning to the user’s specific mission.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Point 3
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">⚡ 3. Agentic Scenario Sandbox</div>
            <div class="feature-tagline">From "What is" to "What if" in seconds.</div>
            <div class="feature-desc">Use the interactive Chaos Dashboard to inject anomalies like gate closures or weather delays, and watch as our AI agents instantly reroute thousands of attendees via live Firestore snapshots.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Point 4
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🧠 4. Hybrid RAG Knowledge Base</div>
            <div class="feature-tagline">Static policies meet dynamic realities.</div>
            <div class="feature-desc">Our agents combine deep-vector searches of event FAQs with live venue data, answering complex questions like "Where is the shortest taco line near my seat?" with sub-second latency.</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Point 5
        st.markdown("""
        <div class="feature-card">
            <div class="feature-title">🚀 5. Serverless Scale & Security</div>
            <div class="feature-tagline">Enterprise-grade orchestration on Google Cloud.</div>
            <div class="feature-desc">Built on a decoupled microservices architecture using LangGraph, MCP, and Vertex AI, EventFlow AI scales effortlessly from local theaters to global stadiums without compromising security.</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        st.subheader("Secure Access")
        st.markdown('<div class="login-tagline">Enter your credentials to begin</div>', unsafe_allow_html=True)
        
        display_name = st.text_input("Name", placeholder="e.g. Jordan", key="login_name")
        
        role = st.radio(
            "Access Role",
            ["🎫 Attendee", "📊 Event Manager"],
            index=0
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Demo Login", use_container_width=True, type="primary"):
            if not display_name:
                st.error("Please enter a name.")
            else:
                persona_type = "attendee" if "Attendee" in role else "manager"
                st.session_state["user"] = {
                    "name": display_name,
                    "persona": persona_type
                }
                st.session_state["authenticated"] = True
                st.rerun()

        st.markdown('<div style="text-align:center;"><div class="demo-badge">Prototype · Authentication Disabled</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
