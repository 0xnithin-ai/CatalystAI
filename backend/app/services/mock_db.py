from typing import Dict, List
from app.schemas import Session, Candidate, Experiment

# In-memory storage for the MVP
sessions_db: Dict[str, Session] = {}
candidates_db: Dict[str, List[Candidate]] = {} # keyed by session_id
experiments_db: Dict[str, List[Experiment]] = {} # keyed by session_id
