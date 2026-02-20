from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FeedbackEvent
from app.schemas import FeedbackRecord


def export_feedback(db: Session, limit: int = 500) -> list[FeedbackRecord]:
    rows = db.execute(select(FeedbackEvent).order_by(FeedbackEvent.created_at.desc()).limit(limit)).scalars().all()
    return [
        FeedbackRecord(
            id=row.id,
            item_id=row.item_id,
            feedback_type=row.feedback_type,
            before_value=row.before_value,
            after_value=row.after_value,
            source=row.source,
            notes=row.notes,
            created_at=row.created_at,
        )
        for row in rows
    ]
