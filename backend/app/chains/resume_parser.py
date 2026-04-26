from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from ..config import settings
from ..models.schemas import ResumeData
from ..models.prompts import RESUME_PARSER_PROMPT


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )


async def parse_resume(resume_text: str) -> ResumeData:
    """Parse raw resume text into structured ResumeData using structured output."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(ResumeData)

    prompt = RESUME_PARSER_PROMPT.format(resume_text=resume_text)
    result: ResumeData = await structured_llm.ainvoke([HumanMessage(content=prompt)])
    return result
