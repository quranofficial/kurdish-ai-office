from app.agents.catalog import AGENTS
from app.agents.router import route_task, requires_human_approval

def test_all_sixteen_agents_are_registered():
    assert len(AGENTS) == 16
    assert len({agent.key for agent in AGENTS}) == 16

def test_developer_task_routes_to_developer():
    assert route_task("Fix Python API bug").agent.key == "developer"

def test_translation_task_routes_to_translator():
    assert route_task("Translate this paragraph into Kurdish").agent.key == "translator"

def test_unknown_task_routes_to_manager():
    assert route_task("Do something unusual").agent.key == "manager"

def test_sensitive_action_requires_approval():
    assert requires_human_approval("Publish the announcement") is True
    assert requires_human_approval("Research competitor pricing") is False
