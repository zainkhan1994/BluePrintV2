from __future__ import annotations

import csv
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import (
    ConnectorAuditLog,
    ConnectorCredential,
    ConnectorHealthSnapshot,
    ConnectorOrchestrationRun,
    ConnectorOrchestrationRunItem,
    ConnectorPolicy,
    ConnectorPolicyRevision,
    ConnectorEscalationPolicy,
    ConnectorNotificationChannel,
    ConnectorNotificationDelivery,
    ConnectorRemediationAction,
    ConnectorRun,
    ConnectorSchedule,
    ConnectorScheduleDeadLetter,
    ConnectorSlaAlert,
    ConnectorSimulationRun,
    ConnectorState,
    ConnectorWebhookEvent,
    Item,
)
from app.schemas import (
    ConnectorAuditRecord,
    ConnectorPolicyRecord,
    ConnectorPolicyRevisionRecord,
    ConnectorDeadLetterRecord,
    ConnectorCredentialRecord,
    ConnectorScheduleRecord,
    ConnectorSimulationRecord,
    ConnectorSimulationResponse,
    ConnectorPolicyRecommendationResponse,
    ConnectorPolicyAutoApplyResponse,
    ConnectorOrchestrationItemRecord,
    ConnectorOrchestrationRunResponse,
    ConnectorHealthRecord,
    ConnectorRemediationRecord,
    ConnectorRemediationTriggerResponse,
    ConnectorEscalationPolicyRecord,
    ConnectorNotificationChannelRecord,
    ConnectorNotificationDeliveryRecord,
    ConnectorNotificationTestResponse,
    ConnectorEscalationEvaluateResponse,
    ConnectorSlaAlertRecord,
    ConnectorSlaEvaluationResponse,
    ConnectorWebhookTriggerResponse,
    ConnectorScheduleRunResponse,
    ConnectorStateRecord,
    ConnectorSyncResponse,
    ItemCreate,
)
from app.services.ingestion import ingest_item


SUPPORTED_CONNECTORS = {"local_json", "local_csv", "notes_dir"}
MAX_BACKOFF_MINUTES = 24 * 60
SEVERITY_ORDER = {"info": 0, "warning": 1, "critical": 2}


def _get_or_create_state(db: Session, connector_name: str) -> ConnectorState:
    state = db.execute(
        select(ConnectorState).where(ConnectorState.connector_name == connector_name)
    ).scalar_one_or_none()
    if state:
        return state
    state = ConnectorState(connector_name=connector_name, status="idle")
    db.add(state)
    db.commit()
    db.refresh(state)
    return state


def _get_or_create_policy(db: Session, connector_name: str) -> ConnectorPolicy:
    policy = db.execute(
        select(ConnectorPolicy).where(ConnectorPolicy.connector_name == connector_name)
    ).scalar_one_or_none()
    if policy:
        return policy
    policy = ConnectorPolicy(connector_name=connector_name, enabled=True, rate_limit_per_hour=120, max_concurrent_runs=1)
    db.add(policy)
    db.commit()
    db.refresh(policy)
    return policy


def _log_audit(
    db: Session,
    connector_name: str,
    action: str,
    result: str,
    details: str | None = None,
    run_id: int | None = None,
) -> None:
    row = ConnectorAuditLog(
        connector_name=connector_name,
        action=action,
        result=result,
        details=details,
        run_id=run_id,
    )
    db.add(row)
    db.commit()


def _count_recent_runs(db: Session, connector_name: str, hours: int = 1) -> int:
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    rows = db.execute(
        select(ConnectorRun.id)
        .where(ConnectorRun.connector_name == connector_name)
        .where(ConnectorRun.created_at >= cutoff)
    ).all()
    return len(rows)


def _count_active_runs(db: Session, connector_name: str) -> int:
    rows = db.execute(
        select(ConnectorRun.id)
        .where(ConnectorRun.connector_name == connector_name)
        .where(ConnectorRun.status == "running")
    ).all()
    return len(rows)


def _check_policy(db: Session, connector_name: str) -> tuple[bool, str | None]:
    policy = _get_or_create_policy(db, connector_name)
    if not policy.enabled:
        return False, "Connector policy disabled sync execution"

    active_runs = _count_active_runs(db, connector_name)
    if active_runs >= int(policy.max_concurrent_runs):
        return False, f"Concurrency limit reached ({active_runs}/{policy.max_concurrent_runs})"

    recent_runs = _count_recent_runs(db, connector_name, hours=1)
    if recent_runs >= int(policy.rate_limit_per_hour):
        return False, f"Rate limit reached ({recent_runs}/{policy.rate_limit_per_hour}) in last hour"

    return True, None


def _read_local_json(path: Path, limit: int) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        return []
    return [row for row in data[:limit] if isinstance(row, dict)]


def _read_local_csv(path: Path, limit: int) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append(dict(row))
    return rows


def _read_notes_dir(path: Path, limit: int, checkpoint_dt: datetime | None = None) -> list[dict]:
    rows: list[dict] = []
    for file in sorted(path.rglob("*")):
        if not file.is_file():
            continue
        if file.suffix.lower() not in {".txt", ".md"}:
            continue
        if checkpoint_dt is not None and datetime.utcfromtimestamp(file.stat().st_mtime) <= checkpoint_dt:
            continue
        rows.append(
            {
                "source_ref": str(file),
                "title": file.stem,
                "description": f"Imported from notes directory: {file.parent.name}",
                "content": file.read_text(encoding="utf-8", errors="ignore"),
                "taxonomy_path": "Unsorted/Imported_Notes",
            }
        )
        if len(rows) >= limit:
            break
    return rows


def _normalize_row(row: dict, connector_name: str, idx: int) -> ItemCreate:
    source_ref = str(row.get("source_ref") or f"{connector_name}-{idx}")
    title = str(row.get("title") or row.get("name") or f"{connector_name} item {idx}")
    description = str(row.get("description") or "")
    content = str(row.get("content") or row.get("text") or row.get("body") or "")
    taxonomy_path = str(row.get("taxonomy_path") or "Unsorted/Imported")
    if not content.strip():
        content = description or title

    return ItemCreate(
        source=connector_name,
        source_ref=source_ref,
        title=title[:500],
        description=description,
        content=content,
        taxonomy_path=taxonomy_path[:500],
        idempotency_key=f"{connector_name}:{source_ref}",
    )


def _parse_checkpoint(checkpoint_value: str | None) -> datetime | None:
    if not checkpoint_value:
        return None
    try:
        value = checkpoint_value.replace("Z", "+00:00")
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except Exception:
        return None


def _row_updated_at(row: dict) -> datetime | None:
    for field_name in ("updated_at", "modified_at", "timestamp"):
        value = row.get(field_name)
        if not value:
            continue
        try:
            parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            if parsed.tzinfo is not None:
                return parsed.astimezone(timezone.utc).replace(tzinfo=None)
            return parsed
        except Exception:
            continue
    return None


def _mask_secret(secret: str | None) -> str | None:
    if not secret:
        return None
    if len(secret) <= 4:
        return "*" * len(secret)
    return f"{'*' * (len(secret) - 4)}{secret[-4:]}"


def _next_backoff_minutes(failure_count: int, base_interval_minutes: int) -> int:
    multiplier = 2 ** max(0, failure_count - 1)
    return min(base_interval_minutes * multiplier, MAX_BACKOFF_MINUTES)


def _fetch_rows_for_connector(
    connector_name: str,
    config: dict,
    limit: int,
    checkpoint_dt: datetime | None,
) -> list[dict]:
    fetched_rows: list[dict] = []
    if connector_name in {"local_json", "local_csv"}:
        raw_path = config.get("path")
        if not raw_path:
            raise ValueError("Missing connector config path")
        path = Path(raw_path)
        if not path.exists():
            raise ValueError(f"Path does not exist: {path}")
        if checkpoint_dt is not None and datetime.utcfromtimestamp(path.stat().st_mtime) <= checkpoint_dt:
            fetched_rows = []
        elif connector_name == "local_json":
            fetched_rows = _read_local_json(path, limit)
        else:
            fetched_rows = _read_local_csv(path, limit)
        if checkpoint_dt is not None:
            filtered_rows: list[dict] = []
            for row in fetched_rows:
                updated_at = _row_updated_at(row)
                if updated_at is None or updated_at > checkpoint_dt:
                    filtered_rows.append(row)
            fetched_rows = filtered_rows
    elif connector_name == "notes_dir":
        raw_path = config.get("path")
        if not raw_path:
            raise ValueError("Missing connector config path")
        path = Path(raw_path)
        if not path.exists() or not path.is_dir():
            raise ValueError(f"Directory does not exist: {path}")
        fetched_rows = _read_notes_dir(path, limit, checkpoint_dt=checkpoint_dt)
    return fetched_rows


