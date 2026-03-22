from typing import Annotated
import logging
from fastapi import APIRouter, HTTPException, Body

from app.db.schemas import TriageRunRequest, TriageRunResponse
from app.services import triage_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/triage/run",
    response_model=TriageRunResponse,
    responses={
        500: {"description": "Internal Server Error - Triage processing failed"}
    },
)
async def run_triage_endpoint(
    request: Annotated[TriageRunRequest, Body()],
):
    logger.info(f"[TRIAGE][REQ] limit={request.limit}")
    try:
        return await triage_service.process_triage_run(request)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))