import numpy as np
from scipy.stats import norm
from typing import List, Dict, Any
from app.services.mock_db import candidates_db, experiments_db

def calculate_ei(mu: float, sigma: float, best_so_far: float) -> float:
    """
    Computes Expected Improvement (EI).
    EI = (mu - best) * \Phi(Z) + sigma * \phi(Z)
    """
    if sigma <= 0:
        return max(0.0, mu - best_so_far)
    
    Z = (mu - best_so_far) / sigma
    ei = (mu - best_so_far) * norm.cdf(Z) + sigma * norm.pdf(Z)
    return float(ei)

def get_best_so_far(session_id: str) -> float:
    experiments = experiments_db.get(session_id, [])
    if not experiments:
        return 0.0
    return max([exp.actual_activity for exp in experiments])

def rank_candidates(session_id: str) -> List[Dict[str, Any]]:
    candidates = candidates_db.get(session_id, [])
    best_so_far = get_best_so_far(session_id)
    
    ranked_list = []
    for c in candidates:
        mu = c.predicted_activity
        sigma = c.epistemic_variance
        
        ei = calculate_ei(mu, sigma, best_so_far)
        c_dict = c.model_dump()
        c_dict["expected_improvement"] = ei
        ranked_list.append(c_dict)
        
    ranked_list.sort(key=lambda x: x["expected_improvement"], reverse=True)
    return ranked_list
