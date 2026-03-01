# Customer API Full Guide (Step-by-Step)


Use Swagger at:
- `http://localhost:8100/docs`

Use this format for every test:
1. Run request
2. Confirm HTTP status is `200` (or documented success code)
3. Confirm expected response keys exist
4. Run the "next check" endpoint

---

## 0) Before Testing

### Start backend

```powershell
cd `project`
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8100
```

### Critical queue behavior (most common confusion)

- `POST /items` saves item and enqueues jobs.
- Jobs stay `pending` until `POST /jobs/process` runs.
- There is no always-on worker by default in this project.

---

## 1) System Health

### `GET /health`
- Purpose: basic API health check
- Expected: `{"status":"ok"}`
- Next check: `GET /ready`

### `GET /ready`
- Purpose: DB + vector-store readiness check
- Expected keys: `status`, `vector_store`
- Next check: `GET /`

### `GET /`
- Purpose: root service info
- Expected keys: `service`, `docs`, `health`, `ready`

---

## 2) Core Ingestion and Job Processing

### `POST /items`
- Purpose: ingest one item and enqueue background jobs

```bash
curl -X POST "http://localhost:8100/items" ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"notes\",\"source_ref\":\"demo-001\",\"title\":\"Tax doc\",\"description\":\"W2\",\"content\":\"My tax document for 2025\",\"taxonomy_path\":\"Personal/Important_Documents\",\"idempotency_key\":\"demo-001\"}"
```

- Expected keys: `item`, `created`, `enqueued_job_id`
- Important: item statuses can still be `pending` now
- Next check: `GET /jobs?status=pending`

### `POST /items/bulk`
- Purpose: ingest multiple items in one request
- Expected keys: `results` (array of per-item ingest results)

### `GET /items/{item_id}`
- Purpose: inspect one item status
- Expected keys: item identity + pipeline status fields
- Common values: `pending`, `embedded`, `failed`

### `GET /jobs`
- Purpose: list recent jobs
- Query options: `status`, `limit`
- Expected: array of job objects with `job_type`, `status`, `attempts`

### `POST /jobs/process`
- Purpose: process pending jobs (acts as queue worker trigger)

```bash
curl -X POST "http://localhost:8100/jobs/process?limit=100"
```

- Expected keys: `processed`, `succeeded`, `failed`, `job_ids`
- Success signal: pending jobs decrease, succeeded increases
- Next check: `GET /items/{item_id}`

### `POST /index/rebuild`
- Purpose: re-enqueue embed jobs for all/specified items
- Expected key: `enqueued`

### `POST /index/reembed`
- Purpose: enqueue embedding migration/reindex
- Expected keys: `enqueued`, `message`

---

## 3) Search

### `POST /search/semantic`
- Purpose: semantic chunk search

```bash
curl -X POST "http://localhost:8100/search/semantic" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"tax payment confirmations\",\"top_k\":5,\"min_score\":0.0}"
```

- Expected keys: `query`, `top_k`, `results`
- Result check: top results should be semantically related (not exact keyword only)

### `POST /search/retrieve`
- Purpose: retrieval-oriented deduplicated item results

```bash
curl -X POST "http://localhost:8100/search/retrieve" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"tax filing notes\",\"top_k\":5,\"min_score\":0.0}"
```

- Expected keys: `query`, `top_k`, `results`
- Result check: item-level results with reduced duplication

---

## 4) Tagging

### `POST /tagging/run`
- Purpose: enqueue automated tagging jobs
- Tip: set `process_immediately=true` to process right away
- Expected keys: `enqueued`, `item_ids`, `process_result`

### `GET /items/{item_id}/tags`
- Purpose: view tags for an item
- Expected: tag entries with confidence + status + source/provenance

### `GET /tags/needs-review`
- Purpose: list items with tags in review status
- Expected: array (can be empty if no review-needed items)

### `POST /items/{item_id}/tags/override`
- Purpose: manually approve/reject a tag
- Expected: updated tagging response with manual override reflected

---

## 5) Classification

