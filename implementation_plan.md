# MSME Credit Intelligence Platform — Implementation Plan

## Phase 1: Backend Foundation (Current)
Build the **demo/** backend (FastAPI) with synthetic data, scoring engine, and Claude report generation.

### 1.1 Project Scaffolding
- FastAPI app structure with proper layering
- Pydantic models for all data contracts
- Configuration management via `.env`

### 1.2 Synthetic Data & Mock Repositories
- 5 synthetic MSME records (healthy, stressed, borderline, etc.)
- `MockGSTINRepository` returning typed `GSTINData`

### 1.3 Scoring Engine
- Feature extraction (40+ features from GST data)
- XGBoost model trained on synthetic dataset
- SHAP value extraction for explainability

### 1.4 Report Generation
- Claude API integration with `CreditMemo` Pydantic schema
- Input sanitization for prompt injection defense
- PDF generation with WeasyPrint

### 1.5 Async Job Queue
- Redis-based job queue (in-memory fallback for dev)
- Job status polling endpoints

### 1.6 API Endpoints
- `POST /api/v1/reports` — Trigger scoring job
- `GET /api/v1/reports/{job_id}/status` — Poll status
- `GET /api/v1/reports/{job_id}` — Get full result
- `GET /api/v1/reports` — List reports
- `GET /api/v1/health` — Health check

## Phase 2: Minimalistic Testing UI
A clean, beautiful but minimal frontend to test all backend endpoints.

### Design Inspiration
- **deng.theedgar.dev** — Clean mono layout, design engineer aesthetic
- **Pasito** — Fluid micro-interactions, step-based flows
- **Vaul** — Drawer components, smooth animations
- **Family Wallet** — Multi-state components, predictable transitions

### UI Screens
1. **GSTIN Input** — Clean form with validation
2. **Job Status** — Polling with animated progress
3. **Report View** — Score gauge, SHAP factors, narrative
4. **Reports List** — Card grid of all generated reports

## Phase 3: Production Frontend (Later)
Full Next.js + shadcn/ui dashboard with charts, RBAC, etc.
