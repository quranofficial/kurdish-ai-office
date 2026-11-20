from datetime import datetime

import pytest

from app.services import tasks as task_service


class FakeResult:
    def __init__(self, data):
        self.data = data


class FakeQuery:
    def __init__(self, data=None):
        self.data = data or []
        self.filters = []
        self.updated = None
        self.limit_value = None

    def select(self, *_args):
        return self

    def update(self, values):
        self.updated = values
        return self

    def eq(self, key, value):
        self.filters.append((key, value))
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def execute(self):
        return FakeResult(self.data)


class FakeDB:
    def __init__(self, query):
        self.query = query

    def table(self, _name):
        return self.query


def test_list_tasks_filters_status_and_caps_requested_limit(monkeypatch):
    query = FakeQuery([{"id": "task-1", "status": "waiting_approval"}])
    monkeypatch.setattr(task_service, "get_supabase", lambda: FakeDB(query))

    result = task_service.list_tasks(status_filter="waiting_approval", limit=10)

    assert result[0]["status"] == "waiting_approval"
    assert ("status", "waiting_approval") in query.filters
    assert query.limit_value == 10


def test_list_tasks_rejects_unknown_status_before_database_call(monkeypatch):
    monkeypatch.setattr(
        task_service,
        "get_supabase",
        lambda: (_ for _ in ()).throw(AssertionError("database should not be called")),
    )
    with pytest.raises(ValueError, match="Unsupported task status"):
        task_service.list_tasks(status_filter="made_up")


def test_approve_task_only_transitions_waiting_approval_task(monkeypatch):
    query = FakeQuery([{
        "id": "task-123",
        "title": "Publish campaign",
        "status": "queued",
        "approved_at": "2026-11-20T12:00:00+00:00",
    }])
    monkeypatch.setattr(task_service, "get_supabase", lambda: FakeDB(query))

    result = task_service.approve_task("task-123")

    assert result["status"] == "queued"
    assert result["execution"] == "queued_not_started"
    assert query.updated["status"] == "queued"
    assert datetime.fromisoformat(query.updated["approved_at"]).tzinfo is not None
    assert ("id", "task-123") in query.filters
    assert ("status", "waiting_approval") in query.filters
    assert ("requires_approval", True) in query.filters


def test_approve_task_rejects_task_not_waiting_for_approval(monkeypatch):
    query = FakeQuery([])
    monkeypatch.setattr(task_service, "get_supabase", lambda: FakeDB(query))

    with pytest.raises(ValueError, match="not waiting for approval"):
        task_service.approve_task("task-404")
