from __future__ import annotations

import json
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import ApiMetric, DeadLetterJob, EvaluationRun, Item, Job, ProactiveSignal
from app.schemas import (
    DeadLetterRecord,
    EvaluationDetail,
    EvaluationRunResponse,
    JobMetricsResponse,
    JobMetricsRow,
    MetricsSummaryResponse,
)


def record_api_metric(
    db: Session,
    endpoint: str,
    method: str,
    status_code: int,
    latency_ms: float,
) -> None:
    db.add(
        ApiMetric(
            endpoint=endpoint,
            method=method,
            status_code=status_code,
            latency_ms=latency_ms,
            success=200 <= status_code < 400,
        )
    )
    db.commit()


def get_metrics_summary(db: Session) -> MetricsSummaryResponse:
    total_items = db.execute(select(func.count(Item.id))).scalar_one() or 0
    total_jobs = db.execute(select(func.count(Job.id))).scalar_one() or 0
    pending_jobs = db.execute(select(func.count(Job.id)).where(Job.status == "pending")).scalar_one() or 0
    failed_jobs = db.execute(select(func.count(Job.id)).where(Job.status == "failed")).scalar_one() or 0
    dead_letter_jobs = db.execute(select(func.count(DeadLetterJob.id)).where(DeadLetterJob.status == "open")).scalar_one() or 0
    open_signals = db.execute(
        select(func.count(ProactiveSignal.id)).where(ProactiveSignal.status == "open")
    ).scalar_one() or 0
    latest_eval = db.execute(
        select(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(1)
    ).scalar_one_or_none()

    return MetricsSummaryResponse(
        total_items=int(total_items),
        total_jobs=int(total_jobs),
        pending_jobs=int(pending_jobs),
        failed_jobs=int(failed_jobs),
        dead_letter_jobs=int(dead_letter_jobs),
        open_signals=int(open_signals),
        latest_evaluation_score=(latest_eval.score if latest_eval else None),
        generated_at=datetime.utcnow(),
    )


def get_job_metrics(db: Session) -> JobMetricsResponse:
    job_types = db.execute(select(Job.job_type).group_by(Job.job_type)).scalars().all()
    rows: list[JobMetricsRow] = []
    for job_type in job_types:
        total = db.execute(select(func.count(Job.id)).where(Job.job_type == job_type)).scalar_one() or 0
        succeeded = db.execute(
            select(func.count(Job.id)).where(Job.job_type == job_type, Job.status == "succeeded")
        ).scalar_one() or 0
        failed = db.execute(
            select(func.count(Job.id)).where(Job.job_type == job_type, Job.status == "failed")
        ).scalar_one() or 0
        dead_letter = db.execute(
            select(func.count(Job.id)).where(Job.job_type == job_type, Job.status == "dead_letter")
        ).scalar_one() or 0
        pending = db.execute(
            select(func.count(Job.id)).where(Job.job_type == job_type, Job.status == "pending")
        ).scalar_one() or 0
        rows.append(
            JobMetricsRow(
                job_type=job_type,
                total=int(total),
                succeeded=int(succeeded),
                failed=int(failed),
                dead_letter=int(dead_letter),
                pending=int(pending),
            )
        )
    return JobMetricsResponse(rows=rows, generated_at=datetime.utcnow())


def run_evaluation(db: Session, suite_name: str, days: int) -> EvaluationRunResponse:
    since = datetime.utcnow() - timedelta(days=days)
    total_items = db.execute(select(func.count(Item.id)).where(Item.created_at >= since)).scalar_one() or 0
    embedded_items = db.execute(
        select(func.count(Item.id)).where(Item.created_at >= since, Item.status == "embedded")
    ).scalar_one() or 0
    tagged_items = db.execute(
        select(func.count(Item.id)).where(Item.created_at >= since, Item.tag_count > 0)
    ).scalar_one() or 0
    classified_items = db.execute(
        select(func.count(Item.id)).where(Item.created_at >= since, Item.classification_label.is_not(None))
    ).scalar_one() or 0
    insights_items = db.execute(
        select(func.count(Item.id)).where(Item.created_at >= since, Item.insight_count > 0)
    ).scalar_one() or 0
    proactive_items = db.execute(
        select(func.count(Item.id)).where(Item.created_at >= since, Item.proactive_count > 0)
    ).scalar_one() or 0

    denom = max(1, int(total_items))
    embed_rate = float(embedded_items) / denom
    tag_rate = float(tagged_items) / denom
    class_rate = float(classified_items) / denom
    insight_rate = float(insights_items) / denom
    proactive_rate = float(proactive_items) / denom

    checks = [
        ("embed_coverage", embed_rate, 0.90, "Share of recent items successfully embedded."),
        ("tag_coverage", tag_rate, 0.70, "Share of recent items with at least one tag."),
        ("classification_coverage", class_rate, 0.70, "Share of recent items classified."),
        ("insight_coverage", insight_rate, 0.70, "Share of recent items with generated insights."),
        ("proactive_coverage", proactive_rate, 0.50, "Share of recent items with proactive signals."),
    ]

    details: list[EvaluationDetail] = []
    passed = 0
    for name, value, threshold, note in checks:
        ok = value >= threshold
        if ok:
            passed += 1
        details.append(
            EvaluationDetail(
                name=name,
                passed=ok,
                value=round(value, 4),
                threshold=threshold,
                note=note,
            )
        )

    checks_total = len(checks)
    score = round(passed / max(1, checks_total), 4)
    summary = f"Evaluation {suite_name}: {passed}/{checks_total} checks passed over last {days} days."

    row = EvaluationRun(
        suite_name=suite_name,
        score=score,
        status="completed",
        checks_total=checks_total,
        checks_passed=passed,
        summary=summary,
        details_json=json.dumps([d.model_dump() for d in details]),
    )
    db.add(row)
    db.commit()
    db.refresh(row)

    return EvaluationRunResponse(
        id=row.id,
        suite_name=row.suite_name,
        score=row.score,
        status=row.status,
        checks_total=row.checks_total,
        checks_passed=row.checks_passed,
        summary=row.summary,
        details=details,
        created_at=row.created_at,
    )


def get_latest_evaluation(db: Session) -> EvaluationRunResponse | None:
    row = db.execute(
        select(EvaluationRun).order_by(EvaluationRun.created_at.desc()).limit(1)
    ).scalar_one_or_none()
    if not row:
        return None

    details_json = json.loads(row.details_json or "[]")
    details = [EvaluationDetail(**entry) for entry in details_json]
    return EvaluationRunResponse(
        id=row.id,
        suite_name=row.suite_name,
        score=row.score,
        status=row.status,
        checks_total=row.checks_total,
        checks_passed=row.checks_passed,
        summary=row.summary,
        details=details,
        created_at=row.created_at,
    )


def list_dead_letter(db: Session, limit: int = 100, status: str | None = "open") -> list[DeadLetterRecord]:
    stmt = select(DeadLetterJob).order_by(DeadLetterJob.created_at.desc()).limit(limit)
    if status:
        stmt = (
            select(DeadLetterJob)
            .where(DeadLetterJob.status == status)
            .order_by(DeadLetterJob.created_at.desc())
            .limit(limit)
        )
    rows = db.execute(stmt).scalars().all()
    return [
        DeadLetterRecord(
            id=row.id,
            job_id=row.job_id,
            item_id=row.item_id,
            job_type=row.job_type,
            attempts=row.attempts,
            last_error=row.last_error,
            status=row.status,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]


def requeue_dead_letter(db: Session, dead_letter_ids: list[int], limit: int) -> tuple[int, list[int]]:
    if dead_letter_ids:
        rows = db.execute(
            select(DeadLetterJob).where(DeadLetterJob.id.in_(dead_letter_ids), DeadLetterJob.status == "open")
        ).scalars().all()
    else:
        rows = db.execute(
            select(DeadLetterJob).where(DeadLetterJob.status == "open").order_by(DeadLetterJob.created_at.asc()).limit(limit)
        ).scalars().all()

    requeued = 0
    used_ids: list[int] = []
    for row in rows:
        job = db.get(Job, row.job_id)
        if not job:
            continue
        job.status = "pending"
        job.last_error = None
        db.add(job)
        row.status = "requeued"
        db.add(row)
        requeued += 1
        used_ids.append(row.id)
    db.commit()
    return requeued, used_ids
