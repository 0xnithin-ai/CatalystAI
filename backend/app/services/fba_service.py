"""
Flux Balance Analysis Service for Metabolic Pathway Design
Simulates genome-scale metabolic modeling for enzyme engineering
"""
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

# Simplified metabolic network for lignocellulosic ethanol production
# In production: Use COBRApy with genome-scale models (iML1515, etc.)

class MetabolicPathway:
    """Represents a simplified metabolic pathway"""
    
    def __init__(self, name: str, reactions: List[str], flux_bounds: Dict[str, Tuple[float, float]]):
        self.name = name
        self.reactions = reactions
        self.flux_bounds = flux_bounds
        self.current_fluxes = {}
    
# Pre-defined pathway: Lignocellulosic Biomass → Ethanol
BIOMASS_TO_ETHANOL_PATHWAY = {
    "reactions": [
        {"id": "R1", "name": "Cellulose_Degradation", "equation": "Cellulose → Glucose", "enzyme": "Cellulase"},
        {"id": "R2", "name": "Hemicellulose_Degradation", "equation": "Hemicellulose → Xylose", "enzyme": "Xylanase"},
        {"id": "R3", "name": "Glucose_Transport", "equation": "Glucose_ext → Glucose_int", "enzyme": "GlucoseTransporter"},
        {"id": "R4", "name": "Xylose_Transport", "equation": "Xylose_ext → Xylose_int", "enzyme": "XyloseTransporter"},
        {"id": "R5", "name": "Glycolysis", "equation": "Glucose → 2 Pyruvate + 2 ATP", "enzyme": "Glycolysis_Enzymes"},
        {"id": "R6", "name": "Xylose_Metabolism", "equation": "Xylose → Pyruvate + ATP", "enzyme": "XyloseDehydrogenase"},
        {"id": "R7", "name": "Pyruvate_to_Ethanol", "equation": "Pyruvate → Ethanol + CO2", "enzyme": "PDC_ADH"},
        {"id": "R8", "name": "Ethanol_Export", "equation": "Ethanol_int → Ethanol_ext", "enzyme": "EthanolTransporter"},
        {"id": "R9", "name": "Biomass_Formation", "equation": "ATP + Metabolites → Biomass", "enzyme": "NA"},
    ],
    "stoichiometry": {
        # Simplified stoichiometric matrix (reactions x metabolites)
        # Rows: reactions, Cols: metabolites
        "metabolites": ["Cellulose", "Glucose", "Xylose", "Pyruvate", "Ethanol", "ATP", "Biomass"],
        "matrix": np.array([
            [-1,  1,  0,  0,  0,  0,  0],  # R1: Cellulose → Glucose
            [ 0,  0,  1,  0,  0,  0,  0],  # R2: Hemicellulose → Xylose (hemi not tracked)
            [ 0, -1,  0,  0,  0,  0,  0],  # R3: Glucose transport
            [ 0,  0, -1,  0,  0,  0,  0],  # R4: Xylose transport
            [ 0, -1,  0,  2,  0,  2,  0],  # R5: Glycolysis
            [ 0,  0, -1,  1,  0,  1,  0],  # R6: Xylose metabolism
            [ 0,  0,  0, -1,  1,  0,  0],  # R7: Pyruvate → Ethanol
            [ 0,  0,  0,  0, -1,  0,  0],  # R8: Ethanol export
            [ 0,  0,  0,  0,  0, -3,  1],  # R9: Biomass (consumes ATP)
        ])
    }
}

def simulate_fba(
    target_product: str = "Ethanol",
    enzyme_modifications: Optional[List[Dict[str, Any]]] = None,
    optimize_for: str = "product"  # "product" or "biomass"
) -> Dict[str, Any]:
    """
    Simulate Flux Balance Analysis to predict metabolic flux distribution.
    
    Args:
        target_product: Target metabolite to optimize for
        enzyme_modifications: List of enzyme activity modifications
            [{"reaction_id": "R1", "activity_multiplier": 1.5}, ...]
        optimize_for: Optimization objective ("product" or "biomass")
    
    Returns:
        Dictionary with flux predictions and bottleneck analysis
    """
    reactions = BIOMASS_TO_ETHANOL_PATHWAY["reactions"]
    
    # Base flux values (mmol/gDW/h)
    base_fluxes = {
        "R1": 10.0,  # Cellulose degradation (rate-limiting in wild-type)
        "R2": 8.0,   # Hemicellulose degradation
        "R3": 9.5,
        "R4": 7.5,
        "R5": 9.0,
        "R6": 7.0,
        "R7": 15.0,
        "R8": 14.5,
        "R9": 2.0,
    }
    
    # Apply enzyme modifications
    modified_fluxes = base_fluxes.copy()
    if enzyme_modifications:
        for mod in enzyme_modifications:
            rxn_id = mod["reaction_id"]
            multiplier = mod["activity_multiplier"]
            if rxn_id in modified_fluxes:
                modified_fluxes[rxn_id] *= multiplier
    
    # Identify bottlenecks (reactions with flux < 80% of downstream capacity)
    flux_values = list(modified_fluxes.values())
    mean_flux = np.mean(flux_values)
    
    bottlenecks = []
    for rxn_id, flux in modified_fluxes.items():
        if flux < 0.8 * mean_flux:
            rxn_info = next((r for r in reactions if r["id"] == rxn_id), None)
            if rxn_info:
                bottlenecks.append({
                    "reaction_id": rxn_id,
                    "reaction_name": rxn_info["name"],
                    "enzyme": rxn_info["enzyme"],
                    "current_flux": round(flux, 2),
                    "limiting_factor": round((mean_flux - flux) / mean_flux * 100, 1)
                })
    
    # Calculate product yield
    # Ethanol flux depends on pyruvate flux (R7) and export capacity (R8)
    ethanol_flux = min(modified_fluxes["R7"], modified_fluxes["R8"])
    
    # Theoretical max based on glucose + xylose uptake
    carbon_input = modified_fluxes["R3"] + modified_fluxes["R4"]
    theoretical_max_ethanol = carbon_input * 0.9  # 90% theoretical yield
    
    yield_efficiency = (ethanol_flux / theoretical_max_ethanol) * 100 if theoretical_max_ethanol > 0 else 0
    
    return {
        "target_product": target_product,
        "product_flux": round(ethanol_flux, 2),
        "flux_unit": "mmol/gDW/h",
        "yield_efficiency": round(yield_efficiency, 1),
        "theoretical_max": round(theoretical_max_ethanol, 2),
        "bottlenecks": bottlenecks,
        "flux_distribution": {rxn_id: round(flux, 2) for rxn_id, flux in modified_fluxes.items()},
        "optimization_suggestions": generate_optimization_suggestions(bottlenecks)
    }

