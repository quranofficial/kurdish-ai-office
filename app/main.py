from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings

settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Shared backend for the AI Office web dashboard and Telegram bot.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.get("/", tags=["system"])
async def root():
    return {"name": settings.app_name, "status": "running", "version": "0.1.0"}

@app.get("/health", tags=["system"])
async def health():
    return {
        "status": "healthy",
        "environment": settings.environment,
        "database_configured": bool(settings.supabase_url and settings.supabase_service_role_key),
        "ai_configured": bool(settings.openai_api_key),
        "telegram_configured": bool(settings.telegram_bot_token),
    }
