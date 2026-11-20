import asyncio
import hmac
from uuid import UUID

from openai import APIConnectionError, APIStatusError, APITimeoutError

from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request, status
from telegram import Bot

from app.agents.catalog import list_agents
from app.config import get_settings
from app.schemas.assistant import AssistantRequest
from app.schemas.tasks import TaskCreate
from app.services.assistant import generate_assistant_reply
from app.services.tasks import approve_task, create_task, list_tasks

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


def telegram_command_response(message: str, public_app_url: str) -> str | None:
    command = message.split(maxsplit=1)[0].split("@", maxsplit=1)[0].lower()
    if command == "/start":
        return (
            "بەخێربێیت بۆ Kurdish AI Office – Professional Edition!\n\n"
            "من یاریدەدەری ئۆفیسی زیرەکم. دەتوانیت بە کوردی داواکارییەکانت بنووسیت.\n"
            "بۆ بینینی فەرمانەکان /help بنووسە."
        )
    if command in {"/help", "/office"}:
        dashboard = f"\nداشبۆرد: {public_app_url}" if public_app_url.startswith("https://") else ""
        return (
            "فەرمانە بەردەستەکان:\n"
            "/start - دەستپێکردن\n"
            "/help - ڕێنمایی\n"
            "/agents - بینینی ١٦ ئەجێنت\n"
            "/office - زانیاری ئۆفیس و داشبۆرد\n"
            "/projects - دۆخی پرۆژەکان\n"
            "/report - ڕاپۆرتی ئۆفیس\n"
            "/tasks - لیستی ئەرکەکان\n"
            "/approve ID - پەسەندکردنی ئەرک"
            f"{dashboard}\n\n"
            "هەروەها دەتوانیت ڕاستەوخۆ پرسیارەکەت بە کوردی بنووسیت."
        )
    if command == "/agents":
        agents = list_agents()
        return "ئەجێنتەکانی ئۆفیس:\n" + "\n".join(
            f"{index}. {agent['name']} — {agent['department']}"
            for index, agent in enumerate(agents, start=1)
        )
    if command == "/projects":
        return (
            "بەشی پرۆژەکان لە داشبۆرددا دیزاین کراوە، بەڵام پەیوەندی داتابەیس و بەڕێوەبردنی پرۆژەکان هێشتا چالاک نەکراون. "
            "دوای ڕێکخستنی Supabase، دەتوانین لیست و دۆخی پرۆژەکان لێرە پیشان بدەین."
        )
    if command == "/report":
        return (
            "ڕاپۆرتی ئۆفیس:\n"
            "• ١٦ ئەجێنت لە کاتەلۆگی سیستەمدا ئامادەن.\n"
            "• وەڵامدانی AI لە بنەڕەتدا ئامادەیە.\n"
            "• تۆمارکردنی ئەرک و ڕاپۆرتی داتابەیس هێشتا چالاک نەکراون.\n"
            "• هیچ کردارێکی دەرەکی یان ئۆتۆماتیکی بەبێ پەسەندی مرۆڤ ئەنجام نادرێت."
        )
    if command == "/task":
        return (
            "بەشی تۆمارکردنی ئەرک هێشتا پێویستی بە ڕێکخستنی داتابەیس هەیە. "
            "ئێستا دەتوانیت داواکارییەکەت وەک نامەی ئاسایی بنووسیت تا AI یارمەتیت بدات."
        )
    if command == "/stop":
        return "هیچ ئەرکێکی خۆکاری چالاک نییە بۆ وەستاندن."
    return None


@router.get("/agents", tags=["agents"])
async def agents():
    return {"count": len(list_agents()), "agents": list_agents()}