def generate_optimization_suggestions(bottlenecks: List[Dict[str, Any]]) -> List[str]:
    """Generate actionable suggestions to resolve bottlenecks"""
    suggestions = []
    
    for bn in bottlenecks:
        enzyme = bn["enzyme"]
        limiting = bn["limiting_factor"]
        
        if "Cellulase" in enzyme:
            suggestions.append(
                f"⚡ Overexpress {enzyme} or engineer thermostability (current bottleneck: {limiting}%)"
            )
        elif "Transport" in enzyme:
            suggestions.append(
                f"🔧 Increase {enzyme} copy number or improve membrane localization ({limiting}% limiting)"
            )
        else:
            suggestions.append(
                f"🧬 Optimize {enzyme} expression or replace with higher-activity homolog ({limiting}% limiting)"
            )
    
    if not suggestions:
        suggestions.append("✅ No major bottlenecks detected. System is well-balanced.")
    
    return suggestions

def predict_enzyme_impact(
    enzyme_id: str,
    current_activity: float,
    proposed_activity: float
) -> Dict[str, Any]:
    """
    Predict the impact of improving a specific enzyme on overall pathway flux.
    
    Args:
        enzyme_id: Enzyme identifier (e.g., "Cellulase")
        current_activity: Current relative activity (1.0 = wild-type)
        proposed_activity: Proposed activity after engineering
    
    Returns:
        Impact analysis with predicted yield improvement
    """
    # Map enzyme to reaction
    enzyme_to_reaction = {
        "Cellulase": "R1",
        "Xylanase": "R2",
        "PDC_ADH": "R7",  # Pyruvate decarboxylase / alcohol dehydrogenase
        "XyloseDehydrogenase": "R6"
    }
    
    reaction_id = enzyme_to_reaction.get(enzyme_id, "R1")
    
    # Baseline FBA
    baseline = simulate_fba()
    
    # Modified FBA with improved enzyme
    modified = simulate_fba(
        enzyme_modifications=[{
            "reaction_id": reaction_id,
            "activity_multiplier": proposed_activity / current_activity
        }]
    )
    
    improvement = modified["product_flux"] - baseline["product_flux"]
    improvement_pct = (improvement / baseline["product_flux"] * 100) if baseline["product_flux"] > 0 else 0
    
    return {
        "enzyme_id": enzyme_id,
        "reaction_id": reaction_id,
        "baseline_flux": baseline["product_flux"],
        "modified_flux": modified["product_flux"],
        "improvement_absolute": round(improvement, 2),
        "improvement_percent": round(improvement_pct, 1),
        "new_bottlenecks": modified["bottlenecks"],
        "recommendation": (
            f"Engineering {enzyme_id} to {proposed_activity}x activity would increase ethanol production by {improvement_pct:.1f}%"
        )
    }

def design_enzyme_cocktail(
    substrate: str = "lignocellulose",
    optimization_goal: str = "max_yield"
) -> Dict[str, Any]:
    """
    Design optimal enzyme cocktail for biomass degradation.
    
    Returns:
        Recommended enzyme composition and ratios
    """
    if substrate == "lignocellulose":
        # Optimal cocktail for paddy straw (high hemicellulose content)
        cocktail = [
            {
                "enzyme": "Cellulase (Trichoderma reesei)",
                "activity_units": 15.0,
                "ratio": 0.6,
                "role": "Cellulose hydrolysis to glucose",
                "cost_factor": 1.0
            },
            {
                "enzyme": "Xylanase (Thermophilic variant)",
                "activity_units": 8.0,
                "ratio": 0.25,
                "role": "Hemicellulose hydrolysis to xylose",
                "cost_factor": 0.8
            },
            {
                "enzyme": "β-Glucosidase",
                "activity_units": 5.0,
                "ratio": 0.15,
                "role": "Cellobiose conversion (prevents product inhibition)",
                "cost_factor": 1.2
            }
        ]
        
        total_cost = sum(e["activity_units"] * e["cost_factor"] for e in cocktail)
        
        # Simulate FBA with this cocktail
        fba_result = simulate_fba(
            enzyme_modifications=[
                {"reaction_id": "R1", "activity_multiplier": 1.2},
                {"reaction_id": "R2", "activity_multiplier": 1.1},
            ]
        )
        
        return {
            "substrate": substrate,
            "cocktail_composition": cocktail,
            "total_enzyme_loading": sum(e["activity_units"] for e in cocktail),
            "cost_index": round(total_cost, 2),
            "predicted_yield": fba_result["yield_efficiency"],
            "predicted_flux": fba_result["product_flux"]
        }
    
    return {"error": "Substrate type not supported"}
