from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import DeadLetterJob, Item, Job
from app.services.classification import run_classification_for_item
from app.services.insights import generate_item_insight
from app.services.indexer import index_item
from app.services.proactive import generate_proactive_for_item
from app.services.tagging import run_tagging_for_item

MAX_JOB_ATTEMPTS = 3


def process_pending_jobs(db: Session, limit: int = 50) -> dict[str, int | list[int]]:
    jobs = db.execute(
        select(Job).where(Job.status == "pending").order_by(Job.created_at.asc()).limit(limit)
    ).scalars().all()

    processed = 0
    succeeded = 0
    failed = 0
    job_ids: list[int] = []

    for job in jobs:
        processed += 1
        job_ids.append(job.id)
        job.status = "processing"
        job.attempts += 1
        db.add(job)
        db.commit()
        db.refresh(job)

        try:
            item = db.get(Item, job.item_id)
            if item is None:
                raise ValueError(f"Item not found: {job.item_id}")
            if job.job_type == "embed":
                index_item(db, item)
            elif job.job_type == "tag":
                run_tagging_for_item(db, item)
            elif job.job_type == "classify":
                run_classification_for_item(db, item)
            elif job.job_type == "insight":
                generate_item_insight(db, item)
            elif job.job_type == "proactive":
                generate_proactive_for_item(db, item)
            else:
                raise ValueError(f"Unsupported job type: {job.job_type}")
            job.status = "succeeded"
            job.last_error = None
            succeeded += 1
        except Exception as exc:  # noqa: BLE001 - keep broad to avoid worker death.
            failed += 1
            job.status = "failed"
            job.last_error = str(exc)
            item = db.get(Item, job.item_id)
            if item is not None:
                if job.job_type == "embed":
                    item.status = "failed"
                    item.error_reason = str(exc)
                elif job.job_type == "tag":
                    item.tagging_status = "failed"
                    item.tagging_error = str(exc)
                elif job.job_type == "classify":
                    item.classification_status = "failed"
                    item.classification_error = str(exc)
                elif job.job_type == "insight":
                    item.insight_status = "failed"
                    item.insight_error = str(exc)
                elif job.job_type == "proactive":
                    item.proactive_status = "failed"
                    item.proactive_error = str(exc)
                db.add(item)
            if job.attempts >= MAX_JOB_ATTEMPTS:
                job.status = "dead_letter"
                existing_dl = db.execute(
                    select(DeadLetterJob).where(DeadLetterJob.job_id == job.id)
                ).scalar_one_or_none()
                if existing_dl:
                    existing_dl.attempts = job.attempts
                    existing_dl.last_error = str(exc)
                    existing_dl.status = "open"
                    db.add(existing_dl)
                else:
                    db.add(
                        DeadLetterJob(
                            job_id=job.id,
                            item_id=job.item_id,
                            job_type=job.job_type,
                            attempts=job.attempts,
                            last_error=str(exc),
                            status="open",
                        )
                    )
        finally:
            db.add(job)
            db.commit()

    return {
        "processed": processed,
        "succeeded": succeeded,
        "failed": failed,
        "job_ids": job_ids,
    }
