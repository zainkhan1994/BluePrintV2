# API Test Checklist (Swagger `/docs`)

Use this file while testing in `http://localhost:8100/docs`.

- Mark each item as done: `[x]`
- Record status code and notes in the tables
- Keep dynamic IDs in the scratch section

---

## Scratch IDs

- `item_id`:
- `insight_id`:
- `signal_id`:
- `alert_id`:

---

## A) Base System

- [ ] `GET /health`
- [ ] `GET /`
- [ ] `GET /ready`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/health` |  |  |  |
| `/` |  |  |  |
| `/ready` |  |  |  |

---

## B) Core Data Pipeline

- [ ] `POST /items` (run 2-3 times)
- [ ] `POST /items/bulk` (optional)
- [ ] `GET /items/{item_id}`
- [ ] `POST /jobs/process`
- [ ] `GET /jobs`
- [ ] `POST /index/rebuild`
- [ ] `POST /index/reembed` (optional)

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/items` |  |  |  |
| `/items/bulk` |  |  |  |
| `/items/{item_id}` |  |  |  |
| `/jobs/process` |  |  |  |
| `/jobs` |  |  |  |
| `/index/rebuild` |  |  |  |
| `/index/reembed` |  |  |  |

---

## C) Search and Retrieval (Customer Missing Part)

- [ ] `POST /search/semantic`
- [ ] `POST /search/retrieve`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/search/semantic` |  |  |  |
| `/search/retrieve` |  |  |  |

---

## D) Automated Tagging (Customer Missing Part)

- [ ] `POST /tagging/run`
- [ ] `GET /items/{item_id}/tags`
- [ ] `GET /tags/needs-review`
- [ ] `POST /items/{item_id}/tags/override`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/tagging/run` |  |  |  |
| `/items/{item_id}/tags` |  |  |  |
| `/tags/needs-review` |  |  |  |
| `/items/{item_id}/tags/override` |  |  |  |

---

## E) Automated Classification (Customer Missing Part)

- [ ] `POST /classification/run`
- [ ] `GET /items/{item_id}/classification`
- [ ] `GET /classification/needs-review`
- [ ] `POST /items/{item_id}/classification/override`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/classification/run` |  |  |  |
| `/items/{item_id}/classification` |  |  |  |
| `/classification/needs-review` |  |  |  |
| `/items/{item_id}/classification/override` |  |  |  |

---

## F) Insights, Summaries, Proactive

- [ ] `POST /insights/generate`
- [ ] `GET /insights`
- [ ] `GET /insights/{insight_id}`
- [ ] `POST /summaries/item/{item_id}`
- [ ] `POST /summaries/window`
- [ ] `POST /briefs/cross-domain`
- [ ] `POST /proactive/run`
- [ ] `POST /timeline/activity`
- [ ] `GET /proactive/signals`
- [ ] `POST /proactive/signals/{signal_id}/resolve`
- [ ] `POST /assistant/digest`
- [ ] `POST /assistant/recommendations`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/insights/generate` |  |  |  |
| `/insights` |  |  |  |
| `/insights/{insight_id}` |  |  |  |
| `/summaries/item/{item_id}` |  |  |  |
| `/summaries/window` |  |  |  |
| `/briefs/cross-domain` |  |  |  |
| `/proactive/run` |  |  |  |
| `/timeline/activity` |  |  |  |
| `/proactive/signals` |  |  |  |
| `/proactive/signals/{signal_id}/resolve` |  |  |  |
| `/assistant/digest` |  |  |  |
| `/assistant/recommendations` |  |  |  |

---

## G) Metrics and Reliability

- [ ] `GET /metrics/summary`
- [ ] `GET /metrics/jobs`
- [ ] `POST /evaluation/run`
- [ ] `GET /evaluation/latest`
- [ ] `GET /maintenance/dead-letter`
- [ ] `POST /maintenance/dead-letter/requeue`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/metrics/summary` |  |  |  |
| `/metrics/jobs` |  |  |  |
| `/evaluation/run` |  |  |  |
| `/evaluation/latest` |  |  |  |
| `/maintenance/dead-letter` |  |  |  |
| `/maintenance/dead-letter/requeue` |  |  |  |

---

## H) Connectors Core

- [ ] `POST /connectors/{connector_name}/sync`
- [ ] `GET /connectors/status`
- [ ] `POST /connectors/{connector_name}/auth`
- [ ] `GET /connectors/auth`
- [ ] `POST /connectors/{connector_name}/schedule`
- [ ] `GET /connectors/schedules`
- [ ] `POST /connectors/schedules/run-due`
- [ ] `POST /connectors/{connector_name}/webhook`
- [ ] `GET /connectors/dead-letter`
- [ ] `POST /connectors/dead-letter/requeue`
- [ ] `GET /connectors/audit`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/connectors/{connector_name}/sync` |  |  |  |
| `/connectors/status` |  |  |  |
| `/connectors/{connector_name}/auth` |  |  |  |
| `/connectors/auth` |  |  |  |
| `/connectors/{connector_name}/schedule` |  |  |  |
| `/connectors/schedules` |  |  |  |
| `/connectors/schedules/run-due` |  |  |  |
| `/connectors/{connector_name}/webhook` |  |  |  |
| `/connectors/dead-letter` |  |  |  |
| `/connectors/dead-letter/requeue` |  |  |  |
| `/connectors/audit` |  |  |  |

