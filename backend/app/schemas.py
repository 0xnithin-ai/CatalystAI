from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Candidate(BaseModel):
    id: str
    smiles: Optional[str] = None
    predicted_activity: float
    predicted_selectivity: float
    predicted_stability: float
    epistemic_variance: float
    source: str  # e.g., "generated", "retrieved"

class Constraints(BaseModel):
    temperature_range: Optional[List[float]] = None
    pressure_range: Optional[List[float]] = None
    model_config = {"extra": "allow"}

class SessionCreate(BaseModel):
    reaction: str
    constraints: Constraints

class Session(SessionCreate):
    id: str

class Experiment(BaseModel):
    candidate_id: str
    actual_activity: float
    actual_selectivity: float
    actual_stability: float
