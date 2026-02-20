from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


ItemStatus = Literal["pending", "embedded", "failed"]
JobStatus = Literal["pending", "processing", "succeeded", "failed", "dead_letter"]
TagStatus = Literal["accepted", "needs_review", "rejected"]
ClassificationStatus = Literal["accepted", "needs_review", "rejected"]


class ItemCreate(BaseModel):
    source: str = Field(min_length=1, max_length=80)
    source_ref: str | None = Field(default=None, max_length=255)
    title: str = Field(min_length=1, max_length=500)
    description: str = ""
    content: str = Field(min_length=1)
    taxonomy_path: str | None = Field(default=None, max_length=500)
    idempotency_key: str | None = Field(default=None, max_length=255)


class BulkItemCreate(BaseModel):
    items: list[ItemCreate]


class ItemResponse(BaseModel):
    id: str
    source: str
    source_ref: str | None
    title: str
    description: str
    taxonomy_path: str | None
    status: ItemStatus
    error_reason: str | None
    chunk_count: int
    embedding_model_version: str | None
    tagging_status: str
    tagging_error: str | None
    tag_count: int
    classification_status: str
    classification_error: str | None
    classification_label: str | None
    classification_confidence: float | None
    insight_status: str
    insight_error: str | None
    insight_count: int
    proactive_status: str
    proactive_error: str | None
    proactive_count: int
    created_at: datetime
    updated_at: datetime
    ingested_at: datetime | None
    embedded_at: datetime | None
    tagged_at: datetime | None
    classified_at: datetime | None
    insighted_at: datetime | None
    proactive_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class IngestResponse(BaseModel):
    item: ItemResponse
    created: bool
    enqueued_job_id: int | None


class BulkIngestResponse(BaseModel):
    results: list[IngestResponse]


class RebuildRequest(BaseModel):
    item_ids: list[str] = []


class JobResponse(BaseModel):
    id: int
    item_id: str
    job_type: str
    status: JobStatus
    attempts: int
    last_error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobProcessResponse(BaseModel):
    processed: int
    succeeded: int
    failed: int
    job_ids: list[int]


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=50)
    source: str | None = Field(default=None, max_length=80)
    taxonomy_path_prefix: str | None = Field(default=None, max_length=500)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)


class SearchResult(BaseModel):
    item_id: str
    chunk_id: str
    chunk_index: int
    score: float
    source: str
    source_ref: str | None
    taxonomy_path: str | None
    title: str
    snippet: str


class SearchResponse(BaseModel):
    query: str
    top_k: int
    results: list[SearchResult]


class RetrievalResult(BaseModel):
    item_id: str
    score: float
    source: str
    source_ref: str | None
    taxonomy_path: str | None
    title: str
    snippets: list[str]
    chunk_hits: int


class RetrievalResponse(BaseModel):
    query: str
    top_k: int
    results: list[RetrievalResult]


class TagResult(BaseModel):
    item_tag_id: int
    tag_id: int
    tag_slug: str
    display_name: str
    confidence: float
    status: TagStatus
    source: str
    rule_id: str | None
    matched_terms: str | None
    is_manual_override: bool
    created_at: datetime
    updated_at: datetime


class TaggingResponse(BaseModel):
    item_id: str
    tagging_status: str
    tag_count: int
    tags: list[TagResult]


class TagJobResponse(BaseModel):
    enqueued: int
    item_ids: list[str]
    process_result: JobProcessResponse | None = None


class TaggingRunRequest(BaseModel):
    item_ids: list[str] = []
    process_immediately: bool = False


class TagOverrideRequest(BaseModel):
    tag_slug: str = Field(min_length=1, max_length=120)
    action: Literal["approve", "reject"] = "approve"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    notes: str | None = Field(default=None, max_length=2000)


class ClassificationResult(BaseModel):
    item_classification_id: int
    class_id: int
    class_slug: str
    display_name: str
    confidence: float
    status: ClassificationStatus
    source: str
    rule_id: str | None
    matched_terms: str | None
    is_manual_override: bool
    created_at: datetime
    updated_at: datetime


class ClassificationResponse(BaseModel):
    item_id: str
    classification_status: str
    classification_label: str | None
    classification_confidence: float | None
    classification: ClassificationResult | None


class ClassificationJobResponse(BaseModel):
    enqueued: int
    item_ids: list[str]
    process_result: JobProcessResponse | None = None


class ClassificationRunRequest(BaseModel):
    item_ids: list[str] = []
    process_immediately: bool = False