### `POST /classification/run`
- Purpose: enqueue automated classification jobs
- Tip: set `process_immediately=true` to process right away
- Expected keys: `enqueued`, `item_ids`, `process_result`

### `GET /items/{item_id}/classification`
- Purpose: view classification result for one item
- Expected: class label + confidence + status/source

### `GET /classification/needs-review`
- Purpose: list items requiring classification review
- Expected: array (can be empty)

### `POST /items/{item_id}/classification/override`
- Purpose: manually approve/reject classification
- Expected: updated classification response with manual override metadata

---

## 6) Insights, Summaries, Proactive

### `POST /insights/generate`
- Purpose: generate item/window insight records
- Expected keys: `enqueued`, `item_ids`, `process_result`

### `GET /insights`
- Purpose: list generated insights
- Expected key: `insights`

### `GET /insights/{insight_id}`
- Purpose: fetch one insight
- Expected: insight record fields + evidence metadata

### `POST /summaries/item/{item_id}`
- Purpose: generate item summary
- Expected: summary + evidence fields + timestamp

### `POST /summaries/window`
- Purpose: generate time-window summary
- Expected: counts and summary details for chosen window

### `POST /briefs/cross-domain`
- Purpose: generate cross-domain brief
- Expected: consolidated multi-domain summary output

### `POST /proactive/run`
- Purpose: generate proactive signals
- Expected keys: `enqueued`, `item_ids`, `process_result`

### `POST /timeline/activity`
- Purpose: query timeline behavior events
- Expected key: `events`

### `GET /proactive/signals`
- Purpose: list proactive signals
- Expected key: `signals`

### `POST /proactive/signals/{signal_id}/resolve`
- Purpose: resolve/dismiss one signal
- Expected: updated signal with changed status

### `POST /assistant/digest`
- Purpose: create short behavior digest
- Expected keys: `days`, `digest`, `generated_at`

### `POST /assistant/recommendations`
- Purpose: digest + top recommendations
- Expected keys: `digest`, `top_signals`, `generated_at`

---

## 7) Reliability and Metrics

### `GET /metrics/summary`
- Purpose: reliability/system-level metrics
- Expected: coherent non-negative totals

### `GET /metrics/jobs`
- Purpose: job throughput/failure metrics by job type
- Expected: per-job counters (`total`, `succeeded`, `failed`, etc.)

### `POST /evaluation/run`
- Purpose: run quality checks
- Expected keys: score/check totals/details

### `GET /evaluation/latest`
- Purpose: get latest evaluation
- Expected: latest run record

### `GET /maintenance/dead-letter`
- Purpose: list dead-letter jobs
- Expected keys: `records`, `generated_at`

### `POST /maintenance/dead-letter/requeue`
- Purpose: requeue dead-letter jobs
- Expected keys: `requeued`, `dead_letter_ids`

---

## 8) Connectors (Core)

### `POST /connectors/{connector_name}/sync`
- Purpose: manual connector sync
- Expected: run status + fetched/ingested counts + run IDs

### `GET /connectors/status`
- Purpose: connector status + checkpoints
- Expected: connector entries with last run/checkpoint state

### `POST /connectors/{connector_name}/auth`
- Purpose: configure connector auth metadata
- Expected: connector/auth status + saved message

### `GET /connectors/auth`
- Purpose: list connector credential states
- Expected: masked secrets only (no raw secret values)

### `POST /connectors/{connector_name}/schedule`
- Purpose: upsert schedule settings
- Expected: schedule config + `next_run_at`

### `GET /connectors/schedules`
- Purpose: list schedules
- Expected: all saved schedule rows

### `POST /connectors/schedules/run-due`
- Purpose: run due schedules
- Expected: triggered count + per-run outcomes

### `POST /connectors/{connector_name}/webhook`
- Purpose: event-driven sync trigger
- Expected: event + run result (or 400 for invalid secret)

### `GET /connectors/dead-letter`
- Purpose: list connector schedule dead-letter records
- Expected: records with attempts + last error

### `POST /connectors/dead-letter/requeue`
- Purpose: requeue connector dead-letter schedules
- Expected: `requeued` count + IDs

