"""
Advanced Acquisition Functions for Multi-Objective Bayesian Optimization
Extends beyond basic Expected Improvement to show technical sophistication
"""
import numpy as np
from scipy.stats import norm
from typing import List, Dict, Any, Optional, Tuple
from app.services.mock_db import candidates_db, experiments_db

def calculate_ei(mu: float, sigma: float, best_so_far: float, xi: float = 0.01) -> float:
    """
    Expected Improvement with exploration parameter xi.
    
    Args:
        mu: Predicted mean
        sigma: Epistemic uncertainty
        best_so_far: Current best observed value
        xi: Exploration parameter (default 0.01)
    """
    if sigma <= 0:
        return max(0.0, mu - best_so_far - xi)
    
    Z = (mu - best_so_far - xi) / sigma
    ei = (mu - best_so_far - xi) * norm.cdf(Z) + sigma * norm.pdf(Z)
    return float(ei)

def calculate_pi(mu: float, sigma: float, best_so_far: float, xi: float = 0.01) -> float:
    """
    Probability of Improvement (PI).
    More conservative than EI - focuses on probability of beating current best.
    
    Args:
        mu: Predicted mean
        sigma: Epistemic uncertainty  
        best_so_far: Current best observed value
        xi: Exploration parameter
    """
    if sigma <= 0:
        return 1.0 if mu > best_so_far + xi else 0.0
    
    Z = (mu - best_so_far - xi) / sigma
    return float(norm.cdf(Z))

def calculate_ucb(mu: float, sigma: float, kappa: float = 2.0) -> float:
    """
    Upper Confidence Bound (UCB).
    Optimistic strategy: pick candidates with high upper confidence bound.
    
    Args:
        mu: Predicted mean
        sigma: Epistemic uncertainty
        kappa: Exploration-exploitation trade-off (higher = more exploration)
    """
    return float(mu + kappa * sigma)

def calculate_thompson_sampling_score(mu: float, sigma: float) -> float:
    """
    Thompson Sampling: Sample from posterior distribution.
    Stochastic acquisition function providing natural exploration-exploitation balance.
    """
    return float(np.random.normal(mu, sigma))

def calculate_ei_per_second(
    mu: float,
    sigma: float,
    best_so_far: float,
    synthesis_time: float,
    assay_time: float
) -> float:
    """
    Expected Improvement per Unit Cost (EI/C).
    Accounts for experimental cost/time in candidate selection.
    
    Args:
        synthesis_time: Hours to synthesize candidate
        assay_time: Hours to run assay
    """
    ei = calculate_ei(mu, sigma, best_so_far)
    total_time = synthesis_time + assay_time
    
    if total_time <= 0:
        return ei
    
    return ei / total_time

def calculate_knowledge_gradient(
    mu: float,
    sigma: float,
    best_so_far: float,
    remaining_budget: int
) -> float:
    """
    Knowledge Gradient (KG).
    Approximates the expected value of information from one more measurement.
    Optimal for finite-horizon optimization.
    """
    if sigma <= 0:
        return 0.0
    
    # Simplified KG calculation (exact requires DP)
    Z = (mu - best_so_far) / sigma
    kg = sigma * (Z * norm.cdf(Z) + norm.pdf(Z))
    
    # Discount by remaining budget (prioritize near-term gains when budget is low)
    discount_factor = min(1.0, remaining_budget / 10.0)
    return float(kg * discount_factor)

def calculate_ei_pareto(
    candidate: Dict[str, Any],
    pareto_front: List[Dict[str, Any]],
    objectives: List[str] = ["predicted_activity", "predicted_selectivity", "predicted_stability"]
) -> float:
    """
    Expected Improvement for Multi-Objective Optimization.
    Measures expected hypervolume improvement of Pareto front.
    
    Args:
        candidate: Candidate to evaluate
        pareto_front: Current Pareto-optimal candidates
        objectives: List of objective names to optimize
    """
    if not pareto_front:
        # If no pareto front yet, use average of objectives
        return np.mean([candidate.get(obj, 0) for obj in objectives])
    
    # Compute dominated hypervolume improvement (simplified)
    # Real implementation would use exact hypervolume calculation
    candidate_vals = np.array([candidate.get(obj, 0) for obj in objectives])
    
    # Check if candidate dominates any pareto point
    dominates_count = 0
    for pf_point in pareto_front:
        pf_vals = np.array([pf_point.get(obj, 0) for obj in objectives])
        if np.all(candidate_vals >= pf_vals) and np.any(candidate_vals > pf_vals):
            dominates_count += 1
    
    # Score based on domination count and objective values
    avg_objective_value = np.mean(candidate_vals)
    domination_bonus = dominates_count * 10.0
    
    # Add uncertainty bonus
    uncertainty = candidate.get("epistemic_variance", 0)
    uncertainty_bonus = uncertainty * 0.5
    
    return float(avg_objective_value + domination_bonus + uncertainty_bonus)

