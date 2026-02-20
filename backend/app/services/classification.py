from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import ClassDefinition, FeedbackEvent, Item, ItemClassification
from app.schemas import ClassificationResponse, ClassificationResult
from app.services.model_assist import score_keywords_with_model_assist


AUTO_ACCEPT_THRESHOLD = 0.75
REVIEW_THRESHOLD = 0.45
FALLBACK_CLASS_SLUG = "unsorted_needs_review"

CLASS_RULES: list[dict[str, Any]] = [
    {
        "slug": "personal_important_documents",
        "display_name": "Personal/Important_Documents",
        "description": "Tax, identity, legal, and core personal documents.",
        "rule_id": "class_personal_docs_v1",
        "keywords": ["tax", "irs", "w2", "1099", "document", "id", "passport", "receipt"],
    },
    {
        "slug": "health_doctors",
        "display_name": "Health/Doctors",
        "description": "Doctor visits, treatment notes, and care plans.",
        "rule_id": "class_health_doctors_v1",
        "keywords": ["doctor", "provider", "clinic", "visit", "prescription", "diagnosis"],
    },
    {
        "slug": "health_lab_work",
        "display_name": "Health/Lab_Work",
        "description": "Lab reports, diagnostics, and test results.",
        "rule_id": "class_health_lab_v1",
        "keywords": ["lab", "panel", "test", "blood", "result", "diagnostic"],
    },
    {
        "slug": "work_tools",
        "display_name": "Work/Tools",
        "description": "Work planning artifacts, tools, and execution notes.",
        "rule_id": "class_work_tools_v1",
        "keywords": ["sprint", "milestone", "roadmap", "blocker", "delivery", "project"],
    },
    {
        "slug": "personal_financial",
        "display_name": "Personal/Financial",
        "description": "Bills, accounts, statements, and personal finances.",
        "rule_id": "class_personal_financial_v1",
        "keywords": ["bank", "bill", "statement", "invoice", "payment", "account", "financial"],
    },
    {
        "slug": FALLBACK_CLASS_SLUG,
        "display_name": "Unsorted/Needs_Review",
        "description": "Fallback bucket for uncertain classifications.",
        "rule_id": "class_fallback_v1",
        "keywords": [],
    },
]


