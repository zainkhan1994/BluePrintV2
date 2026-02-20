# Blueprint Backend (Phases 1-16)

Current foundation for persistent memory:

- Metadata API service (FastAPI)
- Persistent metadata DB (SQLite via SQLAlchemy)
- Local vector index (Chroma persistent collection)
- Ingestion + indexing job flow with item status tracking

## What this implements

- `POST /items` - ingest one item (idempotent by `idempotency_key`)
- `POST /items/bulk` - ingest many items
- `GET /items/{item_id}` - inspect item and pipeline state
- `POST /index/rebuild` - enqueue reindex for selected/all items
- `POST /jobs/process` - process pending embedding/index jobs
- `GET /jobs` - inspect job queue status
- `POST /search/semantic` - semantic chunk search
- `POST /search/retrieve` - retrieval-oriented deduped item search
- `POST /tagging/run` - enqueue automated tagging jobs for all/specified items
- `GET /items/{item_id}/tags` - list tags, confidence, and provenance for an item
- `POST /items/{item_id}/tags/override` - manual approve/reject tag override
- `GET /tags/needs-review` - list items that have tags in review status
- `POST /classification/run` - enqueue automated classification jobs
- `GET /items/{item_id}/classification` - view current classification result
- `POST /items/{item_id}/classification/override` - manual classification override
- `GET /classification/needs-review` - list items requiring classification review
- `POST /insights/generate` - create insight records from item memory
- `GET /insights` - list generated insights
- `GET /insights/{insight_id}` - fetch one insight
- `POST /summaries/item/{item_id}` - evidence-backed item summary
- `POST /summaries/window` - time-window summary
- `POST /briefs/cross-domain` - cross-domain memory brief
- `POST /proactive/run` - generate proactive signals from memory state
- `POST /timeline/activity` - query behavioral timeline events
- `GET /proactive/signals` - list proactive signals
- `POST /proactive/signals/{signal_id}/resolve` - resolve or dismiss a signal
- `POST /assistant/digest` - generate short behavior digest
- `POST /assistant/recommendations` - digest + top open recommendations
- `GET /metrics/summary` - system-level reliability and health metrics
- `GET /metrics/jobs` - per-job-type throughput and failure metrics
- `POST /evaluation/run` - execute quality checks over recent data
- `GET /evaluation/latest` - fetch latest evaluation results
- `GET /maintenance/dead-letter` - list jobs moved to dead-letter queue
- `POST /maintenance/dead-letter/requeue` - requeue dead-letter jobs
- `POST /connectors/{connector_name}/sync` - ingest external/local source data via connector
- `GET /connectors/status` - connector sync state and checkpoint view
- `POST /connectors/{connector_name}/auth` - configure connector credential/auth metadata
- `GET /connectors/auth` - list connector credential state (masked secrets)
- `POST /connectors/{connector_name}/schedule` - create/update connector schedule configuration
- `GET /connectors/schedules` - list connector schedule states
- `POST /connectors/schedules/run-due` - execute due connector schedules (checkpoint-aware)
- `POST /connectors/{connector_name}/webhook` - event-triggered connector sync (optional secret validation)
- `GET /connectors/dead-letter` - connector schedule dead-letter records
- `POST /connectors/dead-letter/requeue` - re-enable and requeue connector schedules from dead-letter
- `POST /connectors/{connector_name}/policy` - set connector governance policy (rate + concurrency)
- `GET /connectors/policies` - list connector governance policies
- `POST /connectors/{connector_name}/simulate` - dry-run connector sync preview (no ingestion side effects)
- `GET /connectors/simulations` - inspect recent connector simulation runs
- `POST /connectors/{connector_name}/policy/recommend` - generate data-driven policy recommendation
- `POST /connectors/{connector_name}/policy/auto-apply` - apply recommended policy with guardrail clamps
- `GET /connectors/policy/revisions` - list policy change revisions
- `POST /connectors/{connector_name}/policy/rollback` - rollback latest applied policy revision
- `POST /connectors/{connector_name}/policy/guardrail-check` - evaluate failure ratio and optionally auto-rollback
- `POST /connectors/{connector_name}/priority` - set connector priority/group/pause override
- `POST /connectors/groups/{group_name}/pause` - pause all connectors in a group
- `POST /connectors/groups/{group_name}/resume` - resume all connectors in a group
- `POST /connectors/orchestrate/run` - run multiple connectors in one orchestration pass
- `GET /connectors/health` - connector health scorecard (success/failure/latency/dead-letter signals)
- `POST /connectors/sla/evaluate` - evaluate SLA thresholds and optionally auto-remediate connectors
- `GET /connectors/sla/alerts` - list connector SLA alerts
- `POST /connectors/sla/alerts/{alert_id}/resolve` - resolve SLA alert
- `POST /connectors/{connector_name}/remediation` - trigger manual connector remediation action
- `GET /connectors/remediation/actions` - list remediation action history
- `POST /connectors/notifications/channels` - create/update notification channels
- `GET /connectors/notifications/channels` - list notification channels
- `POST /connectors/notifications/test` - send simulated test notification
- `GET /connectors/notifications/deliveries` - list notification delivery logs
- `POST /connectors/{connector_name}/escalation` - create/update escalation policy
- `GET /connectors/escalation/policies` - list escalation policies
- `POST /connectors/escalation/evaluate` - evaluate and trigger escalation policies
- `GET /connectors/audit` - list connector governance/audit log events
- `GET /feedback/export` - export manual override feedback dataset
- `POST /index/reembed` - enqueue embedding migration/reindex jobs
- `GET /health` and `GET /ready` - service/db/vector readiness

## Quick start

