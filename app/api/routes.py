import hmac
from fastapi import APIRouter, Depends, Header, HTTPException, status
from app.agents.catalog import list_agents
from app.config import get_settings
from app.schemas.tasks import TaskCreate
from app.services.tasks import create_task

router = APIRouter(prefix="/api/v1")

def require_office_key(authorization: str | None = Header(default=None)) -> None:
    configured = get_settings().office_api_key
    if not configured:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Task API is locked until OFFICE_API_KEY is configured.")
    supplied = authorization.removeprefix("Bearer ").strip() if authorization else ""
    if not hmac.compare_digest(supplied, configured):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid office API key.")

@router.get("/agents", tags=["agents"])
async def agents():
    return {"count": len(list_agents()), "agents": list_agents()}

@router.post("/tasks", tags=["tasks"], dependencies=[Depends(require_office_key)])
async def submit_task(payload: TaskCreate):
    try:
        return create_task(payload)
    except RuntimeError as exc:
        message = str(exc)
        if "Supabase is not configured" in message:
            raise HTTPException(status_code=503, detail=message) from exc
        raise HTTPException(status_code=500, detail=message) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Task persistence failed. Check the database connection and schema.") from exc
