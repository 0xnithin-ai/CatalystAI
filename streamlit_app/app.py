import streamlit as st
import requests
import pandas as pd
import numpy as np
import os

API_URL = os.getenv("API_URL", "https://catalystai-1.onrender.com")

st.set_page_config(
    page_title="CatalystAI Discovery Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional styling
st.markdown("""
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1d2e 0%, #0f1117 100%);
        border-right: 1px solid #2d3142;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 600;
    }

    /* Sidebar: force readable text (Streamlit defaults are often dark-on-dark here) */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] [data-testid="stSidebarContent"] {
        color: #eef1f7 !important;
    }

    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] li {
        color: #eef1f7 !important;
    }

    [data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] strong {
        color: #ffffff !important;
        font-weight: 600;
    }

    [data-testid="stSidebar"] [data-testid="stCaption"] {
        color: #c8d0e0 !important;
    }

    [data-testid="stSidebar"] [data-testid="stCaption"] p,
    [data-testid="stSidebar"] [data-testid="stCaption"] span {
        color: #c8d0e0 !important;
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {
        color: #f4f6fb !important;
    }

    /* Number / text input widgets: label row */
    [data-testid="stSidebar"] .stNumberInput label p,
    [data-testid="stSidebar"] .stTextInput label p {
        color: #f4f6fb !important;
    }

    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.18) !important;
        background-color: rgba(255,255,255,0.12) !important;
    }
    
    /* Headers */
    h1 {
        color: #00d4aa;
        font-weight: 700;
        letter-spacing: -0.5px;
        font-size: 2.5rem !important;
    }
    
    h2 {
        color: #e0e0e0;
        font-weight: 600;
        letter-spacing: -0.3px;
        margin-top: 2rem;
    }
    
    h3 {
        color: #b0b0b0;
        font-weight: 500;
        font-size: 1.1rem;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00d4aa 0%, #00a884 100%);
        color: #ffffff;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        letter-spacing: 0.3px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 212, 170, 0.2);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #00a884 0%, #008869 100%);
        box-shadow: 0 6px 20px rgba(0, 212, 170, 0.3);
        transform: translateY(-2px);
    }
    
    /* Secondary Buttons */
    .stButton > button[kind="secondary"] {
        background: transparent;
        border: 2px solid #00d4aa;
        color: #00d4aa;
        box-shadow: none;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(0, 212, 170, 0.1);
        transform: translateY(-2px);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: #00d4aa;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.85rem;
        font-weight: 500;
        color: #808080;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem;
        font-weight: 600;
    }
    
    /* Cards */
    .info-card {
        background: linear-gradient(135deg, #1a1d2e 0%, #252836 100%);
        border: 1px solid #2d3142;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    }
    
    .success-card {
        background: linear-gradient(135deg, #0f3d2f 0%, #0a2820 100%);
        border: 1px solid #00d4aa;
        border-left: 4px solid #00d4aa;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #3d2f0f 0%, #2d2208 100%);
        border: 1px solid #ffa726;
        border-left: 4px solid #ffa726;
        border-radius: 8px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: #1a1d2e;
        border-radius: 8px 8px 0 0;
        padding: 0.75rem 1.5rem;
        color: #808080;
        font-weight: 500;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: #252836;
        color: #00d4aa;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4aa 0%, #00a884 100%);
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Dataframe */
    .dataframe {
        border: 1px solid #2d3142 !important;
        border-radius: 8px;
        overflow: hidden;
    }
    
    .dataframe thead tr th {
        background: #1a1d2e !important;
        color: #00d4aa !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        font-size: 0.85rem;
        letter-spacing: 0.5px;
        padding: 1rem !important;
    }
    
    .dataframe tbody tr:hover {
        background: #1a1d2e !important;
    }
    
    /* Input Fields */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stSelectbox > div > div > div {
        background: #1a1d2e;
        border: 1px solid #2d3142;
        border-radius: 8px;
        color: #ffffff;
        padding: 0.6rem 1rem;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus {
        border-color: #00d4aa;
        box-shadow: 0 0 0 1px #00d4aa;
    }
    
    /* Divider */
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 1px solid #2d3142;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: #1a1d2e;
        border-radius: 8px;
        font-weight: 500;
        color: #e0e0e0;
    }
    
    .streamlit-expanderHeader:hover {
        background: #252836;
        color: #00d4aa;
    }
    
    /* Caption */
    .caption {
        color: #808080;
        font-size: 0.85rem;
        font-weight: 400;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    
    .status-approved {
        background: rgba(0, 212, 170, 0.2);
        color: #00d4aa;
        border: 1px solid #00d4aa;
    }
    
    .status-warning {
        background: rgba(255, 167, 38, 0.2);
        color: #ffa726;
        border: 1px solid #ffa726;
    }

    .status-blocked {
        background: rgba(239, 83, 80, 0.2);
        color: #ef5350;
        border: 1px solid #ef5350;
    }

    /* Home landing (no active session) */
    .home-landing {
        padding: 3rem 2.5rem 3.25rem;
        margin: 0 auto 2.5rem auto;
        max-width: 960px;
        background: radial-gradient(ellipse 90% 70% at 12% 0%, rgba(0, 212, 170, 0.09) 0%, transparent 50%),
                    linear-gradient(180deg, #161a28 0%, #0f1117 45%, #0a0c12 100%);
        border: 1px solid #2d3142;
        border-radius: 20px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.35), inset 0 1px 0 rgba(255,255,255,0.04);
    }

    .home-landing-inner {
        max-width: 38rem;
        margin: 0 auto;
        padding-left: 0.875rem;
        border-left: 3px solid rgba(0, 212, 170, 0.45);
        text-align: left;
    }

    .home-pill {
        display: inline-block;
        padding: 0.35rem 0.95rem;
        border-radius: 999px;
        font-size: 0.688rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        color: #8ba3b8;
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 0 0 1.25rem 0;
    }

    .home-hero-title {
        margin: 0 0 1rem 0 !important;
        padding: 0 !important;
        font-size: clamp(2.35rem, 5.5vw, 3.1rem) !important;
        font-weight: 700 !important;
        letter-spacing: -0.04em !important;
        line-height: 1.06 !important;
        color: #f4f7fb !important;
        font-family: 'Inter', sans-serif !important;
        text-align: left !important;
    }

    .home-accent {
        color: #00d4aa !important;
    }

    .home-tagline {
        margin: 0 0 1rem 0 !important;
        max-width: none !important;
        font-size: 1.0625rem;
        font-weight: 400;
        line-height: 1.62;
        letter-spacing: -0.01em;
        color: #c2cad6 !important;
        text-align: left !important;
    }

    .home-intro {
        margin: 0 !important;
        max-width: none !important;
        font-size: 0.9375rem;
        line-height: 1.72;
        letter-spacing: 0.01em;
        color: #8e98a8 !important;
        text-align: left !important;
    }

    /* Section headings — same measure as hero copy */
    .home-section-title {
        box-sizing: border-box;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.14em !important;
        text-transform: uppercase !important;
        color: #6b7789 !important;
        max-width: 38rem;
        margin: 2.25rem auto 1rem auto !important;
        padding-left: calc(0.875rem + 3px) !important;
        text-align: left !important;
    }
    .home-card-wrap {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 0 0 2.25rem 0;
    }

    @media (max-width: 900px) {
        .home-card-wrap {
            grid-template-columns: 1fr;
        }
    }

    .home-card {
        background: rgba(26, 29, 46, 0.75);
        border: 1px solid #323748;
        border-radius: 14px;
        padding: 1.35rem 1.4rem 1.4rem;
        text-align: left;
        height: 100%;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.22);
        transition: border-color 0.25s ease, box-shadow 0.25s ease;
    }

    .home-card:hover {
        border-color: rgba(0, 212, 170, 0.35);
        box-shadow: 0 6px 28px rgba(0, 212, 170, 0.06);
    }

    .home-card h4 {
        margin: 0 0 0.5rem 0;
        font-size: 1rem;
        font-weight: 600;
        color: #eef1f6 !important;
        letter-spacing: -0.02em;
    }

    .home-card p {
        margin: 0;
        font-size: 0.88rem;
        line-height: 1.55;
        color: #939dad !important;
    }

    .home-pipeline {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.5rem;
        padding: 1.25rem 1.5rem;
        background: rgba(15, 17, 23, 0.65);
        border: 1px solid #2a2f3d;
        border-radius: 14px;
        margin: 0 0 2rem 0;
    }

    .home-pstep {
        flex: 1;
        min-width: 105px;
        text-align: center;
    }

    .home-pstep-num {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 8px;
        font-size: 0.82rem;
        font-weight: 700;
        color: #00d4aa;
        background: rgba(0, 212, 170, 0.12);
        border: 1px solid rgba(0, 212, 170, 0.25);
        margin-bottom: 0.45rem;
    }

    .home-pstep-label {
        display: block;
        font-size: 0.8rem;
        font-weight: 600;
        color: #cfd5df !important;
        margin-bottom: 0.2rem;
    }

    .home-pstep-desc {
        font-size: 0.72rem;
        line-height: 1.35;
        color: #7a8494 !important;
    }

    .home-cta-panel {
        box-sizing: border-box;
        max-width: 38rem;
        margin: 0 auto 1.5rem auto;
        padding: 1.35rem 1.35rem 1.35rem calc(1.35rem + 0.875rem + 3px);
        background: rgba(0, 212, 170, 0.06);
        border: 1px solid rgba(0, 212, 170, 0.22);
        border-radius: 14px;
        text-align: left;
    }

    .home-cta-panel p {
        margin: 0 0 0.4rem 0;
        font-size: 1rem;
        font-weight: 600;
        color: #e8ecf2 !important;
    }

    .home-cta-panel span {
        display: block;
        font-size: 0.875rem;
        line-height: 1.55;
        color: #95a2b6 !important;
    }

    .home-foot {
        box-sizing: border-box;
        max-width: 38rem;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: calc(0.875rem + 3px) !important;
        text-align: left !important;
        font-size: 0.78rem !important;
        color: #5c6676 !important;
        letter-spacing: 0.02em;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
for key, default in [
    ("session_id", None), ("candidates", []),
    ("target_type", "catalyst"), ("iteration", 0),
    ("best_score_history", []), ("score_baseline", None)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# Sidebar
with st.sidebar:
    st.markdown("### Target Configuration")
    st.markdown("**Track:** Chemical Catalysis (Direction 1)")
    st.caption("Optimize ethanol → SAF conversion catalysts")
    
    st.markdown("---")
    
    reaction_smiles = st.text_input(
        "Target Reaction (SMILES)",
        "CCO→CC(=O)O",
        help="Ethanol oxidation to acetic acid"
    )
    
    col_temp = st.columns(2)
    with col_temp[0]:
        temp_min = st.number_input("Min Temp (°C)", value=200)
    with col_temp[1]:
        temp_max = st.number_input("Max Temp (°C)", value=400)
    
    st.markdown("---")
    
    col_action = st.columns(2)
    
    with col_action[0]:
        if st.button("New Session", use_container_width=True):
            payload = {
                "reaction": reaction_smiles,
                "constraints": {"temperature_range": [temp_min, temp_max], "pressure_range": [1, 20]}
            }
            try:
                res = requests.post(f"{API_URL}/api/sessions", json=payload)
                if res.status_code == 200:
                    st.session_state["session_id"] = res.json()["id"]
                    st.session_state["target_type"] = "catalyst"
                    st.session_state["candidates"] = []
                    st.session_state["iteration"] = 0
                    st.session_state["best_score_history"] = []
                    st.session_state["score_baseline"] = None
                    st.success("Session created successfully")
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"API connection failed: {e}")
    
    with col_action[1]:
        if st.button("Load Demo", use_container_width=True):
            try:
                res = requests.post(f"{API_URL}/api/rank", json={"session_id": "demo-historical-session"})
                if res.status_code == 200:
                    st.session_state["session_id"] = "demo-historical-session"
                    st.session_state["target_type"] = "catalyst"
                    st.session_state["candidates"] = res.json()["candidates"]
                    st.session_state["iteration"] = 1
                    st.session_state["best_score_history"] = [70.0, 85.0]
                    st.session_state["score_baseline"] = 70.0
                    st.success("Demo session loaded")
                else:
                    st.error("Demo session not found")
            except Exception as e:
                st.error(f"Connection error: {e}")
    
    if st.session_state["session_id"]:
        st.markdown("---")
        st.caption(f"**Session ID:** `{st.session_state['session_id'][:16]}...`")
        st.caption(f"**Iteration:** {st.session_state['iteration']}")

# Workspace header (hidden on landing page to avoid duplicate titles)
if st.session_state["session_id"]:
    st.markdown("<h1>CatalystAI Discovery Platform</h1>", unsafe_allow_html=True)
    st.caption("AI-Powered Molecular Discovery Engine · GPS Renewables Initiative · 2G Ethanol-to-SAF pathway")

# Progress Metrics Banner
if st.session_state["session_id"] and st.session_state["best_score_history"]:
    history = st.session_state["best_score_history"]
    
    st.markdown("### Active Learning Progress")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Learning Iteration", st.session_state["iteration"])
    with col2:
        st.metric(
            "Baseline Score",
            f"{history[0]:.1f}%",
            help="Best activity before feedback"
        )
    with col3:
        st.metric(
            "Current Best",
            f"{history[-1]:.1f}%",
            delta=f"+{history[-1] - history[0]:.1f}%" if len(history) > 1 else None,
            help="Best activity after active learning"
        )
    with col4:
        improvement = history[-1] - history[0]
        st.metric(
            "Improvement",
            f"+{improvement:.1f}%",
            help="Active learning gain"
        )
    
    st.markdown("---")

# Main Content
if st.session_state["session_id"]:
    
    tabs = st.tabs([
        "Generation & Ranking",
        "Pareto Analysis",
        "Strategy Comparison",
        "Multi-Acquisition",
        "Feedback Loop",
        "Literature Database",
        "Metabolic Analysis",
        "Safety Screening"
    ])
    
    # TAB 1: Generation & Ranking
    with tabs[0]:
        st.markdown("### Candidate Generation & Ranking")
        
        col_gen = st.columns([1, 1, 1, 3])
        
        with col_gen[0]:
            if st.button("Generate Candidates", use_container_width=True):
                with st.spinner("Querying generative models..."):
                    res = requests.post(
                        f"{API_URL}/api/generate",
                        json={"session_id": st.session_state["session_id"], "target_type": "catalyst"}
                    )
                    if res.status_code == 200:
                        cands = res.json()["candidates"]
                        st.session_state["candidates"] = cands
                        if not st.session_state["best_score_history"]:
                            baseline = max(c["predicted_activity"] for c in cands)
                            st.session_state["score_baseline"] = baseline
                            st.session_state["best_score_history"] = [baseline]
                        st.success(f"Generated {len(cands)} candidates")
        
        with col_gen[1]:
            if st.button("Rank by EI", use_container_width=True):
                with st.spinner("Running Bayesian optimization..."):
                    res = requests.post(
                        f"{API_URL}/api/rank",
                        json={"session_id": st.session_state["session_id"]}
                    )
                    if res.status_code == 200:
                        st.session_state["candidates"] = res.json()["candidates"]
                        st.success("Ranked by Expected Improvement")
        
        with col_gen[2]:
            if st.button("Rank by Score", use_container_width=True):
                with st.spinner("Ranking by prediction..."):
                    res = requests.post(
                        f"{API_URL}/api/rank-by-score",
                        json={"session_id": st.session_state["session_id"]}
                    )
                    if res.status_code == 200:
                        st.session_state["candidates"] = res.json()["candidates"]
                        st.success("Ranked by predicted score")
        
        if st.session_state["candidates"]:
            st.markdown("#### Candidate List")
            df = pd.DataFrame(st.session_state["candidates"])
            cols = ["id", "smiles", "predicted_activity", "predicted_selectivity",
                    "predicted_stability", "epistemic_variance", "source"]
            if "expected_improvement" in df.columns:
                cols.insert(2, "expected_improvement")
            st.dataframe(df[cols], use_container_width=True, height=400)
            
            st.markdown("---")
            st.markdown("#### 3D Crystal Structure Viewer")
            st.info("Simulating DiffCSP output — zeolite-framework catalyst (PDB: 7S5B)")
            from streamlit_molstar import st_molstar_rcsb
            st_molstar_rcsb('7S5B')
        else:
            st.info("Click 'Generate Candidates' or 'Load Demo' to begin")
    
    # TAB 2: Pareto Analysis
    with tabs[1]:
        st.markdown("### Multi-Objective Pareto Front")
        
        if st.session_state["candidates"]:
            import plotly.express as px
            df = pd.DataFrame(st.session_state["candidates"])
            
            def is_pareto_optimal(df):
                n = len(df)
                pareto = np.ones(n, dtype=bool)
                vals = df[["predicted_activity", "predicted_selectivity", "predicted_stability"]].values
                for i in range(n):
                    for j in range(n):
                        if i != j and (vals[j] >= vals[i]).all() and (vals[j] > vals[i]).any():
                            pareto[i] = False
                            break
                return pareto
            
            df["pareto_optimal"] = is_pareto_optimal(df)
            df["label"] = df.apply(lambda r: f"OPTIMAL: {r['id']}" if r["pareto_optimal"] else r["id"], axis=1)

            def pareto_category(row):
                src = "Generated" if row["source"] == "generated" else "Retrieved"
                tier = "Pareto-optimal" if row["pareto_optimal"] else "Non-Pareto"
                return f"{src} ({tier})"

            df["_pareto_category"] = df.apply(pareto_category, axis=1)

            pareto_color_map = {
                "Generated (Pareto-optimal)": "#00d4aa",
                "Generated (Non-Pareto)": "#0a9076",
                "Retrieved (Pareto-optimal)": "#d0d8e4",
                "Retrieved (Non-Pareto)": "#6b7789",
            }
            category_order = list(pareto_color_map.keys())
            
            hover_data = {"epistemic_variance": True, "source": True, "pareto_optimal": True}
            if "expected_improvement" in df.columns:
                hover_data["expected_improvement"] = True
            
            fig = px.scatter_3d(
                df,
                x="predicted_activity",
                y="predicted_selectivity",
                z="predicted_stability",
                color="_pareto_category",
                hover_name="label",
                hover_data=hover_data,
                title="3D Pareto Front Visualization",
                color_discrete_map=pareto_color_map,
                category_orders={"_pareto_category": category_order},
                labels={
                    "predicted_activity": "Activity (%)",
                    "predicted_selectivity": "Selectivity (%)",
                    "predicted_stability": "Stability (%)",
                    "_pareto_category": "Category",
                },
            )
            
            axis_tick = dict(color="#cdd6e3", size=11)
            
            fig.update_layout(
                paper_bgcolor="#0f1117",
                plot_bgcolor="#0f1117",
                font=dict(color="#e8ecf2", family="Inter, sans-serif", size=12),
                title_font_size=18,
                title_font_color="#00d4aa",
                legend=dict(
                    title=dict(text="Category", font=dict(color="#eef2f8", size=13)),
                    font=dict(color="#e8ecf2", size=12),
                    bgcolor="rgba(26, 29, 46, 0.98)",
                    bordercolor="#5c6578",
                    borderwidth=1,
                    tracegroupgap=8,
                ),
                hoverlabel=dict(
                    bgcolor="#1a2230",
                    font_size=12,
                    font_color="#ffffff",
                    bordercolor="#3d4654",
                ),
                scene=dict(
                    bgcolor="#0f1117",
                    xaxis=dict(
                        backgroundcolor="#1a1d2e",
                        gridcolor="#3d4654",
                        showbackground=True,
                        tickfont=axis_tick,
                    ),
                    yaxis=dict(
                        backgroundcolor="#1a1d2e",
                        gridcolor="#3d4654",
                        showbackground=True,
                        tickfont=axis_tick,
                    ),
                    zaxis=dict(
                        backgroundcolor="#1a1d2e",
                        gridcolor="#3d4654",
                        showbackground=True,
                        tickfont=axis_tick,
                    ),
                ),
                height=620,
                margin=dict(l=0, r=0, t=52, b=0),
            )
            
            # Axis titles keep text from px.labels; enforce light colors for readability
            fig.update_scenes(
                xaxis_title_font=dict(color="#eef2f8", size=13),
                yaxis_title_font=dict(color="#eef2f8", size=13),
                zaxis_title_font=dict(color="#eef2f8", size=13),
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            pareto_count = int(df["pareto_optimal"].sum())
            st.success(f"{pareto_count} Pareto-optimal candidates identified out of {len(df)} total")
        else:
            st.info("Generate candidates first to visualize the Pareto front")
    
    # TAB 3: Strategy Comparison
    with tabs[2]:
        st.markdown("### Expected Improvement vs. Greedy Ranking")
        
        st.markdown("""
        **The Limitation of Greedy Ranking:**
        
        Models trained on limited data may be overconfident about similar structures.
        High predicted score ≠ high information gain.
        
        **Expected Improvement Solution:**
        - Rewards candidates predicted to beat current best
        - Prioritizes high epistemic uncertainty regions
        - *"Don't just exploit what you know — explore what you don't"*
        """)
        
        if st.session_state["candidates"] and st.session_state["session_id"]:
            col_compare = st.columns(2)
            
            with st.spinner("Fetching both rankings..."):
                r_score = requests.post(
                    f"{API_URL}/api/rank-by-score",
                    json={"session_id": st.session_state["session_id"]}
                )
                r_ei = requests.post(
                    f"{API_URL}/api/rank",
                    json={"session_id": st.session_state["session_id"]}
                )
            
            if r_score.status_code == 200 and r_ei.status_code == 200:
                df_score = pd.DataFrame(r_score.json()["candidates"])
                df_score["rank"] = range(1, len(df_score) + 1)
                
                df_ei = pd.DataFrame(r_ei.json()["candidates"])
                df_ei["rank"] = range(1, len(df_ei) + 1)
                
                with col_compare[0]:
                    st.markdown("#### Ranked by Predicted Score")
                    st.caption("Greedy strategy — highest predicted activity only")
                    show_cols = ["rank", "id", "predicted_activity", "epistemic_variance"]
                    st.dataframe(df_score[show_cols].head(5), use_container_width=True)
                    st.caption(f"Top pick: **{df_score.iloc[0]['id']}** ({df_score.iloc[0]['predicted_activity']:.1f}%)")
                
                with col_compare[1]:
                    st.markdown("#### Ranked by Expected Improvement")
                    st.caption("Bayesian strategy — balances score and uncertainty")
                    show_cols_ei = ["rank", "id", "expected_improvement", "epistemic_variance", "predicted_activity"]
                    st.dataframe(df_ei[show_cols_ei].head(5), use_container_width=True)
                    st.caption(f"Top pick: **{df_ei.iloc[0]['id']}** (EI: {df_ei.iloc[0].get('expected_improvement', 0):.2f})")
                
                top_score_id = df_score.iloc[0]["id"]
                top_ei_id = df_ei.iloc[0]["id"]
                
                if top_score_id != top_ei_id:
                    st.warning(f"""
                    **Ranking Divergence Detected**
                    
                    Score ranking: `{top_score_id}`  
                    EI ranking: `{top_ei_id}`
                    
                    EI selected a different candidate to maximize information gain from the next experiment.
                    """)
                else:
                    st.info("Both rankings converge on the same top candidate")
        else:
            st.info("Generate candidates first to compare strategies")
    
    # TAB 4: Multi-Acquisition
    with tabs[3]:
        st.markdown("### Advanced Acquisition Functions")
        
        st.markdown("""
        Different acquisition strategies optimize for different goals:
        
        - **Expected Improvement (EI):** Balanced exploration/exploitation
        - **Probability of Improvement (PI):** Conservative, high success rate
        - **Upper Confidence Bound (UCB):** Optimistic, favors uncertainty
        - **EI per Cost:** Resource-aware, accounts for synthesis time
        - **Knowledge Gradient:** Optimal for finite experimental budgets
        """)
        
        if st.session_state["candidates"]:
            if st.button("Compare All Strategies", use_container_width=False):
                with st.spinner("Running multi-strategy analysis..."):
                    try:
                        res = requests.get(
                            f"{API_URL}/api/rank/compare-acquisition",
                            params={"session_id": st.session_state["session_id"]}
                        )
                        if res.status_code == 200:
                            comparison = res.json()
                            
                            st.info(comparison["insight"])
                            
                            col_met = st.columns(2)
                            col_met[0].metric("Functions Compared", comparison["total_functions"])
                            col_met[1].metric("Unique Top Picks", comparison["unique_top_picks"])
                            
                            st.markdown("#### Top Candidate from Each Strategy")
                            comp_data = []
                            for func_id, result in comparison["comparison"].items():
                                comp_data.append({
                                    "Strategy": result["function_name"],
                                    "Top Candidate": result["top_candidate_id"],
                                    "Predicted Activity": f"{result['predicted_activity']:.1f}%",
                                    "Uncertainty": f"{result['epistemic_variance']:.2f}",
                                    "SMILES": result.get("top_candidate_smiles", "N/A")[:40] + "..."
                                })
                            
                            df_comp = pd.DataFrame(comp_data)
                            st.dataframe(df_comp, use_container_width=True)
                            
                            if comparison["consensus"]:
                                st.success("Strong consensus — all strategies agree on top candidate")
                            else:
                                st.warning("""
                                **Strategy Divergence:**
                                - EI: Best overall balance
                                - UCB: Explore uncertain regions
                                - EI per Cost: Limited synthesis budget
                                """)
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            st.markdown("---")
            st.markdown("#### Custom Acquisition Function")
            
            acq_func = st.selectbox(
                "Select Strategy",
                ["ei", "pi", "ucb", "ei_per_cost", "kg"],
                format_func=lambda x: {
                    "ei": "Expected Improvement",
                    "pi": "Probability of Improvement",
                    "ucb": "Upper Confidence Bound",
                    "ei_per_cost": "EI per Cost",
                    "kg": "Knowledge Gradient"
                }[x]
            )
            
            params = {}
            if acq_func == "ucb":
                kappa = st.slider("Kappa (exploration parameter)", 0.5, 5.0, 2.0, 0.5)
                params["kappa"] = kappa
            elif acq_func == "ei_per_cost":
                col_time = st.columns(2)
                with col_time[0]:
                    synthesis_time = st.number_input("Synthesis Time (hrs)", 1.0, 10.0, 2.0)
                with col_time[1]:
                    assay_time = st.number_input("Assay Time (hrs)", 1.0, 10.0, 4.0)
                params["synthesis_time"] = synthesis_time
                params["assay_time"] = assay_time
            elif acq_func == "kg":
                remaining_budget = st.number_input("Remaining Budget", 1, 50, 15)
                params["remaining_budget"] = remaining_budget
            
            if st.button(f"Rank by {acq_func.upper()}", use_container_width=False):
                with st.spinner(f"Applying {acq_func} strategy..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/api/rank/acquisition",
                            json={
                                "session_id": st.session_state["session_id"],
                                "function_name": acq_func,
                                "params": params
                            }
                        )
                        if res.status_code == 200:
                            st.session_state["candidates"] = res.json()["candidates"]
                            st.success(f"Ranked by {res.json()['function']}")
                            
                            df = pd.DataFrame(st.session_state["candidates"])
                            display_cols = ["id", "predicted_activity", "epistemic_variance"]
                            
                            score_col = [c for c in df.columns if c not in display_cols and 
                                       c not in ["smiles", "source", "predicted_selectivity", 
                                                "predicted_stability", "acquisition_function"]]
                            if score_col:
                                display_cols.insert(1, score_col[0])
                            
                            st.dataframe(df[display_cols].head(10), use_container_width=True)
                    except Exception as e:
                        st.error(f"Error: {e}")
        else:
            st.info("Generate candidates first to compare acquisition functions")
    
    # TAB 5: Feedback Loop
    with tabs[4]:
        st.markdown("### Active Learning Feedback Loop")
        
        st.markdown("""
        **Closed-Loop Discovery Process:**
        
        Generate → Rank (EI) → Synthesize → Measure → Update → Re-rank
        
        Each iteration updates `best_so_far` and reprioritizes high-uncertainty candidates.
        """)
        
        if st.session_state["candidates"]:
            cand_ids = [c["id"] for c in st.session_state["candidates"]]
            selected_cand = st.selectbox(
                "Select candidate (simulating lab synthesis and testing)",
                cand_ids
            )
            
            col_measure = st.columns(3)
            with col_measure[0]:
                act_val = st.slider("Measured Activity (%)", 0.0, 100.0, 75.0)
            with col_measure[1]:
                sel_val = st.slider("Measured Selectivity (%)", 0.0, 100.0, 70.0)
            with col_measure[2]:
                stab_val = st.slider("Measured Stability (%)", 0.0, 100.0, 70.0)
            
            if st.button("Log Results & Update Model", use_container_width=False):
                with st.spinner("Processing experimental data..."):
                    payload = {
                        "candidate_id": selected_cand,
                        "actual_activity": act_val,
                        "actual_selectivity": sel_val,
                        "actual_stability": stab_val
                    }
                    res = requests.post(f"{API_URL}/api/webhook/mock-eln", json=payload)
                    if res.status_code == 200:
                        data = res.json()
                        new_best = data["new_best_so_far"]
                        iteration = data["iteration"]
                        
                        st.session_state["iteration"] = iteration
                        history = st.session_state["best_score_history"]
                        if not history:
                            history = [act_val]
                        history.append(new_best)
                        st.session_state["best_score_history"] = history
                        
                        st.success(f"Iteration {iteration} complete")
                        
                        col_result = st.columns(3)
                        col_result[0].metric("Measured Activity", f"{act_val:.1f}%")
                        col_result[1].metric("New Session Best", f"{new_best:.1f}%")
                        if len(history) > 1:
                            col_result[2].metric("Gain vs Baseline", f"+{new_best - history[0]:.1f}%")
                        
                        st.info("Navigate to 'Generation & Ranking' → 'Rank by EI' to see updated priorities")
        else:
            st.info("Generate candidates first to use the feedback loop")
    
    # TAB 6: Literature Database
    with tabs[5]:
        st.markdown("### Literature Retrieval System")
        
        st.markdown("""
        Vector database search of scientific literature for baseline performance
        and knowledge-grounded candidate generation.
        """)
        
        if st.button("Extract Baseline Performance"):
            with st.spinner("Searching literature database..."):
                try:
                    res = requests.get(
                        f"{API_URL}/api/literature/baseline",
                        params={
                            "reaction": reaction_smiles,
                            "target_type": st.session_state.get("target_type", "catalyst")
                        }
                    )
                    if res.status_code == 200:
                        baseline = res.json()
                        st.success("Literature baseline extracted successfully")
                        
                        col_base = st.columns(3)
                        col_base[0].metric("Baseline Activity", f"{baseline['baseline_activity']:.1f}%")
                        col_base[1].metric("Baseline Selectivity", f"{baseline['baseline_selectivity']:.1f}%")
                        col_base[2].metric("Baseline Stability", f"{baseline['baseline_stability']:.1f}%")
                        
                        st.info(f"**Source:** {baseline['source']}")
                        st.caption(f"Confidence: {baseline['confidence']} • Citations: {baseline['citations']}")
                except Exception as e:
                    st.error(f"Error: {e}")
        
        st.markdown("---")
        st.markdown("#### Custom Literature Search")
        
        search_query = st.text_input("Search Query", "high selectivity ethanol oligomerization")
        
        col_search = st.columns([2, 1])
        with col_search[0]:
            search_type = st.selectbox("Target Type", ["catalyst", "enzyme"])
        with col_search[1]:
            top_k = st.slider("Results", 1, 5, 3)
        
        if st.button("Search Literature"):
            with st.spinner("Performing semantic search..."):
                try:
                    res = requests.get(
                        f"{API_URL}/api/literature/search",
                        params={"query": search_query, "target_type": search_type, "top_k": top_k}
                    )
                    if res.status_code == 200:
                        data = res.json()
                        results = data["results"]
                        
                        st.success(f"Found {len(results)} relevant publications")
                        
                        for i, paper in enumerate(results, 1):
                            with st.expander(f"{i}. {paper['title']} ({paper['year']})"):
                                st.markdown(f"**Authors:** {paper['authors']}")
                                st.markdown(f"**Journal:** {paper['journal']}")
                                st.markdown(f"**Finding:** {paper['finding']}")
                                
                                col_metrics = st.columns(4)
                                col_metrics[0].metric("Activity", f"{paper['activity']:.1f}%")
                                col_metrics[1].metric("Selectivity", f"{paper['selectivity']:.1f}%")
                                col_metrics[2].metric("Stability", f"{paper['stability']:.1f}%")
                                col_metrics[3].metric("Similarity", f"{paper['similarity_score']:.2f}")
                                
                                st.caption(f"Citations: {paper['citations']} • Confidence: {paper['confidence']}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # TAB 7: Metabolic Analysis
    with tabs[6]:
        st.markdown("### Flux Balance Analysis")
        
        st.markdown("""
        **Synthetic Biology Track (Direction 2)**
        
        Genome-scale metabolic modeling for enzyme pathway optimization.
        Identifies bottleneck reactions and predicts yield improvements.
        """)
        
        col_fba = st.columns(2)
        
        with col_fba[0]:
            st.markdown("#### Base Pathway Simulation")
            if st.button("Run FBA Simulation"):
                with st.spinner("Solving stoichiometric constraints..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/api/fba/simulate",
                            json={"target_product": "Ethanol", "optimize_for": "product"}
                        )
                        if res.status_code == 200:
                            fba = res.json()
                            st.success("FBA simulation complete")
                            
                            col_flux = st.columns(3)
                            col_flux[0].metric("Product Flux", f"{fba['product_flux']} {fba['flux_unit']}")
                            col_flux[1].metric("Yield Efficiency", f"{fba['yield_efficiency']}%")
                            col_flux[2].metric("Theoretical Max", f"{fba['theoretical_max']}")
                            
                            if fba["bottlenecks"]:
                                st.warning(f"{len(fba['bottlenecks'])} Bottlenecks Detected")
                                for bn in fba["bottlenecks"]:
                                    st.markdown(
                                        f"- **{bn['reaction_name']}** ({bn['enzyme']}): "
                                        f"{bn['limiting_factor']}% below average flux"
                                    )
                                
                                st.markdown("**Optimization Suggestions:**")
                                for sug in fba["optimization_suggestions"]:
                                    st.markdown(f"- {sug}")
                            else:
                                st.success("Pathway is well-balanced")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        with col_fba[1]:
            st.markdown("#### Enzyme Impact Prediction")
            enzyme_options = ["Cellulase", "Xylanase", "PDC_ADH", "XyloseDehydrogenase"]
            selected_enzyme = st.selectbox("Select Enzyme", enzyme_options)
            proposed_activity = st.slider("Proposed Activity (× wild-type)", 1.0, 3.0, 1.5, 0.1)
            
            if st.button("Predict Impact"):
                with st.spinner("Running counterfactual analysis..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/api/fba/enzyme-impact",
                            json={
                                "enzyme_id": selected_enzyme,
                                "current_activity": 1.0,
                                "proposed_activity": proposed_activity
                            }
                        )
                        if res.status_code == 200:
                            impact = res.json()
                            st.success("Impact prediction complete")
                            
                            col_impact = st.columns(2)
                            col_impact[0].metric("Baseline Flux", f"{impact['baseline_flux']}")
                            col_impact[1].metric(
                                "Modified Flux",
                                f"{impact['modified_flux']}",
                                delta=f"+{impact['improvement_absolute']}"
                            )
                            
                            st.metric("Yield Improvement", f"+{impact['improvement_percent']}%")
                            st.info(impact["recommendation"])
                            
                            if impact["new_bottlenecks"]:
                                st.warning("New bottlenecks emerged:")
                                for bn in impact["new_bottlenecks"]:
                                    st.markdown(f"- {bn['reaction_name']}")
                    except Exception as e:
                        st.error(f"Error: {e}")
        
        st.markdown("---")
        st.markdown("#### Enzyme Cocktail Design")
        
        if st.button("Generate Optimal Cocktail"):
            with st.spinner("Optimizing enzyme ratios..."):
                try:
                    res = requests.get(
                        f"{API_URL}/api/fba/design-cocktail",
                        params={"substrate": "lignocellulose", "optimization_goal": "max_yield"}
                    )
                    if res.status_code == 200:
                        cocktail_data = res.json()
                        st.success("Optimal cocktail designed")
                        
                        col_cocktail = st.columns(3)
                        col_cocktail[0].metric("Total Enzyme Loading", f"{cocktail_data['total_enzyme_loading']:.1f} U")
                        col_cocktail[1].metric("Cost Index", f"{cocktail_data['cost_index']:.2f}")
                        col_cocktail[2].metric("Predicted Yield", f"{cocktail_data['predicted_yield']:.1f}%")
                        
                        st.markdown("**Enzyme Composition:**")
                        df_cocktail = pd.DataFrame(cocktail_data["cocktail_composition"])
                        st.dataframe(df_cocktail, use_container_width=True)
                except Exception as e:
                    st.error(f"Error: {e}")
    
    # TAB 8: Safety Screening
    with tabs[7]:
        st.markdown("### Biosecurity TEVV Screening")
        
        st.markdown("""
        **Testing, Evaluation, Validation & Verification**
        
        All generated biological sequences are screened against:
        - CDC Select Agents Registry
        - Known toxin databases (diphtheria, botulinum, ricin)
        - Virulence factor motifs
        
        Sequences with homology to restricted agents are automatically blocked.
        """)
        
        if st.session_state.get("target_type") == "enzyme" or st.button("Screen Candidates"):
            with st.spinner("Running biosecurity screening..."):
                try:
                    res = requests.post(
                        f"{API_URL}/api/biosecurity/batch-screen",
                        json={
                            "session_id": st.session_state["session_id"],
                            "target_type": "enzyme"
                        }
                    )
                    if res.status_code == 200:
                        screen_result = res.json()
                        
                        col_screen = st.columns(4)
                        col_screen[0].metric("Total Screened", screen_result["total_screened"])
                        col_screen[1].metric("Approved", screen_result["approved"])
                        col_screen[2].metric("Review Required", screen_result["review_required"])
                        col_screen[3].metric("Blocked", screen_result["blocked"])
                        
                        if screen_result["all_safe"]:
                            st.success("All candidates passed biosecurity screening")
                        else:
                            st.warning("Some candidates require review or were blocked")
                        
                        if screen_result.get("results"):
                            st.markdown("#### Detailed Screening Results")
                            for result in screen_result["results"][:5]:
                                status_class = {
                                    "APPROVED": "status-approved",
                                    "REVIEW_REQUIRED": "status-warning",
                                    "BLOCKED": "status-blocked"
                                }.get(result["status"], "")
                                
                                with st.expander(
                                    f"{result['sequence_id']} — "
                                    f"<span class='status-badge {status_class}'>{result['status']}</span>",
                                    expanded=False
                                ):
                                    st.markdown(f"**Clearance Level:** {result['clearance_level']}")
                                    st.markdown(f"**Sequence Length:** {result['sequence_length']} aa")
                                    st.markdown(f"**Synthesis Permitted:** {'Yes' if result['synthesis_permitted'] else 'No'}")
                                    
                                    if result["violations"]:
                                        st.error("**Violations:**")
                                        for v in result["violations"]:
                                            st.markdown(f"- {v['severity'].upper()}: {v['agent']}")
                                            st.markdown(f"  Pattern: `{v['matched_pattern']}` at position {v['position']}")
                                            st.markdown(f"  {v['recommendation']}")
                                    
                                    if result["warnings"]:
                                        st.warning("**Warnings:**")
                                        for w in result["warnings"]:
                                            st.markdown(f"- {w['description']} (Risk: {w['risk_level']})")
                except Exception as e:
                    if "only applies to biological" in str(e).lower():
                        st.info("Biosecurity screening applies to enzyme/biological sequences only")
                    else:
                        st.error(f"Error: {e}")
        else:
            st.info("Biosecurity screening applies to enzyme sequences (Synthetic Biology track)")
        
        st.markdown("---")
        
        if st.button("View Compliance Report"):
            try:
                res = requests.get(f"{API_URL}/api/biosecurity/compliance-report")
                if res.status_code == 200:
                    report = res.json()
                    st.success("TEVV System Operational")
                    
                    st.markdown(f"**TEVV Version:** {report['tevv_version']}")
                    st.markdown(f"**Last Database Update:** {report['last_database_update']}")
                    
                    st.markdown("**Screening Databases:**")
                    for db in report["screening_databases"]:
                        st.markdown(f"- {db}")
                    
                    st.markdown("**Compliance Standards:**")
                    for std in report["compliance_standards"]:
                        st.markdown(f"- {std}")
                    
                    col_report = st.columns(2)
                    col_report[0].metric("False Positive Rate", report["false_positive_rate"])
                    col_report[1].metric("False Negative Rate", report["false_negative_rate"])
            except Exception as e:
                st.error(f"Error: {e}")

else:
    st.markdown(
        """
        <div class="home-landing">
            <div class="home-landing-inner">
                <div class="home-pill">GPS Renewables · Molecular Discovery</div>
                <h1 class="home-hero-title">Catalyst<span class="home-accent">AI</span></h1>
                <p class="home-tagline">Closed-loop discovery for ethanol-to-SAF catalysts—generative design, predictive ranking, and lab feedback in one workspace.</p>
                <p class="home-intro">Traditional screening spans years; CatalystAI targets weeks by combining surrogate models, Bayesian acquisition, and explicit uncertainty—so each experiment earns the maximum information toward your objectives.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="home-section-title">Platform capabilities</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="home-card-wrap">
            <div class="home-card">
                <h4>Lab-in-the-loop</h4>
                <p>A continuous cycle: propose candidates, rank by information value, prioritize synthesis,
                and fold wet-lab readouts back into the model.</p>
            </div>
            <div class="home-card">
                <h4>Uncertainty-first ranking</h4>
                <p>Expected improvement balances predicted performance against epistemic variance—prioritizing
                experiments that resolve the model—not just chasing the highest point estimate.</p>
            </div>
            <div class="home-card">
                <h4>Integrated toolchain</h4>
                <p>Literature baselines, multi-objective Pareto views, metabolic analysis, and biosecurity
                screening—all accessible from one Streamlit dashboard backed by FastAPI.</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="home-section-title">Discovery pipeline</p>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="home-pipeline">
            <div class="home-pstep">
                <div class="home-pstep-num">1</div>
                <span class="home-pstep-label">Generate</span>
                <span class="home-pstep-desc">Novel compositions &amp; scaffolds</span>
            </div>
            <div class="home-pstep">
                <div class="home-pstep-num">2</div>
                <span class="home-pstep-label">Predict</span>
                <span class="home-pstep-desc">Activity, selectivity, stability</span>
            </div>
            <div class="home-pstep">
                <div class="home-pstep-num">3</div>
                <span class="home-pstep-label">Rank</span>
                <span class="home-pstep-desc">Bayesian EI / strategies</span>
            </div>
            <div class="home-pstep">
                <div class="home-pstep-num">4</div>
                <span class="home-pstep-label">Synthesize</span>
                <span class="home-pstep-desc">Top-priority candidates</span>
            </div>
            <div class="home-pstep">
                <div class="home-pstep-num">5</div>
                <span class="home-pstep-label">Feedback</span>
                <span class="home-pstep-desc">Update &amp; re-rank</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="home-cta-panel">
            <p>Start from the sidebar</p>
            <span><strong>Load Demo</strong> for a guided session with pre-ranked candidates ·
            <strong>New Session</strong> to configure your reaction and constraints from scratch.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<p class="home-foot">GPS Renewables molecular discovery hackathon · 2025 · '
        "2G ethanol-to-SAF pathway emphasis</p>",
        unsafe_allow_html=True,
    )
