from __future__ import annotations
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    severity: Optional[str] = Field(None, pattern="^(low|medium|high|critical)$")
    user_email: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class TicketPatch(BaseModel):
    status: Optional[str] = None
    owner: Optional[str] = None
    severity: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    resolution: Optional[str] = None


class NoteOut(BaseModel):
    id: int
    note_type: str
    content: str
    created_by: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketOut(BaseModel):
    id: str
    title: str
    description: str
    category: Optional[str] =None
    severity: Optional[str] =None
    priority: Optional[str] =None
    status: str
    owner: Optional[str] =None
    user_email: Optional[str] =None
    resolution: Optional[str] =None
    metadata: Optional[dict[str, Any]] = Field(None, alias="metadata_")
    created_at: datetime
    updated_at: datetime
    notes: list[NoteOut] = []

    model_config = {"from_attributes": True, "populate_by_name": True}



class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1, max_length=64)
    message: str = Field(..., min_length=1)


class Citation(BaseModel):
    doc_id: str
    chunk_id: int


class ToolCallLog(BaseModel):
    agent: str
    tool: str
    args: dict[str, Any]
    result: Any


class IntentState(BaseModel):
    intent: str = "faq"
    confidence: float = 0.0


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: list[Citation] = []
    created_ticket_id: Optional[str] = None
    tool_calls: list[ToolCallLog] = []
    state: IntentState


class TriageRunRequest(BaseModel):
    limit: int = Field(5, ge=1, le=50)


class TriageUpdate(BaseModel):
    ticket_id: str
    status: str


class TriageRunResponse(BaseModel):
    processed: int
    updates: list[TriageUpdate]