def run_connector_sync(
    db: Session,
    connector_name: str,
    config: dict,
    limit: int,
    use_checkpoint: bool = True,
) -> ConnectorSyncResponse:
    if connector_name not in SUPPORTED_CONNECTORS:
        raise ValueError(f"Unsupported connector: {connector_name}")

    allowed, block_reason = _check_policy(db, connector_name)
    if not allowed:
        rejected_run = ConnectorRun(
            connector_name=connector_name,
            status="rejected",
            fetched_count=0,
            ingested_count=0,
            error_count=1,
            run_details=block_reason,
            started_at=datetime.utcnow(),
            ended_at=datetime.utcnow(),
        )
        db.add(rejected_run)
        db.commit()
        db.refresh(rejected_run)
        _log_audit(
            db=db,
            connector_name=connector_name,
            action="sync.rejected_policy",
            result="blocked",
            details=block_reason,
            run_id=rejected_run.id,
        )
        return ConnectorSyncResponse(
            connector_name=connector_name,
            status="rejected",
            fetched_count=0,
            ingested_count=0,
            error_count=1,
            run_id=rejected_run.id,
            details=block_reason,
        )

    state = _get_or_create_state(db, connector_name)
    state.status = "running"
    state.last_error = None
    db.add(state)
    db.commit()

    run = ConnectorRun(
        connector_name=connector_name,
        status="running",
        fetched_count=0,
        ingested_count=0,
        error_count=0,
        run_details=None,
        started_at=datetime.utcnow(),
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    _log_audit(
        db=db,
        connector_name=connector_name,
        action="sync.started",
        result="ok",
        details=f"limit={limit}, use_checkpoint={use_checkpoint}",
        run_id=run.id,
    )

    fetched_rows: list[dict] = []
    checkpoint_dt = _parse_checkpoint(state.checkpoint) if use_checkpoint else None
    try:
        fetched_rows = _fetch_rows_for_connector(
            connector_name=connector_name,
            config=config,
            limit=limit,
            checkpoint_dt=checkpoint_dt,
        )

        ingested = 0
        errors = 0
        for idx, row in enumerate(fetched_rows):
            try:
                payload = _normalize_row(row, connector_name, idx)
                ingest_item(db, payload)
                ingested += 1
            except Exception:
                errors += 1

        run.status = "completed"
        run.fetched_count = len(fetched_rows)
        run.ingested_count = ingested
        run.error_count = errors
        run.run_details = f"connector={connector_name}, limit={limit}, use_checkpoint={use_checkpoint}"
        run.ended_at = datetime.utcnow()
        db.add(run)

        state.status = "idle"
        state.last_run_at = datetime.utcnow()
        state.total_synced_items = int(state.total_synced_items or 0) + ingested
        state.checkpoint = datetime.utcnow().isoformat()
        db.add(state)
        db.commit()
        _log_audit(
            db=db,
            connector_name=connector_name,
            action="sync.completed",
            result="ok",
            details=run.run_details,
            run_id=run.id,
        )
    except Exception as exc:
        run.status = "failed"
        run.error_count = run.error_count + 1
        run.run_details = str(exc)
        run.ended_at = datetime.utcnow()
        db.add(run)

        state.status = "failed"
        state.last_error = str(exc)
        state.last_run_at = datetime.utcnow()
        db.add(state)
        db.commit()
        _log_audit(
            db=db,
            connector_name=connector_name,
            action="sync.failed",
            result="error",
            details=str(exc),
            run_id=run.id,
        )
        return ConnectorSyncResponse(
            connector_name=connector_name,
            status="failed",
            fetched_count=run.fetched_count,
            ingested_count=run.ingested_count,
            error_count=run.error_count,
            run_id=run.id,
            details=str(exc),
        )

    return ConnectorSyncResponse(
        connector_name=connector_name,
        status=run.status,
        fetched_count=run.fetched_count,
        ingested_count=run.ingested_count,
        error_count=run.error_count,
        run_id=run.id,
        details=run.run_details,
    )


def get_connector_status(db: Session) -> list[ConnectorStateRecord]:
    rows = db.execute(select(ConnectorState).order_by(ConnectorState.connector_name.asc())).scalars().all()
    return [
        ConnectorStateRecord(
            connector_name=row.connector_name,
            status=row.status,
            checkpoint=row.checkpoint,
            last_run_at=row.last_run_at,
            last_error=row.last_error,
            total_synced_items=row.total_synced_items,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


def upsert_connector_credential(
    db: Session,
    connector_name: str,
    auth_type: str,
    secret_value: str,
    secret_ref: str | None,
) -> ConnectorCredentialRecord:
    row = db.execute(
        select(ConnectorCredential).where(ConnectorCredential.connector_name == connector_name)
    ).scalar_one_or_none()
    if not row:
        row = ConnectorCredential(connector_name=connector_name)
    row.auth_type = auth_type
    row.secret_value = secret_value
    row.secret_ref = secret_ref
    row.status = "configured"
    db.add(row)
    db.commit()
    db.refresh(row)
    return ConnectorCredentialRecord(
        connector_name=row.connector_name,
        auth_type=row.auth_type,
        status=row.status,
        secret_ref=row.secret_ref,
        masked_secret=_mask_secret(row.secret_value),
        updated_at=row.updated_at,
    )


def list_connector_credentials(db: Session) -> list[ConnectorCredentialRecord]:
    rows = db.execute(
        select(ConnectorCredential).order_by(ConnectorCredential.connector_name.asc())
    ).scalars().all()
    return [
        ConnectorCredentialRecord(
            connector_name=row.connector_name,
            auth_type=row.auth_type,
            status=row.status,
            secret_ref=row.secret_ref,
            masked_secret=_mask_secret(row.secret_value),
            updated_at=row.updated_at,
        )
        for row in rows
    ]


def _schedule_to_record(row: ConnectorSchedule) -> ConnectorScheduleRecord:
    config = json.loads(row.config_json) if row.config_json else {}
    return ConnectorScheduleRecord(
        connector_name=row.connector_name,
        enabled=row.enabled,
        interval_minutes=row.interval_minutes,
        priority=row.priority,
        group_name=row.group_name,
        is_paused=row.is_paused,
        max_attempts=row.max_attempts,
        failure_count=row.failure_count,
        limit=int(config.get("limit", 500)),
        next_run_at=row.next_run_at,
        last_run_at=row.last_run_at,
        last_success_at=row.last_success_at,
        updated_at=row.updated_at,
    )


def upsert_connector_schedule(
    db: Session,
    connector_name: str,
    enabled: bool,
    interval_minutes: int,
    priority: int,
    group_name: str,
    is_paused: bool,
    max_attempts: int,
    limit: int,
    config: dict,
    run_immediately: bool,
) -> ConnectorScheduleRecord:
    if connector_name not in SUPPORTED_CONNECTORS:
        raise ValueError(f"Unsupported connector: {connector_name}")
    row = db.execute(
        select(ConnectorSchedule).where(ConnectorSchedule.connector_name == connector_name)
    ).scalar_one_or_none()
    if not row:
        row = ConnectorSchedule(connector_name=connector_name)
    row.enabled = enabled
    row.interval_minutes = interval_minutes
    row.priority = priority
    row.group_name = group_name
    row.is_paused = is_paused
    row.max_attempts = max_attempts
    payload = {"limit": limit, "config": config}
    row.config_json = json.dumps(payload)
    now = datetime.utcnow()
    row.next_run_at = now if run_immediately else now + timedelta(minutes=interval_minutes)
    db.add(row)
    db.commit()
    db.refresh(row)
    return _schedule_to_record(row)


def list_connector_schedules(db: Session) -> list[ConnectorScheduleRecord]:
    rows = db.execute(select(ConnectorSchedule).order_by(ConnectorSchedule.connector_name.asc())).scalars().all()
    return [_schedule_to_record(row) for row in rows]


def run_due_connector_schedules(db: Session, max_runs: int = 20) -> ConnectorScheduleRunResponse:
    now = datetime.utcnow()
    schedules = db.execute(
        select(ConnectorSchedule)
        .where(ConnectorSchedule.enabled.is_(True))
        .where(ConnectorSchedule.is_paused.is_(False))
        .where(ConnectorSchedule.next_run_at.is_not(None))
        .where(ConnectorSchedule.next_run_at <= now)
        .order_by(ConnectorSchedule.priority.asc())
        .order_by(ConnectorSchedule.next_run_at.asc())
    ).scalars().all()

    scanned = len(schedules)
    triggered = 0
    dead_lettered = 0
    results: list[ConnectorSyncResponse] = []
    for row in schedules[:max_runs]:
        payload = json.loads(row.config_json) if row.config_json else {}
        limit = int(payload.get("limit", 500))
        config = payload.get("config") if isinstance(payload.get("config"), dict) else {}
        result = run_connector_sync(
            db=db,
            connector_name=row.connector_name,
            config=config,
            limit=limit,
            use_checkpoint=True,
        )
        results.append(result)
        triggered += 1
        row.last_run_at = datetime.utcnow()
        if result.status == "completed":
            row.failure_count = 0
            row.last_success_at = datetime.utcnow()
            row.next_run_at = datetime.utcnow() + timedelta(minutes=row.interval_minutes)
        else:
            row.failure_count = int(row.failure_count or 0) + 1
            if row.failure_count >= int(row.max_attempts or 1):
                dead_lettered += 1
                row.enabled = False
                row.next_run_at = None
                dead_letter = ConnectorScheduleDeadLetter(
                    connector_name=row.connector_name,
                    schedule_id=row.id,
                    attempts=row.failure_count,
                    last_error=result.details,
                    status="open",
                    payload_json=row.config_json,
                )
                db.add(dead_letter)
            else:
                backoff_minutes = _next_backoff_minutes(
                    failure_count=row.failure_count,
                    base_interval_minutes=max(1, row.interval_minutes),
                )
                row.next_run_at = datetime.utcnow() + timedelta(minutes=backoff_minutes)
        db.add(row)
        db.commit()

    return ConnectorScheduleRunResponse(
        scanned=scanned,
        triggered=triggered,
        dead_lettered=dead_lettered,
        results=results,
        generated_at=datetime.utcnow(),
    )


def trigger_connector_webhook(
    db: Session,
    connector_name: str,
    event_type: str,
    secret: str | None,
    config: dict,
    limit: int,
    use_checkpoint: bool,
) -> ConnectorWebhookTriggerResponse:
    if connector_name not in SUPPORTED_CONNECTORS:
        raise ValueError(f"Unsupported connector: {connector_name}")

    credential = db.execute(
        select(ConnectorCredential).where(ConnectorCredential.connector_name == connector_name)
    ).scalar_one_or_none()
    if credential and credential.secret_value and secret != credential.secret_value:
        _log_audit(
            db=db,
            connector_name=connector_name,
            action="webhook.rejected",
            result="blocked",
            details="Invalid webhook secret",
            run_id=None,
        )
        raise ValueError("Invalid webhook secret for connector")

    event = ConnectorWebhookEvent(
        connector_name=connector_name,
        event_type=event_type,
        status="received",
        payload_json=json.dumps({"config": config, "limit": limit, "use_checkpoint": use_checkpoint}),
        last_error=None,
        triggered_run_id=None,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    _log_audit(
        db=db,
        connector_name=connector_name,
        action="webhook.received",
        result="ok",
        details=f"event_type={event_type}",
        run_id=None,
    )

    result = run_connector_sync(
        db=db,
        connector_name=connector_name,
        config=config,
        limit=limit,
        use_checkpoint=use_checkpoint,
    )

    event.status = "completed" if result.status == "completed" else "failed"
    event.last_error = result.details if result.status != "completed" else None
    event.triggered_run_id = result.run_id
    db.add(event)
    db.commit()
    db.refresh(event)
    _log_audit(
        db=db,
        connector_name=connector_name,
        action="webhook.completed" if event.status == "completed" else "webhook.failed",
        result="ok" if event.status == "completed" else "error",
        details=event.last_error,
        run_id=event.triggered_run_id,
    )

    return ConnectorWebhookTriggerResponse(
        event_id=event.id,
        connector_name=event.connector_name,
        event_type=event.event_type,
        status=event.status,
        run_id=event.triggered_run_id,
        details=event.last_error,
    )


def list_connector_dead_letter(
    db: Session,
    limit: int = 100,
    status: str = "open",
) -> list[ConnectorDeadLetterRecord]:
    query = select(ConnectorScheduleDeadLetter).order_by(ConnectorScheduleDeadLetter.created_at.desc())
    if status:
        query = query.where(ConnectorScheduleDeadLetter.status == status)
    rows = db.execute(query.limit(limit)).scalars().all()
    return [
        ConnectorDeadLetterRecord(
            id=row.id,
            connector_name=row.connector_name,
            schedule_id=row.schedule_id,
            attempts=row.attempts,
            last_error=row.last_error,
            status=row.status,
            payload_json=row.payload_json,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


def requeue_connector_dead_letter(
    db: Session,
    dead_letter_ids: list[int],
    limit: int = 20,
) -> tuple[int, list[int]]:
    query = select(ConnectorScheduleDeadLetter).where(ConnectorScheduleDeadLetter.status == "open")
    if dead_letter_ids:
        query = query.where(ConnectorScheduleDeadLetter.id.in_(dead_letter_ids))
    rows = db.execute(query.order_by(ConnectorScheduleDeadLetter.id.asc()).limit(limit)).scalars().all()

    requeued_ids: list[int] = []
    for row in rows:
        schedule = None
        if row.schedule_id:
            schedule = db.execute(
                select(ConnectorSchedule).where(ConnectorSchedule.id == row.schedule_id)
            ).scalar_one_or_none()
        if schedule is None:
            schedule = db.execute(
                select(ConnectorSchedule).where(ConnectorSchedule.connector_name == row.connector_name)
            ).scalar_one_or_none()
        if schedule:
            schedule.enabled = True
            schedule.failure_count = 0
            schedule.next_run_at = datetime.utcnow()
            db.add(schedule)
        row.status = "requeued"
        db.add(row)
        requeued_ids.append(row.id)

    db.commit()
    return len(requeued_ids), requeued_ids


def upsert_connector_policy(
    db: Session,
    connector_name: str,
    enabled: bool,
    rate_limit_per_hour: int,
    max_concurrent_runs: int,
) -> ConnectorPolicyRecord:
    if connector_name not in SUPPORTED_CONNECTORS:
        raise ValueError(f"Unsupported connector: {connector_name}")
    row = _get_or_create_policy(db, connector_name)
    row.enabled = enabled
    row.rate_limit_per_hour = rate_limit_per_hour
    row.max_concurrent_runs = max_concurrent_runs
    db.add(row)
    db.commit()
    db.refresh(row)
    _log_audit(
        db=db,
        connector_name=connector_name,
        action="policy.updated",
        result="ok",
        details=f"enabled={enabled}, rate_limit_per_hour={rate_limit_per_hour}, max_concurrent_runs={max_concurrent_runs}",
        run_id=None,
    )
    return ConnectorPolicyRecord(
        connector_name=row.connector_name,
        enabled=row.enabled,
        rate_limit_per_hour=row.rate_limit_per_hour,
        max_concurrent_runs=row.max_concurrent_runs,
        updated_at=row.updated_at,
    )


def list_connector_policies(db: Session) -> list[ConnectorPolicyRecord]:
    rows = db.execute(select(ConnectorPolicy).order_by(ConnectorPolicy.connector_name.asc())).scalars().all()
    return [
        ConnectorPolicyRecord(
            connector_name=row.connector_name,
            enabled=row.enabled,
            rate_limit_per_hour=row.rate_limit_per_hour,
            max_concurrent_runs=row.max_concurrent_runs,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


def list_connector_audits(
    db: Session,
    connector_name: str | None = None,
    action: str | None = None,
    result: str | None = None,
    limit: int = 200,
) -> list[ConnectorAuditRecord]:
    query = select(ConnectorAuditLog).order_by(ConnectorAuditLog.created_at.desc())
    if connector_name:
        query = query.where(ConnectorAuditLog.connector_name == connector_name)
    if action:
        query = query.where(ConnectorAuditLog.action == action)
    if result:
        query = query.where(ConnectorAuditLog.result == result)
    rows = db.execute(query.limit(limit)).scalars().all()
    return [
        ConnectorAuditRecord(
            id=row.id,
            connector_name=row.connector_name,
            action=row.action,
            result=row.result,
            details=row.details,
            run_id=row.run_id,
            created_at=row.created_at,
        )
        for row in rows
    ]


def simulate_connector_sync(
    db: Session,
    connector_name: str,
    config: dict,
    limit: int,
    use_checkpoint: bool = True,
) -> ConnectorSimulationResponse:
    if connector_name not in SUPPORTED_CONNECTORS:
        raise ValueError(f"Unsupported connector: {connector_name}")

    state = _get_or_create_state(db, connector_name)
    simulation = ConnectorSimulationRun(
        connector_name=connector_name,
        status="running",
        fetched_count=0,
        candidate_new_items=0,
        candidate_existing_items=0,
        sample_new_refs="[]",
        simulation_details=None,
        started_at=datetime.utcnow(),
    )
    db.add(simulation)
    db.commit()
    db.refresh(simulation)
    _log_audit(
        db=db,
        connector_name=connector_name,
        action="simulation.started",
        result="ok",
        details=f"limit={limit}, use_checkpoint={use_checkpoint}",
        run_id=None,
    )

    checkpoint_dt = _parse_checkpoint(state.checkpoint) if use_checkpoint else None
    try:
        fetched_rows = _fetch_rows_for_connector(
            connector_name=connector_name,
            config=config,
            limit=limit,
            checkpoint_dt=checkpoint_dt,
        )
        new_refs: list[str] = []
        existing_count = 0
        for idx, row in enumerate(fetched_rows):
            payload = _normalize_row(row, connector_name, idx)
            existing = db.execute(
                select(Item.id).where(Item.source == connector_name).where(Item.source_ref == payload.source_ref)
            ).first()
            if existing:
                existing_count += 1
            elif len(new_refs) < 10:
                new_refs.append(payload.source_ref or "")

        simulation.status = "completed"
        simulation.fetched_count = len(fetched_rows)
        simulation.candidate_existing_items = existing_count
        simulation.candidate_new_items = len(fetched_rows) - existing_count
        simulation.sample_new_refs = json.dumps(new_refs)
        simulation.simulation_details = f"connector={connector_name}, limit={limit}, use_checkpoint={use_checkpoint}"
        simulation.ended_at = datetime.utcnow()
        db.add(simulation)
        db.commit()
        db.refresh(simulation)
        _log_audit(
            db=db,
            connector_name=connector_name,
            action="simulation.completed",
            result="ok",
            details=simulation.simulation_details,
            run_id=None,
        )
        return ConnectorSimulationResponse(
            simulation_id=simulation.id,
            connector_name=connector_name,
            status=simulation.status,
            fetched_count=simulation.fetched_count,
            candidate_new_items=simulation.candidate_new_items,
            candidate_existing_items=simulation.candidate_existing_items,
            sample_new_refs=json.loads(simulation.sample_new_refs or "[]"),
            details=simulation.simulation_details,
            generated_at=datetime.utcnow(),
        )
    except Exception as exc:
        simulation.status = "failed"
        simulation.simulation_details = str(exc)
        simulation.ended_at = datetime.utcnow()
        db.add(simulation)
        db.commit()
        db.refresh(simulation)
        _log_audit(
            db=db,
            connector_name=connector_name,
            action="simulation.failed",
            result="error",
            details=str(exc),
            run_id=None,
        )
        return ConnectorSimulationResponse(
            simulation_id=simulation.id,
            connector_name=connector_name,
            status="failed",
            fetched_count=0,
            candidate_new_items=0,
            candidate_existing_items=0,
            sample_new_refs=[],
            details=str(exc),
            generated_at=datetime.utcnow(),
        )


def list_connector_simulations(
    db: Session,
    connector_name: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> list[ConnectorSimulationRecord]:
    query = select(ConnectorSimulationRun).order_by(ConnectorSimulationRun.created_at.desc())
    if connector_name:
        query = query.where(ConnectorSimulationRun.connector_name == connector_name)
    if status:
        query = query.where(ConnectorSimulationRun.status == status)
    rows = db.execute(query.limit(limit)).scalars().all()
    return [
        ConnectorSimulationRecord(
            simulation_id=row.id,
            connector_name=row.connector_name,
            status=row.status,
            fetched_count=row.fetched_count,
            candidate_new_items=row.candidate_new_items,
            candidate_existing_items=row.candidate_existing_items,
            sample_new_refs=json.loads(row.sample_new_refs or "[]"),
            details=row.simulation_details,
            created_at=row.created_at,
        )
        for row in rows
    ]


def recommend_connector_policy(
    db: Session,
    connector_name: str,
) -> ConnectorPolicyRecommendationResponse:
    if connector_name not in SUPPORTED_CONNECTORS:
        raise ValueError(f"Unsupported connector: {connector_name}")
    recent_runs = db.execute(
        select(ConnectorRun).where(ConnectorRun.connector_name == connector_name).order_by(ConnectorRun.created_at.desc()).limit(50)
    ).scalars().all()
    total_runs = len(recent_runs)
    failed_runs = len([r for r in recent_runs if r.status in {"failed", "rejected"}])
    failure_ratio = (failed_runs / total_runs) if total_runs else 0.0
    avg_items = 0
    if total_runs:
        avg_items = int(sum(int(r.fetched_count or 0) for r in recent_runs) / total_runs)

    if failure_ratio >= 0.4:
        recommended_rate = 30
        recommended_concurrency = 1
        recommended_interval = 15
        reason = "High recent failure ratio; reduce pressure and run less frequently."
    elif avg_items >= 1000:
        recommended_rate = 120
        recommended_concurrency = 1
        recommended_interval = 10
        reason = "Large payload volume observed; keep concurrency low but allow steady throughput."
    else:
        recommended_rate = 180
        recommended_concurrency = 2
        recommended_interval = 5
        reason = "Stable recent behavior; moderate throughput policy is recommended."

    _log_audit(
        db=db,
        connector_name=connector_name,
        action="policy.recommendation.generated",
        result="ok",
        details=f"runs={total_runs}, failures={failed_runs}, avg_items={avg_items}",
        run_id=None,
    )
    return ConnectorPolicyRecommendationResponse(
        connector_name=connector_name,
        recommended_rate_limit_per_hour=recommended_rate,
        recommended_max_concurrent_runs=recommended_concurrency,
        recommended_interval_minutes=recommended_interval,
        reason=reason,
        generated_at=datetime.utcnow(),
    )


def _clamp_policy_recommendation(
    recommended_rate: int,
    recommended_concurrency: int,
    min_rate: int,
    max_rate: int,
    concurrency_cap: int,
) -> tuple[int, int]:
    clamped_rate = max(min_rate, min(max_rate, recommended_rate))
    clamped_concurrency = max(1, min(concurrency_cap, recommended_concurrency))
    return clamped_rate, clamped_concurrency


def auto_apply_connector_policy(
    db: Session,
    connector_name: str,
    enabled: bool,
    dry_run: bool,
    min_rate_limit_per_hour: int,
    max_rate_limit_per_hour: int,
    max_concurrent_runs_cap: int,
) -> ConnectorPolicyAutoApplyResponse:
    if connector_name not in SUPPORTED_CONNECTORS:
        raise ValueError(f"Unsupported connector: {connector_name}")
    if min_rate_limit_per_hour > max_rate_limit_per_hour:
        raise ValueError("min_rate_limit_per_hour must be <= max_rate_limit_per_hour")

    policy = _get_or_create_policy(db, connector_name)
    rec = recommend_connector_policy(db=db, connector_name=connector_name)
    new_rate, new_concurrency = _clamp_policy_recommendation(
        recommended_rate=rec.recommended_rate_limit_per_hour,
        recommended_concurrency=rec.recommended_max_concurrent_runs,
        min_rate=min_rate_limit_per_hour,
        max_rate=max_rate_limit_per_hour,
        concurrency_cap=max_concurrent_runs_cap,
    )
    reason = f"{rec.reason} (clamped by guardrails)"

    if dry_run:
        _log_audit(
            db=db,
            connector_name=connector_name,
            action="policy.auto_apply.dry_run",
            result="ok",
            details=f"new_rate={new_rate}, new_concurrency={new_concurrency}",
            run_id=None,
        )
        return ConnectorPolicyAutoApplyResponse(
            connector_name=connector_name,
            applied=False,
            revision_id=None,
            previous_rate_limit_per_hour=policy.rate_limit_per_hour,
            previous_max_concurrent_runs=policy.max_concurrent_runs,
            new_rate_limit_per_hour=new_rate,
            new_max_concurrent_runs=new_concurrency,
            reason=reason,
            generated_at=datetime.utcnow(),
        )

    revision = ConnectorPolicyRevision(
        connector_name=connector_name,
        previous_enabled=policy.enabled,
        previous_rate_limit_per_hour=policy.rate_limit_per_hour,
        previous_max_concurrent_runs=policy.max_concurrent_runs,
        new_enabled=enabled,
        new_rate_limit_per_hour=new_rate,
        new_max_concurrent_runs=new_concurrency,
        reason=reason,
        status="applied",
    )
    db.add(revision)

    policy.enabled = enabled
    policy.rate_limit_per_hour = new_rate
    policy.max_concurrent_runs = new_concurrency
    db.add(policy)
    db.commit()
    db.refresh(revision)
    db.refresh(policy)

    _log_audit(
        db=db,
        connector_name=connector_name,
        action="policy.auto_apply.applied",
        result="ok",
        details=f"revision_id={revision.id}, new_rate={new_rate}, new_concurrency={new_concurrency}",
        run_id=None,
    )
    return ConnectorPolicyAutoApplyResponse(
        connector_name=connector_name,
        applied=True,
        revision_id=revision.id,
        previous_rate_limit_per_hour=revision.previous_rate_limit_per_hour,
        previous_max_concurrent_runs=revision.previous_max_concurrent_runs,
        new_rate_limit_per_hour=revision.new_rate_limit_per_hour,
        new_max_concurrent_runs=revision.new_max_concurrent_runs,
        reason=reason,
        generated_at=datetime.utcnow(),
    )


def list_connector_policy_revisions(
    db: Session,
    connector_name: str | None = None,
    status: str | None = None,
    limit: int = 100,
) -> list[ConnectorPolicyRevisionRecord]:
    query = select(ConnectorPolicyRevision).order_by(ConnectorPolicyRevision.created_at.desc())
    if connector_name:
        query = query.where(ConnectorPolicyRevision.connector_name == connector_name)
    if status:
        query = query.where(ConnectorPolicyRevision.status == status)
    rows = db.execute(query.limit(limit)).scalars().all()
    return [
        ConnectorPolicyRevisionRecord(
            id=row.id,
            connector_name=row.connector_name,
            previous_enabled=row.previous_enabled,
            previous_rate_limit_per_hour=row.previous_rate_limit_per_hour,
            previous_max_concurrent_runs=row.previous_max_concurrent_runs,
            new_enabled=row.new_enabled,
            new_rate_limit_per_hour=row.new_rate_limit_per_hour,
            new_max_concurrent_runs=row.new_max_concurrent_runs,
            reason=row.reason,
            status=row.status,
            created_at=row.created_at,
        )
        for row in rows
    ]


def rollback_latest_connector_policy_revision(
    db: Session,
    connector_name: str,
) -> tuple[bool, int | None, str]:
    revision = db.execute(
        select(ConnectorPolicyRevision)
        .where(ConnectorPolicyRevision.connector_name == connector_name)
        .where(ConnectorPolicyRevision.status == "applied")
        .order_by(ConnectorPolicyRevision.created_at.desc())
    ).scalar_one_or_none()
    if not revision:
        return False, None, "No applied revision found to rollback."

    policy = _get_or_create_policy(db, connector_name)
    policy.enabled = revision.previous_enabled
    policy.rate_limit_per_hour = revision.previous_rate_limit_per_hour
    policy.max_concurrent_runs = revision.previous_max_concurrent_runs
    revision.status = "rolled_back"
    db.add(policy)
    db.add(revision)
    db.commit()
    db.refresh(revision)

    _log_audit(
        db=db,
        connector_name=connector_name,
        action="policy.rollback",
        result="ok",
        details=f"rolled_back_revision_id={revision.id}",
        run_id=None,
    )
    return True, revision.id, "Latest applied policy revision rolled back."


def guardrail_check_connector_policy(
    db: Session,
    connector_name: str,
    lookback_runs: int,
    failure_ratio_threshold: float,
    auto_rollback: bool,
) -> tuple[float, bool, bool, str]:
    if connector_name not in SUPPORTED_CONNECTORS:
        raise ValueError(f"Unsupported connector: {connector_name}")
    runs = db.execute(
        select(ConnectorRun)
        .where(ConnectorRun.connector_name == connector_name)
        .order_by(ConnectorRun.created_at.desc())
        .limit(lookback_runs)
    ).scalars().all()
    total = len(runs)
    failures = len([r for r in runs if r.status in {"failed", "rejected"}])
    failure_ratio = (failures / total) if total else 0.0
    breached = failure_ratio > failure_ratio_threshold
    rolled_back = False
    message = "Guardrail check passed."

    if breached and auto_rollback:
        rolled_back, revision_id, rollback_msg = rollback_latest_connector_policy_revision(
            db=db, connector_name=connector_name
        )
        if rolled_back:
            message = f"Guardrail breached; rollback executed (revision_id={revision_id})."
        else:
            message = f"Guardrail breached but rollback unavailable: {rollback_msg}"
    elif breached:
        message = "Guardrail breached; auto rollback disabled."

    _log_audit(
        db=db,
        connector_name=connector_name,
        action="policy.guardrail_check",
        result="error" if breached else "ok",
        details=f"failure_ratio={failure_ratio:.4f}, threshold={failure_ratio_threshold}, rolled_back={rolled_back}",
        run_id=None,
    )
    return failure_ratio, breached, rolled_back, message


def update_connector_priority(
    db: Session,
    connector_name: str,
    priority: int,
    group_name: str | None = None,
    is_paused: bool | None = None,
) -> ConnectorScheduleRecord:
    if connector_name not in SUPPORTED_CONNECTORS:
        raise ValueError(f"Unsupported connector: {connector_name}")
    row = db.execute(
        select(ConnectorSchedule).where(ConnectorSchedule.connector_name == connector_name)
    ).scalar_one_or_none()
    if not row:
        row = ConnectorSchedule(connector_name=connector_name, enabled=True, interval_minutes=60)
    row.priority = priority
    if group_name is not None:
        row.group_name = group_name
    if is_paused is not None:
        row.is_paused = is_paused
    db.add(row)
    db.commit()
    db.refresh(row)
    _log_audit(
        db=db,
        connector_name=connector_name,
        action="schedule.priority.updated",
        result="ok",
        details=f"priority={row.priority}, group_name={row.group_name}, is_paused={row.is_paused}",
        run_id=None,
    )
    return _schedule_to_record(row)


def set_connector_group_pause(
    db: Session,
    group_name: str,
    paused: bool,
) -> int:
    rows = db.execute(
        select(ConnectorSchedule).where(ConnectorSchedule.group_name == group_name)
    ).scalars().all()
    for row in rows:
        row.is_paused = paused
        db.add(row)
        _log_audit(
            db=db,
            connector_name=row.connector_name,
            action="schedule.group.pause" if paused else "schedule.group.resume",
            result="ok",
            details=f"group_name={group_name}",
            run_id=None,
        )
    db.commit()
    return len(rows)


def run_connector_orchestration(
    db: Session,
    connector_names: list[str],
    max_connectors: int,
    use_checkpoint: bool,
) -> ConnectorOrchestrationRunResponse:
    selected_names = [name for name in connector_names if name in SUPPORTED_CONNECTORS]
    query = (
        select(ConnectorSchedule)
        .where(ConnectorSchedule.enabled.is_(True))
        .where(ConnectorSchedule.is_paused.is_(False))
        .order_by(ConnectorSchedule.priority.asc())
        .order_by(ConnectorSchedule.connector_name.asc())
    )
    if selected_names:
        query = query.where(ConnectorSchedule.connector_name.in_(selected_names))
    schedules = db.execute(query.limit(max_connectors)).scalars().all()

    orchestration = ConnectorOrchestrationRun(
        status="running",
        requested_connectors=json.dumps(selected_names),
        total_connectors=0,
        succeeded_connectors=0,
        failed_connectors=0,
        blocked_connectors=0,
        run_details=None,
        started_at=datetime.utcnow(),
    )
    db.add(orchestration)
    db.commit()
    db.refresh(orchestration)

    items: list[ConnectorOrchestrationItemRecord] = []
    for schedule in schedules:
        payload = json.loads(schedule.config_json) if schedule.config_json else {}
        limit = int(payload.get("limit", 500))
        config = payload.get("config") if isinstance(payload.get("config"), dict) else {}
        result = run_connector_sync(
            db=db,
            connector_name=schedule.connector_name,
            config=config,
            limit=limit,
            use_checkpoint=use_checkpoint,
        )
        item_row = ConnectorOrchestrationRunItem(
            orchestration_run_id=orchestration.id,
            connector_name=schedule.connector_name,
            status=result.status,
            run_id=result.run_id,
            details=result.details,
        )
        db.add(item_row)
        if result.status == "completed":
            orchestration.succeeded_connectors += 1
        elif result.status == "rejected":
            orchestration.blocked_connectors += 1
        else:
            orchestration.failed_connectors += 1
        items.append(
            ConnectorOrchestrationItemRecord(
                connector_name=schedule.connector_name,
                status=result.status,
                run_id=result.run_id,
                details=result.details,
            )
        )

    orchestration.total_connectors = len(schedules)
    orchestration.status = "completed"
    orchestration.run_details = (
        f"succeeded={orchestration.succeeded_connectors}, "
        f"failed={orchestration.failed_connectors}, blocked={orchestration.blocked_connectors}"
    )
    orchestration.ended_at = datetime.utcnow()
    db.add(orchestration)
    db.commit()
    db.refresh(orchestration)

    _log_audit(
        db=db,
        connector_name="orchestration",
        action="orchestration.run.completed",
        result="ok",
        details=orchestration.run_details,
        run_id=None,
    )
    return ConnectorOrchestrationRunResponse(
        orchestration_run_id=orchestration.id,
        status=orchestration.status,
        total_connectors=orchestration.total_connectors,
        succeeded_connectors=orchestration.succeeded_connectors,
        failed_connectors=orchestration.failed_connectors,
        blocked_connectors=orchestration.blocked_connectors,
        items=items,
        details=orchestration.run_details,
        generated_at=datetime.utcnow(),
    )


def _connector_failure_streak(runs: list[ConnectorRun]) -> int:
    streak = 0
    for row in runs:
        if row.status in {"failed", "rejected"}:
            streak += 1
        else:
            break
    return streak


def _avg_latency_ms(runs: list[ConnectorRun]) -> float:
    latencies: list[float] = []
    for row in runs:
        if row.started_at and row.ended_at:
            latencies.append((row.ended_at - row.started_at).total_seconds() * 1000.0)
    if not latencies:
        return 0.0
    return float(sum(latencies) / len(latencies))


def _health_status(score: float) -> str:
    if score >= 0.85:
        return "healthy"
    if score >= 0.6:
        return "warning"
    return "critical"


def get_connector_health(db: Session, lookback_runs: int = 50) -> list[ConnectorHealthRecord]:
    connectors = sorted(SUPPORTED_CONNECTORS)
    records: list[ConnectorHealthRecord] = []
    for name in connectors:
        runs = db.execute(
            select(ConnectorRun)
            .where(ConnectorRun.connector_name == name)
            .order_by(ConnectorRun.created_at.desc())
            .limit(lookback_runs)
        ).scalars().all()
        total = len(runs)
        success = len([r for r in runs if r.status == "completed"])
        success_rate = (success / total) if total else 1.0
        failure_streak = _connector_failure_streak(runs)
        avg_latency = _avg_latency_ms(runs)
        dead_letter_open_count = len(
            db.execute(
                select(ConnectorScheduleDeadLetter.id)
                .where(ConnectorScheduleDeadLetter.connector_name == name)
                .where(ConnectorScheduleDeadLetter.status == "open")
            ).all()
        )

        score = success_rate
        score -= min(0.4, failure_streak * 0.05)
        score -= min(0.2, dead_letter_open_count * 0.03)
        score -= min(0.2, avg_latency / 20000.0)
        score = max(0.0, min(1.0, score))
        status = _health_status(score)
        details = (
            f"success_rate={success_rate:.2f}, failure_streak={failure_streak}, "
            f"dead_letter_open={dead_letter_open_count}, avg_latency_ms={avg_latency:.1f}"
        )

        schedule = db.execute(
            select(ConnectorSchedule).where(ConnectorSchedule.connector_name == name)
        ).scalar_one_or_none()

        snapshot = db.execute(
            select(ConnectorHealthSnapshot).where(ConnectorHealthSnapshot.connector_name == name)
        ).scalar_one_or_none()
        if not snapshot:
            snapshot = ConnectorHealthSnapshot(connector_name=name)
        snapshot.health_score = score
        snapshot.success_rate = success_rate
        snapshot.failure_streak = failure_streak
        snapshot.avg_latency_ms = avg_latency
        snapshot.dead_letter_open_count = dead_letter_open_count
        snapshot.total_recent_runs = total
        snapshot.status = status
        snapshot.details = details
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        records.append(
            ConnectorHealthRecord(
                connector_name=name,
                health_score=score,
                status=status,
                success_rate=success_rate,
                failure_streak=failure_streak,
                avg_latency_ms=avg_latency,
                dead_letter_open_count=dead_letter_open_count,
                total_recent_runs=total,
                priority=schedule.priority if schedule else None,
                group_name=schedule.group_name if schedule else None,
                is_paused=schedule.is_paused if schedule else None,
                details=details,
                updated_at=snapshot.updated_at,
            )
        )
    return records


def _severity_allowed(alert_severity: str, min_severity: str) -> bool:
    return SEVERITY_ORDER.get(alert_severity, 0) >= SEVERITY_ORDER.get(min_severity, 1)


def upsert_notification_channel(
    db: Session,
    connector_name: str,
    channel_type: str,
    target: str,
    secret: str | None,
    min_severity: str,
    is_enabled: bool,
) -> ConnectorNotificationChannelRecord:
    row = db.execute(
        select(ConnectorNotificationChannel)
        .where(ConnectorNotificationChannel.connector_name == connector_name)
        .where(ConnectorNotificationChannel.channel_type == channel_type)
        .where(ConnectorNotificationChannel.target == target)
    ).scalar_one_or_none()
    if not row:
        row = ConnectorNotificationChannel(
            connector_name=connector_name,
            channel_type=channel_type,
            target=target,
        )
    row.secret = secret
    row.min_severity = min_severity
    row.is_enabled = is_enabled
    db.add(row)
    db.commit()
    db.refresh(row)
    _log_audit(
        db=db,
        connector_name=connector_name,
        action="notification.channel.upserted",
        result="ok",
        details=f"channel_type={channel_type}, target={target}",
        run_id=None,
    )
    return ConnectorNotificationChannelRecord(
        id=row.id,
        connector_name=row.connector_name,
        channel_type=row.channel_type,
        target=row.target,
        min_severity=row.min_severity,
        is_enabled=row.is_enabled,
        updated_at=row.updated_at,
    )


def list_notification_channels(
    db: Session,
    connector_name: str | None = None,
    limit: int = 200,
) -> list[ConnectorNotificationChannelRecord]:
    query = select(ConnectorNotificationChannel).order_by(ConnectorNotificationChannel.updated_at.desc())
    if connector_name:
        query = query.where(ConnectorNotificationChannel.connector_name == connector_name)
    rows = db.execute(query.limit(limit)).scalars().all()
    return [
        ConnectorNotificationChannelRecord(
            id=row.id,
            connector_name=row.connector_name,
            channel_type=row.channel_type,
            target=row.target,
            min_severity=row.min_severity,
            is_enabled=row.is_enabled,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


def _dispatch_notification(
    db: Session,
    connector_name: str,
    severity: str,
    payload_preview: str,
    alert_id: int | None = None,
    specific_channel_id: int | None = None,
) -> tuple[int, int, int]:
    query = select(ConnectorNotificationChannel).where(ConnectorNotificationChannel.is_enabled.is_(True))
    query = query.where(
        (ConnectorNotificationChannel.connector_name == connector_name)
        | (ConnectorNotificationChannel.connector_name == "*")
    )
    if specific_channel_id is not None:
        query = query.where(ConnectorNotificationChannel.id == specific_channel_id)
    channels = db.execute(query).scalars().all()

    attempted = 0
    sent = 0
    failed = 0
    for channel in channels:
        if not _severity_allowed(severity, channel.min_severity):
            continue
        attempted += 1
        # Stub delivery: persist a delivery log to represent dispatch.
        delivery = ConnectorNotificationDelivery(
            connector_name=connector_name,
            alert_id=alert_id,
            channel_id=channel.id,
            channel_type=channel.channel_type,
            target=channel.target,
            status="sent",
            payload_preview=payload_preview[:2000],
            response_preview="simulated_delivery_ok",
        )
        try:
            db.add(delivery)
            db.commit()
            sent += 1
        except Exception:
            db.rollback()
            failed += 1
    return attempted, sent, failed


def send_test_notification(
    db: Session,
    connector_name: str,
    severity: str,
    message: str,
) -> ConnectorNotificationTestResponse:
    attempted, sent, failed = _dispatch_notification(
        db=db,
        connector_name=connector_name,
        severity=severity,
        payload_preview=f"test:{message}",
        alert_id=None,
    )
    _log_audit(
        db=db,
        connector_name=connector_name,
        action="notification.test.sent",
        result="ok" if failed == 0 else "error",
        details=f"attempted={attempted}, sent={sent}, failed={failed}",
        run_id=None,
    )
    return ConnectorNotificationTestResponse(
        attempted_channels=attempted,
        sent=sent,
        failed=failed,
        generated_at=datetime.utcnow(),
    )


def list_notification_deliveries(
    db: Session,
    connector_name: str | None = None,
    limit: int = 200,
) -> list[ConnectorNotificationDeliveryRecord]:
    query = select(ConnectorNotificationDelivery).order_by(ConnectorNotificationDelivery.created_at.desc())
    if connector_name:
        query = query.where(ConnectorNotificationDelivery.connector_name == connector_name)
    rows = db.execute(query.limit(limit)).scalars().all()
    return [
        ConnectorNotificationDeliveryRecord(
            id=row.id,
            connector_name=row.connector_name,
            alert_id=row.alert_id,
            channel_id=row.channel_id,
            channel_type=row.channel_type,
            target=row.target,
            status=row.status,
            payload_preview=row.payload_preview,
            response_preview=row.response_preview,
            created_at=row.created_at,
        )
        for row in rows
    ]


def upsert_escalation_policy(
    db: Session,
    connector_name: str,
    enabled: bool,
    open_alert_count_threshold: int,
    action_type: str,
    notify_channel_id: int | None,
) -> ConnectorEscalationPolicyRecord:
    if connector_name not in SUPPORTED_CONNECTORS:
        raise ValueError(f"Unsupported connector: {connector_name}")
    row = db.execute(
        select(ConnectorEscalationPolicy).where(ConnectorEscalationPolicy.connector_name == connector_name)
    ).scalar_one_or_none()
    if not row:
        row = ConnectorEscalationPolicy(connector_name=connector_name)
    row.enabled = enabled
    row.open_alert_count_threshold = open_alert_count_threshold
    row.action_type = action_type
    row.notify_channel_id = notify_channel_id
    db.add(row)
    db.commit()
    db.refresh(row)
    _log_audit(
        db=db,
        connector_name=connector_name,
        action="escalation.policy.upserted",
        result="ok",
        details=(
            f"enabled={enabled}, threshold={open_alert_count_threshold}, "
            f"action_type={action_type}, notify_channel_id={notify_channel_id}"
        ),
        run_id=None,
    )
    return ConnectorEscalationPolicyRecord(
        connector_name=row.connector_name,
        enabled=row.enabled,
        open_alert_count_threshold=row.open_alert_count_threshold,
        action_type=row.action_type,
        notify_channel_id=row.notify_channel_id,
        updated_at=row.updated_at,
    )


def list_escalation_policies(
    db: Session,
    connector_name: str | None = None,
    limit: int = 200,
) -> list[ConnectorEscalationPolicyRecord]:
    query = select(ConnectorEscalationPolicy).order_by(ConnectorEscalationPolicy.updated_at.desc())
    if connector_name:
        query = query.where(ConnectorEscalationPolicy.connector_name == connector_name)
    rows = db.execute(query.limit(limit)).scalars().all()
    return [
        ConnectorEscalationPolicyRecord(
            connector_name=row.connector_name,
            enabled=row.enabled,
            open_alert_count_threshold=row.open_alert_count_threshold,
            action_type=row.action_type,
            notify_channel_id=row.notify_channel_id,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


def evaluate_escalation_policies(db: Session) -> ConnectorEscalationEvaluateResponse:
    policies = db.execute(
        select(ConnectorEscalationPolicy).where(ConnectorEscalationPolicy.enabled.is_(True))
    ).scalars().all()
    triggered = 0
    for policy in policies:
        open_alerts = len(
            db.execute(
                select(ConnectorSlaAlert.id)
                .where(ConnectorSlaAlert.connector_name == policy.connector_name)
                .where(ConnectorSlaAlert.status == "open")
            ).all()
        )
        if open_alerts < int(policy.open_alert_count_threshold):
            continue
        trigger_connector_remediation(
            db=db,
            connector_name=policy.connector_name,
            action_type=policy.action_type,
            reason=f"Escalation triggered: open_alerts={open_alerts}",
            related_alert_id=None,
        )
        payload = (
            f"escalation connector={policy.connector_name}, open_alerts={open_alerts}, "
            f"threshold={policy.open_alert_count_threshold}, action={policy.action_type}"
        )
        _dispatch_notification(
            db=db,
            connector_name=policy.connector_name,
            severity="critical",
            payload_preview=payload,
            alert_id=None,
            specific_channel_id=policy.notify_channel_id,
        )
        _log_audit(
            db=db,
            connector_name=policy.connector_name,
            action="escalation.triggered",
            result="error",
            details=payload,
            run_id=None,
        )
        triggered += 1
    return ConnectorEscalationEvaluateResponse(
        evaluated_connectors=len(policies),
        escalations_triggered=triggered,
        generated_at=datetime.utcnow(),
    )


def _create_sla_alert(
    db: Session,
    connector_name: str,
    severity: str,
    metric_name: str,
    metric_value: float,
    threshold_value: float,
    details: str,
) -> ConnectorSlaAlert:
    row = ConnectorSlaAlert(
        connector_name=connector_name,
        severity=severity,
        metric_name=metric_name,
        metric_value=metric_value,
        threshold_value=threshold_value,
        status="open",
        details=details,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def _pause_connector_schedule(db: Session, connector_name: str, reason: str, related_alert_id: int | None) -> ConnectorRemediationAction:
    schedule = db.execute(
        select(ConnectorSchedule).where(ConnectorSchedule.connector_name == connector_name)
    ).scalar_one_or_none()
    if not schedule:
        schedule = ConnectorSchedule(connector_name=connector_name, enabled=True, interval_minutes=60)
    schedule.is_paused = True
    db.add(schedule)
    db.commit()

    action = ConnectorRemediationAction(
        connector_name=connector_name,
        action_type="pause_connector",
        status="completed",
        action_details=reason,
        related_alert_id=related_alert_id,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    _log_audit(
        db=db,
        connector_name=connector_name,
        action="sla.remediation.pause_connector",
        result="ok",
        details=reason,
        run_id=None,
    )
    return action


def trigger_connector_remediation(
    db: Session,
    connector_name: str,
    action_type: str,
    reason: str | None = None,
    related_alert_id: int | None = None,
) -> ConnectorRemediationTriggerResponse:
    if connector_name not in SUPPORTED_CONNECTORS:
        raise ValueError(f"Unsupported connector: {connector_name}")
    note = reason or "Manual remediation triggered."
    if action_type == "pause_connector":
        action = _pause_connector_schedule(
            db=db,
            connector_name=connector_name,
            reason=note,
            related_alert_id=related_alert_id,
        )
        return ConnectorRemediationTriggerResponse(
            connector_name=connector_name,
            action_id=action.id,
            action_type=action.action_type,
            status=action.status,
            message="Connector paused by remediation action.",
        )
    if action_type == "reduce_policy_limits":
        policy = _get_or_create_policy(db, connector_name)
        policy.rate_limit_per_hour = max(10, int(policy.rate_limit_per_hour * 0.5))
        policy.max_concurrent_runs = max(1, min(policy.max_concurrent_runs, 1))
        db.add(policy)
        db.commit()
        action = ConnectorRemediationAction(
            connector_name=connector_name,
            action_type="reduce_policy_limits",
            status="completed",
            action_details=note,
            related_alert_id=related_alert_id,
        )
        db.add(action)
        db.commit()
        db.refresh(action)
        _log_audit(
            db=db,
            connector_name=connector_name,
            action="sla.remediation.reduce_policy_limits",
            result="ok",
            details=note,
            run_id=None,
        )
        return ConnectorRemediationTriggerResponse(
            connector_name=connector_name,
            action_id=action.id,
            action_type=action.action_type,
            status=action.status,
            message="Connector policy limits reduced by remediation action.",
        )
    raise ValueError(f"Unsupported remediation action: {action_type}")


def evaluate_connector_sla(
    db: Session,
    min_health_score: float,
    max_failure_streak: int,
    max_dead_letter_open: int,
    auto_remediate: bool,
) -> ConnectorSlaEvaluationResponse:
    health_records = get_connector_health(db=db, lookback_runs=50)
    alerts_created = 0
    remediations = 0
    for record in health_records:
        created_alerts: list[ConnectorSlaAlert] = []
        if record.health_score < min_health_score:
            created_alerts.append(
                _create_sla_alert(
                    db=db,
                    connector_name=record.connector_name,
                    severity="critical",
                    metric_name="health_score",
                    metric_value=record.health_score,
                    threshold_value=min_health_score,
                    details=f"Health score below threshold: {record.health_score:.3f} < {min_health_score:.3f}",
                )
            )
        if record.failure_streak > max_failure_streak:
            created_alerts.append(
                _create_sla_alert(
                    db=db,
                    connector_name=record.connector_name,
                    severity="warning",
                    metric_name="failure_streak",
                    metric_value=float(record.failure_streak),
                    threshold_value=float(max_failure_streak),
                    details=f"Failure streak exceeded: {record.failure_streak} > {max_failure_streak}",
                )
            )
        if record.dead_letter_open_count > max_dead_letter_open:
            created_alerts.append(
                _create_sla_alert(
                    db=db,
                    connector_name=record.connector_name,
                    severity="warning",
                    metric_name="dead_letter_open_count",
                    metric_value=float(record.dead_letter_open_count),
                    threshold_value=float(max_dead_letter_open),
                    details=(
                        "Dead-letter open count exceeded: "
                        f"{record.dead_letter_open_count} > {max_dead_letter_open}"
                    ),
                )
            )
        alerts_created += len(created_alerts)
        for alert in created_alerts:
            _log_audit(
                db=db,
                connector_name=record.connector_name,
                action="sla.alert.created",
                result="error",
                details=f"{alert.metric_name}: {alert.metric_value} vs {alert.threshold_value}",
                run_id=None,
            )
            _dispatch_notification(
                db=db,
                connector_name=record.connector_name,
                severity=alert.severity,
                payload_preview=(
                    f"sla_alert metric={alert.metric_name}, value={alert.metric_value}, "
                    f"threshold={alert.threshold_value}, severity={alert.severity}"
                ),
                alert_id=alert.id,
            )
            if auto_remediate and alert.metric_name in {"health_score", "failure_streak"}:
                trigger_connector_remediation(
                    db=db,
                    connector_name=record.connector_name,
                    action_type="pause_connector",
                    reason=f"Auto remediation for SLA breach: {alert.metric_name}",
                    related_alert_id=alert.id,
                )
                remediations += 1

    escalation_eval = evaluate_escalation_policies(db=db)
    remediations += escalation_eval.escalations_triggered

    return ConnectorSlaEvaluationResponse(
        evaluated_connectors=len(health_records),
        alerts_created=alerts_created,
        remediation_actions=remediations,
        details=(
            f"min_health_score={min_health_score}, max_failure_streak={max_failure_streak}, "
            f"max_dead_letter_open={max_dead_letter_open}, auto_remediate={auto_remediate}"
        ),
        generated_at=datetime.utcnow(),
    )


def list_connector_sla_alerts(
    db: Session,
    status: str | None = "open",
    connector_name: str | None = None,
    limit: int = 100,
) -> list[ConnectorSlaAlertRecord]:
    query = select(ConnectorSlaAlert).order_by(ConnectorSlaAlert.created_at.desc())
    if status:
        query = query.where(ConnectorSlaAlert.status == status)
    if connector_name:
        query = query.where(ConnectorSlaAlert.connector_name == connector_name)
    rows = db.execute(query.limit(limit)).scalars().all()
    return [
        ConnectorSlaAlertRecord(
            id=row.id,
            connector_name=row.connector_name,
            severity=row.severity,
            metric_name=row.metric_name,
            metric_value=row.metric_value,
            threshold_value=row.threshold_value,
            status=row.status,
            details=row.details,
            created_at=row.created_at,
        )
        for row in rows
    ]


def resolve_connector_sla_alert(db: Session, alert_id: int) -> tuple[bool, str]:
    row = db.execute(select(ConnectorSlaAlert).where(ConnectorSlaAlert.id == alert_id)).scalar_one_or_none()
    if not row:
        return False, "Alert not found."
    row.status = "resolved"
    db.add(row)
    db.commit()
    _log_audit(
        db=db,
        connector_name=row.connector_name,
        action="sla.alert.resolved",
        result="ok",
        details=f"alert_id={alert_id}",
        run_id=None,
    )
    return True, "SLA alert resolved."


def list_connector_remediation_actions(
    db: Session,
    connector_name: str | None = None,
    limit: int = 100,
) -> list[ConnectorRemediationRecord]:
    query = select(ConnectorRemediationAction).order_by(ConnectorRemediationAction.created_at.desc())
    if connector_name:
        query = query.where(ConnectorRemediationAction.connector_name == connector_name)
    rows = db.execute(query.limit(limit)).scalars().all()
    return [
        ConnectorRemediationRecord(
            id=row.id,
            connector_name=row.connector_name,
            action_type=row.action_type,
            status=row.status,
            action_details=row.action_details,
            related_alert_id=row.related_alert_id,
            created_at=row.created_at,
        )
        for row in rows
    ]