1. Create virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure env:

```bash
copy .env.example .env
```

3. Run API:

```bash
uvicorn app.main:app --reload --port 8100
```

4. Open docs:

- `http://localhost:8100/docs`

## Minimal test flow

1. Ingest item:

```bash
curl -X POST "http://localhost:8100/items" ^
  -H "Content-Type: application/json" ^
  -d "{\"source\":\"notes\",\"source_ref\":\"n-1\",\"title\":\"Tax doc\",\"description\":\"W2\",\"content\":\"My tax document for 2025\",\"taxonomy_path\":\"Personal/Important_Documents\",\"idempotency_key\":\"demo-001\"}"
```

2. Process pending jobs:

```bash
curl -X POST "http://localhost:8100/jobs/process?limit=50"
```

3. Check readiness:

```bash
curl "http://localhost:8100/ready"
```

4. Semantic search:

```bash
curl -X POST "http://localhost:8100/search/semantic" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"tax payment confirmations\",\"top_k\":5,\"min_score\":0.0}"
```

5. Retrieval search (deduped by item):

```bash
curl -X POST "http://localhost:8100/search/retrieve" ^
  -H "Content-Type: application/json" ^
  -d "{\"query\":\"tax filing notes\",\"top_k\":5,\"min_score\":0.0}"
```

6. Run automated tagging:

```bash
curl -X POST "http://localhost:8100/tagging/run" ^
  -H "Content-Type: application/json" ^
  -d "{\"item_ids\":[],\"process_immediately\":true}"
```

7. Inspect tags for one item:

```bash
curl "http://localhost:8100/items/<item_id>/tags"
```

8. List review queue:

```bash
curl "http://localhost:8100/tags/needs-review?limit=50"
```

9. Manual override example:

```bash
curl -X POST "http://localhost:8100/items/<item_id>/tags/override" ^
  -H "Content-Type: application/json" ^
  -d "{\"tag_slug\":\"tax_documents\",\"action\":\"approve\",\"confidence\":0.99,\"notes\":\"verified by user\"}"
```

10. Run automated classification:

```bash
curl -X POST "http://localhost:8100/classification/run" ^
  -H "Content-Type: application/json" ^
  -d "{\"item_ids\":[],\"process_immediately\":true}"
```

11. Inspect classification for one item:

```bash
curl "http://localhost:8100/items/<item_id>/classification"
```

12. Classification review queue:

```bash
curl "http://localhost:8100/classification/needs-review?limit=50"
```

13. Classification override example:

```bash
curl -X POST "http://localhost:8100/items/<item_id>/classification/override" ^
  -H "Content-Type: application/json" ^
  -d "{\"class_slug\":\"personal_important_documents\",\"action\":\"approve\",\"confidence\":0.98,\"notes\":\"confirmed by user\"}"
```

14. Generate insights:

```bash
curl -X POST "http://localhost:8100/insights/generate" ^
  -H "Content-Type: application/json" ^
  -d "{\"item_ids\":[],\"insight_type\":\"item\",\"window_days\":30,\"process_immediately\":true}"
```

15. List insights:

```bash
curl "http://localhost:8100/insights?limit=20"
```

16. Item summary:

```bash
curl -X POST "http://localhost:8100/summaries/item/<item_id>"
```

17. Window summary:

```bash
curl -X POST "http://localhost:8100/summaries/window" ^
  -H "Content-Type: application/json" ^
  -d "{\"days\":30,\"source\":null,\"taxonomy_prefix\":null,\"use_cache\":true}"
```

18. Cross-domain brief:

```bash
curl -X POST "http://localhost:8100/briefs/cross-domain" ^
  -H "Content-Type: application/json" ^
  -d "{\"days\":30,\"use_cache\":true}"
```

19. Run proactive signal generation:

```bash
curl -X POST "http://localhost:8100/proactive/run" ^
  -H "Content-Type: application/json" ^
  -d "{\"item_ids\":[],\"process_immediately\":true,\"days\":30}"
```

20. Query behavioral timeline:

```bash
curl -X POST "http://localhost:8100/timeline/activity" ^
  -H "Content-Type: application/json" ^
  -d "{\"days\":30,\"event_type\":null,\"limit\":100}"
```

21. List proactive signals:

```bash
curl "http://localhost:8100/proactive/signals?status=open&limit=20"
```

22. Resolve one signal:

```bash
curl -X POST "http://localhost:8100/proactive/signals/<signal_id>/resolve" ^
  -H "Content-Type: application/json" ^
  -d "{\"status\":\"done\"}"
```

23. Assistant digest:

```bash
curl -X POST "http://localhost:8100/assistant/digest?days=7"
```

24. Assistant recommendations:

```bash
curl -X POST "http://localhost:8100/assistant/recommendations?days=7&limit=5"
```

25. Metrics summary:

```bash
curl "http://localhost:8100/metrics/summary"
```

26. Job metrics:

```bash
curl "http://localhost:8100/metrics/jobs"
```

27. Run evaluation:

```bash
curl -X POST "http://localhost:8100/evaluation/run" ^
  -H "Content-Type: application/json" ^
  -d "{\"suite_name\":\"default_suite\",\"days\":30}"
```

28. Latest evaluation:

```bash
curl "http://localhost:8100/evaluation/latest"
```

29. List dead-letter jobs:

```bash
curl "http://localhost:8100/maintenance/dead-letter?status=open&limit=100"
```

30. Requeue dead-letter jobs:

```bash
curl -X POST "http://localhost:8100/maintenance/dead-letter/requeue" ^
  -H "Content-Type: application/json" ^
  -d "{\"dead_letter_ids\":[],\"limit\":20}"
```

