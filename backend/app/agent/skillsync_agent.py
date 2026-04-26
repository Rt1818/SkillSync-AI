from langchain_openai import ChatOpenAI
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_mongodb import MongoDBChatMessageHistory

from ..config import settings
from ..models.schemas import GapAnalysis, JDData, ResumeData
from ..models.prompts import ASSESSMENT_SYSTEM_PROMPT
from .tools import get_search_tool, scrape_url


def get_session_history(session_id: str) -> MongoDBChatMessageHistory:
    """Factory: returns MongoDB-backed chat history for a given session."""
    return MongoDBChatMessageHistory(
        connection_string=settings.MONGODB_URI,
        session_id=session_id,
        database_name=settings.MONGODB_DB_NAME,
        collection_name="message_store",
    )


def build_agent_executor(
    jd_data: JDData,
    resume_data: ResumeData,
    gap_analysis: GapAnalysis,
) -> AgentExecutor:
    """
    Build an AgentExecutor for the conversational assessment phase.
    The agent has access to web_search and scrape_url tools.
    """
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        api_key=settings.OPENAI_API_KEY,
        temperature=0.7,  # slightly creative for conversation
        streaming=True,
    )

    tools = [get_search_tool(), scrape_url]

    # Build gap summary for system prompt
    critical_gaps = gap_analysis.critical_gaps or ["No critical gaps identified"]
    first_gap = critical_gaps[0] if critical_gaps else "general skills"

    gap_summary_lines = []
    for sa in gap_analysis.skill_assessments:
        gap_summary_lines.append(
            f"  • {sa.skill_name}: {sa.gap_category} (score={sa.score}/100) — {sa.notes}"
        )
    gap_analysis_summary = "\n".join(gap_summary_lines) if gap_summary_lines else "No assessments yet."

    system_prompt = ASSESSMENT_SYSTEM_PROMPT.format(
        candidate_name=resume_data.candidate_name,
        role_title=jd_data.role_title,
        company_name=jd_data.company_name,
        gap_analysis_summary=gap_analysis_summary,
        first_gap=first_gap,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_functions_agent(llm=llm, tools=tools, prompt=prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=False,
        handle_parsing_errors=True,
    )
    return executor


def build_agent_with_history(
    jd_data: JDData,
    resume_data: ResumeData,
    gap_analysis: GapAnalysis,
) -> RunnableWithMessageHistory:
    """Wrap the agent executor with MongoDB-backed message history."""
    executor = build_agent_executor(jd_data, resume_data, gap_analysis)

    agent_with_history = RunnableWithMessageHistory(
        executor,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
    )
    return agent_with_history


async def chat_with_agent(
    session_id: str,
    message: str,
    jd_data: JDData,
    resume_data: ResumeData,
    gap_analysis: GapAnalysis,
) -> str:
    """Send a message to the agent and return its response."""
    agent_with_history = build_agent_with_history(jd_data, resume_data, gap_analysis)

    response = await agent_with_history.ainvoke(
        {"input": message},
        config={"configurable": {"session_id": session_id}},
    )
    return response.get("output", "")


async def stream_chat_with_agent(
    session_id: str,
    message: str,
    jd_data: JDData,
    resume_data: ResumeData,
    gap_analysis: GapAnalysis,
):
    """
    Stream the agent's response token by token.
    Yields SSE-formatted strings: 'data: {"content": "..."}\n\n'
    """
    import json

    agent_with_history = build_agent_with_history(jd_data, resume_data, gap_analysis)

    async for event in agent_with_history.astream_events(
        {"input": message},
        config={"configurable": {"session_id": session_id}},
        version="v2",
    ):
        event_name = event.get("event", "")
        if event_name == "on_chat_model_stream":
            chunk = event["data"].get("chunk")
            if chunk and hasattr(chunk, "content") and chunk.content:
                yield f"data: {json.dumps({'content': chunk.content})}\n\n"

    yield "data: [DONE]\n\n"
