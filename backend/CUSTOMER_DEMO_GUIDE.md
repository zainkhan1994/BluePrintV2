# Customer Demo Guide (Environment to End)

## What Customer Asked

Customer said these were missing:

1. Semantic search  
2. Retrieval  
3. Automated tagging  
4. Automated classification

Your objective in the meeting is to prove these four are fully implemented and working.

---

## 1) Environment Setup (Windows, Step-by-Step)

### 1.1 Open terminal and go to backend folder

```powershell
cd "F:\Basic Info\Github\AquaCommander\Blueprint\backend"
```

### 1.2 Ensure Python 3.12 is available

```powershell
py -3.12 --version
```

If not installed:

```powershell
winget install -e --id Python.Python.3.12
```

### 1.3 Create virtual environment

```powershell
py -3.12 -m venv .venv
```

### 1.4 Activate virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks scripts:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 1.5 Install dependencies

```powershell
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

### 1.6 Create `.env`

```powershell
Copy-Item .env.example .env
```

### 1.7 Optional: reset DB/index if schema mismatch appears

```powershell
if (Test-Path .\blueprint_memory.db) { Remove-Item .\blueprint_memory.db -Force }
if (Test-Path .\data\chroma) { Remove-Item .\data\chroma -Recurse -Force }
```

### 1.8 Start backend

```powershell
uvicorn app.main:app --reload --port 8100
```

### 1.9 Open API docs

- `http://localhost:8100/docs`
- `http://localhost:8100/ready`

---

## 2) Live Proof Flow for Meeting (Core Missing Requirements)

### Step A: Ingest sample data

```bash
curl -X POST "http://localhost:8100/items" ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"notes\",\"source_ref\":\"demo-tax-001\",\"title\":\"IRS payment confirmation\",\"description\":\"Tax receipt\",\"content\":\"IRS filing receipt for 2025 and W2 submission completed.\",\"taxonomy_path\":\"Personal/Important_Documents\",\"idempotency_key\":\"demo-tax-001\"}"
```

```bash
curl -X POST "http://localhost:8100/items" ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"notes\",\"source_ref\":\"demo-health-001\",\"title\":\"Lab report upload\",\"description\":\"Blood panel\",\"content\":\"Lipid panel and diagnostic report uploaded from clinic.\",\"taxonomy_path\":\"Health/Lab_Work\",\"idempotency_key\":\"demo-health-001\"}"
```

```bash
curl -X POST "http://localhost:8100/items" ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"notes\",\"source_ref\":\"demo-bill-001\",\"title\":\"Electricity bill paid\",\"description\":\"Utility payment\",\"content\":\"Electricity payment processed for February and invoice archived.\",\"taxonomy_path\":\"Personal/Bills\",\"idempotency_key\":\"demo-bill-001\"}"
```

What to say:
"I am ingesting realistic records so we can validate semantic and automation behavior."

### Step B: Process pipeline

```bash
curl -X POST "http://localhost:8100/jobs/process?limit=500"
```

Expected:
- `succeeded > 0`

What to say:
"This executes background pipeline stages including embedding, tagging, and classification."

### Step C: Prove semantic search

```bash
curl -X POST "http://localhost:8100/search/semantic" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"tax filing receipt\",\"top_k\":5,\"min_score\":0.0}"
```

Expected:
- Tax-related item appears in top results.

What to say:
"This is meaning-based semantic matching, not only keyword matching."

### Step D: Prove retrieval

```bash
curl -X POST "http://localhost:8100/search/retrieve" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"clinic blood panel report\",\"top_k\":5,\"min_score\":0.0}"
```

Expected:
- Deduplicated item-level retrieval results.

What to say:
"This endpoint returns retrieval-ready, cleaner output."

### Step E: Prove automated tagging

Get an `item_id` from earlier responses and run:

```bash
curl "http://localhost:8100/items/<item_id>/tags"
```

Optional review queue:

```bash
curl "http://localhost:8100/tags/needs-review?limit=50"
```

Expected:
- Tags with confidence, status, and source.

What to say:
"Tagging runs automatically with confidence scoring and review controls."

### Step F: Prove automated classification

```bash
curl "http://localhost:8100/items/<item_id>/classification"
```

Optional review queue:

```bash
curl "http://localhost:8100/classification/needs-review?limit=50"
```

Expected:
- Classification label, confidence, and status.

What to say:
"Classification is automated, confidence-aware, and supports manual governance."

---

## 3) Operational Maturity Proof (Optional but Strong)

```bash
curl "http://localhost:8100/connectors/health"
curl -X POST "http://localhost:8100/connectors/sla/evaluate" ^
  -H "Content-Type: application/json" ^
  -d "{\"min_health_score\":0.95,\"max_failure_streak\":0,\"max_dead_letter_open\":0,\"auto_remediate\":true}"
curl "http://localhost:8100/connectors/sla/alerts?status=open&limit=100"
curl "http://localhost:8100/connectors/remediation/actions?limit=100"
curl "http://localhost:8100/connectors/notifications/deliveries?limit=100"
```

