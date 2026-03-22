import logging
from langchain_core.messages import AIMessage, HumanMessage
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.schemas import ChatRequest, ChatResponse, Citation, IntentState, ToolCallLog
from app.services.session_service import load_session, save_session
from app.services.support_graph import SupportState, get_support_graph

logger = logging.getLogger(__name__)

async def process_chat_message(request: ChatRequest, db: AsyncSession) -> ChatResponse:
    session_id = request.session_id
    user_message = request.message

    logger.info(f"[CHAT_SVC][START] session_id={session_id} | processing message")
    session_state = await load_session(db, session_id)

    history_messages = []
    for entry in session_state.get("chat_history", []):
        if entry["role"] == "human":
            history_messages.append(HumanMessage(content=entry["content"]))
        elif entry["role"] == "assistant":
            history_messages.append(AIMessage(content=entry["content"]))

    history_messages.append(HumanMessage(content=user_message))

    initial_state: SupportState = {
        "session_id": session_id,
        "messages": history_messages,
        "chat_history": session_state.get("chat_history", []),
        "created_ticket_ids": session_state.get("created_ticket_ids", []),
        "citations": [],
        "created_ticket_id": None,
        "tool_calls_log": [],
        "intent": "faq",
        "confidence": 0.8,
        "safety_blocked": False,
    }

    graph = get_support_graph()
    try:
        final_state: SupportState = await graph.ainvoke(initial_state)
    except Exception as exc:
        logger.exception("Support graph error")
        raise RuntimeError(f"Agent error: {str(exc)}")

    answer = ""
    for msg in reversed(final_state["messages"]):
        if isinstance(msg, AIMessage) and msg.content:
            answer = msg.content
            break

    max_history = 20
    new_history = list(session_state.get("chat_history", []))
    new_history.append({"role": "human", "content": user_message})
    new_history.append({"role": "assistant", "content": answer})
    new_history = new_history[-max_history:]

    # Persist session
    new_session_state = {
        "chat_history": new_history,
        "created_ticket_ids": final_state.get("created_ticket_ids", []),
    }
    last_ticket = final_state.get("created_ticket_id")
    await save_session(db, session_id, new_session_state, last_ticket_id=last_ticket)

    citations = [
        Citation(doc_id=c["doc_id"], chunk_id=c["chunk_id"])
        for c in final_state.get("citations", [])
    ]
    tool_calls = [
        ToolCallLog(**tc) for tc in final_state.get("tool_calls_log", [])
    ]

    return ChatResponse(
        session_id=session_id,
        answer=answer,
        citations=citations,
        created_ticket_id=final_state.get("created_ticket_id"),
        tool_calls=tool_calls,
        state=IntentState(
            intent=final_state.get("intent", "faq"),
            confidence=final_state.get("confidence", 0.8),
        ),
    )