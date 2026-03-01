from datetime import datetime
from time import perf_counter

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import Insight, Item, Job
from app.schemas import (
    AssistantRecommendationsResponse,
    BulkIngestResponse,
    BulkItemCreate,
    DigestResponse,
    ClassificationJobResponse,
    ClassificationOverrideRequest,
    BulkClassificationOverrideRequest,
    BulkItemResponse,
    ClassificationResponse,
    ClassificationRunRequest,
    CrossDomainBriefRequest,
    CrossDomainBriefResponse,
    ConnectorStatusResponse,
    ConnectorCredentialUpsertRequest,
    ConnectorDeadLetterListResponse,
    ConnectorDeadLetterRequeueRequest,
    ConnectorDeadLetterRequeueResponse,
    ConnectorAuditResponse,
    ConnectorCredentialsResponse,
    ConnectorPoliciesResponse,
    ConnectorPriorityUpdateRequest,
    ConnectorPriorityUpdateResponse,
    ConnectorGroupPauseResponse,
    ConnectorOrchestrationRunRequest,
    ConnectorOrchestrationRunResponse,
    ConnectorHealthResponse,
    ConnectorPolicyAutoApplyRequest,
    ConnectorPolicyAutoApplyResponse,
    ConnectorPolicyGuardrailCheckRequest,
    ConnectorPolicyGuardrailCheckResponse,
    ConnectorPolicyRevisionsResponse,
    ConnectorPolicyRollbackResponse,
    ConnectorPolicyUpsertRequest,
    ConnectorPolicyRecommendationResponse,
    ConnectorNotificationChannelsResponse,
    ConnectorNotificationChannelUpsertRequest,
    ConnectorNotificationTestRequest,
    ConnectorNotificationTestResponse,
    ConnectorNotificationDeliveriesResponse,
    ConnectorEscalationPolicyUpsertRequest,
    ConnectorEscalationPoliciesResponse,
    ConnectorEscalationEvaluateResponse,
    ConnectorRemediationResponse,
    ConnectorRemediationTriggerRequest,
    ConnectorRemediationTriggerResponse,
    ConnectorScheduleRunResponse,
    ConnectorSchedulesResponse,
    ConnectorScheduleUpsertRequest,
    ConnectorSimulationRequest,
    ConnectorSimulationResponse,
    ConnectorSimulationsResponse,
    ConnectorSlaAlertResolveResponse,
    ConnectorSlaAlertsResponse,
    ConnectorSlaEvaluateRequest,
    ConnectorSlaEvaluationResponse,
    ConnectorWebhookTriggerRequest,
    ConnectorWebhookTriggerResponse,
    ConnectorSyncRequest,
    ConnectorSyncResponse,
    DeadLetterListResponse,
    DeadLetterRequeueRequest,
    DeadLetterRequeueResponse,
    EvaluationRunRequest,
    EvaluationRunResponse,
    FeedbackExportResponse,
    IngestResponse,
    InsightGenerateRequest,
    InsightGenerateResponse,
    InsightListResponse,
    InsightRecord,
    ItemCreate,
    ItemSummaryResponse,
    ItemResponse,
    JobProcessResponse,
    JobResponse,
    JobMetricsResponse,
    MetricsSummaryResponse,
    RebuildRequest,
    RetrievalResponse,
    SearchRequest,
    SearchResponse,
    ProactiveListResponse,
    ProactiveResolveRequest,
    ProactiveRunRequest,
    ProactiveRunResponse,
    ProactiveSignalRecord,
    TaggingResponse,
    TaggingRunRequest,
    TagJobResponse,
    TagOverrideRequest,
    TimelineQueryRequest,
    TimelineResponse,
    WindowSummaryRequest,
    WindowSummaryResponse,
)
from app.services.connectors import (
    get_connector_status,
    list_connector_audits,
    list_connector_credentials,
    list_connector_dead_letter,
    list_connector_policies,
    list_connector_policy_revisions,
    list_escalation_policies,
    list_notification_channels,
    list_notification_deliveries,
    list_connector_remediation_actions,
    list_connector_schedules,
    list_connector_simulations,
    list_connector_sla_alerts,
    resolve_connector_sla_alert,
    update_connector_priority,
    set_connector_group_pause,
    run_connector_orchestration,
    evaluate_escalation_policies,
    trigger_connector_remediation,
    get_connector_health,
    auto_apply_connector_policy,
    send_test_notification,
    upsert_escalation_policy,
    upsert_notification_channel,
    guardrail_check_connector_policy,
    recommend_connector_policy,
    rollback_latest_connector_policy_revision,
    requeue_connector_dead_letter,
    run_connector_sync,
    run_due_connector_schedules,
    simulate_connector_sync,
    evaluate_connector_sla,
    trigger_connector_webhook,
    upsert_connector_credential,
    upsert_connector_policy,
    upsert_connector_schedule,
)
from app.services.feedback import export_feedback
from app.services.ingestion import ingest_item
from app.services.jobs import process_pending_jobs
from app.services.search import run_retrieval, run_semantic_search
from app.services.classification import (
    build_classification_response,
    list_classification_needs_review,
    list_items,
    override_item_classification,
    bulk_approve_items,
)
from app.services.insights import (
    build_cross_domain_brief,
    build_item_summary,
    build_window_summary,
    generate_item_insight,
    get_insight,
    list_insights,
)
from app.services.proactive import (
    build_daily_digest,
    list_proactive_signals,
    list_timeline_events,
    update_signal_status,
)
from app.services.phase7 import (
    get_job_metrics,
    get_latest_evaluation,
    get_metrics_summary,
    list_dead_letter,
    record_api_metric,
    requeue_dead_letter,
    run_evaluation,
)
from app.services.tagging import (
    build_tagging_response,
    list_items_with_needs_review,
    override_item_tag,
)
from app.services.vector_store import vector_store


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8085",
        "http://127.0.0.1:8085",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = perf_counter()
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        latency_ms = (perf_counter() - start) * 1000.0
        from app.database import SessionLocal

        db = SessionLocal()
        try:
            record_api_metric(
                db=db,
                endpoint=request.url.path,
                method=request.method,
                status_code=status_code,
                latency_ms=latency_ms,
            )
        except Exception:
            pass
        finally:
            db.close()


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "docs": "/docs", "health": "/health", "ready": "/ready"}