31. Connector sync (JSON):

```bash
curl -X POST "http://localhost:8100/connectors/local_json/sync" ^
  -H "Content-Type: application/json" ^
  -d "{\"config\":{\"path\":\"F:/tmp/blueprint_seed.json\"},\"limit\":500}"
```

32. Connector status:

```bash
curl "http://localhost:8100/connectors/status"
```

33. Export feedback dataset:

```bash
curl "http://localhost:8100/feedback/export?limit=500"
```

34. Re-embed all items (embedding migration):

```bash
curl -X POST "http://localhost:8100/index/reembed" ^
  -H "Content-Type: application/json" ^
  -d "{\"item_ids\":[]}"
```

## Phase 3 validation checklist

- Run `POST /tagging/run` with `process_immediately=true` and confirm jobs are enqueued and processed.
- For a known tax-like item, verify `tax_documents` appears via `GET /items/{item_id}/tags`.
- Re-run tagging and confirm no duplicate item-tag rows are created.
- Confirm medium-confidence tags appear in `GET /tags/needs-review`.
- Apply `POST /items/{item_id}/tags/override` and verify:
  - tag `source` becomes `manual_override`
  - `is_manual_override` is `true`
  - status changes to `accepted` or `rejected` as requested.

## Phase 4 validation checklist

- Run `POST /classification/run` with `process_immediately=true` and verify classify jobs complete.
- For tax-like content, confirm classification aligns to `Personal/Important_Documents`.
- For medical content, confirm classification aligns to `Health/Doctors` or `Health/Lab_Work`.
- Re-run classification and verify only one classification row exists per item (updated, not duplicated).
- Confirm low-confidence items appear in `GET /classification/needs-review`.
- Apply classification override and verify:
  - `source` becomes `manual_override`
  - `is_manual_override` is `true`
  - status changes to `accepted` or `rejected`
  - item summary fields reflect override label/confidence.

## Phase 5 validation checklist

- Run `POST /insights/generate` and confirm `GET /insights` returns new records.
- Verify each insight includes source evidence (`source_item_ids`) and a confidence score.
- Validate `POST /summaries/item/{item_id}` includes summary, evidence list, and timestamp.
- Validate `POST /summaries/window` counts align with actual item volume in the selected range.
- Validate `POST /briefs/cross-domain` reports sources/classes/tags seen in recent data.
- Repeat summary calls with `use_cache=true` and verify stable deterministic output.

## Phase 6 validation checklist

- Run `POST /proactive/run` and confirm proactive jobs generate open signals.
- Validate `POST /timeline/activity` returns ordered events (`ingested`, `embedded`, `tagged`, `classified`, `insighted`).
- Validate `GET /proactive/signals` returns actionable recommendations with confidence and source item IDs.
- Resolve one signal and confirm status transitions via `/proactive/signals/{signal_id}/resolve`.
- Validate `/assistant/digest` reflects recent activity volume and open signal count.
- Validate `/assistant/recommendations` includes digest plus top open signals.

## Phase 7 validation checklist

- Run `GET /metrics/summary` and confirm totals are non-negative and coherent.
- Run `GET /metrics/jobs` and confirm each job type reports total/succeeded/failed/pending/dead_letter.
- Run `POST /evaluation/run` and verify:
  - `score` in `0..1`
  - `checks_total >= checks_passed`
  - details include thresholds and pass/fail states.
- Run `GET /evaluation/latest` and confirm it returns the most recent run.
- Force a failing job (e.g. invalid data) multiple times and verify it transitions to dead-letter after max attempts.
- Requeue dead-letter jobs with `POST /maintenance/dead-letter/requeue` and verify jobs return to `pending`.

## Phase 8 validation checklist

- Set `EMBEDDING_PROVIDER` to `local_hash` or `api` and confirm `/index/reembed` enqueues embed jobs.
- Run connector sync with `local_json`, `local_csv`, and `notes_dir` and verify:
  - non-zero `fetched_count`
  - reasonable `ingested_count`
  - connector checkpoint updates via `/connectors/status`.
- Validate hybrid tagging/classification provenance:
  - items can show `source=model_assist_v1` on strong assisted matches
  - manual overrides still persist as `manual_override`.
- Validate feedback capture by performing manual tag/classification overrides and confirming rows in `/feedback/export`.
- Verify no regressions in Phase 7 reliability (`/metrics/*`, `/evaluation/*`, dead-letter behavior).

## Phase 9 validation checklist

- Configure connector auth with `POST /connectors/{connector_name}/auth` and verify masked output in `GET /connectors/auth`.
- Create a schedule with `POST /connectors/{connector_name}/schedule` and verify `next_run_at` via `GET /connectors/schedules`.
- Trigger scheduler execution with `POST /connectors/schedules/run-due` and confirm due schedules run.
- Re-run due scheduler with no new source changes and confirm incremental behavior (`ingested_count` remains 0 or lower than first run).
- Confirm `GET /connectors/status` checkpoint moves forward after scheduled runs.
- Validate no regressions in manual sync (`POST /connectors/{connector_name}/sync`) and feedback export (`GET /feedback/export`).

## Phase 10 validation checklist

- Configure schedule retry policy (`max_attempts`) and confirm failed schedules apply exponential backoff.
- Force repeated schedule failures and verify schedule enters connector dead-letter and is disabled.
- Confirm dead-letter records appear in `GET /connectors/dead-letter`.
- Requeue dead-letter schedule via `POST /connectors/dead-letter/requeue` and verify schedule is enabled again.
- Trigger webhook sync via `POST /connectors/{connector_name}/webhook` and confirm event + run result.
- If connector auth secret is configured, verify webhook rejects invalid secret and accepts valid secret.

