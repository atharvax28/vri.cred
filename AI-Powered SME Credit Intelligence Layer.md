# CLAUDE.md — MSME Credit Intelligence Platform
# Model: claude-opus-4-6 (extended thinking enabled)
# Derived from: everything-claude-code rules + project architecture

---

## PROJECT IDENTITY

You are the principal engineer for **MSME Credit Intelligence Platform** — an AI-powered credit scoring and narrative reporting system for Indian SME lenders (NBFCs, banks).

This repo contains **two separate, independently deployable environments**:

```
msme-credit-intelligence/
├── demo/        ← CV project / pitch demo (zero infra cost, synthetic data)
└── production/  ← Production-grade system (AWS ap-south-1, real APIs, RBI-compliant)
```

**Never mix demo code into production. Never import across the boundary.**
Each folder is its own monorepo with its own `package.json` / `pyproject.toml` / `.env`.

---

## FULL STACK REFERENCE

Both environments share the same architectural pattern — different implementations per env.

### Frontend
| Layer | Demo | Production |
|---|---|---|
| Framework | Next.js 14 (App Router) | Next.js 14 (App Router) |
| UI System | **shadcn/ui** + Tailwind CSS | **shadcn/ui** + Tailwind CSS |
| Data Fetching | TanStack React Query v5 | TanStack React Query v5 |
| Charts | Recharts (score gauge, trend lines) | Recharts + D3.js (custom SHAP waterfall) |
| Auth | Supabase Auth (client SDK) | Auth0 (OAuth2 + RBAC) |
| Hosting | Vercel (free tier) | Vercel (pro) |

### Backend
| Layer | Demo | Production |
|---|---|---|
| Core API | FastAPI (Python 3.11) | FastAPI (Python 3.11) |
| Webhook Handler | Not needed | Node.js + Express |
| Service-to-Service | Direct function calls | gRPC |
| Hosting | Railway (free tier) | AWS ECS / ap-south-1 |

### AI / ML
| Layer | Demo | Production |
|---|---|---|
| Report Generator | **Claude API** (claude-opus-4-6) | **Claude API** (claude-opus-4-6) |
| Credit Scoring | XGBoost + SHAP (trained on synthetic data) | XGBoost / LightGBM + SHAP (bureau data) |
| NLP / News | Skipped | spaCy + HuggingFace (adverse media) |
| Model Registry | Local pickle file | MLflow |

### Data
| Layer | Demo | Production |
|---|---|---|
| Primary DB | Supabase (free tier Postgres) | AWS RDS PostgreSQL |
| Cache + Queue | Upstash Redis (free tier) | AWS ElastiCache Redis |
| Object Storage | Supabase Storage | AWS S3 + Parquet |
| Event Streaming | Skipped (direct Redis queue) | Apache Kafka |

### Integrations
| Layer | Demo | Production |
|---|---|---|
| GSTIN Verification | Mock data (5 synthetic MSMEs) | Surepass / Masters India GSP API |
| Bureau Data | Mock data | Experian India (via aggregator) |
| MCA21 | Mock data | MCA21 API |
| eCourts | Mock data | eCourts API |
| News Sentiment | Skipped | NewsData.io / GDELT |

### Security
| Layer | Demo | Production |
|---|---|---|
| AuthN/AuthZ | Supabase Auth + RLS | Auth0 + AWS Cognito + RBAC |
| Secrets | `.env.local` (never committed) | HashiCorp Vault |
| WAF | Not needed | AWS WAF + Shield |
| Encryption | TLS (Supabase default) | TLS 1.3 + mTLS + AES-256 column encryption |

### Infra / DevOps
| Layer | Demo | Production |
|---|---|---|
| Cloud | Vercel + Railway + Supabase + Upstash | AWS ap-south-1 (Mumbai) |
| IaC | Not needed | Terraform |
| CI/CD | GitHub Actions | GitHub Actions + Docker + ECR |
| Observability | Skipped | Datadog + Sentry |
| Monthly Cost | **Rs. 0** | **Rs. 1-2L/month** |

---

## REPOSITORY STRUCTURE