class ClassificationOverrideRequest(BaseModel):
    class_slug: str = Field(min_length=1, max_length=160)
    action: Literal["approve", "reject"] = "approve"
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    notes: str | None = Field(default=None, max_length=2000)


class InsightRecord(BaseModel):
    id: int
    insight_type: str
    title: str
    body: str
    confidence: float
    status: str
    source_item_ids: list[str]
    time_range_start: datetime | None
    time_range_end: datetime | None
    generator_version: str
    created_at: datetime
    updated_at: datetime


class InsightGenerateRequest(BaseModel):
    item_ids: list[str] = []
    insight_type: Literal["item", "window", "cross_domain"] = "item"
    window_days: int = Field(default=30, ge=1, le=3650)
    process_immediately: bool = True


class InsightGenerateResponse(BaseModel):
    enqueued: int
    item_ids: list[str]
    process_result: JobProcessResponse | None = None


class InsightListResponse(BaseModel):
    insights: list[InsightRecord]


class WindowSummaryRequest(BaseModel):
    days: int = Field(default=30, ge=1, le=3650)
    source: str | None = Field(default=None, max_length=80)
    taxonomy_prefix: str | None = Field(default=None, max_length=500)
    use_cache: bool = True


class ItemSummaryResponse(BaseModel):
    item_id: str
    summary: str
    evidence: list[str]
    confidence: float
    generated_at: datetime


class WindowSummaryResponse(BaseModel):
    days: int
    summary: str
    evidence: list[str]
    confidence: float
    generated_at: datetime


class CrossDomainBriefRequest(BaseModel):
    days: int = Field(default=30, ge=1, le=3650)
    use_cache: bool = True


class CrossDomainBriefResponse(BaseModel):
    summary: str
    sections: list[str]
    evidence: list[str]
    confidence: float
    generated_at: datetime


class TimelineEventRecord(BaseModel):
    id: int
    item_id: str
    event_type: str
    event_time: datetime
    title: str
    details: str | None
    source: str
    created_at: datetime
    updated_at: datetime


class TimelineQueryRequest(BaseModel):
    days: int = Field(default=30, ge=1, le=3650)
    event_type: str | None = Field(default=None, max_length=80)
    limit: int = Field(default=100, ge=1, le=1000)


class TimelineResponse(BaseModel):
    events: list[TimelineEventRecord]


class ProactiveSignalRecord(BaseModel):
    id: int
    signal_type: str
    severity: str
    title: str
    recommendation: str
    confidence: float
    status: str
    source_item_ids: list[str]
    generator_version: str
    created_at: datetime
    updated_at: datetime


class ProactiveRunRequest(BaseModel):
    item_ids: list[str] = []
    process_immediately: bool = True
    days: int = Field(default=30, ge=1, le=3650)


class ProactiveRunResponse(BaseModel):
    enqueued: int
    item_ids: list[str]
    process_result: JobProcessResponse | None = None


class ProactiveListResponse(BaseModel):
    signals: list[ProactiveSignalRecord]


class ProactiveResolveRequest(BaseModel):
    status: Literal["open", "dismissed", "done"] = "done"


class DigestResponse(BaseModel):
    days: int
    digest: str
    generated_at: datetime


class AssistantRecommendationsResponse(BaseModel):
    digest: str
    top_signals: list[ProactiveSignalRecord]
    generated_at: datetime


class MetricsSummaryResponse(BaseModel):
    total_items: int
    total_jobs: int
    pending_jobs: int
    failed_jobs: int
    dead_letter_jobs: int
    open_signals: int
    latest_evaluation_score: float | None
    generated_at: datetime


class JobMetricsRow(BaseModel):
    job_type: str
    total: int
    succeeded: int
    failed: int
    dead_letter: int
    pending: int


class JobMetricsResponse(BaseModel):
    rows: list[JobMetricsRow]
    generated_at: datetime


class EvaluationRunRequest(BaseModel):
    suite_name: str = Field(default="default_suite", min_length=1, max_length=120)
    days: int = Field(default=30, ge=1, le=3650)


class EvaluationDetail(BaseModel):
    name: str
    passed: bool
    value: float
    threshold: float
    note: str


class EvaluationRunResponse(BaseModel):
    id: int
    suite_name: str
    score: float
    status: str
    checks_total: int
    checks_passed: int
    summary: str
    details: list[EvaluationDetail]
    created_at: datetime


class DeadLetterRecord(BaseModel):
    id: int
    job_id: int
    item_id: str
    job_type: str
    attempts: int
    last_error: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class DeadLetterListResponse(BaseModel):
    records: list[DeadLetterRecord]
    generated_at: datetime