---

## I) Priority, Group Control, Orchestration, Health

- [ ] `POST /connectors/{connector_name}/policy`
- [ ] `GET /connectors/policies`
- [ ] `POST /connectors/{connector_name}/priority`
- [ ] `POST /connectors/groups/{group_name}/pause`
- [ ] `POST /connectors/groups/{group_name}/resume`
- [ ] `POST /connectors/orchestrate/run`
- [ ] `GET /connectors/health`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/connectors/{connector_name}/policy` |  |  |  |
| `/connectors/policies` |  |  |  |
| `/connectors/{connector_name}/priority` |  |  |  |
| `/connectors/groups/{group_name}/pause` |  |  |  |
| `/connectors/groups/{group_name}/resume` |  |  |  |
| `/connectors/orchestrate/run` |  |  |  |
| `/connectors/health` |  |  |  |

---

## J) Simulation and Policy Automation

- [ ] `POST /connectors/{connector_name}/simulate`
- [ ] `GET /connectors/simulations`
- [ ] `POST /connectors/{connector_name}/policy/recommend`
- [ ] `POST /connectors/{connector_name}/policy/auto-apply`
- [ ] `GET /connectors/policy/revisions`
- [ ] `POST /connectors/{connector_name}/policy/rollback`
- [ ] `POST /connectors/{connector_name}/policy/guardrail-check`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/connectors/{connector_name}/simulate` |  |  |  |
| `/connectors/simulations` |  |  |  |
| `/connectors/{connector_name}/policy/recommend` |  |  |  |
| `/connectors/{connector_name}/policy/auto-apply` |  |  |  |
| `/connectors/policy/revisions` |  |  |  |
| `/connectors/{connector_name}/policy/rollback` |  |  |  |
| `/connectors/{connector_name}/policy/guardrail-check` |  |  |  |

---

## K) SLA and Remediation

- [ ] `POST /connectors/sla/evaluate`
- [ ] `GET /connectors/sla/alerts`
- [ ] `POST /connectors/sla/alerts/{alert_id}/resolve`
- [ ] `POST /connectors/{connector_name}/remediation`
- [ ] `GET /connectors/remediation/actions`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/connectors/sla/evaluate` |  |  |  |
| `/connectors/sla/alerts` |  |  |  |
| `/connectors/sla/alerts/{alert_id}/resolve` |  |  |  |
| `/connectors/{connector_name}/remediation` |  |  |  |
| `/connectors/remediation/actions` |  |  |  |

---

## L) Notifications and Escalation

- [ ] `POST /connectors/notifications/channels`
- [ ] `GET /connectors/notifications/channels`
- [ ] `POST /connectors/notifications/test`
- [ ] `GET /connectors/notifications/deliveries`
- [ ] `POST /connectors/{connector_name}/escalation`
- [ ] `GET /connectors/escalation/policies`
- [ ] `POST /connectors/escalation/evaluate`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/connectors/notifications/channels` |  |  |  |
| `/connectors/notifications/channels` (GET) |  |  |  |
| `/connectors/notifications/test` |  |  |  |
| `/connectors/notifications/deliveries` |  |  |  |
| `/connectors/{connector_name}/escalation` |  |  |  |
| `/connectors/escalation/policies` |  |  |  |
| `/connectors/escalation/evaluate` |  |  |  |

---

## M) Feedback Export

- [ ] `GET /feedback/export`

| Endpoint | Status Code | Pass/Fail | Notes |
|---|---:|---|---|
| `/feedback/export` |  |  |  |

---

## Final Summary

- Total endpoints tested:
- Passed:
- Failed:
- Blocked / skipped:
- Final overall status:

