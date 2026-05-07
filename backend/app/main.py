import uuid
import json
import os
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.schemas import SessionCreate, Session, Candidate
from app.services.mock_db import sessions_db, candidates_db

app = FastAPI(title="CatalystAI MVP API", version="1.0.0")

# Configure CORS for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for MVP
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "CatalystAI API is up and running!"}

@app.post("/api/sessions", response_model=Session)
def create_session(session_in: SessionCreate):
    session_id = str(uuid.uuid4())
    new_session = Session(
        id=session_id,
        reaction=session_in.reaction,
        constraints=session_in.constraints
    )
    sessions_db[session_id] = new_session
    candidates_db[session_id] = []  # Initialize empty candidate list for this session
    return new_session

@app.get("/api/candidates")
def get_candidates(session_id: str):
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"candidates": candidates_db.get(session_id, [])}

class GenerateRequest(BaseModel):
    session_id: str
    target_type: str  # "catalyst" or "enzyme"

@app.post("/api/generate")
def generate_candidates(req: GenerateRequest):
    if req.session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_name = "catalysts.json" if req.target_type == "catalyst" else "enzymes.json"
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", file_name)
    
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            
        candidates = []
        for c in data:
            candidate = Candidate(**c)
            candidate.id = f"{req.session_id}_{c['id']}" # Ensure unique ID per session
            candidates.append(candidate)
            
        candidates_db[req.session_id] = candidates
        return {"message": "Generation complete", "count": len(candidates), "candidates": candidates}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class RankRequest(BaseModel):
    session_id: str

@app.post("/api/rank")
def rank_candidates_endpoint(req: RankRequest):
    if req.session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    from app.services.bayesian_service import rank_candidates
    ranked = rank_candidates(req.session_id)
    return {"candidates": ranked, "count": len(ranked)}

@app.post("/api/rank-by-score")
def rank_by_score_endpoint(req: RankRequest):
    """Rank purely by predicted_activity — no Bayesian logic. Used for comparison."""
    if req.session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    candidates = candidates_db.get(req.session_id, [])
    ranked = sorted([c.model_dump() for c in candidates], key=lambda x: x["predicted_activity"], reverse=True)
    return {"candidates": ranked, "count": len(ranked)}

from app.schemas import Experiment
from app.services.mock_db import experiments_db

@app.post("/api/webhook/mock-eln")
def mock_eln_webhook(exp: Experiment):
    session_id = None
    # Locate which session this candidate belongs to
    for sid, candidates in candidates_db.items():
        if any(c.id == exp.candidate_id for c in candidates):
            session_id = sid
            break
            
    if not session_id:
        raise HTTPException(status_code=404, detail="Candidate not found in any active session")
        
    if session_id not in experiments_db:
        experiments_db[session_id] = []
        
    # Task 18: Update in-memory state with new actual metrics
    experiments_db[session_id].append(exp)
    
    # Task 19: Recalculate best_so_far across the session
    from app.services.bayesian_service import get_best_so_far
    new_best = get_best_so_far(session_id)
    
    iteration = len(experiments_db.get(session_id, []))
    return {
        "message": "Experiment logged successfully",
        "new_best_so_far": new_best,
        "iteration": iteration
    }

# ── NEW ENDPOINTS: RAG, FBA, Biosecurity, Advanced Acquisition ────────────────

@app.get("/api/literature/search")
def search_literature(query: str, target_type: str = "catalyst", top_k: int = 3):
    """RAG-based literature retrieval"""
    from app.services.rag_service import retrieve_similar_literature
    results = retrieve_similar_literature(query, target_type, top_k)
    return {"results": results, "count": len(results)}

@app.get("/api/literature/baseline")
def get_baseline_performance(reaction: str, target_type: str = "catalyst"):
    """Extract baseline performance from literature"""
    from app.services.rag_service import extract_baseline_performance
    baseline = extract_baseline_performance(reaction, target_type)
    return baseline

