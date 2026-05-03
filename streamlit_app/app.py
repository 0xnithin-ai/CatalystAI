import streamlit as st
import requests
import pandas as pd
import numpy as np
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="CatalystAI Discovery", layout="wide", page_icon="🧪")

st.markdown("""
<style>
    [data-testid="stSidebar"] { background: #0f1117; }
    h1 { color: #00d4aa; font-family: monospace; }
    .stButton > button { background: #00d4aa; color: black; border-radius: 6px; font-weight: bold; }
    .stButton > button:hover { background: #00b894; }
</style>
""", unsafe_allow_html=True)

st.title("🧪 CatalystAI — Molecular Discovery Platform")
st.caption("AI-powered closed-loop discovery engine | GPS Renewables Hackathon 2025")

# Session state init
if "session_id" not in st.session_state:
    st.session_state["session_id"] = None
if "candidates" not in st.session_state:
    st.session_state["candidates"] = []
if "target_type" not in st.session_state:
    st.session_state["target_type"] = "catalyst"

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🎯 Target Definition")
    target_type = st.selectbox("Track", ["catalyst", "enzyme"],
                               help="Catalyst → Chemical Catalysis | Enzyme → Synthetic Biology")
    reaction_smiles = st.text_input("Target SMILES / Reaction", "CC(=O)O")
    temp_min = st.number_input("Temp Min (°C)", value=25)
    temp_max = st.number_input("Temp Max (°C)", value=300)

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("🚀 Create Session"):
            payload = {
                "reaction": reaction_smiles,
                "constraints": {"temperature_range": [temp_min, temp_max], "pressure_range": [1, 10]}
            }
            try:
                res = requests.post(f"{API_URL}/api/sessions", json=payload)
                if res.status_code == 200:
                    st.session_state["session_id"] = res.json()["id"]
                    st.session_state["target_type"] = target_type
                    st.session_state["candidates"] = []
                    st.success("Session created!")
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Cannot connect to API: {e}")

    with col_b:
        if st.button("🎬 Load Demo"):
            try:
                res = requests.post(f"{API_URL}/api/rank", json={"session_id": "demo-historical-session"})
                if res.status_code == 200:
                    st.session_state["session_id"] = "demo-historical-session"
                    st.session_state["target_type"] = "catalyst"
                    st.session_state["candidates"] = res.json()["candidates"]
                    st.success("Demo loaded — pre-ranked by EI!")
                else:
                    st.error("Demo session not found. Restart backend.")
            except Exception as e:
                st.error(f"Connection error: {e}")

    if st.session_state["session_id"]:
        st.divider()
        st.caption(f"📌 Session: `{st.session_state['session_id'][:12]}...`")
        st.caption(f"🔬 Track: `{st.session_state.get('target_type', '—')}`")

