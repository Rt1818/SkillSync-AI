from datetime import datetime, timezone
from fastapi import APIRouter, Form, UploadFile, File, HTTPException
from typing import Optional
from ...database import get_db
from ...models.schemas import SessionStatus
from ...chains.jd_parser import parse_jd
from ...chains.resume_parser import parse_resume
from ...services.file_service import (
    extract_text_from_file,
    extract_text_from_url,
    validate_file_size,
)

router = APIRouter(prefix="/upload", tags=["Upload"])


async def _get_session_or_404(session_id: str):
    db = get_db()
    doc = await db.sessions.find_one({"session_id": session_id})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return doc


@router.post("/jd")
async def upload_jd(
    session_id: str = Form(...),
    url: Optional[str] = Form(None),
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
):
    """
    Upload / provide a Job Description via:
      - file upload  (PDF / DOCX / TXT)
      - url          (LinkedIn, Indeed, company site, etc.)
      - text         (paste raw JD text)

    Runs the JD Parser Chain and stores result in the session.
    """
    await _get_session_or_404(session_id)

    # ── Extract raw text from whichever source was provided ──
    if file and file.filename:
        validate_file_size(file)
        raw_text = await extract_text_from_file(file)
    elif url:
        raw_text = await extract_text_from_url(url)
    elif text:
        raw_text = text.strip()
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide one of: file, url, or text.",
        )

    if len(raw_text) < 50:
        raise HTTPException(status_code=400, detail="Extracted JD text is too short.")

    # ── Run JD Parser Chain ──
    try:
        jd_data = await parse_jd(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JD parsing failed: {str(e)}")

    # ── Persist to MongoDB ──
    db = get_db()
    await db.sessions.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "jd_data": jd_data.model_dump(),
                "status": SessionStatus.JD_UPLOADED,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return {"success": True, "jd_data": jd_data.model_dump()}


@router.post("/resume")
async def upload_resume(
    session_id: str = Form(...),
    file: UploadFile = File(...),
):
    """
    Upload a resume (PDF / DOCX / TXT).
    Runs the Resume Parser Chain and stores result in the session.
    """
    await _get_session_or_404(session_id)
    validate_file_size(file)

    # ── Extract raw text ──
    raw_text = await extract_text_from_file(file)

    if len(raw_text) < 50:
        raise HTTPException(status_code=400, detail="Resume appears to be empty or unreadable.")

    # ── Run Resume Parser Chain ──
    try:
        resume_data = await parse_resume(raw_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")

    # ── Persist to MongoDB ──
    db = get_db()
    await db.sessions.update_one(
        {"session_id": session_id},
        {
            "$set": {
                "resume_data": resume_data.model_dump(),
                "status": SessionStatus.RESUME_UPLOADED,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    return {"success": True, "resume_data": resume_data.model_dump()}