@app.get("/ready")
def ready(db: Session = Depends(get_db)) -> dict[str, object]:
    db.execute(text("SELECT 1"))
    vector_health = vector_store.health()
    return {"status": "ready", "vector_store": vector_health}


@app.post("/items", response_model=IngestResponse)
def create_item(payload: ItemCreate, db: Session = Depends(get_db)) -> IngestResponse:
    item, created, job = ingest_item(db, payload)
    return IngestResponse(
        item=ItemResponse.model_validate(item),
        created=created,
        enqueued_job_id=job.id if job else None,
    )


@app.post("/items/bulk", response_model=BulkIngestResponse)
def create_items_bulk(payload: BulkItemCreate, db: Session = Depends(get_db)) -> BulkIngestResponse:
    results: list[IngestResponse] = []
    for item_payload in payload.items:
        item, created, job = ingest_item(db, item_payload)
        results.append(
            IngestResponse(
                item=ItemResponse.model_validate(item),
                created=created,
                enqueued_job_id=job.id if job else None,
            )
        )
    return BulkIngestResponse(results=results)


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: str, db: Session = Depends(get_db)) -> ItemResponse:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemResponse.model_validate(item)


@app.post("/index/rebuild")
def rebuild_index(payload: RebuildRequest, db: Session = Depends(get_db)) -> dict[str, int]:
    if payload.item_ids:
        items = db.execute(select(Item).where(Item.id.in_(payload.item_ids))).scalars().all()
    else:
        items = db.execute(select(Item)).scalars().all()

    for item in items:
        item.status = "pending"
        db.add(item)
        db.add(Job(item_id=item.id, job_type="embed", status="pending", attempts=0))
    db.commit()
    return {"enqueued": len(items)}


