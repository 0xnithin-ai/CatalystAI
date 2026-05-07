"""
RAG-Based Literature Retrieval Service
Simulates vector database retrieval of catalyst/enzyme performance data from scientific literature
"""
import numpy as np
from typing import List, Dict, Any, Optional
import json
import os

# Simulated embedding database (in production: Milvus/Qdrant)
# Each entry represents a literature finding with semantic embedding
LITERATURE_DATABASE = [
    {
        "id": "lit_001",
        "title": "High-Performance Zeolite Catalysts for Ethanol Oligomerization",
        "authors": "Chen et al.",
        "year": 2023,
        "journal": "Nature Catalysis",
        "finding": "ZSM-5 modified with Cu/Zn shows 87% selectivity for C4-C12 oligomers at 350°C",
        "catalyst_type": "zeolite-based",
        "activity": 82.0,
        "selectivity": 87.0,
        "stability": 75.0,
        "temperature": 350,
        "embedding": np.random.randn(128).tolist(),  # Mock embedding
        "confidence": "high",
        "citations": 47
    },
    {
        "id": "lit_002",
        "title": "Biomass-Derived Metal Oxides for SAF Precursor Synthesis",
        "authors": "Kumar et al.",
        "year": 2024,
        "journal": "Green Chemistry",
        "finding": "CeO2-ZrO2 mixed oxide shows excellent stability (>500h) for ethanol dehydration",
        "catalyst_type": "metal-oxide",
        "activity": 78.0,
        "selectivity": 72.0,
        "stability": 92.0,
        "temperature": 280,
        "embedding": np.random.randn(128).tolist(),
        "confidence": "high",
        "citations": 32
    },
    {
        "id": "lit_003",
        "title": "Nickel-Based Catalysts for Alcohol Upgrading Reactions",
        "authors": "Patel et al.",
        "year": 2024,
        "journal": "ACS Catalysis",
        "finding": "Ni/Al2O3 achieves 91% activity but suffers from coking at T>400°C",
        "catalyst_type": "supported-metal",
        "activity": 91.0,
        "selectivity": 68.0,
        "stability": 58.0,
        "temperature": 380,
        "embedding": np.random.randn(128).tolist(),
        "confidence": "medium",
        "citations": 28
    },
    {
        "id": "lit_004",
        "title": "Phosphotungstic Acid for Ethanol Conversion to Aviation Fuel Precursors",
        "authors": "Liu et al.",
        "year": 2023,
        "journal": "Applied Catalysis B",
        "finding": "H3PW12O40 on SiO2 shows 85% selectivity to C8+ at moderate temperatures",
        "catalyst_type": "polyoxometalate",
        "activity": 80.0,
        "selectivity": 85.0,
        "stability": 70.0,
        "temperature": 320,
        "embedding": np.random.randn(128).tolist(),
        "confidence": "high",
        "citations": 41
    },
    {
        "id": "lit_005",
        "title": "Cellulase Engineering for Enhanced Lignocellulosic Degradation",
        "authors": "Singh et al.",
        "year": 2024,
        "journal": "Nature Biotechnology",
        "finding": "Thermostable cellulase variant (T50=75°C) maintains 80% activity after 72h",
        "catalyst_type": "enzyme",
        "activity": 88.0,
        "selectivity": 95.0,  # substrate specificity
        "stability": 80.0,  # thermostability
        "temperature": 75,
        "embedding": np.random.randn(128).tolist(),
        "confidence": "high",
        "citations": 63
    },
    {
        "id": "lit_006",
        "title": "Novel Solid Acid Catalysts for Bioethanol Upgrading",
        "authors": "Sharma et al.",
        "year": 2025,
        "journal": "ChemSusChem",
        "finding": "Sulfonated carbon catalyst shows 76% yield to jet fuel range hydrocarbons",
        "catalyst_type": "solid-acid",
        "activity": 76.0,
        "selectivity": 81.0,
        "stability": 68.0,
        "temperature": 340,
        "embedding": np.random.randn(128).tolist(),
        "confidence": "medium",
        "citations": 19
    }
]

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Compute cosine similarity between two vectors"""
    a_arr = np.array(a)
    b_arr = np.array(b)
    return float(np.dot(a_arr, b_arr) / (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)))

def generate_query_embedding(query: str) -> List[float]:
    """
    Mock embedding generation from query text.
    In production: Use sentence-transformers or domain-specific LLM embeddings
    """
    # Seed based on query to get consistent but varied embeddings
    np.random.seed(hash(query) % (2**32))
    embedding = np.random.randn(128)
    np.random.seed(None)  # Reset seed
    return embedding.tolist()

def retrieve_similar_literature(
    query: str,
    target_type: str = "catalyst",
    top_k: int = 3,
    min_confidence: str = "medium"
) -> List[Dict[str, Any]]:
    """
    Retrieve top-k most relevant literature findings based on semantic similarity.
    
    Args:
        query: Search query (e.g., "high selectivity ethanol catalyst")
        target_type: "catalyst" or "enzyme"
        top_k: Number of results to return
        min_confidence: Minimum confidence level ("low", "medium", "high")
    
    Returns:
        List of literature findings with similarity scores
    """
    query_embedding = generate_query_embedding(query)
    
    # Filter by target type and confidence
    confidence_levels = {"low": 0, "medium": 1, "high": 2}
    min_conf_level = confidence_levels[min_confidence]
    
    filtered_db = [
        lit for lit in LITERATURE_DATABASE
        if (target_type == "enzyme" and lit["catalyst_type"] == "enzyme") or
           (target_type == "catalyst" and lit["catalyst_type"] != "enzyme")
    ]
    
    # Compute similarity scores
    results = []
    for lit in filtered_db:
        similarity = cosine_similarity(query_embedding, lit["embedding"])
        conf_level = confidence_levels[lit["confidence"]]
        
        if conf_level >= min_conf_level:
            result = lit.copy()
            result["similarity_score"] = similarity
            result.pop("embedding")  # Remove embedding from response
            results.append(result)
    
    # Sort by similarity and return top-k
    results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return results[:top_k]

def extract_baseline_performance(
    reaction: str,
    target_type: str = "catalyst"
) -> Dict[str, Any]:
    """
    Extract baseline performance metrics from literature for a given reaction.
    This provides the 'state of the art' to beat.
    
    Returns:
        Dictionary with baseline metrics and source citation
    """
    # Retrieve most relevant high-confidence literature
    results = retrieve_similar_literature(
        query=reaction,
        target_type=target_type,
        top_k=1,
        min_confidence="high"
    )
    
    if results:
        baseline = results[0]
        return {
            "baseline_activity": baseline["activity"],
            "baseline_selectivity": baseline["selectivity"],
            "baseline_stability": baseline["stability"],
            "source": f"{baseline['authors']} ({baseline['year']}) - {baseline['title']}",
            "confidence": baseline["confidence"],
            "citations": baseline["citations"]
        }
    else:
        # Fallback if no high-confidence results
        return {
            "baseline_activity": 70.0,
            "baseline_selectivity": 65.0,
            "baseline_stability": 60.0,
            "source": "Estimated from domain knowledge",
            "confidence": "low",
            "citations": 0
        }

def get_literature_context(candidate_smiles: str, target_type: str = "catalyst") -> str:
    """
    Generate natural language context about relevant literature for a candidate.
    This powers the RAG-enhanced explanations.
    """
    results = retrieve_similar_literature(
        query=f"similar to {candidate_smiles}",
        target_type=target_type,
        top_k=2
    )
    
    if not results:
        return "No similar structures found in literature database."
    
    context_parts = []
    for i, lit in enumerate(results, 1):
        context_parts.append(
            f"{i}. {lit['title']} ({lit['year']}): {lit['finding']} "
            f"[Similarity: {lit['similarity_score']:.2f}, Citations: {lit['citations']}]"
        )
    
    return "\n".join(context_parts)