class DeadLetterRequeueRequest(BaseModel):
    dead_letter_ids: list[int] = []
    limit: int = Field(default=20, ge=1, le=500)


class DeadLetterRequeueResponse(BaseModel):
    requeued: int
    dead_letter_ids: list[int]


class ConnectorSyncRequest(BaseModel):
    config: dict = {}
    limit: int = Field(default=500, ge=1, le=5000)
    use_checkpoint: bool = True


class ConnectorSyncResponse(BaseModel):
    connector_name: str
    status: str
    fetched_count: int
    ingested_count: int
    error_count: int
    run_id: int
    details: str | None


class ConnectorStateRecord(BaseModel):
    connector_name: str
    status: str
    checkpoint: str | None
    last_run_at: datetime | None
    last_error: str | None
    total_synced_items: int
    updated_at: datetime


class ConnectorStatusResponse(BaseModel):
    connectors: list[ConnectorStateRecord]
    generated_at: datetime


class ConnectorCredentialUpsertRequest(BaseModel):
    auth_type: str = Field(default="api_key", min_length=1, max_length=40)
    secret_value: str = Field(min_length=1, max_length=8000)
    secret_ref: str | None = Field(default=None, max_length=255)


class ConnectorCredentialRecord(BaseModel):
    connector_name: str
    auth_type: str
    status: str
    secret_ref: str | None
    masked_secret: str | None
    updated_at: datetime


class ConnectorCredentialsResponse(BaseModel):
    records: list[ConnectorCredentialRecord]
    generated_at: datetime


class ConnectorScheduleUpsertRequest(BaseModel):
    enabled: bool = True
    interval_minutes: int = Field(default=60, ge=1, le=10080)
    priority: int = Field(default=50, ge=1, le=1000)
    group_name: str = Field(default="default", min_length=1, max_length=120)
    is_paused: bool = False
    max_attempts: int = Field(default=5, ge=1, le=50)
    limit: int = Field(default=500, ge=1, le=5000)
    config: dict = {}
    run_immediately: bool = False


class ConnectorScheduleRecord(BaseModel):
    connector_name: str
    enabled: bool
    interval_minutes: int
    priority: int
    group_name: str
    is_paused: bool
    max_attempts: int
    failure_count: int
    limit: int
    next_run_at: datetime | None
    last_run_at: datetime | None
    last_success_at: datetime | None
    updated_at: datetime


class ConnectorSchedulesResponse(BaseModel):
    schedules: list[ConnectorScheduleRecord]
    generated_at: datetime


class ConnectorScheduleRunResponse(BaseModel):
    scanned: int
    triggered: int
    dead_lettered: int
    results: list[ConnectorSyncResponse]
    generated_at: datetime


class ConnectorWebhookTriggerRequest(BaseModel):
    secret: str | None = Field(default=None, max_length=8000)
    event_type: str = Field(default="manual", min_length=1, max_length=80)
    config: dict = {}
    limit: int = Field(default=500, ge=1, le=5000)
    use_checkpoint: bool = True


class ConnectorWebhookTriggerResponse(BaseModel):
    event_id: int
    connector_name: str
    event_type: str
    status: str
    run_id: int | None
    details: str | None


class ConnectorDeadLetterRecord(BaseModel):
    id: int
    connector_name: str
    schedule_id: int | None
    attempts: int
    last_error: str | None
    status: str
    payload_json: str | None
    created_at: datetime
    updated_at: datetime


class ConnectorDeadLetterListResponse(BaseModel):
    records: list[ConnectorDeadLetterRecord]
    generated_at: datetime


class ConnectorDeadLetterRequeueRequest(BaseModel):
    dead_letter_ids: list[int] = []
    limit: int = Field(default=20, ge=1, le=500)


class ConnectorDeadLetterRequeueResponse(BaseModel):
    requeued: int
    dead_letter_ids: list[int]


class ConnectorPolicyUpsertRequest(BaseModel):
    enabled: bool = True
    rate_limit_per_hour: int = Field(default=120, ge=1, le=100000)
    max_concurrent_runs: int = Field(default=1, ge=1, le=50)


class ConnectorPolicyRecord(BaseModel):
    connector_name: str
    enabled: bool
    rate_limit_per_hour: int
    max_concurrent_runs: int
    updated_at: datetime


class ConnectorPoliciesResponse(BaseModel):
    policies: list[ConnectorPolicyRecord]
    generated_at: datetime


