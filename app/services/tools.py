from __future__ import annotations

import json
import logging
from typing import Any, Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.services import rag_service
from app.services import ticket_service as ts
from app.db.schemas import TicketCreate, TicketPatch
from app.db.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


class SearchKBInput(BaseModel):
    query: str = Field(..., description="Search query to find relevant KB articles")


class CreateTicketInput(BaseModel):
    title: str = Field(..., description="Short summary of the issue")
    description: str = Field(..., description="Full description of the issue")
    severity: str = Field("medium", description="low | medium | high | critical")
    user_email: Optional[str] = Field(None, description="Email of the user reporting the issue")
    metadata: Optional[dict[str, Any]] = Field(None, description="Extra key-value metadata")


class GetTicketInput(BaseModel):
    ticket_id: str = Field(..., description="The ticket ID, e.g. TCK-ABC123")


class ListOpenTicketsInput(BaseModel):
    limit: int = Field(5, description="Maximum number of open tickets to retrieve")


class UpdateTicketInput(BaseModel):
    ticket_id: str = Field(..., description="Ticket ID to update")
    status: Optional[str] = Field(None, description="OPEN | IN_PROGRESS | WAITING_FOR_USER | RESOLVED")
    owner: Optional[str] = Field(None, description="Billing | Support | Engineering")
    severity: Optional[str] = Field(None)
    category: Optional[str] = Field(None, description="billing | auth | bug | how-to")
    priority: Optional[str] = Field(None, description="P1 | P2 | P3 | P4")
    notes: Optional[str] = Field(None, description="Internal note to append")
    resolution: Optional[str] = Field(None, description="Resolution steps or summary")


async def _search_kb(query: str) -> str:
    logger.info(f"[TOOL][SEARCH_KB][START] query='{query}'")
    chunks = await rag_service.search_kb(query)
    if not chunks:
        return json.dumps({"found": False, "chunks": []})
    return json.dumps({"found": True, "chunks": chunks})


async def _create_ticket(
    title: str,
    description: str,
    severity: str = "medium",
    user_email: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> str:

    logger.info(
        f"[TOOL][CREATE_TICKET][START] title='{title[:40]}...' | "
        f"severity={severity} | has_email={user_email is not None}"
    )
    data = TicketCreate(
        title=title,
        description=description,
        severity=severity,
        user_email=user_email,
        metadata=metadata,
    )
    async with AsyncSessionLocal() as db:
        ticket = await ts.create_ticket(db, data)
        return json.dumps({
            "ticket_id": ticket.id,
            "status": ticket.status,
            "title": ticket.title,
        })


async def _get_ticket(ticket_id: str) -> str:
    logger.info(f"[TOOL][GET_TICKET][START] ticket_id={ticket_id}")
    async with AsyncSessionLocal() as db:
        ticket = await ts.get_ticket(db, ticket_id)
        if not ticket:
            return json.dumps({"error": f"Ticket {ticket_id} not found"})
        notes = [
            {"content": n.content, "type": n.note_type, "by": n.created_by}
            for n in ticket.notes
        ]
        return json.dumps({
            "ticket_id": ticket.id,
            "title": ticket.title,
            "status": ticket.status,
            "severity": ticket.severity,
            "category": ticket.category,
            "owner": ticket.owner,
            "resolution": ticket.resolution,
            "notes": notes,
            "created_at": ticket.created_at.isoformat(),
            "updated_at": ticket.updated_at.isoformat(),
        })


async def _list_open_tickets(limit: int = 5) -> str:
    logger.info(f"[TOOL][LIST_OPEN][START] limit={limit}")
    async with AsyncSessionLocal() as db:
        tickets = await ts.list_open_tickets(db, limit=limit)
        items = [
            {
                "ticket_id": t.id,
                "title": t.title,
                "description": t.description,
                "severity": t.severity,
                "user_email": t.user_email,
                "created_at": t.created_at.isoformat(),
            }
            for t in tickets
        ]
        return json.dumps({"count": len(items), "tickets": items})


async def _update_ticket(
    ticket_id: str,
    status: Optional[str] = None,
    owner: Optional[str] = None,
    severity: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    notes: Optional[str] = None,
    resolution: Optional[str] = None,
) -> str:
    logger.info(
        f"[TOOL][UPDATE_TICKET][START] ticket_id={ticket_id} | "
        f"status={status} | owner={owner} | category={category} | priority={priority} | "
        f"has_notes={notes is not None} | has_resolution={resolution is not None}"
    )

    patch = TicketPatch(
        status=status,
        owner=owner,
        severity=severity,
        category=category,
        priority=priority,
        notes=notes,
        resolution=resolution,
    )
    async with AsyncSessionLocal() as db:
        ticket = await ts.patch_ticket(db, ticket_id, patch)
        if not ticket:
            return json.dumps({"error": f"Ticket {ticket_id} not found"})
        return json.dumps({
            "ticket_id": ticket.id,
            "status": ticket.status,
            "owner": ticket.owner,
            "category": ticket.category,
            "updated": True,
        })



def build_support_tools() -> list[StructuredTool]:
    logger.debug("[TOOLS][BUILD] Building support agent tools (search_kb, create_ticket, get_ticket)")
    return [
        StructuredTool.from_function(
            coroutine=_search_kb,
            name="search_kb",
            description="Search the knowledge base. Use for any FAQ or troubleshooting query.",
            args_schema=SearchKBInput,
        ),
        StructuredTool.from_function(
            coroutine=_create_ticket,
            name="create_ticket",
            description="Create a support ticket. Use when user reports an incident or requests escalation.",
            args_schema=CreateTicketInput,
        ),
        StructuredTool.from_function(
            coroutine=_get_ticket,
            name="get_ticket",
            description="Fetch the current status and details of a ticket by ticket_id.",
            args_schema=GetTicketInput,
        ),
    ]


def build_triage_tools() -> list[StructuredTool]:
    logger.debug("[TOOLS][BUILD] Building triage agent tools (list_open_tickets, get_ticket, update_ticket)")
    return [
        StructuredTool.from_function(
            coroutine=_list_open_tickets,
            name="list_open_tickets",
            description="List open tickets in the queue.",
            args_schema=ListOpenTicketsInput,
        ),
        StructuredTool.from_function(
            coroutine=_get_ticket,
            name="get_ticket",
            description="Get full details of a specific ticket.",
            args_schema=GetTicketInput,
        ),
        StructuredTool.from_function(
            coroutine=_update_ticket,
            name="update_ticket",
            description=(
                "Update a ticket's status, owner, severity, category, priority, "
                "internal notes, and resolution. Use after classifying a ticket."
            ),
            args_schema=UpdateTicketInput,
        ),
    ]
