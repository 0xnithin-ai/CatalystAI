# CatalystAI MVP Presentation Prep

Review date: Monday, 11 May 2026  
Audience: GPS Renewables / HackerEarth reviewers  
Format: 20 minutes total: 5-7 minute presentation + demo, followed by Q&A

---

## 1. Main Goal For The Review

The goal is not to explain every feature. The goal is to prove, quickly and confidently, that CatalystAI is a working MVP for GPS Renewables' molecular discovery problem.

By the end of the demo, the reviewers should remember three things:

1. CatalystAI reduces experimental trial-and-error by ranking catalyst/enzyme candidates using AI and uncertainty-aware active learning.
2. The prototype already demonstrates a closed loop: generate candidates, rank them, simulate lab feedback, and re-rank based on new evidence.
3. The platform is designed for GPS's 2G ethanol-to-SAF context, with expansion into enzyme engineering, literature grounding, and biosecurity controls.

Use this one-line positioning:

> CatalystAI is a lab-in-the-loop discovery platform that helps GPS Renewables choose the next best catalyst or enzyme experiment, not just the highest predicted molecule.

---

## 2. Suggested 20-Minute Structure

### Minute 0-1: Opening

Say:

> We built CatalystAI for the GPS Renewables molecular discovery challenge. The core problem is that the possible catalyst and enzyme design space is huge, while wet-lab testing is expensive and slow. Our MVP helps the scientist decide which experiment to run next by combining AI predictions, uncertainty, Bayesian ranking, and lab feedback.

Do not start with technology names. Start with the business/scientific problem.

### Minute 1-2: Problem And GPS Relevance

Cover:

- GPS is working in the 2G ethanol-to-SAF / bio-based chemicals space.
- Discovery bottleneck: too many possible molecules, too few lab experiments.
- Even a small improvement in activity, selectivity, stability, or enzyme yield can matter at plant scale.
- Traditional screening wastes cycles on candidates that are either obvious or uninformative.

Say:

> The key shift we are making is from "screen many candidates" to "learn maximally from every experiment."

### Minute 2-3: Solution Overview

Explain the closed loop:

1. Generate or retrieve candidate catalysts/enzymes.
2. Predict activity, selectivity, stability, and uncertainty.
3. Rank candidates using Expected Improvement or other acquisition functions.
4. Send top candidates to lab testing.
5. Ingest experimental result through an ELN-style feedback endpoint.
6. Re-rank based on the updated best result.

Say:

> A failed experiment is still useful in CatalystAI, because it teaches the model where its assumptions were wrong.

### Minute 3-6: Live Demo

Recommended demo path:

1. Open the Streamlit dashboard.
2. Start from the home or Generate & Rank view.
3. Load the demo/historical session if available.
4. Show candidate table with activity, selectivity, stability, and uncertainty.
5. Click Rank by Expected Improvement.
6. Explain why the top candidate may not simply be the highest predicted activity.
7. Show the Pareto front visualization.
8. Simulate a lab result.
9. Re-rank and show how the feedback loop changes priority.
10. If time remains, briefly show RAG Literature Retrieval, FBA, or Biosecurity TEVV.

The most important live moment:

> Before lab feedback, CatalystAI recommends the candidate with the best expected improvement. After feedback, it updates the best-so-far value and reprioritizes the next experiment.

### Minute 6-7: Close Strong

Say:

> This MVP is intentionally built as a pilot-ready loop. Today the models are simulated where needed, but the architecture is modular: GPS data, real GNN models, eLabFTW integration, and proprietary assay results can be plugged into the same workflow.

End with:

> Our ask is to take this into the finalist round and validate the loop on a GPS-specific catalyst or enzyme target.

---

## 3. Demo Checklist Before Joining The Call

Do these before the meeting:

- Calendly slot booked for the correct day.
- WhatsApp group joined or at least link saved.
- Laptop charged and charger nearby.
- Stable internet connected.
- Browser tabs cleaned up.
- Streamlit app running.
- FastAPI backend running.
- FastAPI docs page checked once.
- Demo session loaded successfully.
- Candidate ranking tested.
- Simulated lab result tested.
- Re-ranking tested.
- Pareto chart rendering.
- Backup screenshots ready in case live app fails.
- README open as fallback architecture reference.
- `project_description.html` available as visual backup.

