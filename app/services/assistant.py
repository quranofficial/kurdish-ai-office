from dataclasses import dataclass

from google import genai
from google.genai import types

from app.agents.catalog import Agent, get_agent
from app.agents.router import route_task
from app.config import get_settings
from app.schemas.assistant import AssistantRequest


@dataclass(frozen=True)
class AssistantReply:
    agent_key: str
    agent_name: str
    content: str
    model: str


def build_agent_instructions(agent: Agent) -> str:
    capabilities = ", ".join(agent.capabilities)
    return (
        f"You are {agent.name}, part of Kurdish AI Office. "
        f"Department: {agent.department}. Role: {agent.description} "
        f"Your capabilities are limited to: {capabilities}. "
        "Respond in the same language as the user unless they request another language. "
        "For Sorani Kurdish, use clear and natural Sorani script. "
        "Be accurate, distinguish facts from assumptions, and state uncertainty. "
        "Do not claim to have browsed, sent messages, published content, changed files, "
        "made purchases, or performed any external action. You have no tools and cannot "
        "perform external side effects. You may prepare drafts and recommendations only. "
        "If a request involves payment, publishing, messaging, deletion, or another "
        "high-impact action, explain that human approval and a separately authorized "
        "integration are required before execution."
    )


def resolve_agent(request: AssistantRequest) -> Agent:
    if request.agent_key:
        agent = get_agent(request.agent_key)
        if agent is None:
            raise ValueError("Unknown agent_key.")
        return agent
    return route_task(request.message).agent


def generate_assistant_reply(request: AssistantRequest) -> AssistantReply:
    settings = get_settings()
    if not settings.gemini_api_key:
        raise RuntimeError("Gemini is not configured. Set GEMINI_API_KEY on the server.")
    agent = resolve_agent(request)
    with genai.Client(api_key=settings.gemini_api_key) as client:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=request.message,
            config=types.GenerateContentConfig(
                system_instruction=build_agent_instructions(agent),
                max_output_tokens=1600,
            ),
        )
    content = (response.text or "").strip()
    if not content:
        raise RuntimeError("Gemini returned an empty response.")
    return AssistantReply(
        agent_key=agent.key,
        agent_name=agent.name,
        content=content,
        model=settings.gemini_model,
    )
