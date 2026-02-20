from __future__ import annotations

import json
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Item, ItemClassification, ItemTag, ProactiveSignal, TimelineEvent
from app.schemas import ProactiveSignalRecord, TimelineEventRecord


GENERATOR_VERSION = "phase6_proactive_v1"


def _serialize_ids(ids: list[str]) -> str:
    return json.dumps(ids)


def _deserialize_ids(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        data = json.loads(value)
        if isinstance(data, list):
            return [str(x) for x in data]
    except json.JSONDecodeError:
        pass
    return []


def _event_to_record(event: TimelineEvent) -> TimelineEventRecord:
    return TimelineEventRecord(
        id=event.id,
        item_id=event.item_id,
        event_type=event.event_type,
        event_time=event.event_time,
        title=event.title,
        details=event.details,
        source=event.source,
        created_at=event.created_at,
        updated_at=event.updated_at,
    )


def _signal_to_record(signal: ProactiveSignal) -> ProactiveSignalRecord:
    return ProactiveSignalRecord(
        id=signal.id,
        signal_type=signal.signal_type,
        severity=signal.severity,
        title=signal.title,
        recommendation=signal.recommendation,
        confidence=signal.confidence,
        status=signal.status,
        source_item_ids=_deserialize_ids(signal.source_item_ids),
        generator_version=signal.generator_version,
        created_at=signal.created_at,
        updated_at=signal.updated_at,
    )


def _upsert_timeline_event(
    db: Session,
    item: Item,
    event_type: str,
    title: str,
    details: str | None = None,
    event_time: datetime | None = None,
) -> None:
    existing = db.execute(
        select(TimelineEvent).where(TimelineEvent.item_id == item.id, TimelineEvent.event_type == event_type)
    ).scalar_one_or_none()
    when = event_time or datetime.utcnow()
    if existing:
        existing.title = title
        existing.details = details
        existing.event_time = when
        db.add(existing)
    else:
        db.add(
            TimelineEvent(
                item_id=item.id,
                event_type=event_type,
                event_time=when,
                title=title,
                details=details,
            )
        )
    db.commit()


def generate_timeline_for_item(db: Session, item: Item) -> int:
    count_before = db.execute(
        select(TimelineEvent).where(TimelineEvent.item_id == item.id)
    ).scalars().all()
    before_len = len(count_before)

    _upsert_timeline_event(
        db,
        item=item,
        event_type="ingested",
        title=f"Item ingested: {item.title}",
        details=f"Source={item.source}, taxonomy={item.taxonomy_path or 'n/a'}",
        event_time=item.ingested_at or item.created_at or datetime.utcnow(),
    )

    if item.embedded_at:
        _upsert_timeline_event(
            db,
            item=item,
            event_type="embedded",
            title="Item embedded for semantic search",
            details=f"Chunks={item.chunk_count}, model={item.embedding_model_version or 'unknown'}",
            event_time=item.embedded_at,
        )

    if item.tagged_at:
        _upsert_timeline_event(
            db,
            item=item,
            event_type="tagged",
            title="Automated tagging completed",
            details=f"Tag count={item.tag_count}",
            event_time=item.tagged_at,
        )

    if item.classified_at:
        _upsert_timeline_event(
            db,
            item=item,
            event_type="classified",
            title="Automated classification completed",
            details=f"Class={item.classification_label or 'n/a'}, confidence={item.classification_confidence}",
            event_time=item.classified_at,
        )

    if item.insighted_at:
        _upsert_timeline_event(
            db,
            item=item,
            event_type="insighted",
            title="Insight generation completed",
            details=f"Insight count={item.insight_count}",
            event_time=item.insighted_at,
        )

    after_len = len(
        db.execute(select(TimelineEvent).where(TimelineEvent.item_id == item.id)).scalars().all()
    )
    return max(0, after_len - before_len)


def _create_signal(
    db: Session,
    signal_type: str,
    severity: str,
    title: str,
    recommendation: str,
    confidence: float,
    item_ids: list[str],
) -> None:
    db.add(
        ProactiveSignal(
            signal_type=signal_type,
            severity=severity,
            title=title,
            recommendation=recommendation,
            confidence=confidence,
            status="open",
            source_item_ids=_serialize_ids(item_ids),
            generator_version=GENERATOR_VERSION,
        )
    )
    db.commit()


def generate_proactive_for_item(db: Session, item: Item) -> int:
    created = 0

    if item.classification_status == "needs_review":
        _create_signal(
            db,
            signal_type="classification_review",
            severity="medium",
            title=f"Classification needs review for '{item.title[:60]}'",
            recommendation="Review and override classification if needed.",
            confidence=0.80,
            item_ids=[item.id],
        )
        created += 1

    needs_review_tag_count = db.execute(
        select(ItemTag).where(ItemTag.item_id == item.id, ItemTag.status == "needs_review")
    ).scalars().all()
    if needs_review_tag_count:
        _create_signal(
            db,
            signal_type="tag_review",
            severity="medium",
            title=f"Tag review needed for '{item.title[:60]}'",
            recommendation="Approve/reject uncertain tags to improve future automation.",
            confidence=0.78,
            item_ids=[item.id],
        )
        created += 1

    if item.source == "notes" and "tax" in (item.content or "").lower():
        _create_signal(
            db,
            signal_type="tax_followup",
            severity="low",
            title="Tax-related note detected",
            recommendation="Confirm all supporting tax documents are linked and classified.",
            confidence=0.70,
            item_ids=[item.id],
        )
        created += 1

    item.proactive_status = "generated"
    item.proactive_error = None
    item.proactive_count = int(item.proactive_count or 0) + created
    item.proactive_at = datetime.utcnow()
    db.add(item)
    db.commit()
    return created


def build_daily_digest(db: Session, days: int = 7) -> str:
    since = datetime.utcnow() - timedelta(days=days)
    items = db.execute(select(Item).where(Item.created_at >= since)).scalars().all()
    open_signals = db.execute(
        select(ProactiveSignal).where(ProactiveSignal.created_at >= since, ProactiveSignal.status == "open")
    ).scalars().all()
    top_classes = db.execute(
        select(Item.classification_label).where(
            Item.created_at >= since, Item.classification_label.is_not(None)
        )
    ).scalars().all()

    class_counts: dict[str, int] = {}
    for c in top_classes:
        class_counts[c] = class_counts.get(c, 0) + 1
    top_class_lines = sorted(class_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    top_class_str = ", ".join([f"{name}({count})" for name, count in top_class_lines]) or "none"

    return (
        f"Last {days} days digest: {len(items)} items captured, "
        f"{len(open_signals)} open proactive signals, top classes: {top_class_str}."
    )


def list_timeline_events(
    db: Session,
    days: int = 30,
    event_type: str | None = None,
    limit: int = 100,
) -> list[TimelineEventRecord]:
    since = datetime.utcnow() - timedelta(days=days)
    stmt = select(TimelineEvent).where(TimelineEvent.event_time >= since).order_by(TimelineEvent.event_time.desc()).limit(limit)
    if event_type:
        stmt = (
            select(TimelineEvent)
            .where(TimelineEvent.event_time >= since, TimelineEvent.event_type == event_type)
            .order_by(TimelineEvent.event_time.desc())
            .limit(limit)
        )
    rows = db.execute(stmt).scalars().all()
    return [_event_to_record(row) for row in rows]


def list_proactive_signals(
    db: Session,
    status: str | None = None,
    limit: int = 100,
) -> list[ProactiveSignalRecord]:
    stmt = select(ProactiveSignal).order_by(ProactiveSignal.created_at.desc()).limit(limit)
    if status:
        stmt = (
            select(ProactiveSignal)
            .where(ProactiveSignal.status == status)
            .order_by(ProactiveSignal.created_at.desc())
            .limit(limit)
        )
    rows = db.execute(stmt).scalars().all()
    return [_signal_to_record(row) for row in rows]


def update_signal_status(db: Session, signal_id: int, status: str) -> ProactiveSignalRecord | None:
    row = db.get(ProactiveSignal, signal_id)
    if not row:
        return None
    row.status = status
    db.add(row)
    db.commit()
    db.refresh(row)
    return _signal_to_record(row)
