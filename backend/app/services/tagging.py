from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import FeedbackEvent, Item, ItemTag, TagDefinition
from app.schemas import TagResult, TaggingResponse
from app.services.model_assist import score_keywords_with_model_assist


AUTO_ACCEPT_THRESHOLD = 0.75
REVIEW_THRESHOLD = 0.45

TAG_RULES: list[dict[str, Any]] = [
    {
        "slug": "tax_documents",
        "display_name": "Tax Documents",
        "description": "Tax filings, IRS records, and payment confirmations.",
        "rule_id": "tax_docs_v1",
        "keywords": ["tax", "irs", "w2", "1099", "filing", "refund", "receipt"],
    },
    {
        "slug": "medical_records",
        "display_name": "Medical Records",
        "description": "Clinical notes, doctors, and lab reports.",
        "rule_id": "medical_records_v1",
        "keywords": ["doctor", "medical", "lab", "diagnosis", "prescription", "blood pressure"],
    },
    {
        "slug": "project_management",
        "display_name": "Project Management",
        "description": "Tasks, sprints, milestones, and delivery planning.",
        "rule_id": "project_mgmt_v1",
        "keywords": ["project", "sprint", "milestone", "roadmap", "blocker", "delivery"],
    },
    {
        "slug": "financial_records",
        "display_name": "Financial Records",
        "description": "Banking, bills, statements, and payments.",
        "rule_id": "financial_records_v1",
        "keywords": ["bank", "invoice", "payment", "statement", "bill", "account", "financial"],
    },
]


def ensure_tag_definitions(db: Session) -> None:
    existing_by_slug = {
        row.slug: row for row in db.execute(select(TagDefinition)).scalars().all()
    }
    changed = False
    for rule in TAG_RULES:
        existing = existing_by_slug.get(rule["slug"])
        if existing:
            if (
                existing.display_name != rule["display_name"]
                or existing.description != rule["description"]
                or not existing.is_active
            ):
                existing.display_name = rule["display_name"]
                existing.description = rule["description"]
                existing.is_active = True
                db.add(existing)
                changed = True
            continue

        db.add(
            TagDefinition(
                slug=rule["slug"],
                display_name=rule["display_name"],
                description=rule["description"],
                is_active=True,
            )
        )
        changed = True

    if changed:
        db.commit()


def _score_rule(item: Item, keywords: list[str]) -> tuple[float, list[str]]:
    title = (item.title or "").lower()
    description = (item.description or "").lower()
    content = (item.content or "").lower()
    taxonomy = (item.taxonomy_path or "").lower()

    matched_terms: list[str] = []
    score_points = 0.0
    for keyword in keywords:
        kw = keyword.lower()
        matched = False
        if kw in title:
            score_points += 2.0
            matched = True
        if kw in description:
            score_points += 1.5
            matched = True
        if kw in content:
            score_points += 1.0
            matched = True
        if kw in taxonomy:
            score_points += 1.5
            matched = True
        if matched:
            matched_terms.append(keyword)

    denom = max(1.0, (2.0 * len(keywords)) + 2.0)
    confidence = min(1.0, score_points / denom)
    return confidence, sorted(set(matched_terms))


def run_tagging_for_item(db: Session, item: Item) -> int:
    text_size = len((item.title or "").strip()) + len((item.description or "").strip()) + len((item.content or "").strip())
    if text_size < 5:
        item.tagging_status = "failed"
        item.tagging_error = "Insufficient text for tagging."
        item.tag_count = 0
        item.tagged_at = datetime.utcnow()
        db.add(item)
        db.commit()
        return 0

    ensure_tag_definitions(db)
    tag_defs_by_slug = {
        row.slug: row
        for row in db.execute(select(TagDefinition).where(TagDefinition.is_active.is_(True))).scalars().all()
    }

    existing_tags = db.execute(
        select(ItemTag).where(ItemTag.item_id == item.id)
    ).scalars().all()
    existing_by_tag_id = {row.tag_id: row for row in existing_tags}

    for rule in TAG_RULES:
        tag_def = tag_defs_by_slug.get(rule["slug"])
        if tag_def is None:
            continue

        confidence, matched_terms = _score_rule(item, rule["keywords"])
        if REVIEW_THRESHOLD <= confidence < AUTO_ACCEPT_THRESHOLD:
            assist_conf, assist_terms = score_keywords_with_model_assist(
                f"{item.title}\n{item.description}\n{item.content}\n{item.taxonomy_path or ''}",
                rule["keywords"],
            )
            if assist_conf > confidence:
                confidence = assist_conf
                matched_terms = sorted(set(matched_terms + assist_terms))
        if confidence < REVIEW_THRESHOLD:
            # Keep any manual override untouched; otherwise leave the tag absent.
            continue

        status = "accepted" if confidence >= AUTO_ACCEPT_THRESHOLD else "needs_review"
        source_name = "model_assist_v1" if confidence >= AUTO_ACCEPT_THRESHOLD and len(matched_terms) >= 3 else "rule_engine_v1"
        existing = existing_by_tag_id.get(tag_def.id)
        if existing and existing.is_manual_override:
            continue

        if existing:
            existing.confidence = confidence
            existing.status = status
            existing.source = source_name
            existing.rule_id = rule["rule_id"]
            existing.matched_terms = ", ".join(matched_terms)
            existing.is_manual_override = False
            db.add(existing)
        else:
            db.add(
                ItemTag(
                    item_id=item.id,
                    tag_id=tag_def.id,
                    confidence=confidence,
                    status=status,
                    source=source_name,
                    rule_id=rule["rule_id"],
                    matched_terms=", ".join(matched_terms),
                    is_manual_override=False,
                )
            )

    db.commit()

    tag_count = db.execute(
        select(func.count(ItemTag.id)).where(
            ItemTag.item_id == item.id, ItemTag.status.in_(["accepted", "needs_review"])
        )
    ).scalar_one()
    item.tag_count = int(tag_count or 0)
    item.tagging_status = "tagged"
    item.tagging_error = None
    item.tagged_at = datetime.utcnow()
    db.add(item)
    db.commit()
    return item.tag_count


