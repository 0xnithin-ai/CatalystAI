# CatalystAI — AI-Powered Molecular Discovery Platform

**AI FOR BHARAT  2026**

An AI-powered platform for de novo catalyst and enzyme discovery — replacing trial-and-error with a continuous, self-improving Lab-in-the-Loop.

---

## 🎯 Problem Statement

The global push toward sustainable aviation fuel and bio-based chemicals is fundamentally constrained by a discovery problem:
- **Design space:** >10^60 potential molecules
- **Lab throughput:** ~hundreds per month
- **Time to discovery:** Years of manual screening
- **GPS Renewables' need:** Optimize 2G Ethanol-to-SAF pathway catalysts

**CatalystAI compresses discovery from years to weeks** using generative AI + Bayesian active learning.

---

## 🚀 Core Innovation: The Lab-in-the-Loop

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Generate   │ ──▶ │   Predict    │ ──▶ │  Rank (EI)  │ ──▶ │  Synthesize  │
│  (DiffCSP)  │     │  (GNN/FBA)   │     │  (Bayesian) │     │  (Wet Lab)   │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
                                                                       │
┌─────────────┐     ┌──────────────┐     ┌─────────────┐            │
│   Update    │ ◀── │   Validate   │ ◀── │   Measure   │ ◀──────────┘
│ Model Weights│     │ (Human-in-  │     │   Results   │
│             │     │   the-Loop)  │     │             │
└─────────────┘     └──────────────┘     └─────────────┘
```

---

## 🧪 Comprehensive Feature Set

### **Direction 1: Chemical Catalysis**

#### 1. **Generative Design** (Mocked for MVP)
- DiffCSP for novel crystal lattice generation
- Conditional cDVAE for material structure design
- Novel IP generation beyond database retrieval

#### 2. **RAG-Based Literature Retrieval** ✅ NEW
- Vector database semantic search (Milvus-style)
- Extract baseline performance from scientific literature
- Knowledge-grounded candidate generation
- Literature context for explainability

#### 3. **Predictive Ranking**
- GNN surrogate models (trained on Open Catalyst Project data)
- Activity, selectivity, and stability prediction
- **Epistemic uncertainty quantification** via deep ensembles

#### 4. **Advanced Bayesian Optimization** ✅ ENHANCED
- **5 Acquisition Functions:**
  - Expected Improvement (EI) — Default, balanced
  - Probability of Improvement (PI) — Conservative
  - Upper Confidence Bound (UCB) — Optimistic exploration
  - EI per Cost — Resource-aware optimization
  - Knowledge Gradient (KG) — Finite-horizon optimal
- Multi-objective Pareto front optimization
- Side-by-side strategy comparison

### **Direction 2: Synthetic Biology**

#### 5. **Metabolic Flux Balance Analysis** ✅ NEW
- Genome-scale metabolic modeling (COBRApy-style)
- Lignocellulosic biomass → ethanol pathway simulation
- Bottleneck identification (cellulase, xylanase, etc.)
- Enzyme impact prediction
- Optimal enzyme cocktail design

#### 6. **Protein Engineering Pipeline** (Simulated)
- RFdiffusion backbone generation
- ProteinMPNN sequence design
- ESM3 zero-shot fitness prediction

### **Safety & Compliance**

#### 7. **Biosecurity TEVV Layer** ✅ NEW
- **Mandatory screening** against:
  - CDC Select Agents Registry
  - Known toxin databases (diphtheria, botulinum, ricin, anthrax)
  - Virulence factor motifs
- Automatic blocking of restricted sequences
- Compliance reporting (NIH Guidelines, DURC, NSABB)
- Audit logging for regulatory documentation

#### 8. **Active Learning Feedback Loop**
- ELN webhook integration (eLabFTW/Labtools.AI)
- Human-in-the-loop validation
- Transfer learning retraining simulation
- Model versioning with provenance tracking

---

## 💻 System Architecture

### Backend (FastAPI)
```
backend/
├── app/
│   ├── main.py                    # API endpoints
│   ├── schemas.py                 # Pydantic models
│   └── services/
│       ├── bayesian_service.py    # Expected Improvement
│       ├── acquisition_service.py  # Multi-acquisition functions 
│       ├── rag_service.py          # Literature retrieval 
│       ├── fba_service.py          # Metabolic modeling 
│       ├── biosecurity_service.py  # TEVV screening
│       └── mock_db.py             # In-memory storage
└── requirements.txt
```

### Frontend (Streamlit → Next.js)
```
streamlit_app/
└── app.py                         # 8-tab comprehensive dashboard
    ├── Generate & Rank
    ├── Pareto Front
    ├── Why EI? (Comparison)
    ├── Multi-Acquisition Comparison  
    ├── ELN Feedback Loop
    ├── RAG Literature Retrieval      
    ├── Metabolic FBA (Enzyme Track)  
    └── Biosecurity TEVV              
