import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://backend:8000") # Use docker network name by default
# If running locally without docker compose, uncomment below or set env var
# API_URL = "http://localhost:8000"

st.set_page_config(page_title="CatalystAI Discovery", layout="wide")

# Task 20: CSS Injection for basic styling
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.title(" CatalystAI Molecular Discovery Platform")

# Manage state
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None
if "candidates" not in st.session_state:
    st.session_state["candidates"] = []

# Sidebar for Target Definition (Tasks 21 & 22)
with st.sidebar:
    st.header("1. Target Reaction")
    target_type = st.selectbox("Target Type", ["catalyst", "enzyme"])
    reaction_smiles = st.text_input("Reaction/Target SMILES", "CC(=O)O")
    temp_min = st.number_input("Temp Min (C)", value=25)
    temp_max = st.number_input("Temp max (C)", value=100)
    
    if st.button("Create Session"):
        payload = {
            "reaction": reaction_smiles,
            "constraints": {
                "temperature_range": [temp_min, temp_max],
                "pressure_range": [1, 10]
            }
        }
        try:
            res = requests.post(f"{API_URL}/api/sessions", json=payload)
            if res.status_code == 200:
                st.session_state["session_id"] = res.json()["id"]
                st.session_state["target_type"] = target_type
                st.success("Session Created!")
            else:
                st.error(f"Failed to create session: {res.text}")
        except Exception as e:
            st.error(f"Connection error: {e}")

# Main area
if st.session_state["session_id"]:
    st.subheader(f"Active Session: {st.session_state['session_id'][:8]}...")
    
    # Generate Button
    if st.button("2. Generate Candidates"):
        with st.spinner("Generating..."):
            payload = {
                "session_id": st.session_state["session_id"],
                "target_type": st.session_state["target_type"]
            }
            res = requests.post(f"{API_URL}/api/generate", json=payload)
            if res.status_code == 200:
                st.session_state["candidates"] = res.json()["candidates"]
                st.success(f"Generated {res.json()['count']} candidates!")
    
    # Display Candidates (Task 23 & 24)
    if st.session_state["candidates"]:
        st.header("Candidate Pool")
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("Rank by Expected Improvement"):
                with st.spinner("Ranking via Bayesian Logic..."):
                    res = requests.post(f"{API_URL}/api/rank", json={"session_id": st.session_state["session_id"]})
                    if res.status_code == 200:
                        st.session_state["candidates"] = res.json()["candidates"]
                        st.success("Re-ranked successfully!")
        
        # Table of candidates
        df = pd.DataFrame(st.session_state["candidates"])
        # Format the dataframe columns for better readability
        cols = ["id", "smiles", "predicted_activity", "predicted_selectivity", "predicted_stability", "epistemic_variance", "source"]
        if "expected_improvement" in df.columns:
            cols.insert(2, "expected_improvement")
            
        st.dataframe(df[cols], use_container_width=True)

        st.divider()
        
        col_plot, col_3d = st.columns(2)
        
        with col_plot:
            # Task 27 & 28: 3D Scatter Plot with color coding
            st.header("Pareto Front Analysis")
            import plotly.express as px
            fig = px.scatter_3d(
                df, x='predicted_activity', y='predicted_selectivity', z='predicted_stability',
                color='source', # Distinguishes generated vs retrieved
                hover_name='id',
                title="Activity vs Selectivity vs Stability"
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_3d:
            # Task 29 & 30: Molstar 3D Viewer
            st.header("3D Structure Viewer")
            from streamlit_molstar import st_molstar_rcsb
            selected_for_3d = st.selectbox("Select candidate to view structure", df['id'].tolist())
            
            if st.session_state.get("target_type") == "enzyme":
                st.info("Rendering homologous backbone from PDB (Mocking RFdiffusion)")
                st_molstar_rcsb('1LOL')
            else:
                st.info("Rendering crystal lattice (Mocking DiffCSP)")
                st_molstar_rcsb('7S5B')

        # Simulate Lab Result (Task 25)
        st.divider()
        st.header("Simulate ELN Feedback")
        cand_ids = [c["id"] for c in st.session_state["candidates"]]
        selected_cand = st.selectbox("Select Candidate to synthesis & test", cand_ids)
        act_val = st.slider("Actual Activity Result", 0.0, 100.0, 50.0)
        
        if st.button("Log Result to ELN"):
            with st.spinner("Logging to ELN & Triggering Active Learning..."):
                payload = {
                    "candidate_id": selected_cand,
                    "actual_activity": act_val,
                    "actual_selectivity": 50.0,
                    "actual_stability": 50.0
                }
                res = requests.post(f"{API_URL}/api/webhook/mock-eln", json=payload)
                if res.status_code == 200:
                    st.success(f"Result Logged via Webhook! New Session 'Best So Far': {res.json()['new_best_so_far']}")
                    st.info("Hit the 'Rank by Expected Improvement' button again to see the Active Learning shift priorities!")
else:
    st.info("Please create a session in the sidebar to begin.")