class ConnectorAuditRecord(BaseModel):
    id: int
    connector_name: str
    action: str
    result: str
    details: str | None
    run_id: int | None
    created_at: datetime


class ConnectorAuditResponse(BaseModel):
    records: list[ConnectorAuditRecord]
    generated_at: datetime


class ConnectorSimulationRequest(BaseModel):
    config: dict = {}
    limit: int = Field(default=500, ge=1, le=5000)
    use_checkpoint: bool = True


class ConnectorSimulationResponse(BaseModel):
    simulation_id: int
    connector_name: str
    status: str
    fetched_count: int
    candidate_new_items: int
    candidate_existing_items: int
    sample_new_refs: list[str]
    details: str | None
    generated_at: datetime


class ConnectorSimulationRecord(BaseModel):
    simulation_id: int
    connector_name: str
    status: str
    fetched_count: int
    candidate_new_items: int
    candidate_existing_items: int
    sample_new_refs: list[str]
    details: str | None
    created_at: datetime


class ConnectorSimulationsResponse(BaseModel):
    records: list[ConnectorSimulationRecord]
    generated_at: datetime


class ConnectorPolicyRecommendationResponse(BaseModel):
    connector_name: str
    recommended_rate_limit_per_hour: int
    recommended_max_concurrent_runs: int
    recommended_interval_minutes: int
    reason: str
    generated_at: datetime


class ConnectorPolicyAutoApplyRequest(BaseModel):
    enabled: bool = True
    dry_run: bool = False
    min_rate_limit_per_hour: int = Field(default=10, ge=1, le=100000)
    max_rate_limit_per_hour: int = Field(default=500, ge=1, le=100000)
    max_concurrent_runs_cap: int = Field(default=3, ge=1, le=50)


class ConnectorPolicyAutoApplyResponse(BaseModel):
    connector_name: str
    applied: bool
    revision_id: int | None
    previous_rate_limit_per_hour: int
    previous_max_concurrent_runs: int
    new_rate_limit_per_hour: int
    new_max_concurrent_runs: int
    reason: str
    generated_at: datetime


class ConnectorPolicyRevisionRecord(BaseModel):
    id: int
    connector_name: str
    previous_enabled: bool
    previous_rate_limit_per_hour: int
    previous_max_concurrent_runs: int
    new_enabled: bool
    new_rate_limit_per_hour: int
    new_max_concurrent_runs: int
    reason: str | None
    status: str
    created_at: datetime


class ConnectorPolicyRevisionsResponse(BaseModel):
    records: list[ConnectorPolicyRevisionRecord]
    generated_at: datetime


class ConnectorPolicyRollbackResponse(BaseModel):
    rolled_back: bool
    connector_name: str
    revision_id: int | None
    message: str


class ConnectorPolicyGuardrailCheckRequest(BaseModel):
    lookback_runs: int = Field(default=20, ge=1, le=500)
    failure_ratio_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    auto_rollback: bool = True


class ConnectorPolicyGuardrailCheckResponse(BaseModel):
    connector_name: str
    lookback_runs: int
    failure_ratio: float
    threshold: float
    breached: bool
    rolled_back: bool
    message: str


class ConnectorPriorityUpdateRequest(BaseModel):
    priority: int = Field(default=50, ge=1, le=1000)
    group_name: str | None = Field(default=None, min_length=1, max_length=120)
    is_paused: bool | None = None


class ConnectorPriorityUpdateResponse(BaseModel):
    connector_name: str
    priority: int
    group_name: str
    is_paused: bool
    message: str


class ConnectorGroupPauseResponse(BaseModel):
    group_name: str
    paused: bool
    updated_connectors: int
    message: str


class ConnectorOrchestrationRunRequest(BaseModel):
    connector_names: list[str] = []
    max_connectors: int = Field(default=20, ge=1, le=200)
    use_checkpoint: bool = True


class ConnectorOrchestrationItemRecord(BaseModel):
    connector_name: str
    status: str
    run_id: int | None
    details: str | None


class ConnectorOrchestrationRunResponse(BaseModel):
    orchestration_run_id: int
    status: str
    total_connectors: int
    succeeded_connectors: int
    failed_connectors: int
    blocked_connectors: int
    items: list[ConnectorOrchestrationItemRecord]
    details: str | None
    generated_at: datetime


class ConnectorHealthRecord(BaseModel):
    connector_name: str
    health_score: float
    status: str
    success_rate: float
    failure_streak: int
    avg_latency_ms: float
    dead_letter_open_count: int
    total_recent_runs: int
    priority: int | None
    group_name: str | None
    is_paused: bool | None
    details: str | None
    updated_at: datetime


