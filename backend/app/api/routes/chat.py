from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from ...database import get_db
from ...models.schemas import ChatRequest, ChatHistoryResponse, ChatMessage, JDData, ResumeData, GapAnalysis
from ...agent.skillsync_agent import stream_chat_with_agent, get_session_history

router = APIRouter(prefix="/chat", tags=["Chat"])


async def _load_session_context(session_id: str):
    """Load JD, Resume, and GapAnalysis from a session doc."""
    db = get_db()
    doc = await db.sessions.find_one({"session_id": session_id})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    if not doc.get("jd_data"):
        raise HTTPException(status_code=400, detail="Upload a Job Description first.")
    if not doc.get("resume_data"):
        raise HTTPException(status_code=400, detail="Upload a Resume first.")
    if not doc.get("gap_analysis"):
        raise HTTPException(
            status_code=400,
            detail="Run gap analysis first (POST /api/analysis/generate).",
        )

    jd_data = JDData(**doc["jd_data"])
    resume_data = ResumeData(**doc["resume_data"])
    gap_analysis = GapAnalysis(**doc["gap_analysis"])
    return jd_data, resume_data, gap_analysis


@router.post("/stream")
async def chat_stream(body: ChatRequest):
    """
    Send a message to the SkillSync Agent and stream the response via SSE.
    The agent has access to web_search and scrape_url tools.
    Chat history is persisted in MongoDB per session.
    """
    jd_data, resume_data, gap_analysis = await _load_session_context(body.session_id)

    async def event_generator():
        async for chunk in stream_chat_with_agent(
            session_id=body.session_id,
            message=body.message,
            jd_data=jd_data,
            resume_data=resume_data,
            gap_analysis=gap_analysis,
        ):
            yield chunk

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable Nginx buffering
        },
    )


@router.get("/{session_id}/history", response_model=ChatHistoryResponse)
async def get_chat_history(session_id: str):
    """Retrieve the full chat history for a session."""
    history = get_session_history(session_id)
    messages_raw = history.messages  # list of BaseMessage

    messages = []
    for msg in messages_raw:
        role = "human" if msg.type == "human" else "ai"
        messages.append(ChatMessage(role=role, content=msg.content))

    return ChatHistoryResponse(session_id=session_id, messages=messages)


@router.delete("/{session_id}/history")
async def clear_chat_history(session_id: str):
    """Clear the chat history for a session (for re-assessment)."""
    history = get_session_history(session_id)
    history.clear()
    return {"success": True, "message": "Chat history cleared."}