def get_item_tags(db: Session, item_id: str) -> list[TagResult]:
    rows = db.execute(
        select(ItemTag, TagDefinition)
        .join(TagDefinition, TagDefinition.id == ItemTag.tag_id)
        .where(ItemTag.item_id == item_id)
        .order_by(ItemTag.confidence.desc(), TagDefinition.slug.asc())
    ).all()

    return [
        TagResult(
            item_tag_id=item_tag.id,
            tag_id=tag_def.id,
            tag_slug=tag_def.slug,
            display_name=tag_def.display_name,
            confidence=item_tag.confidence,
            status=item_tag.status,
            source=item_tag.source,
            rule_id=item_tag.rule_id,
            matched_terms=item_tag.matched_terms,
            is_manual_override=item_tag.is_manual_override,
            created_at=item_tag.created_at,
            updated_at=item_tag.updated_at,
        )
        for item_tag, tag_def in rows
    ]


def build_tagging_response(db: Session, item: Item) -> TaggingResponse:
    tags = get_item_tags(db, item.id)
    return TaggingResponse(
        item_id=item.id,
        tagging_status=item.tagging_status,
        tag_count=item.tag_count,
        tags=tags,
    )


def override_item_tag(
    db: Session,
    item: Item,
    tag_slug: str,
    action: str,
    confidence: float,
    notes: str | None = None,
) -> TaggingResponse:
    ensure_tag_definitions(db)
    tag_def = db.execute(
        select(TagDefinition).where(TagDefinition.slug == tag_slug)
    ).scalar_one_or_none()
    if tag_def is None:
        tag_def = TagDefinition(
            slug=tag_slug,
            display_name=tag_slug.replace("_", " ").title(),
            description="Created from manual override.",
            is_active=True,
        )
        db.add(tag_def)
        db.commit()
        db.refresh(tag_def)

    row = db.execute(
        select(ItemTag).where(ItemTag.item_id == item.id, ItemTag.tag_id == tag_def.id)
    ).scalar_one_or_none()

    status = "accepted" if action == "approve" else "rejected"
    matched_terms = f"manual_override: {notes}" if notes else "manual_override"
    if row:
        before_value = row.status
        row.status = status
        row.confidence = confidence
        row.source = "manual_override"
        row.rule_id = "manual_override_v1"
        row.matched_terms = matched_terms
        row.is_manual_override = True
        db.add(row)
    else:
        before_value = None
        db.add(
            ItemTag(
                item_id=item.id,
                tag_id=tag_def.id,
                confidence=confidence,
                status=status,
                source="manual_override",
                rule_id="manual_override_v1",
                matched_terms=matched_terms,
                is_manual_override=True,
            )
        )

    db.commit()
    db.add(
        FeedbackEvent(
            item_id=item.id,
            feedback_type="tag_override",
            before_value=before_value,
            after_value=f"{tag_slug}:{status}:{confidence}",
            source="manual_override",
            notes=notes,
        )
    )
    db.commit()
    item.tag_count = int(
        db.execute(
            select(func.count(ItemTag.id)).where(
                ItemTag.item_id == item.id, ItemTag.status.in_(["accepted", "needs_review"])
            )
        ).scalar_one()
        or 0
    )
    item.tagging_status = "tagged"
    item.tagged_at = datetime.utcnow()
    db.add(item)
    db.commit()
    return build_tagging_response(db, item)


def list_items_with_needs_review(db: Session, limit: int = 50) -> list[TaggingResponse]:
    item_ids = db.execute(
        select(ItemTag.item_id)
        .where(ItemTag.status == "needs_review")
        .group_by(ItemTag.item_id)
        .limit(limit)
    ).scalars().all()

    if not item_ids:
        return []

    items = db.execute(select(Item).where(Item.id.in_(item_ids))).scalars().all()
    return [build_tagging_response(db, item) for item in items]
