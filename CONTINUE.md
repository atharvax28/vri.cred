# CONTINUE.md — Context Handoff (Claude Code / Gemini 3.1 Pro)

This file exists because **model credits ran out**. When credits are reinstated, use this as the working context to continue without re-discovery.

## What happened / current state (so far)

- **Workspace**: `c:\Users\athar\Downloads\vri.cred`
- **Git**: Not a git repo currently.
- **Goal**: Build an **AI-powered MSME credit scoring + narrative credit memo** system (India SME lenders). Current focus is a **demo backend**.

### Docs present in repo

- `implementation_plan.md`
  - Phase 1 is “Backend Foundation (Current)” + later phases for a minimal testing UI.
- `AI-Powered SME Credit Intelligence Layer.md`
  - A large “CLAUDE.md-style” architecture / standards doc describing demo vs production patterns, endpoints, security standards, etc.

### Code present (demo backend)

There is a Python FastAPI backend in:

- `demo/backend/`
  - `pyproject.toml` defines dependencies: FastAPI, Uvicorn, Pydantic v2, httpx, numpy, xgboost, shap, scikit-learn, plus dev deps (pytest/ruff/mypy).
  - `src/main.py` creates the FastAPI app and wires dependencies in `lifespan()`.
  - `src/api/routes.py` implements endpoints and a dependency wiring pattern (`init_dependencies()` + `get_repo/get_model/get_report_gen`).
  - `src/api/__init__.py` currently empty (ok).

#### Implemented backend endpoints (from `demo/backend/src/api/routes.py`)

- `GET /health`
  - Returns model readiness, timestamp, version.
- `GET /api/v1/gstins`
  - Lists available demo GSTINs from the mock repository.
- `GET /api/v1/gstins/{gstin}`
  - Returns details for one GSTIN, 404 if not in demo dataset.
- `POST /api/v1/score`
  - Runs scoring pipeline, returns VRI score + PD + risk grade + SHAP factors.
- `POST /api/v1/report`
  - Runs scoring pipeline, then generates a **credit memo** via `ReportGenerator`.
  - If Anthropic key isn’t set, generator may fall back (per docstring in code).

#### Dependency wiring / startup sequence (from `demo/backend/src/main.py`)

- On startup:
  - Initialize `CreditScoringModel()`
  - `load_model()` else `train_demo_model()`
  - Create `MockGSTINRepository()` and `ReportGenerator()`
  - Call `init_dependencies(repo, model, report_gen)`

## How to continue after credits reset (instructions for the next model)

### Immediate next step

1. **Read** the three primary context files:
   - `CONTINUE.md` (this file)
   - `implementation_plan.md`
   - `AI-Powered SME Credit Intelligence Layer.md`
2. **Confirm the backend runs** locally and endpoints respond.

### Run commands (Windows / PowerShell)

From `demo/backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
uvicorn src.main:app --reload
```

Then open:
- `http://127.0.0.1:8000/docs`

### Quick API smoke tests

```powershell
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/api/v1/gstins
```

Then pick a GSTIN from the list:

```powershell
curl http://127.0.0.1:8000/api/v1/gstins/27AABCM1234D1Z5
curl -Method POST http://127.0.0.1:8000/api/v1/score -ContentType "application/json" -Body '{"gstin":"27AABCM1234D1Z5"}'
curl -Method POST http://127.0.0.1:8000/api/v1/report -ContentType "application/json" -Body '{"gstin":"27AABCM1234D1Z5"}'
```

## Known constraints / important notes

- **Credits issue**: Both Claude Code and Gemini 3.1 Pro hit credit limits; this file is the persistence mechanism.
- **Architecture doc vs actual tree**: `AI-Powered SME Credit Intelligence Layer.md` describes a larger “demo vs production” monorepo vision; the current workspace contains **only the demo backend** portion (no `demo/frontend/` folder found in the current file listing).
- **No secrets committed**: `.env.example` and `.env.local.example` exist under `demo/backend/`.

## Next tasks (high priority)

- Verify the demo backend starts cleanly and the OpenAPI docs load.
- Confirm `POST /api/v1/report` behavior:
  - With no Anthropic key, does it gracefully fall back?
  - With key, does it generate memo reliably?
- If the next step is UI work per `implementation_plan.md`, add a minimal frontend (Phase 2) only after backend smoke tests succeed.

## If the model is interrupted again

Before stopping for any reason (credit limit, interruption, context overflow), **update this `CONTINUE.md`** with:
- What changed (files edited/added)
- Current errors (if any) + exact stack traces
- Next command to run
- Next TODOs