@app.post("/jobs/process", response_model=JobProcessResponse)
def process_jobs(
    limit: int = Query(default=50, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> JobProcessResponse:
    result = process_pending_jobs(db, limit=limit)
    return JobProcessResponse(**result)


@app.get("/jobs", response_model=list[JobResponse])
def list_jobs(
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> list[JobResponse]:
    stmt = select(Job).order_by(Job.created_at.desc()).limit(limit)
    if status:
        stmt = select(Job).where(Job.status == status).order_by(Job.created_at.desc()).limit(limit)
    jobs = db.execute(stmt).scalars().all()
    return [JobResponse.model_validate(job) for job in jobs]


@app.post("/search/semantic", response_model=SearchResponse)
def search_semantic(payload: SearchRequest) -> SearchResponse:
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    results = run_semantic_search(payload)
    return SearchResponse(query=query, top_k=payload.top_k, results=results)


@app.post("/search/retrieve", response_model=RetrievalResponse)
def retrieve(payload: SearchRequest) -> RetrievalResponse:
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    results = run_retrieval(payload)
    return RetrievalResponse(query=query, top_k=payload.top_k, results=results)


@app.post("/tagging/run", response_model=TagJobResponse)
def run_tagging(payload: TaggingRunRequest, db: Session = Depends(get_db)) -> TagJobResponse:
    if payload.item_ids:
        items = db.execute(select(Item).where(Item.id.in_(payload.item_ids))).scalars().all()
    else:
        items = db.execute(select(Item)).scalars().all()

    item_ids = [item.id for item in items]
    for item in items:
        item.tagging_status = "pending"
        item.tagging_error = None
        db.add(item)
        db.add(Job(item_id=item.id, job_type="tag", status="pending", attempts=0))
    db.commit()

    process_result = None
    if payload.process_immediately and item_ids:
        process_result = JobProcessResponse(**process_pending_jobs(db, limit=max(50, len(item_ids) * 2)))

    return TagJobResponse(enqueued=len(item_ids), item_ids=item_ids, process_result=process_result)


@app.get("/items/{item_id}/tags", response_model=TaggingResponse)
def get_item_tags(item_id: str, db: Session = Depends(get_db)) -> TaggingResponse:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return build_tagging_response(db, item)


@app.post("/items/{item_id}/tags/override", response_model=TaggingResponse)
def set_tag_override(
    item_id: str,
    payload: TagOverrideRequest,
    db: Session = Depends(get_db),
) -> TaggingResponse:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return override_item_tag(
        db=db,
        item=item,
        tag_slug=payload.tag_slug,
        action=payload.action,
        confidence=payload.confidence,
        notes=payload.notes,
    )


@app.get("/tags/needs-review", response_model=list[TaggingResponse])
def get_tags_needing_review(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[TaggingResponse]:
    return list_items_with_needs_review(db, limit=limit)


@app.post("/classification/run", response_model=ClassificationJobResponse)
def run_classification(
    payload: ClassificationRunRequest,
    db: Session = Depends(get_db),
) -> ClassificationJobResponse:
    if payload.item_ids:
        items = db.execute(select(Item).where(Item.id.in_(payload.item_ids))).scalars().all()
    else:
        items = db.execute(select(Item)).scalars().all()

    item_ids = [item.id for item in items]
    for item in items:
        item.classification_status = "pending"
        item.classification_error = None
        db.add(item)
        db.add(Job(item_id=item.id, job_type="classify", status="pending", attempts=0))
    db.commit()

    process_result = None
    if payload.process_immediately and item_ids:
        process_result = JobProcessResponse(**process_pending_jobs(db, limit=max(50, len(item_ids) * 3)))

    return ClassificationJobResponse(
        enqueued=len(item_ids),
        item_ids=item_ids,
        process_result=process_result,
    )


@app.get("/items/{item_id}/classification", response_model=ClassificationResponse)
def get_item_classification(
    item_id: str,
    db: Session = Depends(get_db),
) -> ClassificationResponse:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return build_classification_response(db, item)


@app.post("/items/{item_id}/classification/override", response_model=ClassificationResponse)
def set_classification_override(
    item_id: str,
    payload: ClassificationOverrideRequest,
    db: Session = Depends(get_db),
) -> ClassificationResponse:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return override_item_classification(
        db=db,
        item=item,
        class_slug=payload.class_slug,
        action=payload.action,
        confidence=payload.confidence,
        notes=payload.notes,
    )


@app.get("/classification/needs-review", response_model=list[ClassificationResponse])
def get_classification_needing_review(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> list[ClassificationResponse]:
    return list_classification_needs_review(db, limit=limit)


@app.post("/classification/bulk-approve", response_model=list[ClassificationResponse])
def bulk_approve_classification(
    payload: BulkClassificationOverrideRequest,
    db: Session = Depends(get_db),
) -> list[ClassificationResponse]:
    return bulk_approve_items(
        db=db,
        item_ids=payload.item_ids,
        class_slug=payload.class_slug,
        notes=payload.notes,
    )


@app.get("/items", response_model=BulkItemResponse)
def get_items(
    status: str | None = Query(default=None),
    classification_label: str | None = Query(default=None),
    query: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> BulkItemResponse:
    items, total = list_items(
        db=db,
        status=status,
        classification_label=classification_label,
        query=query,
        limit=limit,
        offset=offset,
    )
    return BulkItemResponse(
        items=[ItemResponse.model_validate(i) for i in items],
        total=total,
        offset=offset,
        limit=limit,
    )


@app.post("/insights/generate", response_model=InsightGenerateResponse)
def generate_insights(
    payload: InsightGenerateRequest,
    db: Session = Depends(get_db),
) -> InsightGenerateResponse:
    if payload.item_ids:
        items = db.execute(select(Item).where(Item.id.in_(payload.item_ids))).scalars().all()
    else:
        items = db.execute(select(Item)).scalars().all()

    item_ids = [item.id for item in items]
    if payload.process_immediately:
        for item in items:
            item.insight_status = "pending"
            item.insight_error = None
            db.add(item)
            db.commit()
            if payload.insight_type == "item":
                generate_item_insight(db, item)
        return InsightGenerateResponse(
            enqueued=len(item_ids),
            item_ids=item_ids,
            process_result=None,
        )

    for item in items:
        item.insight_status = "pending"
        item.insight_error = None
        db.add(item)
        db.add(Job(item_id=item.id, job_type="insight", status="pending", attempts=0))
    db.commit()
    return InsightGenerateResponse(enqueued=len(item_ids), item_ids=item_ids, process_result=None)


@app.get("/insights", response_model=InsightListResponse)
def get_insights(
    limit: int = Query(default=50, ge=1, le=1000),
    insight_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> InsightListResponse:
    return InsightListResponse(insights=list_insights(db, limit=limit, insight_type=insight_type))


@app.get("/insights/{insight_id}", response_model=InsightRecord)
def get_insight_by_id(insight_id: int, db: Session = Depends(get_db)) -> InsightRecord:
    record = get_insight(db, insight_id)
    if not record:
        raise HTTPException(status_code=404, detail="Insight not found")
    return record


@app.post("/summaries/item/{item_id}", response_model=ItemSummaryResponse)
def summarize_item(item_id: str, db: Session = Depends(get_db)) -> ItemSummaryResponse:
    item = db.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return build_item_summary(db, item_id)


@app.post("/summaries/window", response_model=WindowSummaryResponse)
def summarize_window(payload: WindowSummaryRequest, db: Session = Depends(get_db)) -> WindowSummaryResponse:
    return build_window_summary(
        db=db,
        days=payload.days,
        source=payload.source,
        taxonomy_prefix=payload.taxonomy_prefix,
        use_cache=payload.use_cache,
    )


@app.post("/briefs/cross-domain", response_model=CrossDomainBriefResponse)
def cross_domain_brief(payload: CrossDomainBriefRequest, db: Session = Depends(get_db)) -> CrossDomainBriefResponse:
    return build_cross_domain_brief(db=db, days=payload.days, use_cache=payload.use_cache)


@app.post("/proactive/run", response_model=ProactiveRunResponse)
def run_proactive(payload: ProactiveRunRequest, db: Session = Depends(get_db)) -> ProactiveRunResponse:
    if payload.item_ids:
        items = db.execute(select(Item).where(Item.id.in_(payload.item_ids))).scalars().all()
    else:
        items = db.execute(select(Item)).scalars().all()

    item_ids = [item.id for item in items]
    if payload.process_immediately:
        for item in items:
            item.proactive_status = "pending"
            item.proactive_error = None
            db.add(item)
            db.add(Job(item_id=item.id, job_type="proactive", status="pending", attempts=0))
        db.commit()
        result = process_pending_jobs(db, limit=max(100, len(item_ids) * 5)) if item_ids else None
        process_result = JobProcessResponse(**result) if result else None
        return ProactiveRunResponse(enqueued=len(item_ids), item_ids=item_ids, process_result=process_result)

    for item in items:
        item.proactive_status = "pending"
        item.proactive_error = None
        db.add(item)
        db.add(Job(item_id=item.id, job_type="proactive", status="pending", attempts=0))
    db.commit()
    return ProactiveRunResponse(enqueued=len(item_ids), item_ids=item_ids, process_result=None)


@app.post("/timeline/activity", response_model=TimelineResponse)
def get_timeline_activity(payload: TimelineQueryRequest, db: Session = Depends(get_db)) -> TimelineResponse:
    events = list_timeline_events(
        db=db,
        days=payload.days,
        event_type=payload.event_type,
        limit=payload.limit,
    )
    return TimelineResponse(events=events)


@app.get("/proactive/signals", response_model=ProactiveListResponse)
def get_proactive_signals(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> ProactiveListResponse:
    return ProactiveListResponse(signals=list_proactive_signals(db=db, status=status, limit=limit))


@app.post("/proactive/signals/{signal_id}/resolve", response_model=ProactiveSignalRecord)
def resolve_proactive_signal(
    signal_id: int,
    payload: ProactiveResolveRequest,
    db: Session = Depends(get_db),
) -> ProactiveSignalRecord:
    updated = update_signal_status(db=db, signal_id=signal_id, status=payload.status)
    if not updated:
        raise HTTPException(status_code=404, detail="Signal not found")
    return updated


@app.post("/assistant/digest", response_model=DigestResponse)
def assistant_digest(days: int = Query(default=7, ge=1, le=3650), db: Session = Depends(get_db)) -> DigestResponse:
    return DigestResponse(days=days, digest=build_daily_digest(db=db, days=days), generated_at=datetime.utcnow())


@app.post("/assistant/recommendations", response_model=AssistantRecommendationsResponse)
def assistant_recommendations(
    days: int = Query(default=7, ge=1, le=3650),
    limit: int = Query(default=5, ge=1, le=50),
    db: Session = Depends(get_db),
) -> AssistantRecommendationsResponse:
    digest = build_daily_digest(db=db, days=days)
    top_signals = list_proactive_signals(db=db, status="open", limit=limit)
    return AssistantRecommendationsResponse(
        digest=digest,
        top_signals=top_signals,
        generated_at=datetime.utcnow(),
    )


@app.get("/metrics/summary", response_model=MetricsSummaryResponse)
def metrics_summary(db: Session = Depends(get_db)) -> MetricsSummaryResponse:
    return get_metrics_summary(db)


@app.get("/metrics/jobs", response_model=JobMetricsResponse)
def metrics_jobs(db: Session = Depends(get_db)) -> JobMetricsResponse:
    return get_job_metrics(db)


@app.post("/evaluation/run", response_model=EvaluationRunResponse)
def evaluation_run(payload: EvaluationRunRequest, db: Session = Depends(get_db)) -> EvaluationRunResponse:
    return run_evaluation(db=db, suite_name=payload.suite_name, days=payload.days)


@app.get("/evaluation/latest", response_model=EvaluationRunResponse)
def evaluation_latest(db: Session = Depends(get_db)) -> EvaluationRunResponse:
    latest = get_latest_evaluation(db)
    if not latest:
        raise HTTPException(status_code=404, detail="No evaluation run found")
    return latest


@app.get("/maintenance/dead-letter", response_model=DeadLetterListResponse)
def maintenance_dead_letter(
    limit: int = Query(default=100, ge=1, le=1000),
    status: str | None = Query(default="open"),
    db: Session = Depends(get_db),
) -> DeadLetterListResponse:
    return DeadLetterListResponse(
        records=list_dead_letter(db=db, limit=limit, status=status),
        generated_at=datetime.utcnow(),
    )


@app.post("/maintenance/dead-letter/requeue", response_model=DeadLetterRequeueResponse)
def maintenance_requeue_dead_letter(
    payload: DeadLetterRequeueRequest,
    db: Session = Depends(get_db),
) -> DeadLetterRequeueResponse:
    requeued, ids = requeue_dead_letter(db=db, dead_letter_ids=payload.dead_letter_ids, limit=payload.limit)
    return DeadLetterRequeueResponse(requeued=requeued, dead_letter_ids=ids)


@app.post("/connectors/{connector_name}/sync", response_model=ConnectorSyncResponse)
def connector_sync(
    connector_name: str,
    payload: ConnectorSyncRequest,
    db: Session = Depends(get_db),
) -> ConnectorSyncResponse:
    try:
        return run_connector_sync(
            db=db,
            connector_name=connector_name,
            config=payload.config,
            limit=payload.limit,
            use_checkpoint=payload.use_checkpoint,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/connectors/status", response_model=ConnectorStatusResponse)
def connectors_status(db: Session = Depends(get_db)) -> ConnectorStatusResponse:
    return ConnectorStatusResponse(connectors=get_connector_status(db), generated_at=datetime.utcnow())


@app.post("/connectors/{connector_name}/auth")
def connector_auth_upsert(
    connector_name: str,
    payload: ConnectorCredentialUpsertRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    record = upsert_connector_credential(
        db=db,
        connector_name=connector_name,
        auth_type=payload.auth_type,
        secret_value=payload.secret_value,
        secret_ref=payload.secret_ref,
    )
    return {
        "connector_name": record.connector_name,
        "auth_type": record.auth_type,
        "status": record.status,
        "message": "Connector credential saved.",
    }


@app.get("/connectors/auth", response_model=ConnectorCredentialsResponse)
def connectors_auth_list(db: Session = Depends(get_db)) -> ConnectorCredentialsResponse:
    return ConnectorCredentialsResponse(records=list_connector_credentials(db), generated_at=datetime.utcnow())


@app.post("/connectors/{connector_name}/policy")
def connector_policy_upsert(
    connector_name: str,
    payload: ConnectorPolicyUpsertRequest,
    db: Session = Depends(get_db),
) -> dict[str, str | int | bool]:
    try:
        record = upsert_connector_policy(
            db=db,
            connector_name=connector_name,
            enabled=payload.enabled,
            rate_limit_per_hour=payload.rate_limit_per_hour,
            max_concurrent_runs=payload.max_concurrent_runs,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "connector_name": record.connector_name,
        "enabled": record.enabled,
        "rate_limit_per_hour": record.rate_limit_per_hour,
        "max_concurrent_runs": record.max_concurrent_runs,
        "message": "Connector policy saved.",
    }


@app.get("/connectors/policies", response_model=ConnectorPoliciesResponse)
def connectors_policies_list(db: Session = Depends(get_db)) -> ConnectorPoliciesResponse:
    return ConnectorPoliciesResponse(policies=list_connector_policies(db), generated_at=datetime.utcnow())


@app.post("/connectors/{connector_name}/priority", response_model=ConnectorPriorityUpdateResponse)
def connector_priority_update(
    connector_name: str,
    payload: ConnectorPriorityUpdateRequest,
    db: Session = Depends(get_db),
) -> ConnectorPriorityUpdateResponse:
    try:
        record = update_connector_priority(
            db=db,
            connector_name=connector_name,
            priority=payload.priority,
            group_name=payload.group_name,
            is_paused=payload.is_paused,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ConnectorPriorityUpdateResponse(
        connector_name=record.connector_name,
        priority=record.priority,
        group_name=record.group_name,
        is_paused=record.is_paused,
        message="Connector priority/group state updated.",
    )


@app.post("/connectors/groups/{group_name}/pause", response_model=ConnectorGroupPauseResponse)
def connector_group_pause(group_name: str, db: Session = Depends(get_db)) -> ConnectorGroupPauseResponse:
    updated = set_connector_group_pause(db=db, group_name=group_name, paused=True)
    return ConnectorGroupPauseResponse(
        group_name=group_name,
        paused=True,
        updated_connectors=updated,
        message="Connector group paused.",
    )


@app.post("/connectors/groups/{group_name}/resume", response_model=ConnectorGroupPauseResponse)
def connector_group_resume(group_name: str, db: Session = Depends(get_db)) -> ConnectorGroupPauseResponse:
    updated = set_connector_group_pause(db=db, group_name=group_name, paused=False)
    return ConnectorGroupPauseResponse(
        group_name=group_name,
        paused=False,
        updated_connectors=updated,
        message="Connector group resumed.",
    )


@app.post("/connectors/orchestrate/run", response_model=ConnectorOrchestrationRunResponse)
def connectors_orchestrate_run(
    payload: ConnectorOrchestrationRunRequest,
    db: Session = Depends(get_db),
) -> ConnectorOrchestrationRunResponse:
    return run_connector_orchestration(
        db=db,
        connector_names=payload.connector_names,
        max_connectors=payload.max_connectors,
        use_checkpoint=payload.use_checkpoint,
    )


@app.get("/connectors/health", response_model=ConnectorHealthResponse)
def connectors_health(
    lookback_runs: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
) -> ConnectorHealthResponse:
    return ConnectorHealthResponse(
        records=get_connector_health(db=db, lookback_runs=lookback_runs),
        generated_at=datetime.utcnow(),
    )


@app.post("/connectors/notifications/channels")
def connectors_notification_channel_upsert(
    payload: ConnectorNotificationChannelUpsertRequest,
    db: Session = Depends(get_db),
) -> dict[str, str | int | bool]:
    record = upsert_notification_channel(
        db=db,
        connector_name=payload.connector_name,
        channel_type=payload.channel_type,
        target=payload.target,
        secret=payload.secret,
        min_severity=payload.min_severity,
        is_enabled=payload.is_enabled,
    )
    return {
        "id": record.id,
        "connector_name": record.connector_name,
        "channel_type": record.channel_type,
        "target": record.target,
        "is_enabled": record.is_enabled,
        "message": "Notification channel saved.",
    }


@app.get("/connectors/notifications/channels", response_model=ConnectorNotificationChannelsResponse)
def connectors_notification_channels(
    connector_name: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> ConnectorNotificationChannelsResponse:
    return ConnectorNotificationChannelsResponse(
        records=list_notification_channels(
            db=db,
            connector_name=connector_name,
            limit=limit,
        ),
        generated_at=datetime.utcnow(),
    )


@app.post("/connectors/notifications/test", response_model=ConnectorNotificationTestResponse)
def connectors_notification_test(
    payload: ConnectorNotificationTestRequest,
    db: Session = Depends(get_db),
) -> ConnectorNotificationTestResponse:
    return send_test_notification(
        db=db,
        connector_name=payload.connector_name,
        severity=payload.severity,
        message=payload.message,
    )


@app.get("/connectors/notifications/deliveries", response_model=ConnectorNotificationDeliveriesResponse)
def connectors_notification_deliveries(
    connector_name: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> ConnectorNotificationDeliveriesResponse:
    return ConnectorNotificationDeliveriesResponse(
        records=list_notification_deliveries(
            db=db,
            connector_name=connector_name,
            limit=limit,
        ),
        generated_at=datetime.utcnow(),
    )


@app.post("/connectors/{connector_name}/escalation")
def connector_escalation_upsert(
    connector_name: str,
    payload: ConnectorEscalationPolicyUpsertRequest,
    db: Session = Depends(get_db),
) -> dict[str, str | int | bool | None]:
    try:
        record = upsert_escalation_policy(
            db=db,
            connector_name=connector_name,
            enabled=payload.enabled,
            open_alert_count_threshold=payload.open_alert_count_threshold,
            action_type=payload.action_type,
            notify_channel_id=payload.notify_channel_id,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "connector_name": record.connector_name,
        "enabled": record.enabled,
        "open_alert_count_threshold": record.open_alert_count_threshold,
        "action_type": record.action_type,
        "notify_channel_id": record.notify_channel_id,
        "message": "Escalation policy saved.",
    }


@app.get("/connectors/escalation/policies", response_model=ConnectorEscalationPoliciesResponse)
def connectors_escalation_policies(
    connector_name: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> ConnectorEscalationPoliciesResponse:
    return ConnectorEscalationPoliciesResponse(
        records=list_escalation_policies(
            db=db,
            connector_name=connector_name,
            limit=limit,
        ),
        generated_at=datetime.utcnow(),
    )


@app.post("/connectors/escalation/evaluate", response_model=ConnectorEscalationEvaluateResponse)
def connectors_escalation_evaluate(db: Session = Depends(get_db)) -> ConnectorEscalationEvaluateResponse:
    return evaluate_escalation_policies(db=db)


@app.post("/connectors/sla/evaluate", response_model=ConnectorSlaEvaluationResponse)
def connectors_sla_evaluate(
    payload: ConnectorSlaEvaluateRequest,
    db: Session = Depends(get_db),
) -> ConnectorSlaEvaluationResponse:
    return evaluate_connector_sla(
        db=db,
        min_health_score=payload.min_health_score,
        max_failure_streak=payload.max_failure_streak,
        max_dead_letter_open=payload.max_dead_letter_open,
        auto_remediate=payload.auto_remediate,
    )


@app.get("/connectors/sla/alerts", response_model=ConnectorSlaAlertsResponse)
def connectors_sla_alerts(
    status: str | None = Query(default="open"),
    connector_name: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> ConnectorSlaAlertsResponse:
    return ConnectorSlaAlertsResponse(
        records=list_connector_sla_alerts(
            db=db,
            status=status,
            connector_name=connector_name,
            limit=limit,
        ),
        generated_at=datetime.utcnow(),
    )


@app.post("/connectors/sla/alerts/{alert_id}/resolve", response_model=ConnectorSlaAlertResolveResponse)
def connectors_sla_alert_resolve(
    alert_id: int,
    db: Session = Depends(get_db),
) -> ConnectorSlaAlertResolveResponse:
    ok, message = resolve_connector_sla_alert(db=db, alert_id=alert_id)
    return ConnectorSlaAlertResolveResponse(
        alert_id=alert_id,
        status="resolved" if ok else "not_found",
        message=message,
    )


@app.post("/connectors/{connector_name}/remediation", response_model=ConnectorRemediationTriggerResponse)
def connectors_remediation_trigger(
    connector_name: str,
    payload: ConnectorRemediationTriggerRequest,
    db: Session = Depends(get_db),
) -> ConnectorRemediationTriggerResponse:
    try:
        return trigger_connector_remediation(
            db=db,
            connector_name=connector_name,
            action_type=payload.action_type,
            reason=payload.reason,
            related_alert_id=None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/connectors/remediation/actions", response_model=ConnectorRemediationResponse)
def connectors_remediation_actions(
    connector_name: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> ConnectorRemediationResponse:
    return ConnectorRemediationResponse(
        records=list_connector_remediation_actions(
            db=db,
            connector_name=connector_name,
            limit=limit,
        ),
        generated_at=datetime.utcnow(),
    )


@app.post("/connectors/{connector_name}/simulate", response_model=ConnectorSimulationResponse)
def connector_simulate(
    connector_name: str,
    payload: ConnectorSimulationRequest,
    db: Session = Depends(get_db),
) -> ConnectorSimulationResponse:
    try:
        return simulate_connector_sync(
            db=db,
            connector_name=connector_name,
            config=payload.config,
            limit=payload.limit,
            use_checkpoint=payload.use_checkpoint,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/connectors/simulations", response_model=ConnectorSimulationsResponse)
def connectors_simulations_list(
    connector_name: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> ConnectorSimulationsResponse:
    return ConnectorSimulationsResponse(
        records=list_connector_simulations(
            db=db,
            connector_name=connector_name,
            status=status,
            limit=limit,
        ),
        generated_at=datetime.utcnow(),
    )


@app.post("/connectors/{connector_name}/policy/recommend", response_model=ConnectorPolicyRecommendationResponse)
def connector_policy_recommend(
    connector_name: str,
    db: Session = Depends(get_db),
) -> ConnectorPolicyRecommendationResponse:
    try:
        return recommend_connector_policy(db=db, connector_name=connector_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/connectors/{connector_name}/policy/auto-apply", response_model=ConnectorPolicyAutoApplyResponse)
def connector_policy_auto_apply(
    connector_name: str,
    payload: ConnectorPolicyAutoApplyRequest,
    db: Session = Depends(get_db),
) -> ConnectorPolicyAutoApplyResponse:
    try:
        return auto_apply_connector_policy(
            db=db,
            connector_name=connector_name,
            enabled=payload.enabled,
            dry_run=payload.dry_run,
            min_rate_limit_per_hour=payload.min_rate_limit_per_hour,
            max_rate_limit_per_hour=payload.max_rate_limit_per_hour,
            max_concurrent_runs_cap=payload.max_concurrent_runs_cap,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/connectors/policy/revisions", response_model=ConnectorPolicyRevisionsResponse)
def connectors_policy_revisions(
    connector_name: str | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> ConnectorPolicyRevisionsResponse:
    return ConnectorPolicyRevisionsResponse(
        records=list_connector_policy_revisions(
            db=db,
            connector_name=connector_name,
            status=status,
            limit=limit,
        ),
        generated_at=datetime.utcnow(),
    )


@app.post("/connectors/{connector_name}/policy/rollback", response_model=ConnectorPolicyRollbackResponse)
def connector_policy_rollback(
    connector_name: str,
    db: Session = Depends(get_db),
) -> ConnectorPolicyRollbackResponse:
    rolled_back, revision_id, message = rollback_latest_connector_policy_revision(
        db=db,
        connector_name=connector_name,
    )
    return ConnectorPolicyRollbackResponse(
        rolled_back=rolled_back,
        connector_name=connector_name,
        revision_id=revision_id,
        message=message,
    )


@app.post("/connectors/{connector_name}/policy/guardrail-check", response_model=ConnectorPolicyGuardrailCheckResponse)
def connector_policy_guardrail_check(
    connector_name: str,
    payload: ConnectorPolicyGuardrailCheckRequest,
    db: Session = Depends(get_db),
) -> ConnectorPolicyGuardrailCheckResponse:
    try:
        failure_ratio, breached, rolled_back, message = guardrail_check_connector_policy(
            db=db,
            connector_name=connector_name,
            lookback_runs=payload.lookback_runs,
            failure_ratio_threshold=payload.failure_ratio_threshold,
            auto_rollback=payload.auto_rollback,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ConnectorPolicyGuardrailCheckResponse(
        connector_name=connector_name,
        lookback_runs=payload.lookback_runs,
        failure_ratio=failure_ratio,
        threshold=payload.failure_ratio_threshold,
        breached=breached,
        rolled_back=rolled_back,
        message=message,
    )


@app.post("/connectors/{connector_name}/schedule")
def connector_schedule_upsert(
    connector_name: str,
    payload: ConnectorScheduleUpsertRequest,
    db: Session = Depends(get_db),
) -> dict[str, str | int | bool | None]:
    try:
        record = upsert_connector_schedule(
            db=db,
            connector_name=connector_name,
            enabled=payload.enabled,
            interval_minutes=payload.interval_minutes,
            priority=payload.priority,
            group_name=payload.group_name,
            is_paused=payload.is_paused,
            max_attempts=payload.max_attempts,
            limit=payload.limit,
            config=payload.config,
            run_immediately=payload.run_immediately,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "connector_name": record.connector_name,
        "enabled": record.enabled,
        "interval_minutes": record.interval_minutes,
        "priority": record.priority,
        "group_name": record.group_name,
        "is_paused": record.is_paused,
        "max_attempts": record.max_attempts,
        "next_run_at": record.next_run_at.isoformat() if record.next_run_at else None,
        "message": "Connector schedule saved.",
    }


@app.get("/connectors/schedules", response_model=ConnectorSchedulesResponse)
def connectors_schedules_list(db: Session = Depends(get_db)) -> ConnectorSchedulesResponse:
    return ConnectorSchedulesResponse(schedules=list_connector_schedules(db), generated_at=datetime.utcnow())


@app.post("/connectors/schedules/run-due", response_model=ConnectorScheduleRunResponse)
def connectors_run_due_schedules(
    max_runs: int = Query(default=20, ge=1, le=200),
    db: Session = Depends(get_db),
) -> ConnectorScheduleRunResponse:
    return run_due_connector_schedules(db=db, max_runs=max_runs)


@app.post("/connectors/{connector_name}/webhook", response_model=ConnectorWebhookTriggerResponse)
def connector_webhook_trigger(
    connector_name: str,
    payload: ConnectorWebhookTriggerRequest,
    db: Session = Depends(get_db),
) -> ConnectorWebhookTriggerResponse:
    try:
        return trigger_connector_webhook(
            db=db,
            connector_name=connector_name,
            event_type=payload.event_type,
            secret=payload.secret,
            config=payload.config,
            limit=payload.limit,
            use_checkpoint=payload.use_checkpoint,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/connectors/dead-letter", response_model=ConnectorDeadLetterListResponse)
def connectors_dead_letter(
    limit: int = Query(default=100, ge=1, le=1000),
    status: str = Query(default="open"),
    db: Session = Depends(get_db),
) -> ConnectorDeadLetterListResponse:
    return ConnectorDeadLetterListResponse(
        records=list_connector_dead_letter(db=db, limit=limit, status=status),
        generated_at=datetime.utcnow(),
    )


@app.post("/connectors/dead-letter/requeue", response_model=ConnectorDeadLetterRequeueResponse)
def connectors_dead_letter_requeue(
    payload: ConnectorDeadLetterRequeueRequest,
    db: Session = Depends(get_db),
) -> ConnectorDeadLetterRequeueResponse:
    requeued, ids = requeue_connector_dead_letter(
        db=db,
        dead_letter_ids=payload.dead_letter_ids,
        limit=payload.limit,
    )
    return ConnectorDeadLetterRequeueResponse(requeued=requeued, dead_letter_ids=ids)


@app.get("/connectors/audit", response_model=ConnectorAuditResponse)
def connectors_audit_list(
    connector_name: str | None = Query(default=None),
    action: str | None = Query(default=None),
    result: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=2000),
    db: Session = Depends(get_db),
) -> ConnectorAuditResponse:
    return ConnectorAuditResponse(
        records=list_connector_audits(
            db=db,
            connector_name=connector_name,
            action=action,
            result=result,
            limit=limit,
        ),
        generated_at=datetime.utcnow(),
    )


@app.get("/feedback/export", response_model=FeedbackExportResponse)
def feedback_export(
    limit: int = Query(default=500, ge=1, le=5000),
    db: Session = Depends(get_db),
) -> FeedbackExportResponse:
    return FeedbackExportResponse(records=export_feedback(db, limit=limit), generated_at=datetime.utcnow())


@app.post("/index/reembed")
def reembed_index(payload: RebuildRequest, db: Session = Depends(get_db)) -> dict[str, int | str]:
    if payload.item_ids:
        items = db.execute(select(Item).where(Item.id.in_(payload.item_ids))).scalars().all()
    else:
        items = db.execute(select(Item)).scalars().all()

    for item in items:
        item.status = "pending"
        db.add(item)
        db.add(Job(item_id=item.id, job_type="embed", status="pending", attempts=0))
    db.commit()
    return {"enqueued": len(items), "message": "Embedding reindex jobs enqueued."}