@app.post("/api/fba/simulate")
def simulate_flux_balance(
    target_product: str = "Ethanol",
    enzyme_modifications: Optional[List[Dict[str, Any]]] = None,
    optimize_for: str = "product"
):
    """Simulate metabolic flux balance analysis"""
    from app.services.fba_service import simulate_fba
    result = simulate_fba(target_product, enzyme_modifications, optimize_for)
    return result

@app.post("/api/fba/enzyme-impact")
def predict_enzyme_impact(
    enzyme_id: str,
    current_activity: float = 1.0,
    proposed_activity: float = 1.5
):
    """Predict impact of enzyme engineering on pathway flux"""
    from app.services.fba_service import predict_enzyme_impact
    result = predict_enzyme_impact(enzyme_id, current_activity, proposed_activity)
    return result

@app.get("/api/fba/design-cocktail")
def design_enzyme_cocktail(substrate: str = "lignocellulose", optimization_goal: str = "max_yield"):
    """Design optimal enzyme cocktail"""
    from app.services.fba_service import design_enzyme_cocktail
    result = design_enzyme_cocktail(substrate, optimization_goal)
    return result

@app.post("/api/biosecurity/screen")
def screen_biosecurity(sequence: str, sequence_id: str, enzyme_family: Optional[str] = None):
    """Screen a single sequence against biosecurity databases"""
    from app.services.biosecurity_service import screen_sequence
    result = screen_sequence(sequence, sequence_id, enzyme_family)
    return result

class BatchScreenRequest(BaseModel):
    session_id: str
    target_type: str = "enzyme"

@app.post("/api/biosecurity/batch-screen")
def batch_screen_biosecurity(req: BatchScreenRequest):
    """Batch screen all candidates in a session"""
    if req.session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    from app.services.biosecurity_service import batch_screen_candidates
    candidates = [c.model_dump() for c in candidates_db.get(req.session_id, [])]
    result = batch_screen_candidates(candidates, req.target_type)
    return result

@app.get("/api/biosecurity/compliance-report")
def get_compliance_report():
    """Get TEVV compliance report"""
    from app.services.biosecurity_service import get_tevv_compliance_report
    return get_tevv_compliance_report()

class AcquisitionRankRequest(BaseModel):
    session_id: str
    function_name: str = "ei"  # ei, pi, ucb, ts, ei_per_cost, kg, ei_pareto
    params: Optional[Dict[str, Any]] = None

@app.post("/api/rank/acquisition")
def rank_by_acquisition_function(req: AcquisitionRankRequest):
    """Rank candidates using specified acquisition function"""
    if req.session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    from app.services.acquisition_service import rank_by_acquisition_function
    params = req.params or {}
    ranked = rank_by_acquisition_function(req.session_id, req.function_name, **params)
    return {"candidates": ranked, "count": len(ranked), "function": req.function_name}

@app.get("/api/rank/compare-acquisition")
def compare_acquisition_functions_endpoint(session_id: str):
    """Compare multiple acquisition functions side-by-side"""
    if session_id not in sessions_db:
        raise HTTPException(status_code=404, detail="Session not found")
    
    from app.services.acquisition_service import compare_acquisition_functions
    comparison = compare_acquisition_functions(session_id)
    return comparison

# Task 33: Seed Demo State
from app.schemas import Constraints
demo_session_id = "demo-historical-session"
sessions_db[demo_session_id] = Session(
    id=demo_session_id,
    reaction="Demo Pre-Seeded Reaction",
    constraints=Constraints(temperature_range=[0, 100], pressure_range=[1, 5])
)
try:
    file_path = os.path.join(os.path.dirname(__file__), "fixtures", "catalysts.json")
    with open(file_path, "r") as f:
        data = json.load(f)
        cands = []
        for c in data:
            cand = Candidate(**c)
            cand.id = f"{demo_session_id}_{cand.id}"
            cands.append(cand)
        candidates_db[demo_session_id] = cands
        
    experiments_db[demo_session_id] = [
        Experiment(candidate_id=cands[0].id, actual_activity=85.0, actual_selectivity=50.0, actual_stability=60.0)
    ]
except Exception as e:
    print("Failed to load demo seed:", e)

