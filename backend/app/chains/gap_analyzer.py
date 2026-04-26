import json
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from tavily import TavilyClient
from ..config import settings
from ..models.schemas import GapAnalysis, JDData, ResumeData, LearningPlan, InterviewPrep
from ..models.prompts import GAP_ANALYZER_PROMPT, LEARNING_PLAN_PROMPT, INTERVIEW_PREP_PROMPT


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )


def get_tavily() -> TavilyClient:
    return TavilyClient(api_key=settings.TAVILY_API_KEY)


async def analyze_gaps(jd_data: JDData, resume_data: ResumeData) -> GapAnalysis:
    """Compare JD requirements vs resume skills → produce scored gap analysis."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(GapAnalysis)

    prompt = GAP_ANALYZER_PROMPT.format(
        jd_data=jd_data.model_dump_json(indent=2),
        resume_data=resume_data.model_dump_json(indent=2),
    )
    result: GapAnalysis = await structured_llm.ainvoke([HumanMessage(content=prompt)])
    return result


async def generate_learning_plan(
    gap_analysis: GapAnalysis,
    jd_data: JDData,
    resume_data: ResumeData,
) -> LearningPlan:
    """
    1. Tavily-search resources for each gap skill
    2. Pass real URLs to LLM → structured LearningPlan
    """
    tavily = get_tavily()

    # Build targeted search queries for each missing/weak skill
    gap_skills = [
        a.skill_name
        for a in gap_analysis.skill_assessments
        if a.gap_category in ("MISSING", "WEAK", "MODERATE")
    ][:6]  # cap at 6 skills to stay within API limits

    search_results: dict = {}
    for skill in gap_skills:
        queries = [
            f"best YouTube tutorial {skill} complete course 2024",
            f"best way to learn {skill} documentation beginner guide",
        ]
        skill_results = []
        for q in queries:
            try:
                res = tavily.search(q, max_results=3)
                skill_results.extend(res.get("results", []))
            except Exception:
                pass
        search_results[skill] = skill_results

    llm = get_llm()
    structured_llm = llm.with_structured_output(LearningPlan)

    prompt = LEARNING_PLAN_PROMPT.format(
        candidate_name=resume_data.candidate_name,
        role_title=jd_data.role_title,
        company_name=jd_data.company_name,
        gap_analysis=gap_analysis.model_dump_json(indent=2),
        search_results=json.dumps(search_results, indent=2),
    )
    result: LearningPlan = await structured_llm.ainvoke([HumanMessage(content=prompt)])
    return result


async def generate_interview_prep(
    jd_data: JDData,
    resume_data: ResumeData,
    gap_analysis: GapAnalysis,
) -> InterviewPrep:
    """
    1. Tavily-search company interview process
    2. Pass real data to LLM → structured InterviewPrep
    """
    tavily = get_tavily()
    company = jd_data.company_name
    role = jd_data.role_title

    search_queries = [
        f"{company} {role} interview process rounds 2024",
        f"{company} software engineer interview questions glassdoor",
        f"LeetCode problems asked at {company} interview",
        f"{company} {role} interview experience blog",
    ]

    search_results = []
    for q in search_queries:
        try:
            res = tavily.search(q, max_results=4)
            search_results.extend(res.get("results", []))
        except Exception:
            pass

    llm = get_llm()
    structured_llm = llm.with_structured_output(InterviewPrep)

    gap_summary = {
        "overall_score": gap_analysis.overall_match_score,
        "critical_gaps": gap_analysis.critical_gaps,
        "strengths": gap_analysis.strengths,
    }

    prompt = INTERVIEW_PREP_PROMPT.format(
        candidate_name=resume_data.candidate_name,
        role_title=role,
        company_name=company,
        resume_summary=resume_data.summary,
        gap_summary=json.dumps(gap_summary, indent=2),
        search_results=json.dumps(search_results, indent=2),
    )
    result: InterviewPrep = await structured_llm.ainvoke([HumanMessage(content=prompt)])
    return result
