"""Register the Telegram webhook for the deployed Kurdish AI Office API."""

import asyncio
import os

from telegram import Bot

from app.config import get_settings


async def main() -> None:
    settings = get_settings()
    base_url = os.getenv("PUBLIC_APP_URL", "").strip().rstrip("/")
    if not settings.telegram_bot_token or not settings.telegram_webhook_secret:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN and TELEGRAM_WEBHOOK_SECRET first.")
    if not base_url.startswith("https://"):
        raise SystemExit("Set PUBLIC_APP_URL to the deployed HTTPS Vercel URL.")
    async with Bot(token=settings.telegram_bot_token) as bot:
        result = await bot.set_webhook(
            url=f"{base_url}/api/v1/telegram/webhook",
            secret_token=settings.telegram_webhook_secret,
            allowed_updates=["message"],
            drop_pending_updates=False,
        )
    print("Telegram webhook registered." if result else "Telegram did not confirm webhook registration.")


if __name__ == "__main__":
    asyncio.run(main())