```
msme-credit-intelligence/
|
+-- demo/                                  <- DEMO ENVIRONMENT
|   +-- backend/                           # FastAPI on Railway
|   |   +-- pyproject.toml
|   |   +-- .env.local.example
|   |   +-- src/
|   |   |   +-- api/
|   |   |   |   +-- v1/
|   |   |   |   |   +-- reports.py
|   |   |   |   |   +-- borrowers.py
|   |   |   |   |   +-- health.py
|   |   |   |   +-- middleware/
|   |   |   |       +-- auth.py            # Supabase JWT validation
|   |   |   |       +-- rate_limit.py      # Upstash Redis rate limit
|   |   |   +-- scoring/
|   |   |   |   +-- service.py             # ScoringService (orchestrator)
|   |   |   |   +-- features.py            # Feature extraction (40+ features)
|   |   |   |   +-- model.py               # XGBoost + SHAP wrapper
|   |   |   |   +-- jobs.py                # Redis job queue
|   |   |   |   +-- repositories.py        # MockGSTINRepository (5 MSMEs)
|   |   |   +-- reports/
|   |   |   |   +-- generator.py           # Claude API + CreditMemo schema
|   |   |   |   +-- pdf.py                 # WeasyPrint renderer
|   |   |   |   +-- templates/
|   |   |   |       +-- credit_memo.html
|   |   |   +-- auth/
|   |   |   |   +-- jwt.py
|   |   |   |   +-- rbac.py                # analyst / approver / admin
|   |   |   +-- core/
|   |   |       +-- exceptions.py
|   |   |       +-- logging.py
|   |   |       +-- config.py
|   |   |       +-- utils.py               # sanitize_for_llm_context
|   |   +-- ml/
|   |   |   +-- train_synthetic.py         # Train XGBoost on synthetic data
|   |   |   +-- synthetic_dataset.json     # 50 synthetic MSME records
|   |   |   +-- model.pkl                  # Trained model (gitignored)
|   |   +-- tests/
|   |       +-- unit/
|   |       +-- integration/
|   |       +-- conftest.py
|   |       +-- fixtures/
|   |           +-- mock_gstin_healthy.json
|   |           +-- mock_gstin_borderline.json
|   |           +-- mock_gstin_stressed.json
|   |
|   +-- frontend/                          # Next.js 14 on Vercel
|       +-- package.json
|       +-- .env.local.example
|       +-- tailwind.config.ts
|       +-- components.json                # shadcn/ui config
|       +-- app/
|       |   +-- layout.tsx
|       |   +-- page.tsx                   # Landing (SSR)
|       |   +-- dashboard/
|       |       +-- layout.tsx
|       |       +-- page.tsx               # Reports list
|       |       +-- reports/
|       |       |   +-- [jobId]/page.tsx   # Report detail + PDF viewer
|       |       |   +-- new/page.tsx       # Submit GSTIN form
|       |       +-- borrowers/page.tsx
|       +-- components/
|       |   +-- ui/                        # shadcn/ui primitives (auto-generated)
|       |   |   +-- button.tsx
|       |   |   +-- card.tsx
|       |   |   +-- badge.tsx
|       |   |   +-- dialog.tsx
|       |   |   +-- table.tsx
|       |   |   +-- tabs.tsx
|       |   |   +-- skeleton.tsx
|       |   |   +-- alert.tsx
|       |   |   +-- form.tsx
|       |   |   +-- input.tsx
|       |   |   +-- label.tsx
|       |   |   +-- select.tsx
|       |   +-- charts/                    # Recharts + D3 wrappers
|       |   |   +-- ScoreGauge.tsx         # Radial gauge 0-1000
|       |   |   +-- ShapWaterfall.tsx      # D3 SHAP explanation chart
|       |   |   +-- RevenueTrend.tsx       # GST revenue line chart
|       |   |   +-- RiskRadar.tsx          # Multi-axis risk radar
|       |   +-- reports/
|       |   |   +-- ReportCard.tsx         # Summary card (shadcn Card)
|       |   |   +-- RiskFlagList.tsx       # Badge list of risk flags
|       |   |   +-- RecommendationBadge.tsx
|       |   |   +-- PdfViewer.tsx          # Embedded PDF iframe
|       |   +-- layout/
|       |       +-- Sidebar.tsx
|       |       +-- Header.tsx
|       |       +-- RoleBadge.tsx
|       +-- lib/
|       |   +-- api.ts                     # Typed fetch wrapper
|       |   +-- queries.ts                 # React Query definitions
|       |   +-- utils.ts                   # shadcn cn() + helpers
|       +-- types/
|           +-- report.ts
|           +-- borrower.ts
|
+-- production/                            <- PRODUCTION ENVIRONMENT
    +-- backend/                           # FastAPI on AWS ECS ap-south-1
    |   +-- pyproject.toml
    |   +-- Dockerfile
    |   +-- src/
    |   |   +-- api/                       # Same structure as demo
    |   |   +-- scoring/
    |   |   |   +-- repositories.py        # SurpassGSTINRepository (real API)
    |   |   +-- reports/
    |   |   +-- ingestion/
    |   |   |   +-- gstin.py               # GSP API client (Masters India)
    |   |   |   +-- mca.py                 # MCA21 client
    |   |   |   +-- bureau.py              # Experian aggregator
    |   |   |   +-- news.py                # NewsData.io
    |   |   +-- auth/
    |   |   |   +-- auth0.py               # Auth0 JWT validation
    |   |   |   +-- rbac.py
    |   |   +-- core/
    |   +-- ml/
    |   |   +-- feature_store/             # Feast feature store
    |   |   +-- training/
    |   |   +-- mlflow_registry/
    |   +-- infra/
    |   |   +-- terraform/
    |   |   |   +-- main.tf
    |   |   |   +-- vpc.tf
    |   |   |   +-- rds.tf
    |   |   |   +-- elasticache.tf
    |   |   |   +-- ecs.tf
    |   |   +-- docker-compose.yml
    |   +-- tests/
    |
    +-- frontend/                          # Next.js 14 on Vercel Pro
    |   +-- package.json
    |   +-- components.json
    |   +-- app/                           # Same structure as demo
    |   +-- components/
    |   |   +-- ui/                        # shadcn/ui (same)
    |   |   +-- charts/                    # + advanced D3 charts
    |   |   +-- compliance/
    |   |       +-- ConsentModal.tsx       # DPDP Act consent flow
    |   |       +-- AuditTrail.tsx
    |   +-- lib/
    |
    +-- webhook-handler/                   # Node.js + Express on AWS Lambda
        +-- package.json
        +-- src/
            +-- gst-webhook.ts
            +-- mca-webhook.ts
```