### `GET /connectors/audit`
- Purpose: governance/audit trail
- Expected: action/result records with timestamps

---

## 9) Connector Governance and Orchestration

### `POST /connectors/{connector_name}/policy`
- Purpose: set connector rate/concurrency policy
- Expected: saved policy values + message

### `GET /connectors/policies`
- Purpose: list connector policies
- Expected: policy records

### `POST /connectors/{connector_name}/priority`
- Purpose: set connector priority/group/pause state
- Expected: updated state + confirmation message

### `POST /connectors/groups/{group_name}/pause`
- Purpose: pause all connectors in a group
- Expected: `paused=true`, updated count

### `POST /connectors/groups/{group_name}/resume`
- Purpose: resume all connectors in a group
- Expected: `paused=false`, updated count

### `POST /connectors/orchestrate/run`
- Purpose: run multiple connectors in one pass
- Expected: orchestration run ID + per-connector outcomes

### `GET /connectors/health`
- Purpose: health scorecard
- Expected: `health_score`, status, latency, failure/dead-letter signals

---

## 10) Simulation and Policy Automation

### `POST /connectors/{connector_name}/simulate`
- Purpose: dry-run sync preview without ingestion
- Expected: fetched/new/existing candidate counts + sample refs

### `GET /connectors/simulations`
- Purpose: list simulation runs
- Expected: simulation IDs + statuses + summary counts

### `POST /connectors/{connector_name}/policy/recommend`
- Purpose: data-driven policy recommendation
- Expected: recommended rate/concurrency/interval + reason

### `POST /connectors/{connector_name}/policy/auto-apply`
- Purpose: apply recommendation with guardrails
- Expected: applied flag + revision info + old/new values

### `GET /connectors/policy/revisions`
- Purpose: list policy revisions
- Expected: revision history with status and value deltas

### `POST /connectors/{connector_name}/policy/rollback`
- Purpose: rollback latest applied policy revision
- Expected: rollback status + revision id/message

### `POST /connectors/{connector_name}/policy/guardrail-check`
- Purpose: evaluate failure ratio and optionally auto-rollback
- Expected: failure ratio + breached flag + rollback state

---

## 11) SLA, Remediation, Notifications, Escalation

### `POST /connectors/sla/evaluate`
- Purpose: evaluate SLA thresholds
- Expected: evaluated count + alerts created + remediation counts

### `GET /connectors/sla/alerts`
- Purpose: list SLA alerts
- Expected: metric, threshold, severity, status fields

### `POST /connectors/sla/alerts/{alert_id}/resolve`
- Purpose: resolve one SLA alert
- Expected: resolved status/message

### `POST /connectors/{connector_name}/remediation`
- Purpose: trigger manual remediation action
- Expected: action ID + status + action result

### `GET /connectors/remediation/actions`
- Purpose: remediation history
- Expected: action records with reason and timestamps

### `POST /connectors/notifications/channels`
- Purpose: create/update notification channel
- Expected: channel identity + saved message

### `GET /connectors/notifications/channels`
- Purpose: list channels
- Expected: channel scope/type/target/enabled/min severity

### `POST /connectors/notifications/test`
- Purpose: send simulated notification
- Expected: attempted/sent counters

### `GET /connectors/notifications/deliveries`
- Purpose: view delivery logs
- Expected: delivery rows with status + payload preview

### `POST /connectors/{connector_name}/escalation`
- Purpose: create/update escalation policy
- Expected: policy fields + saved message

### `GET /connectors/escalation/policies`
- Purpose: list escalation policies
- Expected: escalation policy records

### `POST /connectors/escalation/evaluate`
- Purpose: evaluate/trigger escalation
- Expected: escalations triggered + action summary

---

## 12) Feedback Export

### `GET /feedback/export`
- Purpose: export manual override feedback dataset
- Expected keys: `records`, `generated_at`

---

## 13) Quick Demo Script (Customer Meeting)

Run these in order to prove full pipeline:

1. `POST /items`
2. `GET /jobs?status=pending`
3. `POST /jobs/process?limit=100`
4. `GET /items/{item_id}`
5. `POST /search/semantic`
6. `POST /search/retrieve`
7. `GET /items/{item_id}/tags`
8. `GET /items/{item_id}/classification`

If all above pass, the core customer concern is fully addressed.

---

## 14) Swagger Browser Walkthrough (for beginners)

Open `http://localhost:8100/docs` and use this exact process for every API:

1. Click endpoint row (for example `POST /items`)
2. Click `Try it out`
3. Fill path/query/body fields
4. Click `Execute`
5. Check:
   - `Response code` (usually `200`)
   - `Response body` has expected keys
6. For IDs (`item_id`, `insight_id`, `signal_id`, `alert_id`), copy and reuse in next endpoints

Keep this scratch list while testing:
- `item_id`
- `insight_id`
- `signal_id`
- `alert_id`
- `dead_letter_id`
- `channel_id`

---

## 15) Endpoint-by-Endpoint Swagger Test Cards

Each card includes:
- Example input for Swagger
- Expected result keys to confirm success

### A) Base

#### `GET /health`
- Input: none
- Expected: `status = "ok"`

#### `GET /`
- Input: none
- Expected keys: `service`, `docs`, `health`, `ready`

#### `GET /ready`
- Input: none
- Expected keys: `status`, `vector_store`

### B) Ingestion + Queue

#### `POST /items`
- Body example:
```json
{
  "source": "notes",
  "source_ref": "s-item-001",
  "title": "Tax filing confirmation",
  "description": "IRS receipt",
  "content": "Filed taxes and received IRS confirmation.",
  "taxonomy_path": "Personal/Important_Documents",
  "idempotency_key": "s-item-001"
}
```
- Expected keys: `item`, `created`, `enqueued_job_id`

#### `POST /items/bulk`
- Body example:
```json
{
  "items": [
    {
      "source": "notes",
      "source_ref": "s-bulk-001",
      "title": "Lab report",
      "description": "Blood panel",
      "content": "Lipid panel uploaded.",
      "taxonomy_path": "Health/Lab_Work",
      "idempotency_key": "s-bulk-001"
    },
    {
      "source": "notes",
      "source_ref": "s-bulk-002",
      "title": "Utility bill",
      "description": "Electricity",
      "content": "Electricity payment processed.",
      "taxonomy_path": "Personal/Bills",
      "idempotency_key": "s-bulk-002"
    }
  ]
}
```
- Expected keys: `results[]` entries with `item`, `created`, `enqueued_job_id`

#### `GET /items/{item_id}`
- Path param: `item_id=<copied from POST /items response>`
- Expected: item object with status fields (`status`, `tagging_status`, `classification_status`, etc.)

#### `GET /jobs`
- Query example: `status=pending`, `limit=50`
- Expected: list of jobs with `job_type`, `status`, `attempts`

#### `POST /jobs/process`
- Query example: `limit=100`
- Expected keys: `processed`, `succeeded`, `failed`, `job_ids`

#### `POST /index/rebuild`
- Body example:
```json
{
  "item_ids": []
}
```
- Expected key: `enqueued`

#### `POST /index/reembed`
- Body example:
```json
{
  "item_ids": []
}
```
- Expected keys: `enqueued`, `message`

### C) Search

#### `POST /search/semantic`
- Body example:
```json
{
  "query": "IRS tax confirmation",
  "top_k": 5,
  "min_score": 0.0
}
```
- Expected keys: `query`, `top_k`, `results[]`

#### `POST /search/retrieve`
- Body example:
```json
{
  "query": "tax filing notes",
  "top_k": 5,
  "min_score": 0.0
}
```
- Expected keys: `query`, `top_k`, `results[]`

### D) Tagging

#### `POST /tagging/run`
- Body example:
```json
{
  "item_ids": [],
  "process_immediately": true
}
```
- Expected keys: `enqueued`, `item_ids`, `process_result`

#### `GET /items/{item_id}/tags`
- Path param: `item_id=<saved id>`
- Expected: tagging response with tags, confidence, status/source