## Phase 11 validation checklist

- Create connector policy with strict `rate_limit_per_hour` and verify excess sync attempts are rejected.
- Create connector policy with `max_concurrent_runs=1` and verify concurrency guardrails return rejection when exceeded.
- Verify policy changes are visible from `GET /connectors/policies`.
- Verify policy-driven rejections are written to `GET /connectors/audit` with `action=sync.rejected_policy`.
- Verify successful and failed sync flows produce audit records (`sync.started`, `sync.completed`, `sync.failed`).
- Verify webhook secret rejection also appears in connector audit (`action=webhook.rejected`).

## Phase 12 validation checklist

- Run connector simulation and verify it reports `candidate_new_items` vs `candidate_existing_items` without ingesting data.
- Verify simulation runs are listed in `GET /connectors/simulations` with status and sample refs.
- Re-run simulation after ingesting same source and verify existing-item estimates increase.
- Generate policy recommendation from recent runs and verify response includes suggested rate, concurrency, and interval.
- Confirm simulation and recommendation actions are present in connector audit logs.
- Verify no regressions in Phase 11 policy enforcement and audit endpoints.

## Phase 13 validation checklist

- Run `policy/auto-apply` in dry-run mode and verify no policy revision is created.
- Run `policy/auto-apply` in apply mode and verify revision is recorded and policy values are updated.
- Validate policy revisions are visible from `GET /connectors/policy/revisions`.
- Trigger `policy/guardrail-check` with low threshold to force breach and verify optional auto rollback behavior.
- Validate rollback endpoint restores previous policy settings from latest applied revision.
- Verify audit trail includes `policy.auto_apply.*`, `policy.guardrail_check`, and `policy.rollback` events.

## Phase 14 validation checklist

- Set priorities and groups on multiple connectors and verify ordering in orchestration run.
- Pause one connector group and verify orchestration excludes paused group connectors.
- Resume paused group and verify connectors become eligible again.
- Run global orchestration and verify per-connector outcomes (`completed`, `failed`, `rejected`) are captured.
- Check connector health dashboard and verify health score reflects success rate, latency, failure streak, and dead-letter volume.
- Confirm health and orchestration actions are visible through connector audit logs.

## Phase 15 validation checklist

- Run SLA evaluation with strict thresholds and verify alerts are created.
- Validate auto-remediation can pause unstable connectors when enabled.
- Verify SLA alerts list endpoint returns open alerts with metric/threshold details.
- Resolve one alert and confirm its status changes from `open` to `resolved`.
- Trigger manual remediation (`pause_connector` and `reduce_policy_limits`) and validate side effects.
- Confirm remediation history and SLA actions are visible in connector audit logs.

## Phase 16 validation checklist

- Configure notification channels (connector-scoped and global `*`) and verify they are listed.
- Send test notifications and verify delivery log rows are created.
- Trigger SLA evaluation with breaches and verify alert-driven notification delivery entries are created.
- Configure escalation policy and run escalation evaluation to trigger escalation remediation.
- Verify escalation-triggered notifications are logged when notification channel is linked.
- Confirm notification and escalation actions appear in connector audit logs.

## Phase 8 step-by-step test examples with expected results

1. Prepare a JSON seed file (example `F:/tmp/blueprint_seed.json`):

```json
[
  {
    "source_ref": "mail-001",
    "title": "IRS payment confirmation",
    "description": "tax receipt",
    "content": "IRS filing receipt for 2025 and W2 submission complete.",
    "taxonomy_path": "Personal/Important_Documents"
  },
  {
    "source_ref": "health-001",
    "title": "Lab result upload",
    "description": "blood panel",
    "content": "Lipid panel and diagnostic report uploaded from clinic.",
    "taxonomy_path": "Health/Lab_Work"
  }
]
```

2. Run connector:
- `POST /connectors/local_json/sync` with path above.

Expected:
- `status=completed`
- `fetched_count=2`
- `ingested_count` close to 2

3. Process jobs:
- `POST /jobs/process?limit=300`

Expected:
- `succeeded > 0`

4. Check connector state:
- `GET /connectors/status`

Expected:
- entry for `local_json`
- `status=idle`
- `total_synced_items >= ingested_count`
- non-null checkpoint

5. Test hybrid assist outcome:
- inspect an ingested item with `GET /items/{item_id}/tags` and `GET /items/{item_id}/classification`

Expected:
- tag/class sources may appear as `model_assist_v1` where assist lifted confidence
- otherwise remain `rule_*`

6. Test feedback export:
- run manual override endpoints for tag/classification
- call `GET /feedback/export`

Expected:
- records include `feedback_type` (`tag_override` / `classification_override`)
- `before_value`, `after_value`, and `notes` populated

## Phase 9 step-by-step test examples with expected results

1. Configure connector auth metadata:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/auth" ^
  -H "Content-Type: application/json" ^
  -d "{\"auth_type\":\"api_key\",\"secret_value\":\"phase9-demo-secret\",\"secret_ref\":\"local-dev\"}"
```

Expected:
- message confirms credential saved
- connector is `local_json`
- status is `configured`

2. Verify credentials are masked:

```bash
curl "http://localhost:8100/connectors/auth"
```

Expected:
- `local_json` record exists
- `masked_secret` ends with last 4 chars (`cret`)
- raw secret value is never returned

3. Create schedule:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/schedule" ^
  -H "Content-Type: application/json" ^
  -d "{\"enabled\":true,\"interval_minutes\":1,\"limit\":500,\"run_immediately\":true,\"config\":{\"path\":\"F:/tmp/blueprint_seed.json\"}}"
```