---

## SHADCN/UI RULES (FRONTEND — BOTH ENVIRONMENTS)

### Setup Commands
```bash
# Initialize shadcn/ui (run once per frontend folder)
npx shadcn@latest init

# Install components — always use CLI, never copy-paste
npx shadcn@latest add button card badge dialog table tabs
npx shadcn@latest add alert select input label form skeleton
```

### Component Patterns
```tsx
// CORRECT — use shadcn primitives, extend with Tailwind cn()
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

interface ReportCardProps {
  score: number
  recommendation: "APPROVE" | "REVIEW" | "DECLINE"
  gstin: string
  businessName: string
}

export function ReportCard({ score, recommendation, gstin, businessName }: ReportCardProps) {
  const colorMap = {
    APPROVE: "bg-green-500/10 text-green-600 border-green-200",
    REVIEW:  "bg-yellow-500/10 text-yellow-600 border-yellow-200",
    DECLINE: "bg-red-500/10 text-red-600 border-red-200",
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="flex flex-row items-center justify-between">
        <div>
          <CardTitle className="text-base font-semibold">{businessName}</CardTitle>
          <p className="text-xs text-muted-foreground font-mono mt-0.5">{gstin}</p>
        </div>
        <Badge variant="outline" className={cn("text-xs font-bold tracking-wide", colorMap[recommendation])}>
          {recommendation}
        </Badge>
      </CardHeader>
      <CardContent>
        <div className="flex items-baseline gap-1">
          <span className="text-3xl font-bold">{score}</span>
          <span className="text-sm text-muted-foreground">/ 1000</span>
        </div>
      </CardContent>
    </Card>
  )
}
```

