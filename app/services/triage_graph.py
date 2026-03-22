from __future__ import annotations

import json
import logging
import os
from typing import TypedDict, Any
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, ToolMessage, ToolCall
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

from app.config.settings import get_settings
from app.services.tools import build_triage_tools

logger = logging.getLogger(__name__)
settings = get_settings()

os.environ["OPENAI_API_KEY"] = settings.openai_api_key



class TriageState(TypedDict):
    run_id: str
    limit: int
    tickets_to_process: list[dict]
    current_ticket_idx: int
    processed_count: int
    updates: list[dict]



TRIAGE_SYSTEM_PROMPT = """You are an expert technical support triage agent.
Your job is to process support tickets, classify them, and take appropriate action.

For each ticket, you MUST call the `update_ticket` tool and provide ALL of the following arguments:
1. category: 'billing' | 'auth' | 'bug' | 'how-to'
2. severity: 'low' | 'medium' | 'high' | 'critical'
3. priority: 'P1' | 'P2' | 'P3' | 'P4' (You MUST assign a priority based on severity).
4. owner: 'Billing' | 'Support' | 'Engineering'
5. status:
   - 'IN_PROGRESS' (Use this if you have enough info to propose a resolution or begin work).
   - 'WAITING_FOR_USER' (Use this ONLY if critical info is missing to proceed).
   - 'RESOLVED' (Use this if providing a simple known fix).
6. notes: Your detailed reasoning and next steps (internal note).
7. resolution: Step-by-step resolution plan (if applicable).

Classification guidelines:
- Billing errors (E101-E105, E110), payment failures → owner: Billing, category: billing
- Login, 2FA, password, OAuth → owner: Support, category: auth
- API errors, integration failures, 500 errors → owner: Engineering, category: bug
- How-to questions, feature questions → owner: Support, category: how-to

Priority mapping:
- critical = P1
- high = P2
- medium = P3
- low = P4

Always be thorough and professional in your internal notes.
"""


def _get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.chat_model,
        temperature=0.1
    )


async def _execute_triage_tool(
    tc: ToolCall,
    tools_by_name: dict,
    current_ticket_id: str
) -> tuple[ToolMessage, str, str]:
    tool = tools_by_name.get(tc["name"])
    if not tool:
        error_msg = f"Error: Tool {tc['name']} not found."
        return ToolMessage(content=error_msg, tool_call_id=tc["id"]), "IN_PROGRESS", current_ticket_id

    try:
        result = await tool.ainvoke(tc["args"])
    except Exception as exc:
        logger.error("Tool execution error for %s: %s", tc["name"], exc)
        result = json.dumps({"error": str(exc)})

    new_status = "IN_PROGRESS"
    updated_ticket_id = current_ticket_id

    if tc["name"] == "update_ticket":
        try:
            r = json.loads(result) if isinstance(result, str) else result
            new_status = r.get("status", "IN_PROGRESS")
            updated_ticket_id = r.get("ticket_id", current_ticket_id)
        except (ValueError, TypeError):
            logger.debug("Failed to parse update_ticket response.")

    return ToolMessage(content=str(result), tool_call_id=tc["id"]), new_status, updated_ticket_id


async def node_pull_tickets(state: TriageState) -> dict:
    run_id = state["run_id"]
    logger.info(f"[TRIAGE][PULL][START] run_id={run_id} | limit={state['limit']}")
    tools_by_name = {t.name: t for t in build_triage_tools()}
    tool = tools_by_name["list_open_tickets"]

    try:
        result = await tool.ainvoke({"limit": state["limit"]})
        data = json.loads(result)
        tickets = data.get("tickets", [])
    except Exception as exc:
        logger.error(f"Failed to pull tickets: {exc}")
        tickets = []

    logger.info(f"Triage run {state['run_id']}: pulled {len(tickets)} OPEN tickets")
    return {
        "tickets_to_process": tickets,
        "current_ticket_idx": 0,
        "processed_count": 0,
        "updates": [],
    }


async def node_process_ticket(state: TriageState) -> dict:
    idx = state["current_ticket_idx"]
    ticket = state["tickets_to_process"][idx]
    ticket_id = ticket["ticket_id"]
    run_id = state["run_id"]

    logger.info(
        f"[TRIAGE][PROCESS][START] run_id={run_id} | "
        f"ticket={ticket_id} ({idx + 1}/{len(state['tickets_to_process'])}) | "
    )

    tools = build_triage_tools()
    llm = _get_llm().bind_tools(tools)
    tools_by_name = {t.name: t for t in tools}

    user_msg = (
        f"Please triage this support ticket:\n\n"
        f"Ticket ID: {ticket['ticket_id']}\n"
        f"Title: {ticket['title']}\n"
        f"Description: {ticket['description']}\n"
        f"Severity (current): {ticket.get('severity', 'not set')}\n"
        f"User Email: {ticket.get('user_email', 'unknown')}\n"
        f"Created: {ticket.get('created_at', 'unknown')}\n\n"
        f"Classify, determine owner, propose resolution or ask for more info, "
        f"then call update_ticket to persist your decision."
    )

    messages: list[BaseMessage] = [
        SystemMessage(content=TRIAGE_SYSTEM_PROMPT),
        HumanMessage(content=user_msg),
    ]

    ticket_id = ticket["ticket_id"]
    current_status = "IN_PROGRESS"

    for _ in range(3):
        response = await llm.ainvoke(messages)
        messages.append(response)

        if not hasattr(response, "tool_calls") or not response.tool_calls:
            break

        for tc in response.tool_calls:
            tool_msg, new_status, updated_id = await _execute_triage_tool(
                tc, tools_by_name, ticket_id
            )
            messages.append(tool_msg)

            if tc["name"] == "update_ticket":
                current_status = new_status
                ticket_id = updated_id

    updates = list(state.get("updates", []))
    updates.append({"ticket_id": ticket_id, "status": current_status})

    return {
        "current_ticket_idx": idx + 1,
        "processed_count": state.get("processed_count", 0) + 1,
        "updates": updates,
    }

def route_next_ticket(state: TriageState) -> str:
    idx = state["current_ticket_idx"]
    total = len(state["tickets_to_process"])
    if idx < total:
        return "process_ticket"
    return END



def build_triage_graph() -> Any:
    g: Any = StateGraph(TriageState)  # type: ignore

    g.add_node("pull_tickets", node_pull_tickets)
    g.add_node("process_ticket", node_process_ticket)

    g.set_entry_point("pull_tickets")
    g.add_conditional_edges("pull_tickets", route_next_ticket, {
        "process_ticket": "process_ticket",
        END: END,
    })
    g.add_conditional_edges("process_ticket", route_next_ticket, {
        "process_ticket": "process_ticket",
        END: END,
    })

    return g.compile()


_triage_graph = None


def get_triage_graph() -> Any:
    global _triage_graph
    if _triage_graph is None:
        _triage_graph = build_triage_graph()
    return _triage_graph