#### `GET /tags/needs-review`
- Query example: `limit=50`
- Expected: list (can be empty if no low-confidence tags)

#### `POST /items/{item_id}/tags/override`
- Path param: `item_id=<saved id>`
- Body example:
```json
{
  "tag_slug": "tax_documents",
  "action": "approve",
  "confidence": 0.99,
  "notes": "Verified by tester"
}
```
- Expected: tag state shows manual override

### E) Classification

#### `POST /classification/run`
- Body example:
```json
{
  "item_ids": [],
  "process_immediately": true
}
```
- Expected keys: `enqueued`, `item_ids`, `process_result`

#### `GET /items/{item_id}/classification`
- Path param: `item_id=<saved id>`
- Expected: class label/confidence/status/source

#### `GET /classification/needs-review`
- Query example: `limit=50`
- Expected: list (can be empty)

#### `POST /items/{item_id}/classification/override`
- Path param: `item_id=<saved id>`
- Body example:
```json
{
  "class_slug": "personal_important_documents",
  "action": "approve",
  "confidence": 0.98,
  "notes": "Confirmed by tester"
}
```
- Expected: classification source becomes manual override

### F) Insights + Summaries + Proactive + Assistant

#### `POST /insights/generate`
- Body example:
```json
{
  "item_ids": [],
  "insight_type": "item",
  "window_days": 30,
  "process_immediately": true
}
```
- Expected keys: `enqueued`, `item_ids`, `process_result`

#### `GET /insights`
- Query example: `limit=20`
- Expected key: `insights[]`

#### `GET /insights/{insight_id}`
- Path param: `insight_id=<from GET /insights>`
- Expected: single insight record

#### `POST /summaries/item/{item_id}`
- Path param: `item_id=<saved id>`
- Expected: summary text + evidence + timestamp fields

#### `POST /summaries/window`
- Body example:
```json
{
  "days": 30,
  "source": null,
  "taxonomy_prefix": null,
  "use_cache": true
}
```
- Expected: window summary response with counts/details

#### `POST /briefs/cross-domain`
- Body example:
```json
{
  "days": 30,
  "use_cache": true
}
```
- Expected: cross-domain brief output

#### `POST /proactive/run`
- Body example:
```json
{
  "item_ids": [],
  "process_immediately": true,
  "days": 30
}
```
- Expected keys: `enqueued`, `item_ids`, `process_result`

#### `POST /timeline/activity`
- Body example:
```json
{
  "days": 30,
  "event_type": null,
  "limit": 100
}
```
- Expected key: `events[]`

#### `GET /proactive/signals`
- Query example: `status=open`, `limit=20`
- Expected key: `signals[]`

#### `POST /proactive/signals/{signal_id}/resolve`
- Path param: `signal_id=<from proactive signals>`
- Body example:
```json
{
  "status": "done"
}
```
- Expected: updated signal with resolved status

#### `POST /assistant/digest`
- Query example: `days=7`
- Expected keys: `days`, `digest`, `generated_at`

#### `POST /assistant/recommendations`
- Query example: `days=7`, `limit=5`
- Expected keys: `digest`, `top_signals`, `generated_at`

### G) Metrics + Reliability

#### `GET /metrics/summary`
- Input: none
- Expected: system totals and health metrics

#### `GET /metrics/jobs`
- Input: none
- Expected: per-job-type totals (`total`, `succeeded`, `failed`, etc.)

#### `POST /evaluation/run`
- Body example:
```json
{
  "suite_name": "default_suite",
  "days": 30
}
```
- Expected: score/checks/details

#### `GET /evaluation/latest`
- Input: none
- Expected: latest evaluation run object

#### `GET /maintenance/dead-letter`
- Query example: `status=open`, `limit=100`
- Expected keys: `records[]`, `generated_at`

#### `POST /maintenance/dead-letter/requeue`
- Body example:
```json
{
  "dead_letter_ids": [],
  "limit": 20
}
```
- Expected keys: `requeued`, `dead_letter_ids`

