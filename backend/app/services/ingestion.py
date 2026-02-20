from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Item, Job
from app.schemas import ItemCreate


def _enqueue_job(db: Session, item_id: str, job_type: str) -> Job:
    job = Job(item_id=item_id, job_type=job_type, status="pending", attempts=0)
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def ingest_item(db: Session, payload: ItemCreate) -> tuple[Item, bool, Job | None]:
    # Idempotency key has highest priority for strict dedupe semantics.
    if payload.idempotency_key:
        existing = db.execute(
            select(Item).where(Item.idempotency_key == payload.idempotency_key)
        ).scalar_one_or_none()
        if existing:
            return existing, False, None

    existing = None
    if payload.source_ref:
        existing = db.execute(
            select(Item).where(Item.source == payload.source, Item.source_ref == payload.source_ref)
        ).scalar_one_or_none()

    now = datetime.utcnow()
    created = False
    if existing:
        existing.title = payload.title
        existing.description = payload.description
        existing.content = payload.content
        existing.taxonomy_path = payload.taxonomy_path
        existing.status = "pending"
        existing.error_reason = None
        existing.tagging_status = "pending"
        existing.tagging_error = None
        existing.classification_status = "pending"
        existing.classification_error = None
        existing.insight_status = "pending"
        existing.insight_error = None
        existing.proactive_status = "pending"
        existing.proactive_error = None
        existing.ingested_at = now
        db.add(existing)
        db.commit()
        db.refresh(existing)
        item = existing
    else:
        item = Item(
            id=str(uuid4()),
            source=payload.source,
            source_ref=payload.source_ref,
            idempotency_key=payload.idempotency_key,
            title=payload.title,
            description=payload.description,
            content=payload.content,
            taxonomy_path=payload.taxonomy_path,
            status="pending",
            tagging_status="pending",
            classification_status="pending",
            insight_status="pending",
            proactive_status="pending",
            ingested_at=now,
        )
        db.add(item)
        try:
            db.commit()
        except IntegrityError:
            db.rollback()
            # Handle race on unique keys by returning the matching row.
            fallback = None
            if payload.idempotency_key:
                fallback = db.execute(
                    select(Item).where(Item.idempotency_key == payload.idempotency_key)
                ).scalar_one_or_none()
            if not fallback and payload.source_ref:
                fallback = db.execute(
                    select(Item).where(Item.source == payload.source, Item.source_ref == payload.source_ref)
                ).scalar_one_or_none()
            if not fallback:
                raise
            return fallback, False, None

        db.refresh(item)
        created = True

    embed_job = _enqueue_job(db, item.id, "embed")
    _enqueue_job(db, item.id, "tag")
    _enqueue_job(db, item.id, "classify")
    _enqueue_job(db, item.id, "insight")
    _enqueue_job(db, item.id, "proactive")
    return item, created, embed_job
