from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from ...database import get_db
from ...models.schemas import (
    GenerateRequest,
    JDData,
    ResumeData,
    GapAnalysis,
    LearningPlan,
    InterviewPrep,
    SessionStatus,
)
from ...chains.gap_analyzer import analyze_gaps, generate_learning_plan, generate_interview_prep

router = APIRouter(tags=["Results"])


# ────────────────────────────────────────────────────────────────
# Helper
# ────────────────────────────────────────────────────────────────

async def _get_doc_or_404(session_id: str) -> dict:
    db = get_db()
    doc = await db.sessions.find_one({"session_id": session_id})
    if not doc:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found.")
    return doc


# ────────────────────────────────────────────────────────────────
# Gap Analysis
# ────────────────────────────────────────────────────────────────

@router.post("/analysis/generate")
async def generate_analysis(body: GenerateRequest):
    """
    Run the Gap Analyzer Chain on the uploaded JD + Resume.
    Requires both JD and Resume to be uploaded first.
    Stores the analysis in the session document.
    """
    doc = await _get_doc_or_404(body.session_id)

    if not doc.get("jd_data"):
        raise HTTPException(status_code=400, detail="Upload a Job Description first.")
    if not doc.get("resume_data"):
        raise HTTPException(status_code=400, detail="Upload a Resume first.")

    jd_data = JDData(**doc["jd_data"])
    resume_data = ResumeData(**doc["resume_data"])

    try:
        gap_analysis = await analyze_gaps(jd_data, resume_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gap analysis failed: {str(e)}")

    db = get_db()
    await db.sessions.update_one(
        {"session_id": body.session_id},
        {
            "$set": {
                "gap_analysis": gap_analysis.model_dump(),
                "status": SessionStatus.ANALYZED,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    return {"success": True, "gap_analysis": gap_analysis.model_dump()}


@router.get("/analysis/{session_id}")
async def get_analysis(session_id: str):
    """Retrieve the stored gap analysis for a session."""
    doc = await _get_doc_or_404(session_id)
    if not doc.get("gap_analysis"):
        raise HTTPException(status_code=404, detail="Gap analysis not generated yet.")
    return {"success": True, "gap_analysis": doc["gap_analysis"]}


# ────────────────────────────────────────────────────────────────
# Learning Plan
# ────────────────────────────────────────────────────────────────

@router.post("/learning-plan/generate")
async def generate_plan(body: GenerateRequest):
    """
    Generate a personalized learning plan using Tavily web search
    to find real resource URLs (YouTube, docs, courses, LeetCode).
    Requires gap analysis to be completed first.
    """
    doc = await _get_doc_or_404(body.session_id)

    if not doc.get("gap_analysis"):
        raise HTTPException(
            status_code=400,
            detail="Run gap analysis first (POST /api/analysis/generate).",
        )

    jd_data = JDData(**doc["jd_data"])
    resume_data = ResumeData(**doc["resume_data"])
    gap_analysis = GapAnalysis(**doc["gap_analysis"])

    try:
        learning_plan = await generate_learning_plan(gap_analysis, jd_data, resume_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Learning plan generation failed: {str(e)}")

    db = get_db()
    await db.sessions.update_one(
        {"session_id": body.session_id},
        {
            "$set": {
                "learning_plan": learning_plan.model_dump(),
                "status": SessionStatus.PLAN_GENERATED,
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    return {"success": True, "learning_plan": learning_plan.model_dump()}


@router.get("/learning-plan/{session_id}")
async def get_learning_plan(session_id: str):
    """Retrieve the stored learning plan for a session."""
    doc = await _get_doc_or_404(session_id)
    if not doc.get("learning_plan"):
        raise HTTPException(status_code=404, detail="Learning plan not generated yet.")
    return {"success": True, "learning_plan": doc["learning_plan"]}


# ────────────────────────────────────────────────────────────────
# Interview Prep
# ────────────────────────────────────────────────────────────────

@router.post("/interview-prep/generate")
async def generate_prep(body: GenerateRequest):
    """
    Generate a company-specific interview preparation guide.
    Uses Tavily to research the company's interview process, rounds,
    and fetch LeetCode/HackerRank problem links.
    """
    doc = await _get_doc_or_404(body.session_id)

    if not doc.get("gap_analysis"):
        raise HTTPException(
            status_code=400,
            detail="Run gap analysis first (POST /api/analysis/generate).",
        )

    jd_data = JDData(**doc["jd_data"])
    resume_data = ResumeData(**doc["resume_data"])
    gap_analysis = GapAnalysis(**doc["gap_analysis"])

    try:
        interview_prep = await generate_interview_prep(jd_data, resume_data, gap_analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interview prep generation failed: {str(e)}")

    db = get_db()
    await db.sessions.update_one(
        {"session_id": body.session_id},
        {
            "$set": {
                "interview_prep": interview_prep.model_dump(),
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )
    return {"success": True, "interview_prep": interview_prep.model_dump()}


@router.get("/interview-prep/{session_id}")
async def get_interview_prep(session_id: str):
    """Retrieve the stored interview prep guide for a session."""
    doc = await _get_doc_or_404(session_id)
    if not doc.get("interview_prep"):
        raise HTTPException(status_code=404, detail="Interview prep not generated yet.")
    return {"success": True, "interview_prep": doc["interview_prep"]}