### GSTIN Form (shadcn Form + Zod + React Hook Form)
```tsx
"use client"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { z } from "zod"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const schema = z.object({
  gstin: z.string().regex(
    /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/,
    "Enter a valid 15-character GSTIN (e.g. 27AABCM1234D1Z5)"
  ),
})

export function ScoreRequestForm({ onSubmit }: { onSubmit: (gstin: string) => void }) {
  const form = useForm({ resolver: zodResolver(schema) })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit((v) => onSubmit(v.gstin))} className="space-y-4">
        <FormField control={form.control} name="gstin" render={({ field }) => (
          <FormItem>
            <FormLabel>GSTIN</FormLabel>
            <FormControl>
              <Input
                {...field}
                placeholder="27AABCM1234D1Z5"
                className="font-mono uppercase"
                maxLength={15}
                onChange={(e) => field.onChange(e.target.value.toUpperCase())}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit" className="w-full" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? "Scoring..." : "Generate Credit Report"}
        </Button>
      </form>
    </Form>
  )
}
```

### Job Status Polling (React Query)
```tsx
"use client"
import { useQuery } from "@tanstack/react-query"
import { Skeleton } from "@/components/ui/skeleton"
import { Alert, AlertDescription } from "@/components/ui/alert"

export function JobStatusPoller({ jobId }: { jobId: string }) {
  const { data, isLoading, error } = useQuery({
    queryKey: ["job-status", jobId],
    queryFn: async () => {
      const res = await fetch(`/api/v1/reports/${jobId}/status`)
      if (!res.ok) throw new Error("Failed to fetch status")
      return res.json()
    },
    refetchInterval: (query) =>
      query.state.data?.status === "complete" ? false : 3000,
  })

  if (isLoading) return <Skeleton className="h-20 w-full" />
  if (error) return (
    <Alert variant="destructive">
      <AlertDescription>Failed to fetch report status.</AlertDescription>
    </Alert>
  )

  return (
    <p className="text-sm text-muted-foreground">
      Status: <span className="font-medium capitalize">{data?.status}</span>
    </p>
  )
}
```

### Score Gauge (Recharts + shadcn Card)
```tsx
import { RadialBarChart, RadialBar, ResponsiveContainer } from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

function getColor(score: number) {
  if (score >= 700) return "#22c55e"   // green-500
  if (score >= 500) return "#f59e0b"   // amber-500
  return "#ef4444"                      // red-500
}

export function ScoreGauge({ score }: { score: number }) {
  const color = getColor(score)
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm text-muted-foreground">Credit Score</CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center">
        <div className="relative w-40 h-40">
          <ResponsiveContainer width="100%" height="100%">
            <RadialBarChart
              cx="50%" cy="50%"
              innerRadius="70%" outerRadius="90%"
              startAngle={225} endAngle={-45}
              data={[{ value: (score / 1000) * 100, fill: color }]}
            >
              <RadialBar dataKey="value" cornerRadius={6} background={{ fill: "#f1f5f9" }} />
            </RadialBarChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold" style={{ color }}>{score}</span>
            <span className="text-xs text-muted-foreground">/ 1000</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
```

---

## THINKING PROTOCOL

Before writing any code, tool call, or plan, use extended thinking to:

1. **Restate the task** — one sentence, confirms understanding
2. **Identify the environment** — `demo/` or `production/`? Never cross-contaminate
3. **Identify the layer** — Client / API / AI / Data / Integrations / Security / Infra
4. **Check for existing patterns** — does the codebase already solve this?
5. **Flag risks** — security, compliance, performance, India-specific regulatory
6. **Propose the minimal correct implementation** — not the most clever one

Do NOT start writing code until this internal review is complete.

---

## CODING STANDARDS (MANDATORY — NEVER DEVIATE)

### Immutability
```python
# WRONG
def update_score(borrower, new_score):
    borrower['score'] = new_score
    return borrower

# CORRECT
def update_score(borrower: dict, new_score: float) -> dict:
    return {**borrower, 'score': new_score}
```

### File Size
- 200-400 lines typical, **800 lines maximum — hard limit**
- Organize by domain, never by type

### Function Size
- **50 lines maximum per function**
- One function = one responsibility

### Error Handling
```python
# WRONG — silent failure
def fetch_gstin(gstin: str):
    try:
        return api.get(gstin)
    except:
        return None

# CORRECT — explicit, typed, logged
def fetch_gstin(gstin: str) -> GSTINData:
    try:
        return api.get(gstin)
    except httpx.TimeoutException as e:
        logger.error("GSTIN fetch timeout", extra={"gstin": gstin, "error": str(e)})
        raise GSTINFetchError(f"Timeout fetching GSTIN {gstin}") from e
    except httpx.HTTPStatusError as e:
        logger.error("GSTIN HTTP error", extra={"status": e.response.status_code})
        raise GSTINFetchError(f"HTTP {e.response.status_code} for GSTIN {gstin}") from e
```

