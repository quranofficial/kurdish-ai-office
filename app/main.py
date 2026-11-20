from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.config import get_settings

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
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

@app.get("/", tags=["system"])
async def root():
    return {"name": settings.app_name, "status": "running", "version": "0.2.0"}

@app.get("/health", tags=["system"])
async def health():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "database_configured": bool(settings.supabase_url and settings.supabase_service_role_key),
        "ai_configured": bool(settings.openai_api_key),
        "telegram_configured": bool(settings.telegram_bot_token),
        "task_api_unlocked": bool(settings.office_api_key),
    }
