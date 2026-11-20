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