### Input Validation — Always at System Boundaries
```python
from pydantic import BaseModel, field_validator
import re

class ScoringRequest(BaseModel):
    gstin: str
    lender_org_id: str
    requested_by: str

    @field_validator('gstin')
    @classmethod
    def validate_gstin(cls, v: str) -> str:
        if not re.match(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$', v):
            raise ValueError(f"Invalid GSTIN format: {v}")
        return v
```

### No Hardcoded Values
```python
import os
from functools import lru_cache

@lru_cache()
def get_settings() -> dict:
    return {
        "anthropic_api_key": os.environ["ANTHROPIC_API_KEY"],
        "database_url": os.environ["DATABASE_URL"],
        "redis_url": os.environ["UPSTASH_REDIS_URL"],
    }
```

---

## SECURITY (NON-NEGOTIABLE — CHECK BEFORE EVERY COMMIT)

- [ ] No hardcoded secrets anywhere
- [ ] All inputs validated with Pydantic schemas
- [ ] All SQL via parameterized queries — zero string concatenation
- [ ] JWT in httpOnly cookies only — never localStorage
- [ ] RBAC checked before every sensitive operation
- [ ] Error messages never expose stack traces or internal paths
- [ ] No PAN / Aadhaar / raw GSTIN responses in logs
- [ ] Rate limiting on every public endpoint

### Prompt Injection Defense
```python
import html, re

def sanitize_for_llm_context(raw_text: str, max_length: int = 2000) -> str:
    """Strip injection attempts. Call on ALL external data before LLM context."""
    for pattern in [
        r'ignore previous instructions', r'disregard.*instructions',
        r'you are now', r'system:', r'<\|.*\|>', r'\[INST\]',
    ]:
        raw_text = re.sub(pattern, '[REDACTED]', raw_text, flags=re.IGNORECASE)
    return html.escape(raw_text)[:max_length]
```

### Row-Level Security (Supabase — both envs)
```sql
ALTER TABLE credit_reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY "lender_isolation" ON credit_reports
    FOR ALL USING (lender_org_id = current_setting('app.current_lender_org_id'));
```

---

## API DESIGN STANDARDS

```
POST   /api/v1/reports                  # Trigger job -> 202 Accepted
GET    /api/v1/reports/{job_id}/status  # Poll async job
GET    /api/v1/reports/{job_id}         # Get full result
GET    /api/v1/reports                  # List reports for lender org
POST   /api/v1/borrowers/{gstin}/refresh
GET    /api/v1/health
```

Response envelope:
```python
class APIResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[str] = None
    meta: Optional[dict] = None
```

Status codes: 200 OK, 201 Created, 202 Accepted, 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 422 Unprocessable, 429 Too Many Requests, 503 Unavailable.

---

## PYTHON PATTERNS (BACKEND)

### Service Layer
```python
@dataclass
class ScoringService:
    gstin_repo: GSTINRepository      # Protocol — swap mock/real freely
    model: ScoringModelProtocol
    report_generator: ReportGenerator

    async def score_borrower(self, gstin: str, lender_org_id: str) -> ScoringResult:
        gstin_data = await self.gstin_repo.fetch(gstin)
        features = self._extract_features(gstin_data)
        score, shap_values = self.model.predict(features)
        narrative = await self.report_generator.generate(
            gstin=gstin, score=score,
            shap_values=shap_values, raw_data=gstin_data,
        )
        return ScoringResult(gstin=gstin, score=score,
            shap_values=shap_values, narrative=narrative,
            lender_org_id=lender_org_id)
```

### Repository — Demo vs Production
```python
# demo/backend/src/scoring/repositories.py
class MockGSTINRepository:
    """Zero-cost synthetic data. Swap with SurpassGSTINRepository in prod."""
    DEMO_GSTINS = {
        "27AABCM1234D1Z5": {...},  # healthy MSME
        "27XYZBN5678E2Z3": {...},  # stressed MSME
        "27PQRST9012F3Z7": {...},  # borderline MSME
    }
    async def fetch(self, gstin: str) -> GSTINData:
        if gstin not in self.DEMO_GSTINS:
            raise GSTINNotFoundError(gstin)
        return GSTINData(**self.DEMO_GSTINS[gstin])

# production/backend/src/scoring/repositories.py
class SurpassGSTINRepository:
    # COMPLIANCE: DPDP Act 2023 — consent_id must be verified before calling
    async def fetch(self, gstin: str) -> GSTINData: ...
```