# ── MAIN PANEL ────────────────────────────────────────────────────────────────
if st.session_state["session_id"]:

    tab1, tab2, tab3 = st.tabs(["⚗️ Candidate Explorer", "📊 Pareto Visualizer", "🔁 ELN Feedback Loop"])

    # ── TAB 1: Candidate Explorer ─────────────────────────────────────────────
    with tab1:
        col_gen, col_rank, _ = st.columns([1, 1, 3])
        with col_gen:
            if st.button("⚡ Generate Candidates"):
                with st.spinner("Running mock inference pipeline..."):
                    payload = {
                        "session_id": st.session_state["session_id"],
                        "target_type": st.session_state["target_type"]
                    }
                    res = requests.post(f"{API_URL}/api/generate", json=payload)
                    if res.status_code == 200:
                        st.session_state["candidates"] = res.json()["candidates"]
                        st.success(f"Generated {res.json()['count']} candidates!")
                    else:
                        st.error(res.text)

        with col_rank:
            if st.button("🧠 Rank by EI"):
                with st.spinner("Applying Bayesian Expected Improvement..."):
                    res = requests.post(f"{API_URL}/api/rank", json={"session_id": st.session_state["session_id"]})
                    if res.status_code == 200:
                        st.session_state["candidates"] = res.json()["candidates"]
                        st.success("Re-ranked by Expected Improvement!")
                    else:
                        st.error(res.text)

        if st.session_state["candidates"]:
            df = pd.DataFrame(st.session_state["candidates"])
            cols = ["id", "smiles", "predicted_activity", "predicted_selectivity",
                    "predicted_stability", "epistemic_variance", "source"]
            if "expected_improvement" in df.columns:
                cols.insert(2, "expected_improvement")

            st.dataframe(df[cols], width="stretch")

            # Molstar Viewer
            st.divider()
            st.subheader("🔬 3D Structure Viewer (Molstar)")
            from streamlit_molstar import st_molstar_rcsb
            if st.session_state.get("target_type") == "enzyme":
                st.info("Rendering enzyme backbone — simulating RFdiffusion output (PDB: 1LOL — adenylate kinase)")
                st_molstar_rcsb('1LOL')
            else:
                st.info("Rendering crystal lattice — simulating DiffCSP output (PDB: 7S5B — zeolite catalyst)")
                st_molstar_rcsb('7S5B')
        else:
            st.info("Click '⚡ Generate Candidates' above, or '🎬 Load Demo' in the sidebar.")

    # ── TAB 2: Pareto Visualizer ──────────────────────────────────────────────
    with tab2:
        if st.session_state["candidates"]:
            import plotly.express as px
            df = pd.DataFrame(st.session_state["candidates"])

            # Compute Pareto frontier (maximize all three axes)
            def is_pareto_optimal(df):
                n = len(df)
                pareto = np.ones(n, dtype=bool)
                vals = df[["predicted_activity", "predicted_selectivity", "predicted_stability"]].values
                for i in range(n):
                    for j in range(n):
                        if i != j:
                            if (vals[j] >= vals[i]).all() and (vals[j] > vals[i]).any():
                                pareto[i] = False
                                break
                return pareto

            df["pareto_optimal"] = is_pareto_optimal(df)
            df["label"] = df.apply(lambda r: f"★ {r['id']}" if r["pareto_optimal"] else r["id"], axis=1)

            hover_data = {"epistemic_variance": True}
            if "expected_improvement" in df.columns:
                hover_data["expected_improvement"] = True

            fig = px.scatter_3d(
                df,
                x="predicted_activity", y="predicted_selectivity", z="predicted_stability",
                color="source",
                symbol="pareto_optimal",
                hover_name="label",
                hover_data=hover_data,
                title="Pareto Front — Activity vs Selectivity vs Stability",
                color_discrete_map={"generated": "#00d4aa", "retrieved": "#6c757d"},
                labels={
                    "predicted_activity": "Activity (%)",
                    "predicted_selectivity": "Selectivity (%)",
                    "predicted_stability": "Stability (%)"
                }
            )
            fig.update_layout(
                paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", font_color="white",
                scene=dict(
                    xaxis=dict(backgroundcolor="#1a1d2e"),
                    yaxis=dict(backgroundcolor="#1a1d2e"),
                    zaxis=dict(backgroundcolor="#1a1d2e")
                )
            )
            st.plotly_chart(fig, width="stretch")
            pareto_count = int(df["pareto_optimal"].sum())
            st.success(f"★ {pareto_count} Pareto-optimal candidates identified out of {len(df)} total")
        else:
            st.info("Generate candidates first to see the Pareto front visualization.")

    # ── TAB 3: ELN Feedback Loop ──────────────────────────────────────────────
    with tab3:
        st.subheader("🔁 Simulate Wet-Lab Feedback (Mock ELN)")
        st.markdown("""
        **How this works:** Select a candidate, enter the measured experimental results,
        then click **Log Result**. The backend updates `best_so_far` and the Bayesian EI
        scores shift — re-run ranking to see the active learning in action.
        """)
        if st.session_state["candidates"]:
            cand_ids = [c["id"] for c in st.session_state["candidates"]]
            selected_cand = st.selectbox("Select Candidate (simulating synthesis + lab test)", cand_ids)
            act_val = st.slider("Measured Activity Result (%)", 0.0, 100.0, 70.0)
            sel_val = st.slider("Measured Selectivity Result (%)", 0.0, 100.0, 70.0)
            stab_val = st.slider("Measured Stability Result (%)", 0.0, 100.0, 70.0)

            if st.button("📤 Log Result to ELN & Trigger Active Learning"):
                with st.spinner("Sending to ELN webhook → Updating Bayesian model..."):
                    payload = {
                        "candidate_id": selected_cand,
                        "actual_activity": act_val,
                        "actual_selectivity": sel_val,
                        "actual_stability": stab_val
                    }
                    res = requests.post(f"{API_URL}/api/webhook/mock-eln", json=payload)
                    if res.status_code == 200:
                        new_best = res.json()["new_best_so_far"]
                        st.success(f"✅ Experiment logged! New session best: **{new_best:.1f}%** activity")
                        st.info("Go to '⚗️ Candidate Explorer' → click '🧠 Rank by EI' to see reprioritized candidates!")
                    else:
                        st.error(f"Error: {res.text}")
        else:
            st.info("Generate candidates first to use the ELN feedback loop.")

else:
    st.markdown("""
    ## 👋 Welcome to CatalystAI

    **AI-Powered Molecular Discovery Platform** for GPS Renewables' 2G Ethanol-to-SAF pathway.

    ### Getting Started
    1. Use the sidebar to **🚀 Create a Session** — define your target reaction and constraints.
    2. Or click **🎬 Load Demo** to instantly see a pre-loaded SAF catalyst discovery session.

    ### What this MVP demonstrates
    - 🤖 **Generative AI** — DiffCSP / RFdiffusion (cached outputs) for novel catalyst/enzyme design
    - 🔮 **Bayesian Active Learning** — Expected Improvement ranking to prioritize experiments
    - 🔬 **3D Molecular Viewer** — Molstar WebGL crystal lattice / enzyme backbone viewer
    - 📊 **Pareto Front Visualization** — Activity vs Selectivity vs Stability
    - 🔁 **Closed-Loop ELN** — Mock wet-lab feedback triggers model re-prioritization
    """)