Expected:
- response confirms schedule saved
- `next_run_at` is present and near current UTC time

4. List schedules:

```bash
curl "http://localhost:8100/connectors/schedules"
```

Expected:
- `local_json` appears
- schedule enabled
- interval is `1` minute

5. Run due schedules:

```bash
curl -X POST "http://localhost:8100/connectors/schedules/run-due?max_runs=10"
```

Expected:
- `triggered >= 1`
- result includes `connector_name=local_json`
- first run generally shows non-zero `fetched_count` (if seed file exists)

6. Re-run due schedules after initial sync:

```bash
curl -X POST "http://localhost:8100/connectors/schedules/run-due?max_runs=10"
```

Expected:
- if no new updates in source, `ingested_count` should be `0` (or lower than first run)
- confirms checkpoint-aware incremental sync behavior

7. Verify checkpoint advancement:

```bash
curl "http://localhost:8100/connectors/status"
```

Expected:
- `local_json` checkpoint is non-null
- `last_run_at` is updated after scheduled runs
- `status` returns to `idle` when run completes

## Phase 10 step-by-step test examples with expected results

1. Create a schedule with strict retry policy and invalid path:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/schedule" ^
  -H "Content-Type: application/json" ^
  -d "{\"enabled\":true,\"interval_minutes\":1,\"max_attempts\":2,\"limit\":100,\"run_immediately\":true,\"config\":{\"path\":\"F:/tmp/not_exists_phase10.json\"}}"
```

Expected:
- schedule is saved with `max_attempts=2`
- next run is immediate

2. Execute due schedules first time (failure #1):

```bash
curl -X POST "http://localhost:8100/connectors/schedules/run-due?max_runs=10"
```

Expected:
- `triggered >= 1`
- result for `local_json` has `status=failed`
- no dead-letter yet (`dead_lettered=0`)
- schedule remains enabled and next run is pushed forward (backoff)

3. Execute due schedules until second failure:

```bash
curl -X POST "http://localhost:8100/connectors/schedules/run-due?max_runs=10"
```

Expected:
- after reaching `max_attempts`, `dead_lettered >= 1`
- schedule is disabled
- `next_run_at` becomes `null`

4. Verify connector dead-letter list:

```bash
curl "http://localhost:8100/connectors/dead-letter?status=open&limit=50"
```

Expected:
- record exists for `local_json`
- `attempts` reflects max failure count
- `status=open`
- `last_error` includes path/config failure details

5. Requeue connector dead-letter:

```bash
curl -X POST "http://localhost:8100/connectors/dead-letter/requeue" ^
  -H "Content-Type: application/json" ^
  -d "{\"dead_letter_ids\":[],\"limit\":20}"
```

Expected:
- `requeued >= 1`
- returns dead-letter IDs that were requeued

6. Confirm schedule is re-enabled after requeue:

```bash
curl "http://localhost:8100/connectors/schedules"
```

Expected:
- schedule for `local_json` is `enabled=true`
- `failure_count=0`
- `next_run_at` is set near current time

7. Set connector auth secret for webhook test:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/auth" ^
  -H "Content-Type: application/json" ^
  -d "{\"auth_type\":\"api_key\",\"secret_value\":\"phase10-secret\",\"secret_ref\":\"webhook-test\"}"
```

Expected:
- credential saved, configured

8. Trigger webhook with wrong secret:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/webhook" ^
  -H "Content-Type: application/json" ^
  -d "{\"secret\":\"wrong-secret\",\"event_type\":\"file.changed\",\"config\":{\"path\":\"F:/tmp/blueprint_seed.json\"},\"limit\":100,\"use_checkpoint\":true}"
```

Expected:
- HTTP 400 error with invalid webhook secret message

9. Trigger webhook with correct secret:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/webhook" ^
  -H "Content-Type: application/json" ^
  -d "{\"secret\":\"phase10-secret\",\"event_type\":\"file.changed\",\"config\":{\"path\":\"F:/tmp/blueprint_seed.json\"},\"limit\":100,\"use_checkpoint\":true}"
```

Expected:
- response includes `event_id`, `run_id`, and status (`completed` or `failed` depending on source file)
- confirms webhook path can trigger connector sync

## Phase 11 step-by-step test examples with expected results

1. Set strict connector policy:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/policy" ^
  -H "Content-Type: application/json" ^
  -d "{\"enabled\":true,\"rate_limit_per_hour\":2,\"max_concurrent_runs\":1}"
```

Expected:
- policy saved message
- `rate_limit_per_hour=2`
- `max_concurrent_runs=1`

2. Verify policy list:

```bash
curl "http://localhost:8100/connectors/policies"
```

Expected:
- `local_json` policy exists with configured values

3. Run manual sync twice (within the same hour):

```bash
curl -X POST "http://localhost:8100/connectors/local_json/sync" ^
  -H "Content-Type: application/json" ^
  -d "{\"config\":{\"path\":\"F:/tmp/blueprint_seed.json\"},\"limit\":100,\"use_checkpoint\":false}"
```

Run the same command a second time.

Expected:
- first and second attempts typically proceed (completed/failed depending on file validity)
- both create connector run/audit entries

4. Run manual sync third time (should hit rate limit):

```bash
curl -X POST "http://localhost:8100/connectors/local_json/sync" ^
  -H "Content-Type: application/json" ^
  -d "{\"config\":{\"path\":\"F:/tmp/blueprint_seed.json\"},\"limit\":100,\"use_checkpoint\":false}"