### H) Connectors Core

Use `connector_name=local_json` for test examples.

#### `POST /connectors/{connector_name}/sync`
- Path param: `connector_name=local_json`
- Body example:
```json
{
  "config": {
    "path": "F:/tmp/blueprint_seed.json"
  },
  "limit": 500,
  "use_checkpoint": true
}
```
- Expected: run status + fetched/ingested counts

#### `GET /connectors/status`
- Input: none
- Expected: connector status list with checkpoint data

#### `POST /connectors/{connector_name}/auth`
- Path param: `connector_name=local_json`
- Body example:
```json
{
  "auth_type": "api_key",
  "secret_value": "demo-secret",
  "secret_ref": "local-dev"
}
```
- Expected: saved status + message

#### `GET /connectors/auth`
- Input: none
- Expected: masked secret values only

#### `POST /connectors/{connector_name}/schedule`
- Path param: `connector_name=local_json`
- Body example:
```json
{
  "enabled": true,
  "interval_minutes": 5,
  "priority": 10,
  "group_name": "critical",
  "is_paused": false,
  "max_attempts": 3,
  "limit": 500,
  "run_immediately": true,
  "config": {
    "path": "F:/tmp/blueprint_seed.json"
  }
}
```
- Expected: schedule saved + `next_run_at`

#### `GET /connectors/schedules`
- Input: none
- Expected: schedules list

#### `POST /connectors/schedules/run-due`
- Query example: `max_runs=10`
- Expected: triggered count + results list

#### `POST /connectors/{connector_name}/webhook`
- Path param: `connector_name=local_json`
- Body example:
```json
{
  "secret": "demo-secret",
  "event_type": "file.changed",
  "config": {
    "path": "F:/tmp/blueprint_seed.json"
  },
  "limit": 100,
  "use_checkpoint": true
}
```
- Expected: event/run IDs and status (or 400 if secret invalid)

#### `GET /connectors/dead-letter`
- Query example: `status=open`, `limit=50`
- Expected: dead-letter records with attempts and error

#### `POST /connectors/dead-letter/requeue`
- Body example:
```json
{
  "dead_letter_ids": [],
  "limit": 20
}
```
- Expected: `requeued`, `dead_letter_ids`

#### `GET /connectors/audit`
- Query example: `connector_name=local_json`, `limit=100`
- Expected: audit records with action/result/timestamp

### I) Connector Governance, Orchestration, Health

#### `POST /connectors/{connector_name}/policy`
- Path param: `connector_name=local_json`
- Body example:
```json
{
  "enabled": true,
  "rate_limit_per_hour": 20,
  "max_concurrent_runs": 1
}
```
- Expected: policy saved response

#### `GET /connectors/policies`
- Input: none
- Expected: policies list

#### `POST /connectors/{connector_name}/priority`
- Path param: `connector_name=local_json`
- Body example:
```json
{
  "priority": 25,
  "group_name": "critical",
  "is_paused": false
}
```
- Expected: updated priority/group/pause state

#### `POST /connectors/groups/{group_name}/pause`
- Path param: `group_name=critical`
- Expected: `paused=true`, updated connector count

#### `POST /connectors/groups/{group_name}/resume`
- Path param: `group_name=critical`
- Expected: `paused=false`, updated connector count

#### `POST /connectors/orchestrate/run`
- Body example:
```json
{
  "connector_names": [],
  "max_connectors": 20,
  "use_checkpoint": true
}
```
- Expected: orchestration run ID + per-connector outcomes

#### `GET /connectors/health`
- Query example: `lookback_runs=50`
- Expected: health score/status and reliability metrics

### J) Simulation + Policy Automation

#### `POST /connectors/{connector_name}/simulate`
- Path param: `connector_name=local_json`
- Body example:
```json
{
  "config": {
    "path": "F:/tmp/blueprint_seed.json"
  },
  "limit": 500,
  "use_checkpoint": false
}
```
- Expected: simulation counts (`fetched`, `candidate_new_items`, `candidate_existing_items`)

