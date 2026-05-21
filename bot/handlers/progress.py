from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repository import RoadmapRepository, UserRepository
from bot.services.roadmap_service import format_progress_card
from bot.utils import safe_callback_int

router = Router()


@router.callback_query(F.data.startswith("progress_"))
async def handle_progress_callback(callback: CallbackQuery, session: AsyncSession) -> None:
    await callback.answer()
    roadmap_id = await safe_callback_int(callback, "progress_")
    if roadmap_id is None:
        return
    roadmap_repo = RoadmapRepository(session)
    roadmap = await roadmap_repo.get_with_steps(roadmap_id)
    if not roadmap:
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    card = format_progress_card(roadmap, roadmap.steps, user=user)
    await callback.message.answer(card)
