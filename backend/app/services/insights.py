from __future__ import annotations

import json
from datetime import datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import (
    ClassDefinition,
    Insight,
    Item,
    ItemClassification,
    ItemTag,
    SummaryCache,
    TagDefinition,
)
from app.schemas import (
    CrossDomainBriefResponse,
    InsightRecord,
    ItemSummaryResponse,
    WindowSummaryResponse,
)


GENERATOR_VERSION = "insights_v1"


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


def _insight_to_record(insight: Insight) -> InsightRecord:
    return InsightRecord(
        id=insight.id,
        insight_type=insight.insight_type,
        title=insight.title,
        body=insight.body,
        confidence=insight.confidence,
        status=insight.status,
        source_item_ids=_deserialize_ids(insight.source_item_ids),
        time_range_start=insight.time_range_start,
        time_range_end=insight.time_range_end,
        generator_version=insight.generator_version,
        created_at=insight.created_at,
        updated_at=insight.updated_at,
    )


def _cache_get(db: Session, cache_key: str) -> dict | None:
    row = db.execute(select(SummaryCache).where(SummaryCache.cache_key == cache_key)).scalar_one_or_none()
    if not row:
        return None
    try:
        return json.loads(row.payload)
    except json.JSONDecodeError:
        return None


def _cache_set(db: Session, cache_key: str, payload: dict) -> None:
    serialized = json.dumps(payload)
    row = db.execute(select(SummaryCache).where(SummaryCache.cache_key == cache_key)).scalar_one_or_none()
    if row:
        row.payload = serialized
        db.add(row)
    else:
        db.add(SummaryCache(cache_key=cache_key, payload=serialized))
    db.commit()


def _item_evidence(db: Session, item_id: str) -> list[str]:
    tags = db.execute(
        select(TagDefinition.display_name)
        .join(ItemTag, ItemTag.tag_id == TagDefinition.id)
        .where(ItemTag.item_id == item_id, ItemTag.status.in_(["accepted", "needs_review"]))
        .order_by(ItemTag.confidence.desc())
        .limit(3)
    ).scalars().all()
    classification = db.execute(
        select(ClassDefinition.display_name)
        .join(ItemClassification, ItemClassification.class_id == ClassDefinition.id)
        .where(ItemClassification.item_id == item_id)
    ).scalar_one_or_none()

    evidence = [f"tag:{t}" for t in tags]
    if classification:
        evidence.append(f"class:{classification}")
    return evidence


def build_item_summary(db: Session, item_id: str) -> ItemSummaryResponse:
    item = db.get(Item, item_id)
    if not item:
        raise ValueError("Item not found")

    snippet = (item.content or "").strip()
    if len(snippet) > 220:
        snippet = snippet[:220].rstrip() + "..."

    evidence = _item_evidence(db, item.id)
    summary = (
        f"{item.title}: {item.description or 'No description.'} "
        f"Primary content: {snippet or 'No content.'}"
    )
    confidence = 0.80 if evidence else 0.60
    return ItemSummaryResponse(
        item_id=item.id,
        summary=summary,
        evidence=evidence,
        confidence=confidence,
        generated_at=datetime.utcnow(),
    )


def build_window_summary(
    db: Session,
    days: int,
    source: str | None = None,
    taxonomy_prefix: str | None = None,
    use_cache: bool = True,
) -> WindowSummaryResponse:
    cache_key = f"window:{days}:{source or '*'}:{taxonomy_prefix or '*'}"
    if use_cache:
        cached = _cache_get(db, cache_key)
        if cached:
            return WindowSummaryResponse(**cached)

    since = datetime.utcnow() - timedelta(days=days)
    stmt = select(Item).where(Item.created_at >= since)
    if source:
        stmt = stmt.where(Item.source == source)
    if taxonomy_prefix:
        stmt = stmt.where(Item.taxonomy_path.like(f"{taxonomy_prefix}%"))
    items = db.execute(stmt).scalars().all()

    item_count = len(items)
    tagged_count = sum(1 for i in items if (i.tag_count or 0) > 0)
    classified_count = sum(1 for i in items if i.classification_label)

    top_classes = db.execute(
        select(ClassDefinition.display_name, func.count(ItemClassification.id))
        .join(ItemClassification, ItemClassification.class_id == ClassDefinition.id)
        .join(Item, Item.id == ItemClassification.item_id)
        .where(Item.created_at >= since)
        .group_by(ClassDefinition.display_name)
        .order_by(func.count(ItemClassification.id).desc())
        .limit(3)
    ).all()

    class_str = ", ".join([f"{name}({count})" for name, count in top_classes]) if top_classes else "none"
    summary = (
        f"In the last {days} days: {item_count} items ingested, "
        f"{tagged_count} tagged, {classified_count} classified. "
        f"Top classes: {class_str}."
    )
    evidence = [f"items:{item_count}", f"tagged:{tagged_count}", f"classified:{classified_count}"]
    confidence = 0.85 if item_count > 0 else 0.50
    payload = WindowSummaryResponse(
        days=days,
        summary=summary,
        evidence=evidence,
        confidence=confidence,
        generated_at=datetime.utcnow(),
    ).model_dump(mode="json")
    _cache_set(db, cache_key, payload)
    return WindowSummaryResponse(**payload)