class ConnectorHealthResponse(BaseModel):
    records: list[ConnectorHealthRecord]
    generated_at: datetime


class ConnectorSlaEvaluateRequest(BaseModel):
    min_health_score: float = Field(default=0.6, ge=0.0, le=1.0)
    max_failure_streak: int = Field(default=3, ge=0, le=100)
    max_dead_letter_open: int = Field(default=0, ge=0, le=10000)
    auto_remediate: bool = True


class ConnectorSlaAlertRecord(BaseModel):
    id: int
    connector_name: str
    severity: str
    metric_name: str
    metric_value: float
    threshold_value: float
    status: str
    details: str | None
    created_at: datetime


class ConnectorSlaAlertsResponse(BaseModel):
    records: list[ConnectorSlaAlertRecord]
    generated_at: datetime


class ConnectorRemediationRecord(BaseModel):
    id: int
    connector_name: str
    action_type: str
    status: str
    action_details: str | None
    related_alert_id: int | None
    created_at: datetime


class ConnectorRemediationResponse(BaseModel):
    records: list[ConnectorRemediationRecord]
    generated_at: datetime


class ConnectorSlaEvaluationResponse(BaseModel):
    evaluated_connectors: int
    alerts_created: int
    remediation_actions: int
    details: str
    generated_at: datetime


class ConnectorSlaAlertResolveResponse(BaseModel):
    alert_id: int
    status: str
    message: str


class ConnectorRemediationTriggerRequest(BaseModel):
    action_type: str = Field(default="pause_connector", min_length=1, max_length=80)
    reason: str | None = Field(default=None, max_length=2000)


class ConnectorRemediationTriggerResponse(BaseModel):
    connector_name: str
    action_id: int
    action_type: str
    status: str
    message: str


class ConnectorNotificationChannelUpsertRequest(BaseModel):
    connector_name: str = Field(default="*", min_length=1, max_length=120)
    channel_type: str = Field(default="webhook", min_length=1, max_length=80)
    target: str = Field(min_length=1, max_length=500)
    secret: str | None = Field(default=None, max_length=4000)
    min_severity: str = Field(default="warning", min_length=1, max_length=40)
    is_enabled: bool = True


class ConnectorNotificationChannelRecord(BaseModel):
    id: int
    connector_name: str
    channel_type: str
    target: str
    min_severity: str
    is_enabled: bool
    updated_at: datetime


class ConnectorNotificationChannelsResponse(BaseModel):
    records: list[ConnectorNotificationChannelRecord]
    generated_at: datetime


class ConnectorNotificationTestRequest(BaseModel):
    connector_name: str = Field(default="*", min_length=1, max_length=120)
    severity: str = Field(default="warning", min_length=1, max_length=40)
    message: str = Field(default="Test notification", min_length=1, max_length=2000)


class ConnectorNotificationTestResponse(BaseModel):
    attempted_channels: int
    sent: int
    failed: int
    generated_at: datetime


class ConnectorNotificationDeliveryRecord(BaseModel):
    id: int
    connector_name: str
    alert_id: int | None
    channel_id: int | None
    channel_type: str
    target: str
    status: str
    payload_preview: str | None
    response_preview: str | None
    created_at: datetime


class ConnectorNotificationDeliveriesResponse(BaseModel):
    records: list[ConnectorNotificationDeliveryRecord]
    generated_at: datetime


class ConnectorEscalationPolicyUpsertRequest(BaseModel):
    enabled: bool = True
    open_alert_count_threshold: int = Field(default=3, ge=1, le=10000)
    action_type: str = Field(default="reduce_policy_limits", min_length=1, max_length=80)
    notify_channel_id: int | None = None


class ConnectorEscalationPolicyRecord(BaseModel):
    connector_name: str
    enabled: bool
    open_alert_count_threshold: int
    action_type: str
    notify_channel_id: int | None
    updated_at: datetime


class ConnectorEscalationPoliciesResponse(BaseModel):
    records: list[ConnectorEscalationPolicyRecord]
    generated_at: datetime


class ConnectorEscalationEvaluateResponse(BaseModel):
    evaluated_connectors: int
    escalations_triggered: int
    generated_at: datetime


class FeedbackRecord(BaseModel):
    id: int
    item_id: str
    feedback_type: str
    before_value: str | None
    after_value: str | None
    source: str
    notes: str | None
    created_at: datetime


class FeedbackExportResponse(BaseModel):
    records: list[FeedbackRecord]
    generated_at: datetime