Local run commands from the repo:

```bash
docker-compose up --build
```

Expected URLs:

```text
Streamlit Dashboard: http://localhost:8501
FastAPI Docs:       http://localhost:8000/docs
```

---

## 4. Speaker Roles

If two people are presenting:

- Person 1: Opening, problem, GPS relevance, closing.
- Person 2: Live demo and technical Q&A.

If three people are presenting:

- Person 1: Business/scientific problem and GPS relevance.
- Person 2: Demo walkthrough.
- Person 3: Architecture, safety, scalability, and Q&A.

Avoid switching speakers too often. For a 5-7 minute review, handoffs should be minimal.

---

## 5. Slide Outline If You Use Slides

Keep it to 4-5 slides maximum.

### Slide 1: CatalystAI In One Line

Title:

> CatalystAI: Lab-in-the-loop AI for catalyst and enzyme discovery

Content:

- GPS problem: faster discovery for 2G ethanol-to-SAF pathway.
- Bottleneck: huge molecular design space, limited lab throughput.
- Outcome: prioritize the next best experiment.

### Slide 2: The Closed Loop

Show:

Generate -> Predict -> Rank -> Test -> Learn -> Re-rank

Mention:

- Expected Improvement
- Uncertainty
- Wet-lab feedback
- Active learning

### Slide 3: MVP Demo

Show what the reviewers will see:

- Candidate table
- Expected Improvement ranking
- Pareto front
- Simulated ELN feedback
- Re-ranking

### Slide 4: GPS Pilot Path

Show:

- Replace mock candidates with GPS assay data.
- Connect real literature / Materials Project / OCP / enzyme databases.
- Integrate eLabFTW or internal lab data system.
- Fine-tune models on GPS-specific targets.
- Maintain audit trail and data isolation.

### Slide 5: Why We Should Be Shortlisted

Use 3 bullets:

- Working closed-loop MVP, not only a concept.
- Scientifically relevant to catalyst and enzyme discovery.
- Built with safety, explainability, and pilot integration in mind.

---

## 6. Live Demo Script

Use this script while clicking through the product.

### Step 1: Open Dashboard

Say:

> This is the CatalystAI dashboard. The researcher starts with a target reaction or discovery objective, then the system generates and ranks candidates.

### Step 2: Show Candidates

Say:

> Each candidate has predicted activity, selectivity, stability, and epistemic variance. The variance is important because the platform needs to know where it is uncertain.

### Step 3: Rank By Expected Improvement

Say:

> Instead of simply ranking by predicted activity, we rank by Expected Improvement. That balances exploitation and exploration. A candidate with slightly lower predicted activity but higher uncertainty may be more valuable to test next.

### Step 4: Show Pareto Front

Say:

> For GPS, a candidate cannot be judged on one metric alone. Activity, selectivity, and stability all matter. The Pareto view helps researchers pick candidates with the best trade-offs.

### Step 5: Simulate Lab Result

Say:

> Now we simulate the lab result coming back through an ELN-style webhook. This represents the wet-lab result after testing the selected candidate.

### Step 6: Re-rank

Say:

> After the result is logged, the system updates the session's best-known result and reprioritizes the next experiment. This is the core active learning loop.

### Step 7: Optional Safety / Enzyme Track

Say:

> For the biology side, we also included FBA-style pathway analysis and a biosecurity TEVV layer, so generated enzyme sequences can be screened before being recommended.

---

## 7. Features To Emphasize

Prioritize these:

1. Closed-loop active learning
2. Expected Improvement ranking
3. Multi-objective optimization using activity, selectivity, and stability
4. GPS-specific 2G ethanol-to-SAF relevance
5. ELN/lab feedback readiness
6. RAG/literature grounding
7. Biosecurity TEVV for enzyme/protein generation

Do not over-emphasize:

- That some models are mocked in the MVP.
- Every acquisition function.
- Every backend endpoint.
- Future UI redesign.

If asked directly about mocked parts, be honest:

> For the MVP, the generative and predictive layers are simulated with realistic candidate fixtures so we can demonstrate the end-to-end loop. The architecture is designed to replace those services with trained models and GPS assay data during the pilot.

---

## 8. Likely Questions And Strong Answers