### Async Job Queue (Upstash Redis)
```python
class ScoringJobQueue:
    async def enqueue(self, gstin: str, lender_org_id: str, requested_by: str) -> str:
        job_id = str(uuid.uuid4())
        payload = {"job_id": job_id, "gstin": gstin,
            "lender_org_id": lender_org_id, "status": JobStatus.PENDING}
        await self.redis.lpush("scoring:queue", json.dumps(payload))
        await self.redis.setex(f"scoring:status:{job_id}", 3600, json.dumps(payload))
        return job_id

    async def get_status(self, job_id: str) -> dict | None:
        raw = await self.redis.get(f"scoring:status:{job_id}")
        return json.loads(raw) if raw else None
```

---

## CLAUDE API INTEGRATION (REPORT GENERATION)

```python
class CreditMemo(BaseModel):
    executive_summary: str
    score_explanation: str           # Must cite SHAP values by name
    key_risk_flags: list[str]        # Max 5
    positive_indicators: list[str]   # Max 3
    recommendation: str              # "APPROVE" | "REVIEW" | "DECLINE"
    confidence: str                  # "HIGH" | "MEDIUM" | "LOW"
    disclaimer: str                  # RBI compliance — always present

class ReportGenerator:
    MODEL = "claude-opus-4-6"

    async def generate(self, gstin, score, shap_values, raw_data) -> CreditMemo:
        context = self._build_context(score, shap_values, raw_data)
        response = self.client.messages.create(
            model=self.MODEL, max_tokens=1500,
            system=self._system_prompt(),
            messages=[{"role": "user", "content": context}],
        )
        # ALWAYS validate output schema — never trust raw LLM text
        return CreditMemo.model_validate_json(response.content[0].text)

    def _system_prompt(self) -> str:
        return """You are a senior credit analyst generating lender-grade credit memos for MSME borrowers in India.
RULES:
- Respond ONLY with valid JSON matching CreditMemo schema — no preamble, no markdown
- Never APPROVE scores below 550
- Always cite specific data points — no vague language
- Include RBI disclaimer in disclaimer field

OUTPUT SCHEMA:
{
  "executive_summary": "string",
  "score_explanation": "string (cite top SHAP factors by name)",
  "key_risk_flags": ["string"],
  "positive_indicators": ["string"],
  "recommendation": "APPROVE|REVIEW|DECLINE",
  "confidence": "HIGH|MEDIUM|LOW",
  "disclaimer": "string"
}"""

    def _build_context(self, score, shap_values, data) -> str:
        business = sanitize_for_llm_context(data.legal_name, 100)
        factors = sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)[:5]
        factors_text = "\n".join(f"- {k}: {v:+.3f}" for k, v in factors)
        return f"""BORROWER: {business} | GSTIN: {data.gstin}
SCORE: {score:.0f} / 1000
TOP SHAP DRIVERS:\n{factors_text}
FILING: {data.returns_filed_12m}/12 returns | Nil: {data.nil_returns_12m} | Trend: {data.revenue_trend_pct:+.1f}%
LITIGATION: {sanitize_for_llm_context(str(data.litigation_flags), 200)}
Generate credit memo JSON."""
```

---

## TESTING (80% COVERAGE MINIMUM — NON-NEGOTIABLE)

TDD workflow:
```
1. Write test (RED)   2. pytest -x (fail)   3. Implement (GREEN)
4. pytest -x (pass)   5. Refactor           6. pytest --cov >= 80%
```

Test layout (same for both environments):
```
tests/
+-- unit/
|   +-- test_scoring_features.py
|   +-- test_prompt_sanitizer.py
|   +-- test_credit_memo_schema.py
|   +-- test_job_queue.py
+-- integration/
|   +-- test_api_reports.py
|   +-- test_gstin_repository.py
|   +-- test_scoring_pipeline.py
+-- conftest.py
+-- fixtures/
    +-- mock_gstin_healthy.json
    +-- mock_gstin_borderline.json
    +-- mock_gstin_stressed.json
```