def build_cross_domain_brief(db: Session, days: int, use_cache: bool = True) -> CrossDomainBriefResponse:
    cache_key = f"cross_domain:{days}"
    if use_cache:
        cached = _cache_get(db, cache_key)
        if cached:
            return CrossDomainBriefResponse(**cached)

    since = datetime.utcnow() - timedelta(days=days)
    source_counts = db.execute(
        select(Item.source, func.count(Item.id))
        .where(Item.created_at >= since)
        .group_by(Item.source)
        .order_by(func.count(Item.id).desc())
        .limit(5)
    ).all()
    class_counts = db.execute(
        select(ClassDefinition.display_name, func.count(ItemClassification.id))
        .join(ItemClassification, ItemClassification.class_id == ClassDefinition.id)
        .join(Item, Item.id == ItemClassification.item_id)
        .where(Item.created_at >= since)
        .group_by(ClassDefinition.display_name)
        .order_by(func.count(ItemClassification.id).desc())
        .limit(5)
    ).all()
    tag_counts = db.execute(
        select(TagDefinition.display_name, func.count(ItemTag.id))
        .join(ItemTag, ItemTag.tag_id == TagDefinition.id)
        .join(Item, Item.id == ItemTag.item_id)
        .where(Item.created_at >= since)
        .group_by(TagDefinition.display_name)
        .order_by(func.count(ItemTag.id).desc())
        .limit(5)
    ).all()

    source_line = ", ".join([f"{s}:{c}" for s, c in source_counts]) if source_counts else "none"
    class_line = ", ".join([f"{s}:{c}" for s, c in class_counts]) if class_counts else "none"
    tag_line = ", ".join([f"{s}:{c}" for s, c in tag_counts]) if tag_counts else "none"

    summary = (
        f"Cross-domain memory brief ({days}d): sources [{source_line}], "
        f"classes [{class_line}], tags [{tag_line}]."
    )
    sections = [
        f"Source activity: {source_line}",
        f"Classification focus: {class_line}",
        f"Tag focus: {tag_line}",
    ]
    evidence = [
        f"sources:{len(source_counts)}",
        f"classes:{len(class_counts)}",
        f"tags:{len(tag_counts)}",
    ]
    confidence = 0.82 if source_counts or class_counts or tag_counts else 0.50

    payload = CrossDomainBriefResponse(
        summary=summary,
        sections=sections,
        evidence=evidence,
        confidence=confidence,
        generated_at=datetime.utcnow(),
    ).model_dump(mode="json")
    _cache_set(db, cache_key, payload)
    return CrossDomainBriefResponse(**payload)


def generate_item_insight(db: Session, item: Item) -> InsightRecord:
    item_summary = build_item_summary(db, item.id)
    insight = Insight(
        insight_type="item_summary",
        title=f"Item insight: {item.title[:80]}",
        body=item_summary.summary,
        confidence=item_summary.confidence,
        status="generated",
        source_item_ids=_serialize_ids([item.id]),
        time_range_start=None,
        time_range_end=None,
        generator_version=GENERATOR_VERSION,
    )
    db.add(insight)
    db.commit()
    db.refresh(insight)

    item.insight_status = "generated"
    item.insight_error = None
    item.insight_count = int(item.insight_count or 0) + 1
    item.insighted_at = datetime.utcnow()
    db.add(item)
    db.commit()
    return _insight_to_record(insight)


def list_insights(db: Session, limit: int = 50, insight_type: str | None = None) -> list[InsightRecord]:
    stmt = select(Insight).order_by(Insight.created_at.desc()).limit(limit)
    if insight_type:
        stmt = select(Insight).where(Insight.insight_type == insight_type).order_by(Insight.created_at.desc()).limit(limit)
    rows = db.execute(stmt).scalars().all()
    return [_insight_to_record(row) for row in rows]


def get_insight(db: Session, insight_id: int) -> InsightRecord | None:
    row = db.get(Insight, insight_id)
    if not row:
        return None
    return _insight_to_record(row)
