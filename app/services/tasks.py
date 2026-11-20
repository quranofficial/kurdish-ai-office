from datetime import datetime, timezone

from app.agents.router import route_task, requires_human_approval
from app.schemas.tasks import TaskCreate
from app.services.database import get_supabase


def create_task(payload: TaskCreate) -> dict:
    match = route_task(payload.title, payload.description)
    approval = requires_human_approval(payload.title, payload.description)
    db = get_supabase()
    agent_result = db.table("office_agents").select("id").eq("agent_key", match.agent.key).limit(1).execute()
    if not agent_result.data:
        raise RuntimeError("Agent registry is missing. Apply the latest Supabase SQL setup first.")
    row = {
        "title": payload.title,
        "description": payload.description,
        "priority": payload.priority,
        "assigned_agent_id": agent_result.data[0]["id"],
        "status": "waiting_approval" if approval else "queued",
        "requires_approval": approval,
    }
    result = db.table("office_tasks").insert(row).execute()
    if not result.data:
        raise RuntimeError("Task was not saved by the database.")
    saved = result.data[0]
    return {
        "id": saved["id"],
        "title": saved["title"],
        "status": saved["status"],
        "priority": saved["priority"],
        "agent_key": match.agent.key,
        "agent_name": match.agent.name,
        "routing_reason": match.reason,
        "requires_approval": approval,
        "execution": "queued",
    }


def list_tasks(status_filter: str | None = None, limit: int = 30) -> list[dict]:
    allowed_statuses = {
        "queued", "assigned", "in_progress", "waiting_approval",
        "completed", "failed", "cancelled",
    }
    if status_filter is not None and status_filter not in allowed_statuses:
        raise ValueError("Unsupported task status.")
    db = get_supabase()
    query = db.table("office_tasks").select(
        "id,title,description,status,priority,assigned_agent_id,requires_approval,approved_at,created_at,updated_at"
    )
    if status_filter:
        query = query.eq("status", status_filter)
    result = query.order("created_at", desc=True).limit(limit).execute()
    return result.data or []


def approve_task(task_id: str) -> dict:
    db = get_supabase()
    result = (
        db.table("office_tasks")
        .update({
            "status": "queued",
            "approved_at": datetime.now(timezone.utc).isoformat(),
        })
        .eq("id", task_id)
        .eq("status", "waiting_approval")
        .eq("requires_approval", True)
        .execute()
    )
    if not result.data:
        raise ValueError("Task not found or it is not waiting for approval.")
    saved = result.data[0]
    return {
        "id": saved["id"],
        "title": saved["title"],
        "status": saved["status"],
        "approved_at": saved["approved_at"],
        "execution": "queued_not_started",
    }