---

## VERIFICATION LOOP (AFTER EVERY FEATURE)

```bash
# Backend
ruff check src/ tests/
mypy src/ --strict
bandit -r src/ -ll
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
grep -rn "sk-\|api_key\s*=\s*['\"]" src/ tests/ --include="*.py"

# Frontend
npx tsc --noEmit
npx eslint app/ components/ lib/
```

Report:
```
VERIFICATION REPORT
===================
Lint:      [PASS/FAIL]
Types:     [PASS/FAIL]
Security:  [PASS/FAIL]
Tests:     [PASS/FAIL] (N/M, X% coverage)
Secrets:   [PASS/FAIL]
Status: READY / NOT READY
```

---

## GIT WORKFLOW

Prefix every branch with environment:
```
demo/feature-score-gauge
demo/fix-nil-return-handling
prod/feature-gstn-real-api
prod/security-vault-integration
```

Commit format:
```
feat(demo): add SHAP waterfall chart component
fix(demo): handle nil GST returns in feature extraction
feat(prod): integrate Surepass GSTIN API
security(prod): migrate secrets to HashiCorp Vault
```

---

## AGENTS — WHEN TO USE WHICH

| Situation | Agent |
|---|---|
| New feature | `planner` first, always |
| Writing code | `tdd-guide` — tests first |
| After writing | `code-reviewer` |
| Auth / PII / payments | `security-reviewer` |
| Architecture decision | `architect` |
| Build errors | `build-error-resolver` |
| Schema change | `database-reviewer` |

---

## DEMO BUILD CHECKLIST (`demo/` ONLY)

**Week 1 — Skeleton**
- [ ] `demo/backend/` FastAPI scaffolded, all layers typed
- [ ] `demo/frontend/` Next.js 14 + shadcn/ui init + Tailwind
- [ ] Supabase project — tables + RLS policies
- [ ] Upstash Redis — free tier connected
- [ ] `.env.local.example` for both

**Week 2-3 — Scoring Engine**
- [ ] MockGSTINRepository — 3 synthetic MSMEs
- [ ] 40 features extracted from synthetic data
- [ ] XGBoost trained on 50 records → `ml/model.pkl`
- [ ] SHAP extraction
- [ ] Async job queue end-to-end

**Week 4 — Claude Reports**
- [ ] Prompt + CreditMemo Pydantic schema
- [ ] Input sanitization
- [ ] WeasyPrint PDF
- [ ] Integration test: GSTIN -> score -> memo -> PDF in < 90 seconds

**Week 5 — Frontend**
- [ ] ScoreGauge (Recharts)
- [ ] ShapWaterfall (D3)
- [ ] RevenueTrend (Recharts)
- [ ] ReportCard + RiskFlagList (shadcn)
- [ ] Job polling (React Query)
- [ ] PDF viewer

**Week 6 — Pitch Polish**
- [ ] 3 demo GSTINs one-click launchable
- [ ] Loom script (3 min)
- [ ] README with architecture diagram + Production Roadmap
- [ ] 5-slide deck

---

## PRODUCTION ADDITIONS (`production/` ONLY)

Do NOT build in `demo/`. Add after first NBFC pilot signed:

- Surepass / Masters India GSP (real GSTIN)
- Experian aggregator (bureau data)
- Auth0 RBAC (analyst / approver / admin)
- HashiCorp Vault (secrets)
- Terraform (IaC, AWS ap-south-1)
- Apache Kafka (event streaming)
- Feast feature store
- MLflow model registry
- ConsentModal.tsx (DPDP Act)
- AES-256 column encryption on PAN / Aadhaar
- Datadog + Sentry

---

## COMPLIANCE COMMENT TEMPLATES

All code touching borrower data:
```python
# COMPLIANCE: DPDP Act 2023 — Explicit borrower consent required.
# consent_id must be verified in borrower_consents table before calling.
```

All credit decision code:
```python
# COMPLIANCE: RBI Guidelines — Decisions must be explainable.
# SHAP values mandatory. CreditMemo.disclaimer must be present.
```

---

## THE ONE QUESTION

> **"Would an NBFC credit analyst trust output from this code?"**

If no — fix it before moving on.
