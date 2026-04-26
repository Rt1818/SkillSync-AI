from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from ..config import settings
from ..models.schemas import JDData
from ..models.prompts import JD_PARSER_PROMPT


def get_llm() -> ChatOpenAI:
    return ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0,
    )


async def parse_jd(jd_text: str) -> JDData:
    """Parse raw JD text into structured JDData using structured output."""
    llm = get_llm()
    structured_llm = llm.with_structured_output(JDData)

    prompt = JD_PARSER_PROMPT.format(jd_text=jd_text)
    result: JDData = await structured_llm.ainvoke([HumanMessage(content=prompt)])
    return result