What to say:
"Beyond missing features, the platform includes monitoring, SLA governance, remediation, notifications, and escalation."

---

## 4) Customer Meeting Script (Simple)

Use this statement:

"You asked for four missing capabilities: semantic search, retrieval, automated tagging, and automated classification.  
All four are implemented and validated live through dedicated endpoints.  
In addition, reliability and operations controls were added (scheduling, health scoring, SLA, remediation, notifications, escalation), so the solution is production-ready."

---

## 5) Evidence Checklist (Screenshots)

Capture these:

1. `POST /search/semantic` result  
2. `POST /search/retrieve` result  
3. `GET /items/{id}/tags`  
4. `GET /items/{id}/classification`  
5. `GET /connectors/health`  
6. `POST /connectors/sla/evaluate` + `GET /connectors/sla/alerts`

These are enough to prove both functional completeness and operational maturity.

---

## 6) Common Troubleshooting

- `pip` not recognized  
  Use `python -m pip ...`

- SQLite schema errors (`no such column`, etc.)  
  Delete `blueprint_memory.db` and restart backend

- Python compatibility issues  
  Recreate venv with Python 3.12

- SLA returns zero alerts  
  Means current system is healthy; use stricter thresholds or induce a controlled failure test

---

## 7) Detailed Test Examples and Expected Results

Use these during the meeting when customer asks for concrete proof.

### 7.1 Create item test

Request:

```bash
curl -X POST "http://localhost:8100/items" ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"notes\",\"source_ref\":\"meeting-001\",\"title\":\"Tax filing confirmation\",\"description\":\"IRS receipt\",\"content\":\"Filed taxes and received IRS confirmation for 2025.\",\"taxonomy_path\":\"Personal/Important_Documents\",\"idempotency_key\":\"meeting-001\"}"
```

Expected result pattern:

```json
{
  "item_id": "<non-empty>",
  "status": "ingested",
  "message": "Item ingested..."
}
```

### 7.2 Process jobs test

Request:

```bash
curl -X POST "http://localhost:8100/jobs/process?limit=200"
```

Expected result pattern:

```json
{
  "processed": 1,
  "succeeded": 1,
  "failed": 0
}
```

### 7.3 Semantic search test (missing part #1)

Request:

```bash
curl -X POST "http://localhost:8100/search/semantic" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"IRS tax confirmation\",\"top_k\":5,\"min_score\":0.0}"
```

Expected result:
- At least one top result about tax filing
- Score is present for each result

Example result shape:

```json
{
  "query": "IRS tax confirmation",
  "results": [
    {
      "item_id": "<id>",
      "score": 0.6,
      "snippet": "Filed taxes and received IRS confirmation..."
    }
  ]
}
```

### 7.4 Retrieval test (missing part #2)

Request:

```bash
curl -X POST "http://localhost:8100/search/retrieve" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"tax confirmation document\",\"top_k\":5,\"min_score\":0.0}"
```

Expected result:
- Duplicates reduced (item-oriented output)
- Clear context/snippet for retrieved items

### 7.5 Automated tagging test (missing part #3)

Request:

```bash
curl "http://localhost:8100/items/<item_id>/tags"
```

Expected result:
- One or more tags
- Confidence and status fields present

Example result shape:

```json
{
  "item_id": "<id>",
  "tags": [
    {
      "tag_slug": "tax_documents",
      "confidence": 0.85,
      "status": "accepted"
    }
  ]
}
```

### 7.6 Automated classification test (missing part #4)

Request:

```bash
curl "http://localhost:8100/items/<item_id>/classification"
```

Expected result:
- Classification label present
- Confidence and status present

Example result shape:

```json
{
  "item_id": "<id>",
  "classification": {
    "class_slug": "personal_important_documents",
    "confidence": 0.82,
    "status": "accepted"
  }
}
```

### 7.7 Optional governance test

Requests:

```bash
curl "http://localhost:8100/tags/needs-review?limit=50"
curl "http://localhost:8100/classification/needs-review?limit=50"
```

Expected result:
- If low-confidence predictions exist, items appear in review lists.
- If not, empty array is still correct.

### 7.8 Operational proof (optional close)

Requests:

```bash
curl "http://localhost:8100/connectors/health"
curl -X POST "http://localhost:8100/connectors/sla/evaluate" ^
  -H "Content-Type: application/json" ^
  -d "{\"min_health_score\":0.95,\"max_failure_streak\":0,\"max_dead_letter_open\":0,\"auto_remediate\":true}"
```

Expected result:
- Health endpoint shows connector score and status
- SLA endpoint returns evaluated connector count and alert/remediation counts
