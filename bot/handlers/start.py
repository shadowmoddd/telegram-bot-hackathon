from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repository import UserRepository
from bot.keyboards.inline import roadmap_start_keyboard
from bot.utils import escape

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.clear()
    user_repo = UserRepository(session)
    await user_repo.get_or_create(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )
    logger.info(f"User started bot: telegram_id={message.from_user.id}")

    await message.answer(
        f"Привет, <b>{escape(message.from_user.first_name)}</b> 👋\n\n"
        "Хочешь освоить новую профессию или прокачать навыки, но не знаешь с чего начать?\n\n"
        "<b>Progressors Learning</b> составит персональный маршрут под твой уровень и цель — "
        "только бесплатные материалы на русском языке, только то что реально нужно.\n\n"
        "Открывай приложение 👇",
        reply_markup=roadmap_start_keyboard(),
    )


@router.message(F.text == "🔃 Перезапустить бота")
async def cmd_restart(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await cmd_start(message, state, session)