#### `GET /connectors/simulations`
- Query example: `connector_name=local_json`, `limit=20`
- Expected: simulation records list

#### `POST /connectors/{connector_name}/policy/recommend`
- Path param: `connector_name=local_json`
- Body: none
- Expected: recommended rate/concurrency/interval + reason

#### `POST /connectors/{connector_name}/policy/auto-apply`
- Path param: `connector_name=local_json`
- Body example:
```json
{
  "enabled": true,
  "dry_run": false,
  "min_rate_limit_per_hour": 20,
  "max_rate_limit_per_hour": 200,
  "max_concurrent_runs_cap": 2
}
```
- Expected: applied flag + revision details

#### `GET /connectors/policy/revisions`
- Query example: `connector_name=local_json`, `limit=20`
- Expected: revision rows with previous/new policy values

#### `POST /connectors/{connector_name}/policy/rollback`
- Path param: `connector_name=local_json`
- Expected: `rolled_back`, `revision_id`, `message`

#### `POST /connectors/{connector_name}/policy/guardrail-check`
- Path param: `connector_name=local_json`
- Body example:
```json
{
  "lookback_runs": 20,
  "failure_ratio_threshold": 0.3,
  "auto_rollback": true
}
```
- Expected: `failure_ratio`, `breached`, `rolled_back`, `message`

### K) SLA + Remediation + Notifications + Escalation

#### `POST /connectors/sla/evaluate`
- Body example:
```json
{
  "min_health_score": 0.95,
  "max_failure_streak": 0,
  "max_dead_letter_open": 0,
  "auto_remediate": true
}
```
- Expected: evaluated count + alerts/remediation counts

#### `GET /connectors/sla/alerts`
- Query example: `status=open`, `limit=100`
- Expected: alert rows with threshold and severity

#### `POST /connectors/sla/alerts/{alert_id}/resolve`
- Path param: `alert_id=<from SLA alerts>`
- Expected: resolved status/message

#### `POST /connectors/{connector_name}/remediation`
- Path param: `connector_name=local_json`
- Body example:
```json
{
  "action_type": "reduce_policy_limits",
  "reason": "manual throttle test"
}
```
- Expected: action ID + completion status

#### `GET /connectors/remediation/actions`
- Query example: `connector_name=local_json`, `limit=100`
- Expected: remediation action history

#### `POST /connectors/notifications/channels`
- Body example:
```json
{
  "connector_name": "*",
  "channel_type": "webhook",
  "target": "https://example.invalid/alerts",
  "secret": "demo-secret",
  "min_severity": "warning",
  "is_enabled": true
}
```
- Expected: channel saved with ID and message

#### `GET /connectors/notifications/channels`
- Query example: `limit=100`
- Expected: channel records list

#### `POST /connectors/notifications/test`
- Body example:
```json
{
  "connector_name": "local_json",
  "severity": "critical",
  "message": "test notification"
}
```
- Expected: `attempted_channels`, `sent`

#### `GET /connectors/notifications/deliveries`
- Query example: `connector_name=local_json`, `limit=100`
- Expected: delivery logs with status and target

#### `POST /connectors/{connector_name}/escalation`
- Path param: `connector_name=local_json`
- Body example:
```json
{
  "enabled": true,
  "open_alert_count_threshold": 1,
  "action_type": "reduce_policy_limits",
  "notify_channel_id": null
}
```
- Expected: escalation policy saved

#### `GET /connectors/escalation/policies`
- Query example: `connector_name=local_json`, `limit=100`
- Expected: escalation policies list

#### `POST /connectors/escalation/evaluate`
- Body: none
- Expected: escalations triggered count + actions summary

### L) Feedback Export

#### `GET /feedback/export`
- Query example: `limit=500`
- Expected keys: `records[]`, `generated_at`


- "Create item only queues jobs. Processing starts when we execute `/jobs/process`."
- "Now we verify semantic search and retrieval on already-processed data."
- "Now we verify automated tagging and classification with confidence and review flow."
- "Now we verify operations: metrics, SLA, remediation, and alerts."
- "This proves feature completeness and operational readiness."