def ensure_class_definitions(db: Session) -> None:
    existing_by_slug = {
        row.slug: row for row in db.execute(select(ClassDefinition)).scalars().all()
    }
    changed = False
    for rule in CLASS_RULES:
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
            ClassDefinition(
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
    if not keywords:
        return 0.0, []

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


def _select_best_rule(item: Item) -> tuple[dict[str, Any], float, list[str]]:
    best_rule: dict[str, Any] | None = None
    best_confidence = 0.0
    best_terms: list[str] = []
    for rule in CLASS_RULES:
        if rule["slug"] == FALLBACK_CLASS_SLUG:
            continue
        confidence, terms = _score_rule(item, rule["keywords"])
        if REVIEW_THRESHOLD <= confidence < AUTO_ACCEPT_THRESHOLD:
            assist_conf, assist_terms = score_keywords_with_model_assist(
                f"{item.title}\n{item.description}\n{item.content}\n{item.taxonomy_path or ''}",
                rule["keywords"],
            )
            if assist_conf > confidence:
                confidence = assist_conf
                terms = sorted(set(terms + assist_terms))
        if confidence > best_confidence:
            best_confidence = confidence
            best_rule = rule
            best_terms = terms

    if best_rule is None or best_confidence < REVIEW_THRESHOLD:
        fallback_rule = next(rule for rule in CLASS_RULES if rule["slug"] == FALLBACK_CLASS_SLUG)
        return fallback_rule, 0.40, ["fallback"]
    return best_rule, best_confidence, best_terms


def run_classification_for_item(db: Session, item: Item) -> str:
    ensure_class_definitions(db)
    rule, confidence, matched_terms = _select_best_rule(item)

    class_def = db.execute(
        select(ClassDefinition).where(ClassDefinition.slug == rule["slug"])
    ).scalar_one()

    status = "accepted" if confidence >= AUTO_ACCEPT_THRESHOLD else "needs_review"
    if rule["slug"] == FALLBACK_CLASS_SLUG:
        status = "needs_review"

    row = db.execute(
        select(ItemClassification).where(ItemClassification.item_id == item.id)
    ).scalar_one_or_none()

    if row and row.is_manual_override:
        # Preserve explicit user decision.
        item.classification_status = row.status
        item.classification_label = db.execute(
            select(ClassDefinition.display_name).where(ClassDefinition.id == row.class_id)
        ).scalar_one_or_none()
        item.classification_confidence = row.confidence
        item.classified_at = datetime.utcnow()
        item.classification_error = None
        db.add(item)
        db.commit()
        return item.classification_label or ""

    source_name = "model_assist_v1" if confidence >= AUTO_ACCEPT_THRESHOLD and len(matched_terms) >= 3 else "rule_classifier_v1"

    if row:
        row.class_id = class_def.id
        row.confidence = confidence
        row.status = status
        row.source = source_name
        row.rule_id = rule["rule_id"]
        row.matched_terms = ", ".join(matched_terms)
        row.is_manual_override = False
        db.add(row)
    else:
        db.add(
            ItemClassification(
                item_id=item.id,
                class_id=class_def.id,
                confidence=confidence,
                status=status,
                source=source_name,
                rule_id=rule["rule_id"],
                matched_terms=", ".join(matched_terms),
                is_manual_override=False,
            )
        )
    db.commit()

    item.classification_status = status
    item.classification_error = None
    item.classification_label = class_def.display_name
    item.classification_confidence = confidence
    item.classified_at = datetime.utcnow()
    db.add(item)
    db.commit()
    return class_def.display_name


def get_item_classification(db: Session, item_id: str) -> ClassificationResult | None:
    row = db.execute(
        select(ItemClassification, ClassDefinition)
        .join(ClassDefinition, ClassDefinition.id == ItemClassification.class_id)
        .where(ItemClassification.item_id == item_id)
    ).first()

    if not row:
        return None

    item_classification, class_def = row
    return ClassificationResult(
        item_classification_id=item_classification.id,
        class_id=class_def.id,
        class_slug=class_def.slug,
        display_name=class_def.display_name,
        confidence=item_classification.confidence,
        status=item_classification.status,
        source=item_classification.source,
        rule_id=item_classification.rule_id,
        matched_terms=item_classification.matched_terms,
        is_manual_override=item_classification.is_manual_override,
        created_at=item_classification.created_at,
        updated_at=item_classification.updated_at,
    )


def build_classification_response(db: Session, item: Item) -> ClassificationResponse:
    current = get_item_classification(db, item.id)
    return ClassificationResponse(
        item_id=item.id,
        classification_status=item.classification_status,
        classification_label=item.classification_label,
        classification_confidence=item.classification_confidence,
        classification=current,
    )


def override_item_classification(
    db: Session,
    item: Item,
    class_slug: str,
    action: str,
    confidence: float,
    notes: str | None = None,
) -> ClassificationResponse:
    ensure_class_definitions(db)
    class_def = db.execute(
        select(ClassDefinition).where(ClassDefinition.slug == class_slug)
    ).scalar_one_or_none()
    if class_def is None:
        class_def = ClassDefinition(
            slug=class_slug,
            display_name=class_slug.replace("_", " ").title(),
            description="Created from manual override.",
            is_active=True,
        )
        db.add(class_def)
        db.commit()
        db.refresh(class_def)

    row = db.execute(
        select(ItemClassification).where(ItemClassification.item_id == item.id)
    ).scalar_one_or_none()
    status = "accepted" if action == "approve" else "rejected"
    matched_terms = f"manual_override: {notes}" if notes else "manual_override"

    before_value = None
    if row:
        before_value = f"{row.status}:{row.confidence}:{row.class_id}"
        row.class_id = class_def.id
        row.confidence = confidence
        row.status = status
        row.source = "manual_override"
        row.rule_id = "manual_override_v1"
        row.matched_terms = matched_terms
        row.is_manual_override = True
        db.add(row)
    else:
        db.add(
            ItemClassification(
                item_id=item.id,
                class_id=class_def.id,
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
            feedback_type="classification_override",
            before_value=before_value,
            after_value=f"{status}:{confidence}:{class_slug}",
            source="manual_override",
            notes=notes,
        )
    )
    db.commit()

    item.classification_status = status
    item.classification_error = None
    item.classification_label = class_def.display_name
    item.classification_confidence = confidence
    item.classified_at = datetime.utcnow()
    db.add(item)
    db.commit()
    return build_classification_response(db, item)


def list_classification_needs_review(db: Session, limit: int = 50) -> list[ClassificationResponse]:
    item_ids = db.execute(
        select(ItemClassification.item_id)
        .where(ItemClassification.status == "needs_review")
        .limit(limit)
    ).scalars().all()
    if not item_ids:
        return []
    items = db.execute(select(Item).where(Item.id.in_(item_ids))).scalars().all()
    return [build_classification_response(db, item) for item in items]