### Q: What exactly is working today?

Answer:

> The working MVP includes a FastAPI backend, Streamlit dashboard, candidate generation from fixtures, Expected Improvement ranking, Pareto visualization, ELN-style lab feedback simulation, re-ranking, literature retrieval mock, FBA-style enzyme analysis, and biosecurity screening logic.

### Q: Are the AI models fully trained?

Answer:

> Not fully. For the hackathon MVP, we focused on proving the workflow and decision loop. The model interfaces are modular, so trained GNNs, diffusion models, or GPS proprietary assay models can replace the simulated services without changing the user workflow.

### Q: Why Expected Improvement instead of ranking by predicted activity?

Answer:

> Ranking by predicted activity alone is greedy. Expected Improvement considers both predicted performance and uncertainty, so it can recommend experiments that are likely to improve the best result or teach the model something valuable.

### Q: How does this help GPS Renewables specifically?

Answer:

> GPS needs faster discovery for catalysts and enzymes linked to biomass conversion and ethanol-to-SAF pathways. CatalystAI reduces the number of low-value experiments by prioritizing candidates with the best expected learning and performance trade-off.

### Q: How would you use GPS data?

Answer:

> GPS assay data would become the highest-value training and validation signal. We would ingest historical experiments, tag assay conditions, isolate proprietary data, tune the surrogate models, and use active learning to recommend the next batch of experiments.

### Q: How do you handle failed experiments?

Answer:

> Failed experiments are valuable because they reduce model uncertainty. CatalystAI logs them, updates the session, and uses the result to improve the next ranking cycle.

### Q: What is the production roadmap?

Answer:

> First, connect real GPS data and validate on one target pathway. Second, replace mocked predictors with trained surrogate models. Third, integrate lab systems like eLabFTW. Fourth, add enterprise controls such as authentication, audit logs, tenant isolation, and model versioning.

### Q: What is the biggest technical risk?

Answer:

> The biggest risk is data quality and domain shift. Literature data, public datasets, and GPS assay data may not match perfectly. We address this by tagging provenance, weighting GPS-specific data, keeping uncertainty estimates visible, and using human validation before retraining.

### Q: Why should this team be shortlisted?

Answer:

> Because we built more than a static concept. We built a working discovery loop that is relevant to GPS's catalyst and enzyme problem, shows how lab feedback improves decisions, and has a clear path from MVP to pilot.

---

## 9. What To Avoid Saying

Avoid:

- "Everything is fully production ready."
- "The model can discover the best catalyst automatically."
- "We do not need scientists in the loop."
- "The AI replaces the lab."
- "The generated candidates are already experimentally validated."

Better phrasing:

- "Pilot-ready architecture."
- "Decision support for scientists."
- "Prioritizes the next best experiment."
- "Reduces wasted screening cycles."
- "Demonstrates the closed-loop workflow."

---

## 10. Backup Plan If The Demo Fails

If the app fails, do not panic. Switch to this flow:

1. Open `README.md`.
2. Show the architecture and demo flow section.
3. Open `project_description.html`.
4. Show the product visuals and architecture sections.
5. Explain the demo using screenshots or code structure.
6. Offer to share the repo/run instructions after the call.

Say:

> The local service seems to be misbehaving, so I will walk through the exact implemented flow using the project artifacts. The key loop is already built in the backend and dashboard: generate, rank, log lab result, and re-rank.

---

## 11. Final 30-Second Closing

Use this if they ask for a final summary:

> CatalystAI is a closed-loop AI discovery MVP for GPS Renewables' catalyst and enzyme challenges. It combines candidate generation, uncertainty-aware prediction, Bayesian experiment ranking, Pareto trade-off analysis, and lab feedback. The prototype demonstrates the full decision loop today, and the next step is to plug in GPS-specific assay data to validate it on a real catalyst or enzyme target.

---

## 12. Last-Minute Rehearsal Checklist

Practice these aloud:

- One-line pitch in under 15 seconds.
- Problem explanation in under 45 seconds.
- Demo walkthrough in under 4 minutes.
- Honest answer about mocked models.
- Why GPS should care.
- Why Expected Improvement matters.
- Final closing in under 30 seconds.

Time target:

- Presentation + demo: 6 minutes.
- Leave 14 minutes for Q&A.

