import asyncio
import os
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.strategy import FSMStrategy
from aiogram.types import TelegramObject, Update
from loguru import logger

from bot.config import settings
from bot.db.database import async_session_factory, init_db
from bot.db.repository import UserRepository
from bot.handlers import start, profile, roadmap, feedback, progress
from bot.middlewares.throttling import ThrottlingMiddleware


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with async_session_factory() as session:
            data["session"] = session
            result = await handler(event, data)

        user_id = _extract_user_id(event)
        if user_id:
            task = asyncio.create_task(_update_last_active(user_id))
            task.add_done_callback(
                lambda t: logger.debug(f"last_active task error: {t.exception()}")
                if not t.cancelled() and t.exception() else None
            )

        return result


def _extract_user_id(event: TelegramObject) -> int | None:
    if isinstance(event, Update):
        if event.message and event.message.from_user:
            return event.message.from_user.id
        if event.callback_query and event.callback_query.from_user:
            return event.callback_query.from_user.id
    return None


async def _update_last_active(telegram_id: int) -> None:
    try:
        async with async_session_factory() as session:
            repo = UserRepository(session)
            await repo.update_last_active(telegram_id)
    except Exception as e:
        logger.debug(f"last_active_at update failed for {telegram_id}: {e}")


async def main() -> None:
    os.makedirs("data", exist_ok=True)

    await init_db()
    logger.info("Database initialized")

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    storage = MemoryStorage()
    dp = Dispatcher(storage=storage, fsm_strategy=FSMStrategy.GLOBAL_USER)

    dp.update.outer_middleware(ThrottlingMiddleware())
    dp.update.middleware(DatabaseMiddleware())

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(roadmap.router)
    dp.include_router(feedback.router)
    dp.include_router(progress.router)

    logger.info("Bot starting...")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
