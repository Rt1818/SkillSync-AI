import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from ...database import get_db
from ...models.schemas import CreateSessionResponse, Session, SessionStatus

router = APIRouter(prefix="/sessions", tags=["Sessions"])


@router.post("", response_model=CreateSessionResponse)
async def create_session():
    """Create a new SkillSync session and return the session_id."""
    db = get_db()
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)

    doc = {
        "session_id": session_id,
        "created_at": now,
        "updated_at": now,
        "status": SessionStatus.CREATED,
        "jd_data": None,
        "resume_data": None,
        "gap_analysis": None,
        "learning_plan": None,
        "interview_prep": None,
    }
    await db.sessions.insert_one(doc)

    return CreateSessionResponse(
        session_id=session_id,
        status=SessionStatus.CREATED,
        created_at=now,
    )


@router.get("/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """Retrieve full session data by session_id."""
    db = get_db()
    doc = await db.sessions.find_one({"session_id": session_id})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")

    doc.pop("_id", None)
    return Session(**doc)


@router.get("", response_model=list[Session])
async def get_all_sessions():
    """Retrieve all sessions for the history sidebar."""
    db = get_db()
    cursor = db.sessions.find({}).sort("created_at", -1)
    sessions = []
    async for doc in cursor:
        doc.pop("_id", None)
        sessions.append(Session(**doc))
    return sessions
