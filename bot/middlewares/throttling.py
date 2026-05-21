from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from cachetools import TTLCache
from loguru import logger

RATE_LIMIT = 1.0
HEAVY_CALLBACKS = {
    "profile_confirm", "roadmap_start", "roadmap_regenerate",
    "roadmap_continue", "adj_harder", "adj_easier",
    "adj_more_video", "adj_more_articles", "adj_change_goal",
}
HEAVY_RATE_LIMIT = 10.0


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self):
        self.msg_cache: TTLCache = TTLCache(maxsize=10_000, ttl=RATE_LIMIT)
        self.heavy_cache: TTLCache = TTLCache(maxsize=10_000, ttl=HEAVY_RATE_LIMIT)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Update):
            return await handler(event, data)

        user_id: int | None = None

        if event.message and event.message.from_user:
            user_id = event.message.from_user.id
            if user_id in self.msg_cache:
                logger.debug(f"Message throttled for user {user_id}")
                return
            self.msg_cache[user_id] = True

        elif event.callback_query and event.callback_query.from_user:
            user_id = event.callback_query.from_user.id
            cb_data = event.callback_query.data or ""

            if cb_data in HEAVY_CALLBACKS or any(cb_data.startswith(p) for p in ("adj_", "fb_hard_", "fb_easy_", "fb_format_")):
                if user_id in self.heavy_cache:
                    logger.debug(f"Heavy callback throttled for user {user_id}: {cb_data}")
                    await event.callback_query.answer("⏳ Подожди немного...", show_alert=False)
                    return
                self.heavy_cache[user_id] = True

        return await handler(event, data)