```

Expected:
- response `status=rejected`
- `details` indicates rate limit reached
- `run_id` is still present (rejected run is recorded)

5. Inspect audit logs for policy rejections:

```bash
curl "http://localhost:8100/connectors/audit?connector_name=local_json&action=sync.rejected_policy&limit=50"
```

Expected:
- at least one record
- `result=blocked`
- `details` includes rate or concurrency reason

6. Inspect all recent sync audit logs:

```bash
curl "http://localhost:8100/connectors/audit?connector_name=local_json&limit=100"
```

Expected:
- includes a sequence such as:
  - `sync.started`
  - `sync.completed` or `sync.failed`
  - `sync.rejected_policy` when blocked

7. Webhook rejection audit check (optional):

```bash
curl -X POST "http://localhost:8100/connectors/local_json/webhook" ^
  -H "Content-Type: application/json" ^
  -d "{\"secret\":\"wrong-secret\",\"event_type\":\"file.changed\",\"config\":{\"path\":\"F:/tmp/blueprint_seed.json\"},\"limit\":100,\"use_checkpoint\":true}"
```

Then query:

```bash
curl "http://localhost:8100/connectors/audit?connector_name=local_json&action=webhook.rejected&limit=20"
```

Expected:
- webhook call returns 400 invalid secret
- audit list contains `webhook.rejected` with `result=blocked`

## Phase 12 step-by-step test examples with expected results

1. Prepare or reuse a seed file:

```json
[
  {
    "source_ref": "p12-001",
    "title": "Utility payment receipt",
    "description": "monthly utilities",
    "content": "Electricity payment processed for February.",
    "taxonomy_path": "Personal/Bills",
    "updated_at": "2026-02-20T11:00:00"
  },
  {
    "source_ref": "p12-002",
    "title": "Clinic reminder",
    "description": "appointment note",
    "content": "Follow-up clinic appointment scheduled.",
    "taxonomy_path": "Health/Doctors",
    "updated_at": "2026-02-20T11:05:00"
  }
]
```

2. Run dry-run simulation (no ingestion):

```bash
curl -X POST "http://localhost:8100/connectors/local_json/simulate" ^
  -H "Content-Type: application/json" ^
  -d "{\"config\":{\"path\":\"F:/tmp/blueprint_seed.json\"},\"limit\":500,\"use_checkpoint\":false}"
```

Expected:
- `status=completed`
- `fetched_count` close to row count in file
- `candidate_new_items` likely > 0 for first run
- returns `sample_new_refs` (up to 10 refs)

3. Verify simulation list:

```bash
curl "http://localhost:8100/connectors/simulations?connector_name=local_json&limit=20"
```

Expected:
- recent simulation record present
- includes simulation ID, status, fetched/new/existing counts, and sample refs

4. Perform actual sync for same source:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/sync" ^
  -H "Content-Type: application/json" ^
  -d "{\"config\":{\"path\":\"F:/tmp/blueprint_seed.json\"},\"limit\":500,\"use_checkpoint\":false}"
```

Expected:
- sync runs (subject to policy limits)
- items are ingested/updated as normal

5. Re-run simulation after sync:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/simulate" ^
  -H "Content-Type: application/json" ^
  -d "{\"config\":{\"path\":\"F:/tmp/blueprint_seed.json\"},\"limit\":500,\"use_checkpoint\":false}"
```

Expected:
- `candidate_existing_items` increases versus first simulation
- `candidate_new_items` drops for unchanged dataset

6. Generate policy recommendation:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/policy/recommend"
```

Expected:
- returns:
  - `recommended_rate_limit_per_hour`
  - `recommended_max_concurrent_runs`
  - `recommended_interval_minutes`
  - `reason`
- recommendation changes with observed run/failure history over time

7. Verify audit events for simulation + recommendation:

```bash
curl "http://localhost:8100/connectors/audit?connector_name=local_json&limit=100"
```

Expected:
- includes actions such as:
  - `simulation.started`
  - `simulation.completed` or `simulation.failed`
  - `policy.recommendation.generated`

## Phase 13 step-by-step test examples with expected results

1. Dry-run auto-apply recommendation:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/policy/auto-apply" ^
  -H "Content-Type: application/json" ^
  -d "{\"enabled\":true,\"dry_run\":true,\"min_rate_limit_per_hour\":20,\"max_rate_limit_per_hour\":200,\"max_concurrent_runs_cap\":2}"
```

Expected:
- `applied=false`
- `revision_id=null`
- returns previous and proposed new values
- no persisted revision yet

2. Verify revision list is unchanged after dry-run:

```bash
curl "http://localhost:8100/connectors/policy/revisions?connector_name=local_json&limit=20"
```

Expected:
- no new revision from dry-run call

3. Apply auto-policy for real:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/policy/auto-apply" ^
  -H "Content-Type: application/json" ^
  -d "{\"enabled\":true,\"dry_run\":false,\"min_rate_limit_per_hour\":20,\"max_rate_limit_per_hour\":200,\"max_concurrent_runs_cap\":2}"
```

Expected:
- `applied=true`
- `revision_id` is non-null
- policy values are updated to clamped recommendation

4. Verify policy and revision history:

```bash
curl "http://localhost:8100/connectors/policies"
```

```bash
curl "http://localhost:8100/connectors/policy/revisions?connector_name=local_json&limit=20"
```

Expected:
- policy reflects new applied values
- revision row shows `previous_*` and `new_*` values with `status=applied`

5. Trigger guardrail check (force breach for testing):

```bash
curl -X POST "http://localhost:8100/connectors/local_json/policy/guardrail-check" ^
  -H "Content-Type: application/json" ^
  -d "{\"lookback_runs\":20,\"failure_ratio_threshold\":0.0,\"auto_rollback\":true}"
```