```

### Visualizations
- **3D Pareto Front** (Plotly) — Activity × Selectivity × Stability
- **Molstar Molecular Viewer** — WebGL crystal lattices
- **Metabolic Flux Diagrams** — Cytoscape.js network graphs (planned)
- **Acquisition Function Heatmaps** — Exploration vs exploitation trade-offs

---

## 🏗️ Technology Stack

| Domain | Technology | Justification |
|--------|-----------|--------------|
| Backend API | FastAPI | Async performance; native ML compatibility |
| Deep Learning | PyTorch + PyTorch Geometric | Industry standard for GNNs |
| Vector DB | Milvus (simulated) | Sub-millisecond semantic search |
| Metabolic Modeling | COBRApy | SBML parsing; Python native |
| Cheminformatics | RDKit | Valency validation; SMILES parsing |
| Frontend (MVP) | Streamlit | Rapid scientific prototyping |
| Frontend (Production) | Next.js | Scalable multi-tenant SaaS |
| Molecular Viz | Molstar (React) | WebGL-accelerated; PDB-grade |
| ELN Integration | eLabFTW API | Open-source; webhook support |

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+ (if running locally)

### Run with Docker (Recommended)

```bash
# Clone repository
cd CatalystAI

# Start services
docker-compose up --build

# Access endpoints
# - Streamlit Dashboard: http://localhost:8501
# - FastAPI Docs: http://localhost:8000/docs
```

### Run Locally (Development)

```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend (separate terminal)
cd streamlit_app
pip install -r requirements.txt
streamlit run app.py --server.port=8501
```

---

## 📊 API Endpoints

### Core Discovery
- `POST /api/sessions` — Create new discovery session
- `POST /api/generate` — Generate catalyst/enzyme candidates
- `POST /api/rank` — Rank by Expected Improvement
- `POST /api/rank-by-score` — Rank by predicted activity (baseline)
- `POST /api/webhook/mock-eln` — Log experimental results

### RAG Literature (NEW)
- `GET /api/literature/search` — Semantic literature search
- `GET /api/literature/baseline` — Extract baseline performance

### Metabolic FBA (NEW)
- `POST /api/fba/simulate` — Run flux balance analysis
- `POST /api/fba/enzyme-impact` — Predict enzyme engineering impact
- `GET /api/fba/design-cocktail` — Design optimal enzyme cocktail

### Biosecurity (NEW)
- `POST /api/biosecurity/screen` — Screen single sequence
- `POST /api/biosecurity/batch-screen` — Batch screen candidates
- `GET /api/biosecurity/compliance-report` — TEVV compliance report

### Advanced Optimization (NEW)
- `POST /api/rank/acquisition` — Rank with custom acquisition function
- `GET /api/rank/compare-acquisition` — Compare multiple strategies

---

## 🎯 Key Differentiators for Finals

### 1. **Breadth: Both Directions Covered**
- Direction 1 (Chemical Catalysis): Generative design, GNN prediction, Bayesian optimization
- Direction 2 (Synthetic Biology): FBA, enzyme engineering, metabolic pathway design

### 2. **Depth: Technical Sophistication**
- **5 acquisition functions** (not just EI)
- Uncertainty quantification with epistemic variance
- Multi-objective Pareto optimization
- Literature-grounded generation (RAG)

### 3. **Responsibility: Safety-First**
- Mandatory biosecurity screening (TEVV)
- Toxin/pathogen homology detection
- Regulatory compliance documentation
- Audit trail for restricted agents

### 4. **Scientific Rigor**
- Literature baseline extraction
- Physics-informed heuristic filters
- Stoichiometric constraint modeling (FBA)
- Experimental cost/time optimization

### 5. **Production-Ready Architecture**
- Modular microservice design
- ELN webhook integration
- Model versioning system
- Multi-tenant data isolation (design)

---

## 📈 Demo Flow (Load Demo Button)

1. **Start:** Pre-loaded session with 10 catalyst candidates
2. **Literature:** Extract baseline performance (70% activity from literature)
3. **Rank (EI):** Bayesian ranking highlights high-uncertainty candidates
4. **Compare:** Show how EI differs from greedy score ranking
5. **Log Result:** Simulate lab measurement (85% activity achieved)
6. **Re-rank:** Active learning updates `best_so_far`, reprioritizes candidates
7. **Improvement:** Show +15% gain over literature baseline

**Optional:** Switch to enzyme track → run FBA → screen biosecurity

---

##  Why CatalystAI is Best

- **Direct Impact:** Accelerates 2G Ethanol-to-SAF catalyst discovery
- **Economic:** Reduces screening costs by prioritizing high-EI candidates
- **Scalable:** Handles both catalyst and enzyme tracks (paddy straw pretreatment + conversion)

- **Completeness:** Covers all 4 ML layers (Retrieval, Generation, Prediction, Biology)
- **Innovation:** First to combine RAG + Bayesian BO + FBA + TEVV in one platform
- **Explainability:** Side-by-side comparisons show *why* AI picks certain candidates
- **Safety:** Only submission with biosecurity screening layer

- **MVP → Production Path:** Clear architecture for scaling
- **Scientific Validation:** Built on proven methods (DiffCSP, GNoME, COBRApy)
- **Regulatory Awareness:** TEVV compliance from day one

---


## 📚 References

- Open Catalyst Project (OCP): 260M+ DFT calculations
- Materials Project: Crystal structure database
- COBRApy: Constraint-based metabolic modeling
- RFdiffusion: Protein backbone generation
- BRENDA, KEGG, BiGG: Enzyme/pathway databases

---

## 🔧 Future Roadmap

### Phase 2 (Months 1-4)
- Live GNN surrogate on OCP data
- Real eLabFTW integration
- Multi-user collaboration + RBAC
- GPU cluster for live diffusion

### Phase 3 (Months 5-12)
- Next.js enterprise frontend
- Robotic lab hardware API
- Full audit trail + IP provenance
- CO₂ capture catalyst expansion

---



