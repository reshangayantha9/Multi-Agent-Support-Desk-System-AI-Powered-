from typing import Optional, Annotated
import logging
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.schemas import TicketCreate, TicketOut, TicketPatch
from app.services import ticket_service as ts

router = APIRouter(prefix="/tickets")
logger = logging.getLogger(__name__)

@router.post(
    "",
    response_model=TicketOut,
    status_code=201,
)
async def create_ticket(
    body: TicketCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    logger.info(f"[TICKET][CREATE][REQ] title='{body.title[:30]}...' | severity={body.severity}")
    return await ts.create_ticket(db, body)


@router.get(
    "/{ticket_id}",
    response_model=TicketOut,
    responses={
        404: {"description": "Ticket not found"}
    },
)
async def get_ticket(
    ticket_id: Annotated[str, Path(description="Unique ticket ID")],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    logger.info(f"[TICKET][GET][REQ] ticket_id={ticket_id}")
    ticket = await ts.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket


@router.patch(
    "/{ticket_id}",
    response_model=TicketOut,
    responses={
        404: {"description": "Ticket not found"}
    },
)
async def patch_ticket(
    ticket_id: Annotated[str, Path(description="Unique ticket ID")],
    body: TicketPatch,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    logger.info(
        f"[TICKET][PATCH][REQ] ticket_id={ticket_id} | "
        f"status={body.status} | owner={body.owner} | category={body.category}"
    )
    ticket = await ts.patch_ticket(db, ticket_id, body)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket


@router.get(
    "",
    response_model=list[TicketOut],
)
async def list_tickets(
    db: Annotated[AsyncSession, Depends(get_db)],
    status: Annotated[
        Optional[str],
        Query(description="Filter by status, e.g. OPEN")
    ] = None,
    limit: Annotated[
        int,
        Query(ge=1, le=200, description="Maximum number of tickets to return")
    ] = 50,
):
    logger.info(f"[TICKET][LIST][REQ] status={status} | limit={limit}")
    if status:
        return await ts.list_tickets_by_status(db, status, limit=limit)
    return await ts.list_all_tickets(db, limit=limit)