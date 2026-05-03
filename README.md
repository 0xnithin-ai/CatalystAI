# CatalystAI

CatalystAI is an AI-powered Molecular Discovery Platform covering Chemical Catalysis and Synthetic Biology.

## MVP Architecture
```mermaid
graph TD;
    UI[Streamlit UI] --> API[FastAPI Backend];
    API --> Mock[Mock Generators & Fixtures];
    API --> AL[Active Learning / Bayesian Service];
    UI --> Plotly[3D Pareto Visualizations];
    UI --> Molstar[3D Molecular Viewer];
```

## Running the MVP

1. Make sure you have Docker installed.
2. Run `docker-compose up --build`
3. Access the Streamlit Dashboard at `http://localhost:8501`
4. Access the FastAPI backend docs at `http://localhost:8000/docs`
