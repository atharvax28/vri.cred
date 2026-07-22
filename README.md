# VRI Cred — AI-Powered SME Credit Intelligence Layer

A prototype credit-intelligence layer for small and medium enterprises: it scores credit risk and, crucially, **explains why** — pairing a gradient-boosted model with SHAP feature attributions so a lender can see what drove each decision.

🔗 **Live demo:** https://vricred1.netlify.app

---

## The idea

Traditional SME lending leans on thin, lagging signals. VRI Cred layers alternative and financial data into a single risk score, then surfaces the top contributing factors per applicant — turning a black-box score into an auditable decision.

- **Risk scoring** with a gradient-boosted model (XGBoost)
- **Explainability** via SHAP — per-applicant feature contributions
- **Decision layer** designed to sit on top of existing lending workflows

## Repository contents

- `AI-Powered SME Credit Intelligence Layer.md` — the concept and system design
- `implementation_plan.md` — build plan and milestones
- `demo/` — the deployed interactive demo

## Status

Prototype / demo. See the design docs above for the full architecture.

## License

© Atharva Tayade.