@router.post("/assistant/respond", tags=["assistant"], dependencies=[Depends(require_office_key)])
async def assistant_respond(payload: AssistantRequest):
    try:
        reply = await asyncio.to_thread(generate_assistant_reply, payload)
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
    except APIStatusError as exc:
        error_code = getattr(exc, "code", None) or getattr(exc, "type", None) or "api_error"
        raise HTTPException(
            status_code=502,
            detail=f"OpenAI API returned HTTP {exc.status_code} ({error_code}). Check OPENAI_MODEL, API key permissions, and API billing.",
        ) from exc
    except (APIConnectionError, APITimeoutError) as exc:
        raise HTTPException(
            status_code=503,
            detail="Could not connect to the OpenAI API. Check network access and try again.",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Unexpected AI service error ({type(exc).__name__}). Check Vercel function logs.",
        ) from exc


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


@router.get("/tasks", tags=["tasks"], dependencies=[Depends(require_office_key)])
async def get_tasks(
    task_status: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=30, ge=1, le=100),
):
    try:
        return {"tasks": list_tasks(status_filter=task_status, limit=limit)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Task listing failed. Check the database connection and schema.") from exc


@router.post("/tasks/{task_id}/approve", tags=["tasks"], dependencies=[Depends(require_office_key)])
async def approve_task_endpoint(task_id: UUID):
    try:
        return approve_task(str(task_id))
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Task approval failed. Check the database connection and schema.") from exc


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

    try:
        update = await request.json()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid Telegram update JSON.") from exc
    if not isinstance(update, dict):
        raise HTTPException(status_code=400, detail="Telegram update must be a JSON object.")

    message = update.get("message") or update.get("edited_message") or {}
    if not isinstance(message, dict):
        return {"ok": True, "ignored": True}
    text = (message.get("text") or "").strip()
    chat = message.get("chat") or {}
    if not isinstance(chat, dict):
        return {"ok": True, "ignored": True}
    chat_id = chat.get("id")
    if not text or chat_id is None:
        return {"ok": True, "ignored": True}

    try:
        command = text.split(maxsplit=1)[0].split("@", maxsplit=1)[0].lower()
        sender_id = (message.get("from") or {}).get("id")
        if command in {"/tasks", "/approve"}:
            if sender_id not in settings.office_admin_telegram_id_list:
                outgoing = "ئەم فەرمانە تەنها بۆ بەڕێوەبەرانی ڕێگەپێدراوە."
                agent_key = "authorization"
            elif command == "/tasks":
                pending = list_tasks(status_filter="waiting_approval", limit=10)
                if not pending:
                    outgoing = "هیچ ئەرکێک چاوەڕێی پەسەندکردن ناکات."
                else:
                    outgoing = "ئەرکە چاوەڕوانەکان بۆ پەسەندکردن:\n" + "\n".join(
                        f"• {item['title']}\nID: {item['id']}"
                        for item in pending
                    )
                agent_key = "tasks"
            else:
                parts = text.split(maxsplit=1)
                if len(parts) != 2:
                    outgoing = "بۆ پەسەندکردن: /approve TASK_ID"
                    agent_key = "tasks"
                else:
                    try:
                        approved = approve_task(str(UUID(parts[1].strip())))
                        outgoing = f"ئەرک پەسەند کرا و خرایە ناو ڕیزەی جێبەجێکردن.\n{approved['title']}\nID: {approved['id']}"
                    except (ValueError, TypeError):
                        outgoing = "ناسنامەی ئەرک دروست نییە یان ئەرکەکە چاوەڕێی پەسەندکردن نییە."
                    agent_key = "tasks"
        else:
            command_reply = telegram_command_response(text, settings.public_app_url)
            if command_reply is not None:
                outgoing = command_reply
                agent_key = "command"
            else:
                reply = await asyncio.to_thread(generate_assistant_reply, AssistantRequest(message=text))
                outgoing = f"{reply.agent_name}\n\n{reply.content}"
                agent_key = reply.agent_key

        async with Bot(token=settings.telegram_bot_token) as bot:
            for chunk in split_telegram_message(outgoing):
                await bot.send_message(chat_id=chat_id, text=chunk)
        return {"ok": True, "agent_key": agent_key}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Telegram assistant reply failed. Check server logs.") from exc
