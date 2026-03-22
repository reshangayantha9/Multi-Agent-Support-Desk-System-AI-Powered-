import logging
import uuid
from app.db.schemas import TriageRunRequest, TriageRunResponse, TriageUpdate
from app.services.triage_graph import TriageState, get_triage_graph

logger = logging.getLogger(__name__)

async def process_triage_run(request: TriageRunRequest) -> TriageRunResponse:
    run_id = str(uuid.uuid4())
    logger.info(f"[TRIAGE_SVC][START] run_id={run_id} | limit={request.limit}")

    initial_state: TriageState = {
        "run_id": run_id,
        "limit": request.limit,
        "tickets_to_process": [],
        "current_ticket_idx": 0,
        "processed_count": 0,
        "updates": [],
    }

    graph = get_triage_graph()
    try:
        final_state: TriageState = await graph.ainvoke(initial_state)
    except Exception as exc:
        logger.exception("Triage graph error")
        raise RuntimeError(f"Triage error: {str(exc)}")

    updates = [
        TriageUpdate(ticket_id=u["ticket_id"], status=u["status"])
        for u in final_state.get("updates", [])
    ]

    logger.info(f"[TRIAGE_SVC][RESULT] run_id={run_id} | updates={[f'{u.ticket_id}:{u.status}' for u in updates]}")

    return TriageRunResponse(
        processed=final_state.get("processed_count", 0),
        updates=updates,
    )