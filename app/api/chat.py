from typing import Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.schemas import ChatRequest, ChatResponse
from app.services import chat_service

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        500: {
            "description": "Internal Server Error - Chat processing failed"
        }
    },
)
async def chat_endpoint(
    request: ChatRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    try:
        logger.info(f"[CHAT][REQ] session_id={request.session_id} | message='{request.message[:50]}...'")
        return await chat_service.process_chat_message(request, db)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))