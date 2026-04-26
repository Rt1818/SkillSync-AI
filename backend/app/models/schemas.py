from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from enum import Enum
from datetime import datetime


# ─────────────────────────────────────────────
# JD & Resume Parsing
# ─────────────────────────────────────────────

class SkillRequirement(BaseModel):
    name: str
    importance: Literal["must_have", "nice_to_have"] = "must_have"
    level: Literal["beginner", "intermediate", "advanced"] = "intermediate"

class JDData(BaseModel):
    company_name: str
    role_title: str
    industry: str = ""
    experience_required: str = ""
    required_skills: List[SkillRequirement] = []
    summary: str = ""

class CandidateSkill(BaseModel):
    name: str
    years_of_experience: float = 0.0
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"
    evidence: List[str] = []

class ResumeData(BaseModel):
    candidate_name: str
    email: Optional[str] = None
    current_role: Optional[str] = None
    total_experience_years: float = 0.0
    skills: List[CandidateSkill] = []
    education: List[str] = []
    summary: str = ""


# ─────────────────────────────────────────────
# Gap Analysis
# ─────────────────────────────────────────────

class GapCategory(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    WEAK = "WEAK"
    MISSING = "MISSING"

class SkillAssessment(BaseModel):
    skill_name: str
    jd_level: str
    candidate_level: str
    score: int = Field(..., ge=0, le=100)
    gap_category: GapCategory
    evidence: List[str] = []
    notes: str = ""
    is_adjacent: bool = False  # can quickly learn from existing skills

class GapAnalysis(BaseModel):
    overall_match_score: int = Field(..., ge=0, le=100)
    skill_assessments: List[SkillAssessment] = []
    strengths: List[str] = []
    critical_gaps: List[str] = []
    adjacent_skills: List[str] = []          # e.g. "Docker → Kubernetes"
    recommended_focus_order: List[str] = []  # ordered learning priority


# ─────────────────────────────────────────────
# Learning Plan
# ─────────────────────────────────────────────

class Resource(BaseModel):
    type: Literal["youtube", "article", "course", "practice", "documentation", "other"]
    title: str
    url: str
    description: Optional[str] = None

class Topic(BaseModel):
    title: str
    description: str
    estimated_minutes: int = 60
    resources: List[Resource] = []

class Module(BaseModel):
    title: str
    description: str = ""
    topics: List[Topic] = []
    estimated_hours: float = 1.0

class Course(BaseModel):
    skill_name: str
    priority: int = 1
    gap_category: str
    total_estimated_hours: float
    why_important: str = ""
    modules: List[Module] = []

class LearningPlan(BaseModel):
    total_estimated_hours: float
    completion_timeline_weeks: int
    courses: List[Course] = []


# ─────────────────────────────────────────────
# Interview Prep
# ─────────────────────────────────────────────

class InterviewRound(BaseModel):
    round_number: int
    round_type: str
    description: str = ""
    key_topics: List[str] = []
    preparation_tips: List[str] = []
    resources: List[Resource] = []

class InterviewPrep(BaseModel):
    company_name: str
    role_title: str
    total_rounds: int
    typical_duration_weeks: str = ""
    rounds: List[InterviewRound] = []
    general_tips: List[str] = []


# ─────────────────────────────────────────────
# Session
# ─────────────────────────────────────────────

class SessionStatus(str, Enum):
    CREATED = "created"
    JD_UPLOADED = "jd_uploaded"
    RESUME_UPLOADED = "resume_uploaded"
    ANALYZED = "analyzed"
    ASSESSING = "assessing"
    PLAN_GENERATED = "plan_generated"
    COMPLETED = "completed"

class Session(BaseModel):
    session_id: str
    created_at: datetime
    updated_at: datetime
    status: SessionStatus = SessionStatus.CREATED
    jd_data: Optional[JDData] = None
    resume_data: Optional[ResumeData] = None
    gap_analysis: Optional[GapAnalysis] = None
    learning_plan: Optional[LearningPlan] = None
    interview_prep: Optional[InterviewPrep] = None


# ─────────────────────────────────────────────
# API Request / Response Models
# ─────────────────────────────────────────────

class CreateSessionResponse(BaseModel):
    session_id: str
    status: str
    created_at: datetime

class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatMessage(BaseModel):
    role: Literal["human", "ai", "system"]
    content: str
    timestamp: Optional[datetime] = None

class ChatHistoryResponse(BaseModel):
    session_id: str
    messages: List[ChatMessage]

class GenerateRequest(BaseModel):
    session_id: str

class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "OK"

class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
