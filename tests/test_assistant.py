import pytest

from app.agents.catalog import get_agent
from app.schemas.assistant import AssistantRequest
from app.services.assistant import build_agent_instructions, resolve_agent


def test_assistant_routes_sorani_translation_request():
    agent = resolve_agent(AssistantRequest(message="تکایە ئەم دەقە وەرگێڕە"))
    assert agent.key == "translator"


def test_assistant_can_select_known_agent():
    agent = resolve_agent(AssistantRequest(message="Hello", agent_key="research"))
    assert agent.key == "research"


def test_assistant_rejects_unknown_agent():
    with pytest.raises(ValueError, match="Unknown agent_key"):
        resolve_agent(AssistantRequest(message="Hello", agent_key="not_real"))


def test_agent_instructions_prohibit_external_actions():
    instructions = build_agent_instructions(get_agent("marketing"))
    assert "no tools" in instructions
    assert "human approval" in instructions