Expected:
- `breached=true` (threshold 0 forces breach when any failures/rejections exist)
- if applied revision exists, `rolled_back=true`
- message indicates rollback result

6. Manual rollback endpoint test:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/policy/rollback"
```

Expected:
- if no applied revisions left: `rolled_back=false` with explanatory message
- otherwise: `rolled_back=true`, returns rolled-back `revision_id`

7. Verify audit trail for Phase 13 actions:

```bash
curl "http://localhost:8100/connectors/audit?connector_name=local_json&limit=100"
```

Expected:
- contains actions:
  - `policy.auto_apply.dry_run`
  - `policy.auto_apply.applied`
  - `policy.guardrail_check`
  - `policy.rollback` (if rollback occurred)

## Phase 14 step-by-step test examples with expected results

1. Configure schedule metadata (priority/group) for connectors:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/schedule" ^
  -H "Content-Type: application/json" ^
  -d "{\"enabled\":true,\"interval_minutes\":5,\"priority\":10,\"group_name\":\"critical\",\"is_paused\":false,\"max_attempts\":3,\"limit\":200,\"run_immediately\":true,\"config\":{\"path\":\"F:/tmp/blueprint_seed.json\"}}"
```

```bash
curl -X POST "http://localhost:8100/connectors/local_csv/schedule" ^
  -H "Content-Type: application/json" ^
  -d "{\"enabled\":true,\"interval_minutes\":5,\"priority\":50,\"group_name\":\"standard\",\"is_paused\":false,\"max_attempts\":3,\"limit\":200,\"run_immediately\":true,\"config\":{\"path\":\"F:/tmp/blueprint_seed.csv\"}}"
```

Expected:
- schedules saved with requested priority/group values

2. Optional priority update endpoint test:

```bash
curl -X POST "http://localhost:8100/connectors/local_csv/priority" ^
  -H "Content-Type: application/json" ^
  -d "{\"priority\":80,\"group_name\":\"standard\",\"is_paused\":false}"
```

Expected:
- response confirms updated priority/group/pause state

3. Pause a connector group:

```bash
curl -X POST "http://localhost:8100/connectors/groups/standard/pause"
```

Expected:
- `paused=true`
- `updated_connectors` >= 1 when group contains schedules

4. Run orchestration pass:

```bash
curl -X POST "http://localhost:8100/connectors/orchestrate/run" ^
  -H "Content-Type: application/json" ^
  -d "{\"connector_names\":[],\"max_connectors\":20,\"use_checkpoint\":true}"
```

Expected:
- response includes `orchestration_run_id`
- only non-paused connectors are executed
- item list includes per-connector statuses and run IDs

5. Resume paused group:

```bash
curl -X POST "http://localhost:8100/connectors/groups/standard/resume"
```

Expected:
- `paused=false`
- connectors in group become active again

6. Re-run orchestration:

```bash
curl -X POST "http://localhost:8100/connectors/orchestrate/run" ^
  -H "Content-Type: application/json" ^
  -d "{\"connector_names\":[],\"max_connectors\":20,\"use_checkpoint\":true}"
```

Expected:
- now includes connectors from resumed group
- summary counters (`succeeded_connectors`, `failed_connectors`, `blocked_connectors`) update accordingly

7. Inspect connector health dashboard:

```bash
curl "http://localhost:8100/connectors/health?lookback_runs=50"
```

Expected:
- each connector includes:
  - `health_score` in `0..1`
  - `status` (`healthy` / `warning` / `critical`)
  - `success_rate`, `failure_streak`, `avg_latency_ms`, `dead_letter_open_count`
  - schedule metadata (`priority`, `group_name`, `is_paused`) when configured

8. Validate audit trail for orchestration/governance actions:

```bash
curl "http://localhost:8100/connectors/audit?limit=200"
```

Expected:
- contains records for:
  - `schedule.priority.updated`
  - `schedule.group.pause` / `schedule.group.resume`
  - `orchestration.run.completed`
- plus per-connector sync events from orchestration runs

## Phase 15 step-by-step test examples with expected results

1. Run SLA evaluation with strict thresholds:

```bash
curl -X POST "http://localhost:8100/connectors/sla/evaluate" ^
  -H "Content-Type: application/json" ^
  -d "{\"min_health_score\":0.95,\"max_failure_streak\":0,\"max_dead_letter_open\":0,\"auto_remediate\":true}"
```

Expected:
- `evaluated_connectors` equals number of supported connectors
- `alerts_created` may be > 0 with strict thresholds
- `remediation_actions` may be > 0 when auto-remediation triggers

2. List open SLA alerts:

```bash
curl "http://localhost:8100/connectors/sla/alerts?status=open&limit=100"
```

Expected:
- each record includes `metric_name`, `metric_value`, `threshold_value`, `severity`, and `status=open`

3. Check remediation actions created by auto-remediation:

```bash
curl "http://localhost:8100/connectors/remediation/actions?limit=100"
```

Expected:
- records may include `pause_connector` with `related_alert_id` set

4. Trigger manual remediation: reduce policy limits:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/remediation" ^
  -H "Content-Type: application/json" ^
  -d "{\"action_type\":\"reduce_policy_limits\",\"reason\":\"manual throttle test\"}"
```

Expected:
- response includes non-null `action_id`
- status is `completed`
- policy for connector is reduced (rate/concurrency tightened)

5. Trigger manual remediation: pause connector:

```bash
curl -X POST "http://localhost:8100/connectors/local_csv/remediation" ^
  -H "Content-Type: application/json" ^
  -d "{\"action_type\":\"pause_connector\",\"reason\":\"manual maintenance pause\"}"
