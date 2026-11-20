import asyncio
import hmac

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from telegram import Bot

from app.agents.catalog import list_agents
from app.config import get_settings
from app.schemas.assistant import AssistantRequest
from app.schemas.tasks import TaskCreate
from app.services.assistant import generate_assistant_reply
from app.services.tasks import create_task

router = APIRouter(prefix="/api/v1")


def require_office_key(authorization: str | None = Header(default=None)) -> None:
    configured = get_settings().office_api_key
    if not configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Office API is locked until OFFICE_API_KEY is configured.",
        )
    supplied = authorization.removeprefix("Bearer ").strip() if authorization else ""
    if not hmac.compare_digest(supplied, configured):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid office API key.")


def split_telegram_message(text: str, limit: int = 4000) -> list[str]:
    remaining = text.strip()
    chunks: list[str] = []
    while remaining:
        if len(remaining) <= limit:
            chunks.append(remaining)
            break
        cut = remaining.rfind("\n", 0, limit)
        if cut < limit // 2:
            cut = remaining.rfind(" ", 0, limit)
        if cut < limit // 2:
            cut = limit
        chunks.append(remaining[:cut].strip())
        remaining = remaining[cut:].strip()
    return chunks or [""]


@router.get("/agents", tags=["agents"])
async def agents():
    return {"count": len(list_agents()), "agents": list_agents()}


@router.post("/assistant/respond", tags=["assistant"], dependencies=[Depends(require_office_key)])
async def assistant_respond(payload: AssistantRequest):
    try:
        reply = generate_assistant_reply(payload)
        return {
            "agent_key": reply.agent_key,
            "agent_name": reply.agent_name,
            "model": reply.model,
            "content": reply.content,
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="AI provider request failed. Check server logs.") from exc


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


@router.post("/telegram/register", tags=["telegram"], dependencies=[Depends(require_office_key)])
async def register_telegram_webhook():
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_webhook_secret:
        raise HTTPException(status_code=503, detail="Set TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_SECRET first.")
    if not settings.public_app_url.startswith("https://"):
        raise HTTPException(status_code=503, detail="Set PUBLIC_APP_URL to the deployed HTTPS URL first.")
    try:
        async with Bot(token=settings.telegram_bot_token) as bot:
            ok = await bot.set_webhook(
                url=f"{settings.public_app_url.rstrip('/')}/api/v1/telegram/webhook",
                secret_token=settings.telegram_webhook_secret,
                allowed_updates=["message"],
                drop_pending_updates=False,
            )
        return {"ok": bool(ok), "webhook_url": f"{settings.public_app_url.rstrip('/')}/api/v1/telegram/webhook"}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Telegram webhook registration failed. Check server logs.") from exc


@router.post("/telegram/webhook", tags=["telegram"])
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(default=None),
):
    settings = get_settings()
    if not settings.telegram_bot_token or not settings.telegram_webhook_secret:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Telegram webhook is not configured.",
        )
    if not hmac.compare_digest(x_telegram_bot_api_secret_token or "", settings.telegram_webhook_secret):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Telegram webhook secret.")

    update = await request.json()
    message = update.get("message") or update.get("edited_message") or {}
    text = (message.get("text") or "").strip()
    chat = message.get("chat") or {}
    chat_id = chat.get("id")
    if not text or chat_id is None:
        return {"ok": True, "ignored": True}

    try:
        reply = await asyncio.to_thread(generate_assistant_reply, AssistantRequest(message=text))
        outgoing = f"{reply.agent_name}\n\n{reply.content}"
        async with Bot(token=settings.telegram_bot_token) as bot:
            for chunk in split_telegram_message(outgoing):
                await bot.send_message(chat_id=chat_id, text=chunk)
        return {"ok": True, "agent_key": reply.agent_key}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Telegram assistant reply failed. Check server logs.") from exc
