from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Item(Base):
    __tablename__ = "items"
    __table_args__ = (
        UniqueConstraint("idempotency_key", name="uq_item_idempotency_key"),
        UniqueConstraint("source", "source_ref", name="uq_item_source_ref"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source: Mapped[str] = mapped_column(String(80), index=True)
    source_ref: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)

    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text)
    taxonomy_path: Mapped[str | None] = mapped_column(String(500), nullable=True)

    status: Mapped[str] = mapped_column(String(40), default="pending")
    error_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    chunk_count: Mapped[int] = mapped_column(Integer, default=0)
    embedding_model_version: Mapped[str | None] = mapped_column(String(80), nullable=True)
    tagging_status: Mapped[str] = mapped_column(String(40), default="pending")
    tagging_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    tag_count: Mapped[int] = mapped_column(Integer, default=0)
    classification_status: Mapped[str] = mapped_column(String(40), default="pending")
    classification_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    classification_label: Mapped[str | None] = mapped_column(String(180), nullable=True)
    classification_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    insight_status: Mapped[str] = mapped_column(String(40), default="pending")
    insight_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    insight_count: Mapped[int] = mapped_column(Integer, default=0)
    proactive_status: Mapped[str] = mapped_column(String(40), default="pending")
    proactive_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    proactive_count: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ingested_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    embedded_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    tagged_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    classified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    insighted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    proactive_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[str] = mapped_column(String(64), ForeignKey("items.id"), index=True)
    job_type: Mapped[str] = mapped_column(String(40), default="embed")
    status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TagDefinition(Base):
    __tablename__ = "tag_definitions"
    __table_args__ = (UniqueConstraint("slug", name="uq_tag_definition_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(120), index=True)
    display_name: Mapped[str] = mapped_column(String(180))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ItemTag(Base):
    __tablename__ = "item_tags"
    __table_args__ = (UniqueConstraint("item_id", "tag_id", name="uq_item_tag_pair"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[str] = mapped_column(String(64), ForeignKey("items.id"), index=True)
    tag_id: Mapped[int] = mapped_column(Integer, ForeignKey("tag_definitions.id"), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(40), default="needs_review", index=True)
    source: Mapped[str] = mapped_column(String(80), default="rule_engine_v1")
    rule_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    matched_terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_manual_override: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ClassDefinition(Base):
    __tablename__ = "class_definitions"
    __table_args__ = (UniqueConstraint("slug", name="uq_class_definition_slug"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(160), index=True)
    display_name: Mapped[str] = mapped_column(String(220))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ItemClassification(Base):
    __tablename__ = "item_classifications"
    __table_args__ = (UniqueConstraint("item_id", name="uq_item_classification_item"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[str] = mapped_column(String(64), ForeignKey("items.id"), index=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("class_definitions.id"), index=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(40), default="needs_review", index=True)
    source: Mapped[str] = mapped_column(String(80), default="rule_classifier_v1")
    rule_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    matched_terms: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_manual_override: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    insight_type: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(300))
    body: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(40), default="generated", index=True)
    source_item_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    time_range_start: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    time_range_end: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    generator_version: Mapped[str] = mapped_column(String(80), default="insights_v1")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SummaryCache(Base):
    __tablename__ = "summary_cache"
    __table_args__ = (UniqueConstraint("cache_key", name="uq_summary_cache_key"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cache_key: Mapped[str] = mapped_column(String(255), index=True)
    payload: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[str] = mapped_column(String(64), ForeignKey("items.id"), index=True)
    event_type: Mapped[str] = mapped_column(String(80), index=True)
    event_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    title: Mapped[str] = mapped_column(String(300))
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(80), default="phase6_timeline_v1")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ProactiveSignal(Base):
    __tablename__ = "proactive_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    signal_type: Mapped[str] = mapped_column(String(80), index=True)
    severity: Mapped[str] = mapped_column(String(40), default="info", index=True)
    title: Mapped[str] = mapped_column(String(300))
    recommendation: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(40), default="open", index=True)
    source_item_ids: Mapped[str | None] = mapped_column(Text, nullable=True)
    generator_version: Mapped[str] = mapped_column(String(80), default="phase6_proactive_v1")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ApiMetric(Base):
    __tablename__ = "api_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    endpoint: Mapped[str] = mapped_column(String(180), index=True)
    method: Mapped[str] = mapped_column(String(12), index=True)
    status_code: Mapped[int] = mapped_column(Integer, index=True)
    latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    success: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    suite_name: Mapped[str] = mapped_column(String(120), default="default_suite", index=True)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(40), default="completed", index=True)
    checks_total: Mapped[int] = mapped_column(Integer, default=0)
    checks_passed: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str] = mapped_column(Text)
    details_json: Mapped[str] = mapped_column(Text, default="{}")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DeadLetterJob(Base):
    __tablename__ = "dead_letter_jobs"
    __table_args__ = (UniqueConstraint("job_id", name="uq_dead_letter_job_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(Integer, index=True)
    item_id: Mapped[str] = mapped_column(String(64), index=True)
    job_type: Mapped[str] = mapped_column(String(40), index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="open", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorState(Base):
    __tablename__ = "connector_states"
    __table_args__ = (UniqueConstraint("connector_name", name="uq_connector_state_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(40), default="idle", index=True)
    checkpoint: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_synced_items: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorRun(Base):
    __tablename__ = "connector_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(40), default="completed", index=True)
    fetched_count: Mapped[int] = mapped_column(Integer, default=0)
    ingested_count: Mapped[int] = mapped_column(Integer, default=0)
    error_count: Mapped[int] = mapped_column(Integer, default=0)
    run_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FeedbackEvent(Base):
    __tablename__ = "feedback_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item_id: Mapped[str] = mapped_column(String(64), index=True)
    feedback_type: Mapped[str] = mapped_column(String(80), index=True)
    before_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    after_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String(80), default="manual_override")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorCredential(Base):
    __tablename__ = "connector_credentials"
    __table_args__ = (UniqueConstraint("connector_name", name="uq_connector_credential_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    auth_type: Mapped[str] = mapped_column(String(40), default="api_key")
    secret_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    secret_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="configured", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorSchedule(Base):
    __tablename__ = "connector_schedules"
    __table_args__ = (UniqueConstraint("connector_name", name="uq_connector_schedule_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    interval_minutes: Mapped[int] = mapped_column(Integer, default=60)
    priority: Mapped[int] = mapped_column(Integer, default=50, index=True)
    group_name: Mapped[str] = mapped_column(String(120), default="default", index=True)
    is_paused: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    max_attempts: Mapped[int] = mapped_column(Integer, default=5)
    failure_count: Mapped[int] = mapped_column(Integer, default=0)
    next_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    config_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorScheduleDeadLetter(Base):
    __tablename__ = "connector_schedule_dead_letters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    schedule_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("connector_schedules.id"), nullable=True, index=True)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="open", index=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorWebhookEvent(Base):
    __tablename__ = "connector_webhook_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    event_type: Mapped[str] = mapped_column(String(80), default="manual")
    status: Mapped[str] = mapped_column(String(40), default="received", index=True)
    payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_run_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorPolicy(Base):
    __tablename__ = "connector_policies"
    __table_args__ = (UniqueConstraint("connector_name", name="uq_connector_policy_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    rate_limit_per_hour: Mapped[int] = mapped_column(Integer, default=120)
    max_concurrent_runs: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorAuditLog(Base):
    __tablename__ = "connector_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    action: Mapped[str] = mapped_column(String(80), index=True)
    result: Mapped[str] = mapped_column(String(40), default="ok", index=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    run_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorSimulationRun(Base):
    __tablename__ = "connector_simulation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(40), default="completed", index=True)
    fetched_count: Mapped[int] = mapped_column(Integer, default=0)
    candidate_new_items: Mapped[int] = mapped_column(Integer, default=0)
    candidate_existing_items: Mapped[int] = mapped_column(Integer, default=0)
    sample_new_refs: Mapped[str | None] = mapped_column(Text, nullable=True)
    simulation_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorPolicyRevision(Base):
    __tablename__ = "connector_policy_revisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    previous_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    previous_rate_limit_per_hour: Mapped[int] = mapped_column(Integer, default=120)
    previous_max_concurrent_runs: Mapped[int] = mapped_column(Integer, default=1)
    new_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    new_rate_limit_per_hour: Mapped[int] = mapped_column(Integer, default=120)
    new_max_concurrent_runs: Mapped[int] = mapped_column(Integer, default=1)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(40), default="applied", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorOrchestrationRun(Base):
    __tablename__ = "connector_orchestration_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(40), default="completed", index=True)
    requested_connectors: Mapped[str | None] = mapped_column(Text, nullable=True)
    total_connectors: Mapped[int] = mapped_column(Integer, default=0)
    succeeded_connectors: Mapped[int] = mapped_column(Integer, default=0)
    failed_connectors: Mapped[int] = mapped_column(Integer, default=0)
    blocked_connectors: Mapped[int] = mapped_column(Integer, default=0)
    run_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorOrchestrationRunItem(Base):
    __tablename__ = "connector_orchestration_run_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    orchestration_run_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("connector_orchestration_runs.id"),
        index=True,
    )
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(40), default="completed", index=True)
    run_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorHealthSnapshot(Base):
    __tablename__ = "connector_health_snapshots"
    __table_args__ = (UniqueConstraint("connector_name", name="uq_connector_health_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    health_score: Mapped[float] = mapped_column(Float, default=1.0)
    success_rate: Mapped[float] = mapped_column(Float, default=1.0)
    failure_streak: Mapped[int] = mapped_column(Integer, default=0)
    avg_latency_ms: Mapped[float] = mapped_column(Float, default=0.0)
    dead_letter_open_count: Mapped[int] = mapped_column(Integer, default=0)
    total_recent_runs: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(40), default="healthy", index=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorSlaAlert(Base):
    __tablename__ = "connector_sla_alerts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    severity: Mapped[str] = mapped_column(String(40), default="warning", index=True)
    metric_name: Mapped[str] = mapped_column(String(80), index=True)
    metric_value: Mapped[float] = mapped_column(Float, default=0.0)
    threshold_value: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(40), default="open", index=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorRemediationAction(Base):
    __tablename__ = "connector_remediation_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    action_type: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40), default="completed", index=True)
    action_details: Mapped[str | None] = mapped_column(Text, nullable=True)
    related_alert_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("connector_sla_alerts.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorNotificationChannel(Base):
    __tablename__ = "connector_notification_channels"
    __table_args__ = (UniqueConstraint("connector_name", "channel_type", "target", name="uq_connector_notification_target"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    channel_type: Mapped[str] = mapped_column(String(80), default="webhook", index=True)
    target: Mapped[str] = mapped_column(String(500))
    secret: Mapped[str | None] = mapped_column(Text, nullable=True)
    min_severity: Mapped[str] = mapped_column(String(40), default="warning", index=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorNotificationDelivery(Base):
    __tablename__ = "connector_notification_deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    alert_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("connector_sla_alerts.id"), nullable=True, index=True)
    channel_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("connector_notification_channels.id"), nullable=True, index=True)
    channel_type: Mapped[str] = mapped_column(String(80), default="webhook", index=True)
    target: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(40), default="sent", index=True)
    payload_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_preview: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConnectorEscalationPolicy(Base):
    __tablename__ = "connector_escalation_policies"
    __table_args__ = (UniqueConstraint("connector_name", name="uq_connector_escalation_policy_name"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    connector_name: Mapped[str] = mapped_column(String(120), index=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    open_alert_count_threshold: Mapped[int] = mapped_column(Integer, default=3)
    action_type: Mapped[str] = mapped_column(String(80), default="reduce_policy_limits")
    notify_channel_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("connector_notification_channels.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