```

Expected:
- status is `completed`
- connector schedule shows `is_paused=true`

6. Resolve one open alert:

```bash
curl -X POST "http://localhost:8100/connectors/sla/alerts/<alert_id>/resolve"
```

Expected:
- returns `status=resolved`
- resolved alert no longer appears in `status=open` list

7. Verify SLA/remediation audit events:

```bash
curl "http://localhost:8100/connectors/audit?limit=200"
```

Expected:
- contains events such as:
  - `sla.alert.created`
  - `sla.remediation.pause_connector`
  - `sla.remediation.reduce_policy_limits`
  - `sla.alert.resolved`

## Phase 16 step-by-step test examples with expected results

1. Create a global notification channel (`*` scope):

```bash
curl -X POST "http://localhost:8100/connectors/notifications/channels" ^
  -H "Content-Type: application/json" ^
  -d "{\"connector_name\":\"*\",\"channel_type\":\"webhook\",\"target\":\"https://example.invalid/alerts\",\"secret\":\"demo-secret\",\"min_severity\":\"warning\",\"is_enabled\":true}"
```

Expected:
- channel saved response with channel ID
- message confirms save

2. Create connector-specific notification channel:

```bash
curl -X POST "http://localhost:8100/connectors/notifications/channels" ^
  -H "Content-Type: application/json" ^
  -d "{\"connector_name\":\"local_json\",\"channel_type\":\"email\",\"target\":\"ops-local-json@example.com\",\"secret\":null,\"min_severity\":\"critical\",\"is_enabled\":true}"
```

Expected:
- second channel saved
- connector-specific filtering applies for local_json

3. List notification channels:

```bash
curl "http://localhost:8100/connectors/notifications/channels?limit=100"
```

Expected:
- both channels are listed
- includes connector name, target, type, enabled flag, severity floor

4. Send test notification:

```bash
curl -X POST "http://localhost:8100/connectors/notifications/test" ^
  -H "Content-Type: application/json" ^
  -d "{\"connector_name\":\"local_json\",\"severity\":\"critical\",\"message\":\"phase16 test notification\"}"
```

Expected:
- `attempted_channels >= 1`
- `sent >= 1` (simulated delivery path)

5. Verify notification delivery logs:

```bash
curl "http://localhost:8100/connectors/notifications/deliveries?connector_name=local_json&limit=100"
```

Expected:
- new delivery records appear
- includes channel, target, status, payload preview

6. Configure escalation policy for connector:

```bash
curl -X POST "http://localhost:8100/connectors/local_json/escalation" ^
  -H "Content-Type: application/json" ^
  -d "{\"enabled\":true,\"open_alert_count_threshold\":1,\"action_type\":\"reduce_policy_limits\",\"notify_channel_id\":null}"
```

Expected:
- escalation policy saved for local_json

7. Force SLA alerts (strict threshold):

```bash
curl -X POST "http://localhost:8100/connectors/sla/evaluate" ^
  -H "Content-Type: application/json" ^
  -d "{\"min_health_score\":0.99,\"max_failure_streak\":0,\"max_dead_letter_open\":0,\"auto_remediate\":false}"
```

Expected:
- `alerts_created` may be non-zero
- no auto-remediation when disabled

8. Run escalation evaluation:

```bash
curl -X POST "http://localhost:8100/connectors/escalation/evaluate"
```

Expected:
- `escalations_triggered` increases when open alert threshold is reached
- remediation action (e.g. `reduce_policy_limits`) is recorded

9. Validate escalation policies list:

```bash
curl "http://localhost:8100/connectors/escalation/policies?limit=100"
```

Expected:
- policy row for local_json with threshold and action type

10. Validate audit log includes notification/escalation activity:

```bash
curl "http://localhost:8100/connectors/audit?connector_name=local_json&limit=200"
```

Expected:
- includes actions like:
  - `notification.channel.upserted`
  - `notification.test.sent`
  - `escalation.policy.upserted`
  - `escalation.triggered` (if threshold breached)

## Notes

- Current embedding provider is deterministic local hash embedding (`local-hash-v1`) for plumbing/testing.
- Current tagging provider is rules-first (`rule_engine_v1`) with confidence thresholds and review queue.
- Current classifier is rules-first (`rule_classifier_v1`) with fallback class `Unsorted/Needs_Review`.
- Current insight layer is deterministic rules-first (`insights_v1`) with evidence-backed summaries.
- Current proactive layer is deterministic rules-first (`phase6_proactive_v1`) for timeline and recommendations.
- Phase 7 adds reliability guardrails (`dead_letter`), observability (`api_metrics`), and evaluation tracking (`evaluation_runs`).
- Phase 8 adds connector sync framework, model-assist hybrid scoring, feedback dataset export, and embedding migration endpoint.
- Phase 9 adds connector auth metadata, schedule-driven connector orchestration, and checkpoint-aware incremental scheduled sync.
- Phase 10 adds connector schedule retry backoff, connector dead-letter lifecycle, and webhook-triggered connector sync with secret validation.
- Phase 11 adds connector governance policies (rate + concurrency limits) and connector audit trails for sync/webhook/policy events.
- Phase 12 adds non-destructive connector simulation previews and data-driven policy recommendation generation.
- Phase 13 adds guarded auto-policy application, policy revision history, and rollback/guardrail safety controls.
- Phase 14 adds multi-connector orchestration, group pause/resume controls, priority routing, and connector health score dashboards.
- Phase 15 adds SLA alerting, automated remediation, manual remediation controls, and remediation history tracking.
- Phase 16 adds notification channels, delivery logs, and escalation policies for SLA-driven operational response.
- Swap `app/services/embedding_service.py` for provider-backed semantic embeddings when moving beyond local testing.
