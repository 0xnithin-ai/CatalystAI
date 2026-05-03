import uuid
import json
import os
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

