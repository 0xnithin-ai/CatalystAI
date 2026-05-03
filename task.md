# CatalystAI — Hackathon MVP Tracker
> 3-Day Sprint | 34 Actionable Tasks | 6 Groups
> *Note: Postgres, Redis, and Celery are excluded from this 3-day sprint. We are focusing purely on the core Active Learning loop and UX.*

---

## Day 1 — Setup + Backend core + Fixtures (Tasks 1–13)

### Group 1: Foundation Setup
- [x] **Task 1: [QUICK]** Create root monorepo folders (`backend/`, `streamlit_app/`) and `.gitignore`.
- [x] **Task 2: [BLOCKER]** Set up Python virtual environment in `backend/` and install `fastapi`, `uvicorn`, `pydantic`, `scipy`.
- [x] **Task 3: [QUICK]** Initialize FastAPI app in `backend/app/main.py` with CORS configured.
- [x] **Task 4: [QUICK]** Create `docker-compose.yml` to orchestrate FastAPI and Streamlit locally.

### Group 2: Backend Core & APIs
- [ ] **Task 5: [BLOCKER]** Define Pydantic schema for `Candidate` (id, smiles, predicted_activity, predicted_selectivity, predicted_stability, epistemic_variance, source).
- [ ] **Task 6: [BLOCKER]** Define Pydantic schema for `Session` (id, reaction, constraints).
- [ ] **Task 7: [BLOCKER]** Define Pydantic schema for `Experiment` (candidate_id, actual_activity, actual_selectivity, actual_stability).
- [ ] **Task 8: [CRITICAL]** Build `GET /api/candidates` endpoint to return the current list of candidates for a session.
- [ ] **Task 9: [CRITICAL]** Build `POST /api/sessions` endpoint to start and persist a new discovery session in memory.

### Group 3: Mock Data & Fixtures
- [ ] **Task 10: [BLOCKER]** Create 10 mock Catalyst candidates in a static JSON array with diverse metrics (activity: 40-90, selectivity: 50-95, high variance for OOD points).
- [ ] **Task 11: [BLOCKER]** Create 10 mock Enzyme candidates in a static JSON array with realistic PDB backbones and sequence data.
- [ ] **Task 12: [QUICK]** Build `backend/app/services/mock_db.py` to manage state in-memory (lists for candidates, dictionaries for experiment logs).
- [ ] **Task 13: [CRITICAL]** Create `POST /api/generate` endpoint to simulate inference by returning a subset of the static JSON candidates.

---

## Day 2 — Active Learning service + Streamlit wiring (Tasks 14–25)

### Group 4: Active Learning Service
- [ ] **Task 14: [BLOCKER]** Build `backend/app/services/bayesian_service.py` to hold expected improvement logic.
- [ ] **Task 15: [CRITICAL]** Implement the EI formula inline: `EI = (mu - best) * norm.cdf((mu - best) / sigma) + sigma * norm.pdf((mu - best) / sigma)` using SciPy.
- [ ] **Task 16: [CRITICAL]** Create `POST /api/rank` endpoint to apply the EI formula to all candidates and sort the returned list.
- [ ] **Task 17: [CRITICAL]** Create `POST /api/webhook/mock-eln` to simulate receiving wet-lab feedback for a candidate.
- [ ] **Task 18: [BLOCKER]** Update the in-memory state with the new "actual" metrics when the ELN webhook is triggered.
- [ ] **Task 19: [QUICK]** Add a trigger inside the webhook to recalculate the `best_so_far` value across the session.

### Group 5: Streamlit Dashboard Core
- [ ] **Task 20: [BLOCKER]** Set up `streamlit_app/app.py` with basic multi-page routing and CSS injection.
- [ ] **Task 21: [QUICK]** Build the "Target Reaction Input" form (Input SMILES, select temperature/pressure constraints).
- [ ] **Task 22: [CRITICAL]** Connect the Streamlit form to the FastAPI `POST /api/sessions` endpoint.
- [ ] **Task 23: [CRITICAL]** Build a UI table/grid to display generated candidates by fetching from `GET /api/candidates`.
- [ ] **Task 24: [CRITICAL]** Add a "Rank by Expected Improvement" button that calls `POST /api/rank` and re-renders the list.
- [ ] **Task 25: [QUICK]** Wire up a "Simulate Lab Result" button on individual candidates to POST to the mock ELN webhook.

---

## Day 3 — Visualizations + Polish + Demo prep (Tasks 26–34)

### Group 6: Visualizations & Demo Polish
- [ ] **Task 26: [BLOCKER]** Install `plotly` and `streamlit-plotly-events` in the Streamlit environment.
- [ ] **Task 27: [CRITICAL]** Create a 3D Pareto Front scatter plot visualizing Activity (x), Selectivity (y), and Stability (z).
- [ ] **Task 28: [QUICK]** Add color-coding to the Plotly chart to visually separate generated candidates from retrieved baselines.
- [ ] **Task 29: [BLOCKER]** Install and integrate the `streamlit-molstar` plugin.
- [ ] **Task 30: [CRITICAL]** Render a 3D molecular/crystal structure in Molstar when a specific candidate is selected from the list.
- [ ] **Task 31: [QUICK]** Add basic error handling and loading states in Streamlit (e.g., `st.spinner` during generation/ranking API calls).
- [ ] **Task 32: [CRITICAL]** Perform End-to-End Smoke Test: Run through the full loop (Create Session -> Generate -> Rank -> Log Result -> See Re-Ranking).
- [ ] **Task 33: [CRITICAL]** Demo Prep: Seed the initial backend state with one completed historical session to instantly show the "before/after" value of active learning.
- [ ] **Task 34: [QUICK]** Add final inline documentation and a high-level architecture diagram to `README.md`.
