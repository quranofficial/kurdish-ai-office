from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routes import router as api_router
from app.config import get_settings

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.4.0",
    description="Shared backend for the Kurdish AI Office dashboard and Telegram bot.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
app.include_router(api_router)


@app.get("/", tags=["system"], response_class=FileResponse)
async def root():
    dashboard = Path(__file__).parent / "static" / "index.html"
    return FileResponse(dashboard, media_type="text/html")


@app.get("/health", tags=["system"])
async def health():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "database_configured": bool(settings.supabase_url and settings.supabase_service_role_key),
        "ai_configured": bool(settings.openai_api_key),
        "ai_model": settings.openai_model if settings.openai_api_key else None,
        "telegram_configured": bool(settings.telegram_bot_token),
        "task_api_unlocked": bool(settings.office_api_key),
    }