def rank_by_acquisition_function(
    session_id: str,
    function_name: str = "ei",
    **kwargs
) -> List[Dict[str, Any]]:
    """
    Rank candidates using specified acquisition function.
    
    Args:
        session_id: Session identifier
        function_name: Acquisition function name
            - "ei": Expected Improvement (default)
            - "pi": Probability of Improvement
            - "ucb": Upper Confidence Bound
            - "ts": Thompson Sampling
            - "ei_per_cost": EI per unit cost
            - "kg": Knowledge Gradient
            - "ei_pareto": Multi-objective EI
        **kwargs: Function-specific parameters
    
    Returns:
        Ranked list of candidates with acquisition scores
    """
    candidates = candidates_db.get(session_id, [])
    if not candidates:
        return []
    
    # Get best so far from experiments
    experiments = experiments_db.get(session_id, [])
    best_so_far = max([exp.actual_activity for exp in experiments]) if experiments else 0.0
    
    # Compute acquisition scores
    ranked_list = []
    for c in candidates:
        mu = c.predicted_activity
        sigma = c.epistemic_variance
        
        # Calculate score based on function type
        if function_name == "ei":
            xi = kwargs.get("xi", 0.01)
            score = calculate_ei(mu, sigma, best_so_far, xi)
            score_name = "expected_improvement"
            
        elif function_name == "pi":
            xi = kwargs.get("xi", 0.01)
            score = calculate_pi(mu, sigma, best_so_far, xi)
            score_name = "probability_of_improvement"
            
        elif function_name == "ucb":
            kappa = kwargs.get("kappa", 2.0)
            score = calculate_ucb(mu, sigma, kappa)
            score_name = "upper_confidence_bound"
            
        elif function_name == "ts":
            score = calculate_thompson_sampling_score(mu, sigma)
            score_name = "thompson_sample"
            
        elif function_name == "ei_per_cost":
            synthesis_time = kwargs.get("synthesis_time", 2.0)  # hours
            assay_time = kwargs.get("assay_time", 4.0)
            score = calculate_ei_per_second(mu, sigma, best_so_far, synthesis_time, assay_time)
            score_name = "ei_per_cost"
            
        elif function_name == "kg":
            remaining_budget = kwargs.get("remaining_budget", 20)
            score = calculate_knowledge_gradient(mu, sigma, best_so_far, remaining_budget)
            score_name = "knowledge_gradient"
            
        elif function_name == "ei_pareto":
            # Get current pareto front
            pareto_front = get_pareto_front(candidates)
            score = calculate_ei_pareto(c.model_dump(), pareto_front)
            score_name = "ei_pareto"
            
        else:
            # Default to EI
            score = calculate_ei(mu, sigma, best_so_far)
            score_name = "expected_improvement"
        
        c_dict = c.model_dump()
        c_dict[score_name] = score
        c_dict["acquisition_function"] = function_name
        ranked_list.append(c_dict)
    
    # Sort by score
    ranked_list.sort(key=lambda x: x.get(score_name, 0), reverse=True)
    
    return ranked_list

def get_pareto_front(candidates: List[Any]) -> List[Dict[str, Any]]:
    """Extract Pareto-optimal candidates"""
    if not candidates:
        return []
    
    # Convert to dicts if needed
    cands_list = [c.model_dump() if hasattr(c, 'model_dump') else c for c in candidates]
    
    n = len(cands_list)
    pareto = []
    
    for i in range(n):
        is_dominated = False
        c1 = cands_list[i]
        c1_vals = np.array([
            c1.get("predicted_activity", 0),
            c1.get("predicted_selectivity", 0),
            c1.get("predicted_stability", 0)
        ])
        
        for j in range(n):
            if i == j:
                continue
            c2 = cands_list[j]
            c2_vals = np.array([
                c2.get("predicted_activity", 0),
                c2.get("predicted_selectivity", 0),
                c2.get("predicted_stability", 0)
            ])
            
            # Check if c2 dominates c1
            if np.all(c2_vals >= c1_vals) and np.any(c2_vals > c1_vals):
                is_dominated = True
                break
        
        if not is_dominated:
            pareto.append(c1)
    
    return pareto

def compare_acquisition_functions(
    session_id: str
) -> Dict[str, Any]:
    """
    Compare multiple acquisition functions side-by-side.
    Shows which candidates each strategy would pick.
    
    Returns:
        Comparison dictionary with top picks from each function
    """
    functions = {
        "ei": {"name": "Expected Improvement", "params": {}},
        "pi": {"name": "Probability of Improvement", "params": {}},
        "ucb": {"name": "Upper Confidence Bound", "params": {"kappa": 2.0}},
        "ei_per_cost": {"name": "EI per Cost", "params": {"synthesis_time": 2.0, "assay_time": 4.0}},
        "kg": {"name": "Knowledge Gradient", "params": {"remaining_budget": 15}},
    }
    
    results = {}
    for func_id, func_info in functions.items():
        ranked = rank_by_acquisition_function(
            session_id=session_id,
            function_name=func_id,
            **func_info["params"]
        )
        
        if ranked:
            top_pick = ranked[0]
            results[func_id] = {
                "function_name": func_info["name"],
                "top_candidate_id": top_pick["id"],
                "top_candidate_smiles": top_pick.get("smiles", "N/A"),
                "score": top_pick.get(
                    list(top_pick.keys())[-2],  # Get the score key (second to last)
                    0
                ),
                "predicted_activity": top_pick["predicted_activity"],
                "epistemic_variance": top_pick["epistemic_variance"]
            }
    
    # Analyze agreement
    top_ids = [r["top_candidate_id"] for r in results.values()]
    unique_picks = len(set(top_ids))
    
    return {
        "comparison": results,
        "unique_top_picks": unique_picks,
        "total_functions": len(functions),
        "consensus": unique_picks == 1,
        "insight": (
            "All functions agree on the same top candidate - strong signal!" if unique_picks == 1
            else f"{unique_picks} different top picks - functions disagree, suggesting exploration/exploitation trade-offs"
        )
    }
