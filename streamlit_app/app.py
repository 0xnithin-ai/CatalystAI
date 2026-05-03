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
    .stButton > button:hover { background: #009d7f; }
    .metric-card { background: #1a1d2e; border-radius: 8px; padding: 1rem; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.title("🧪 CatalystAI — Molecular Discovery Platform")
st.caption("AI-powered closed-loop discovery engine | GPS Renewables Hackathon 2025 | SAF Catalyst Track")

# ── Session state ─────────────────────────────────────────────────────────────
for key, default in [
    ("session_id", None), ("candidates", []),
    ("target_type", "catalyst"), ("iteration", 0),
    ("best_score_history", []), ("score_baseline", None)
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🎯 Target Definition")
    st.info("**Track: Chemical Catalysis (Direction 1)**\nTarget: Ethanol → SAF conversion catalyst")

    reaction_smiles = st.text_input("Target SMILES", "CCO→CC(=O)O",
                                    help="Ethanol oxidation to acetic acid, first step in SAF synthesis")
    temp_min = st.number_input("Temp Min (°C)", value=200)
    temp_max = st.number_input("Temp Max (°C)", value=400)

    st.divider()
    col_a, col_b = st.columns(2)

    with col_a:
        if st.button("🚀 New Session"):
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
                    st.success("Session created!")
                else:
                    st.error(res.text)
            except Exception as e:
                st.error(f"Cannot reach API: {e}")

    with col_b:
        if st.button("🎬 Load Demo"):
            try:
                # Load the pre-seeded demo + rank immediately
                res = requests.post(f"{API_URL}/api/rank", json={"session_id": "demo-historical-session"})
                if res.status_code == 200:
                    st.session_state["session_id"] = "demo-historical-session"
                    st.session_state["target_type"] = "catalyst"
                    st.session_state["candidates"] = res.json()["candidates"]
                    st.session_state["iteration"] = 1  # Demo has 1 prior experiment
                    # Seed history to show before/after
                    st.session_state["best_score_history"] = [70.0, 85.0]
                    st.session_state["score_baseline"] = 70.0
                    st.success("Demo loaded!")
                else:
                    st.error("Restart backend — demo session not found.")
            except Exception as e:
                st.error(f"Connection error: {e}")

    if st.session_state["session_id"]:
        st.divider()
        st.caption(f"📌 `{st.session_state['session_id'][:16]}...`")
        st.caption(f"🔁 Iteration: **{st.session_state['iteration']}**")

# ── PROGRESS BANNER (Before vs After Learning) ────────────────────────────────
if st.session_state["session_id"] and st.session_state["best_score_history"]:
    history = st.session_state["best_score_history"]
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🔁 Learning Iteration", st.session_state["iteration"])
    with col2:
        st.metric("📉 Starting Best Score", f"{history[0]:.1f}%",
                  help="Best activity before any wet-lab feedback")
    with col3:
        st.metric("📈 Current Best Score", f"{history[-1]:.1f}%",
                  delta=f"+{history[-1] - history[0]:.1f}%" if len(history) > 1 else None,
                  help="Best activity after active learning re-ranking")
    with col4:
        improvement = history[-1] - history[0]
        st.metric("🚀 AL Gain", f"+{improvement:.1f}%",
                  help="How much the active learning loop improved candidate selection")
    st.divider()

# ── MAIN PANEL ────────────────────────────────────────────────────────────────
if st.session_state["session_id"]:

    tab1, tab2, tab3, tab4 = st.tabs([
        "⚗️ Generate & Rank",
        "📊 Pareto Front",
        "🔬 Why EI? (Key Insight)",
        "🔁 ELN Feedback Loop"
    ])

    # ── TAB 1: Generate & Rank ────────────────────────────────────────────────
    with tab1:
        col_gen, col_rank, col_score, _ = st.columns([1, 1, 1, 2])

        with col_gen:
            if st.button("⚡ Generate Candidates"):
                with st.spinner("Querying DiffCSP mock pipeline..."):
                    res = requests.post(f"{API_URL}/api/generate",
                                        json={"session_id": st.session_state["session_id"],
                                              "target_type": "catalyst"})
                    if res.status_code == 200:
                        cands = res.json()["candidates"]
                        st.session_state["candidates"] = cands
                        # Set baseline best score on first generation
                        if not st.session_state["best_score_history"]:
                            baseline = max(c["predicted_activity"] for c in cands)
                            st.session_state["score_baseline"] = baseline
                            st.session_state["best_score_history"] = [baseline]
                        st.success(f"Generated {res.json()['count']} candidates!")

        with col_rank:
            if st.button("🧠 Rank by EI"):
                with st.spinner("Running Bayesian EI..."):
                    res = requests.post(f"{API_URL}/api/rank",
                                        json={"session_id": st.session_state["session_id"]})
                    if res.status_code == 200:
                        st.session_state["candidates"] = res.json()["candidates"]
                        st.success("Ranked by Expected Improvement!")

        with col_score:
            if st.button("📊 Rank by Score"):
                with st.spinner("Ranking by raw prediction..."):
                    res = requests.post(f"{API_URL}/api/rank-by-score",
                                        json={"session_id": st.session_state["session_id"]})
                    if res.status_code == 200:
                        st.session_state["candidates"] = res.json()["candidates"]
                        st.success("Ranked by predicted score!")

        if st.session_state["candidates"]:
            df = pd.DataFrame(st.session_state["candidates"])
            cols = ["id", "smiles", "predicted_activity", "predicted_selectivity",
                    "predicted_stability", "epistemic_variance", "source"]
            if "expected_improvement" in df.columns:
                cols.insert(2, "expected_improvement")
            st.dataframe(df[cols], width="stretch")

            st.divider()
            st.subheader("🔬 3D Crystal Lattice Viewer (Molstar)")
            st.info("Simulating DiffCSP output — zeolite-framework SAF catalyst (PDB: 7S5B)")
            from streamlit_molstar import st_molstar_rcsb
            st_molstar_rcsb('7S5B')

        else:
            st.info("Click '⚡ Generate Candidates' or '🎬 Load Demo' in the sidebar.")

    # ── TAB 2: Pareto Front ───────────────────────────────────────────────────
    with tab2:
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
            df["label"] = df.apply(lambda r: f"★ {r['id']}" if r["pareto_optimal"] else r["id"], axis=1)

            hover_data = {"epistemic_variance": True, "source": True}
            if "expected_improvement" in df.columns:
                hover_data["expected_improvement"] = True

            fig = px.scatter_3d(
                df,
                x="predicted_activity", y="predicted_selectivity", z="predicted_stability",
                color="source", symbol="pareto_optimal",
                hover_name="label", hover_data=hover_data,
                title="Pareto Front — Activity vs Selectivity vs Stability",
                color_discrete_map={"generated": "#00d4aa", "retrieved": "#6c757d"},
                labels={"predicted_activity": "Activity (%)",
                        "predicted_selectivity": "Selectivity (%)",
                        "predicted_stability": "Stability (%)"}
            )
            fig.update_layout(
                paper_bgcolor="#0f1117", plot_bgcolor="#0f1117", font_color="white",
                scene=dict(xaxis=dict(backgroundcolor="#1a1d2e"),
                           yaxis=dict(backgroundcolor="#1a1d2e"),
                           zaxis=dict(backgroundcolor="#1a1d2e"))
            )
            st.plotly_chart(fig, width="stretch")
            pareto_count = int(df["pareto_optimal"].sum())
            st.success(f"★ {pareto_count} Pareto-optimal candidates out of {len(df)} total")
        else:
            st.info("Generate candidates first to see the Pareto visualization.")

    # ── TAB 3: WHY EI? — Side-by-side Comparison ─────────────────────────────
    with tab3:
        st.subheader("🔬 Why Expected Improvement beats raw prediction ranking")
        st.markdown("""
        **The problem with just sorting by score:**
        > A model trained on limited data might be *overconfident* about candidates
        > it has seen similar structures to. High predicted score ≠ high *information gain*.

        **Expected Improvement solves this by rewarding:**
        - Candidates predicted to beat the current best *AND*
        - Candidates the model is **uncertain about** (high epistemic variance)

        > *"Don't just exploit what you know — explore what you don't."*
        """)

        if st.session_state["candidates"] and st.session_state["session_id"]:
            col_left, col_right = st.columns(2)

            with st.spinner("Fetching both rankings..."):
                r_score = requests.post(f"{API_URL}/api/rank-by-score",
                                        json={"session_id": st.session_state["session_id"]})
                r_ei = requests.post(f"{API_URL}/api/rank",
                                     json={"session_id": st.session_state["session_id"]})

            if r_score.status_code == 200 and r_ei.status_code == 200:
                df_score = pd.DataFrame(r_score.json()["candidates"])
                df_score["rank"] = range(1, len(df_score) + 1)

                df_ei = pd.DataFrame(r_ei.json()["candidates"])
                df_ei["rank"] = range(1, len(df_ei) + 1)

                with col_left:
                    st.markdown("### 📊 Ranked by Predicted Score")
                    st.caption("Greedy — picks highest predicted activity only")
                    show_cols = ["rank", "id", "predicted_activity", "epistemic_variance"]
                    st.dataframe(df_score[show_cols].head(5), width="stretch")
                    st.caption(f"Top pick: **{df_score.iloc[0]['id']}** (score: {df_score.iloc[0]['predicted_activity']:.1f}%)")

                with col_right:
                    st.markdown("### 🧠 Ranked by Expected Improvement")
                    st.caption("Bayesian — balances score + uncertainty for max info gain")
                    show_cols_ei = ["rank", "id", "expected_improvement", "epistemic_variance", "predicted_activity"]
                    st.dataframe(df_ei[show_cols_ei].head(5), width="stretch")
                    st.caption(f"Top pick: **{df_ei.iloc[0]['id']}** (EI: {df_ei.iloc[0].get('expected_improvement', 0):.2f})")

                # Highlight differences
                top_score_id = df_score.iloc[0]["id"]
                top_ei_id = df_ei.iloc[0]["id"]
                if top_score_id != top_ei_id:
                    st.warning(f"""
                    ⚡ **The rankings differ!**
                    - Score ranking picks: `{top_score_id}`
                    - EI ranking picks: `{top_ei_id}`

                    EI chose a **different candidate** because it balances high prediction
                    *with* high uncertainty — maximizing what we learn from the next experiment.
                    """)
                else:
                    st.info("Both rankings agree on the top candidate. Log a lab result and re-rank to see divergence!")
        else:
            st.info("Generate candidates first, then both rankings will appear here for comparison.")

    # ── TAB 4: ELN Feedback Loop ──────────────────────────────────────────────
    with tab4:
        st.subheader("🔁 Simulate Wet-Lab Feedback → Active Learning Loop")
        st.markdown("""
        **The closed loop:**
        `Generate → Rank (EI) → Synthesize Top Candidate → Measure → Log → Re-rank`

        Each iteration, the model updates `best_so_far` and candidates with high
        *epistemic uncertainty* get prioritized — the system learns where to look next.
        """)

        if st.session_state["candidates"]:
            cand_ids = [c["id"] for c in st.session_state["candidates"]]
            selected_cand = st.selectbox("Select Candidate (simulating synthesis + lab test)", cand_ids)
            act_val = st.slider("Measured Activity (%)", 0.0, 100.0, 75.0)
            sel_val = st.slider("Measured Selectivity (%)", 0.0, 100.0, 70.0)
            stab_val = st.slider("Measured Stability (%)", 0.0, 100.0, 70.0)

            if st.button("📤 Log to ELN & Trigger Active Learning"):
                with st.spinner("ELN webhook → Bayesian update..."):
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

                        # Update session state
                        st.session_state["iteration"] = iteration
                        history = st.session_state["best_score_history"]
                        if not history:
                            history = [act_val]
                        history.append(new_best)
                        st.session_state["best_score_history"] = history

                        st.success(f"✅ Iteration {iteration} complete!")
                        col_a, col_b, col_c = st.columns(3)
                        col_a.metric("Measured Activity", f"{act_val:.1f}%")
                        col_b.metric("New Session Best", f"{new_best:.1f}%")
                        if len(history) > 1:
                            col_c.metric("Gain vs Start",
                                         f"+{new_best - history[0]:.1f}%",
                                         delta_color="normal")
                        st.info("🔄 Go to '⚗️ Generate & Rank' → click '🧠 Rank by EI' to see reprioritized candidates!")
                        st.info("🔬 Go to 'Why EI?' tab to see how the ranking diverges from raw score after feedback.")
        else:
            st.info("Generate candidates first to use the ELN feedback loop.")

else:
    st.markdown("""
    ## 👋 Welcome to CatalystAI

    **AI-Powered Molecular Discovery Platform** targeting GPS Renewables' 2G Ethanol-to-SAF pathway.

    ---

    ### 🎯 The problem we solve
    Finding a high-performance SAF catalyst currently takes **years of manual screening**.
    CatalystAI compresses this to **weeks** using generative AI + Bayesian active learning.

    ### 🔁 How the loop works
    ```
    1. Generate   → DiffCSP proposes novel crystal structures (mocked here)
    2. Predict    → GNN surrogate scores activity, selectivity, stability
    3. Rank (EI)  → Bayesian EI picks candidates that maximize information gain
    4. Synthesize → Lab tests the top candidate
    5. Feedback   → Results update the model → loop repeats
    ```

    ### 🚀 Getting Started
    - Click **🎬 Load Demo** in the sidebar for an instant pre-loaded session
    - Or click **🚀 New Session** to start fresh
    """)
