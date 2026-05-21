import asyncio

from aiogram import F, Router
from aiogram.exceptions import TelegramNetworkError
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.utils import safe_callback_int

from bot.db.repository import ProfileRepository, RoadmapRepository, StepRepository, UserRepository
from bot.keyboards.inline import (
    adjustment_keyboard,
    progress_keyboard,
    roadmap_start_keyboard,
    step_actions_keyboard,
)
from bot.keyboards.reply import main_menu_keyboard
from bot.services.roadmap_service import (
    create_roadmap_from_profile,
    format_material_card,
    format_progress_card,
    format_roadmap_overview,
    format_step_card,
)

router = Router()


async def generate_and_show_roadmap(message: Message, session: AsyncSession, user_id: int) -> None:
    profile_repo = ProfileRepository(session)
    profile = await profile_repo.get_by_user_id(user_id)
    if not profile:
        await message.answer("Профиль не найден. Используй /start для начала.")
        return

    try:
        roadmap, steps = await create_roadmap_from_profile(session, user_id, profile)
    except Exception as e:
        logger.error(f"Error creating roadmap: {e}")
        if "429" in str(e) or "rate_limit" in str(e).lower():
            await message.answer("⏳ Сервис временно перегружен. Попробуй снова через несколько минут.")
        else:
            await message.answer("😔 Не удалось построить маршрут. Попробуй ещё раз через /newprofile")
        return

    await message.answer(format_roadmap_overview(roadmap), reply_markup=roadmap_start_keyboard())


async def _send_with_retry(coro_fn, retries: int = 3) -> None:
    for attempt in range(retries):
        try:
            await coro_fn()
            return
        except TelegramNetworkError as e:
            if attempt == retries - 1:
                raise
            logger.warning(f"Network error (attempt {attempt + 1}): {e}, retrying...")
            await asyncio.sleep(1)


async def show_step(message: Message, step, total_steps: int) -> None:
    step_text = format_step_card(step, total_steps)
    await _send_with_retry(lambda: message.answer(step_text))

    materials = step.get_materials()
    for i, material in enumerate(materials, 1):
        mat_text = format_material_card(material, i)
        await _send_with_retry(
            lambda t=mat_text: message.answer(t, disable_web_page_preview=True)
        )

    has_next = step.order_num < total_steps
    kb = step_actions_keyboard(step.id, has_next=has_next)
    await _send_with_retry(lambda: message.answer("Что дальше?", reply_markup=kb))


@router.callback_query(F.data == "roadmap_start")
async def handle_roadmap_start(callback: CallbackQuery, session: AsyncSession) -> None:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Профиль не найден.", show_alert=True)
        return

    roadmap_repo = RoadmapRepository(session)
    roadmap = await roadmap_repo.get_active(user.id)
    if not roadmap:
        await callback.answer("Маршрут не найден.", show_alert=True)
        return

    step_repo = StepRepository(session)
    current_step = await step_repo.get_current_step(roadmap.id)
    if not current_step:
        await callback.answer()
        await callback.message.answer("🎉 Все шаги завершены! Ты молодец!")
        return

    await callback.answer("▶️ Загружаю шаг...")
    await step_repo.update_status(current_step.id, "in_progress")
    await show_step(callback.message, current_step, roadmap.total_steps)


@router.callback_query(F.data == "roadmap_continue")
async def handle_roadmap_continue(callback: CallbackQuery, session: AsyncSession) -> None:
    await handle_roadmap_start(callback, session)


@router.callback_query(F.data.startswith("step_next_"))
async def handle_step_next(callback: CallbackQuery, session: AsyncSession) -> None:
    step_id = await safe_callback_int(callback, "step_next_")
    if step_id is None:
        return
    step_repo = StepRepository(session)
    step = await step_repo.get_by_id(step_id)
    if not step:
        await callback.answer("Шаг не найден.", show_alert=True)
        return

    roadmap_repo = RoadmapRepository(session)
    roadmap = await roadmap_repo.get_with_steps(step.roadmap_id)
    if not roadmap:
        await callback.answer("Маршрут не найден.", show_alert=True)
        return

    candidates = sorted(
        [s for s in roadmap.steps if s.order_num > step.order_num],
        key=lambda s: s.order_num,
    )

    if not candidates:
        user_repo = UserRepository(session)
        user = await user_repo.get_by_telegram_id(callback.from_user.id)
        await callback.answer()
        await callback.message.answer(
            "🎉 <b>Это был последний шаг!</b>\n\n" + format_progress_card(roadmap, roadmap.steps, user=user),
            reply_markup=main_menu_keyboard(),
        )
        return

    next_step = candidates[0]
    if step.status == "in_progress":
        await step_repo.update_status(step_id, "completed", {"action": "moved_on"})
    await callback.answer("📚 Следующий шаг...")
    await step_repo.update_status(next_step.id, "in_progress")
    await show_step(callback.message, next_step, roadmap.total_steps)


@router.callback_query(F.data.startswith("step_complete_"))
async def handle_step_complete(callback: CallbackQuery, session: AsyncSession) -> None:
    await callback.answer("✅ Отмечено!")

    step_id = await safe_callback_int(callback, "step_complete_")
    if step_id is None:
        return
    step_repo = StepRepository(session)
    await step_repo.update_status(step_id, "completed", {"action": "completed"})

    step = await step_repo.get_by_id(step_id)
    if not step:
        return

    roadmap_repo = RoadmapRepository(session)
    roadmap = await roadmap_repo.get_with_steps(step.roadmap_id)
    if not roadmap:
        return

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)

    next_steps = [s for s in roadmap.steps if s.order_num > step.order_num and s.status in ("pending", "in_progress")]
    progress_text = format_progress_card(roadmap, roadmap.steps, user=user)

    if not next_steps:
        all_skills = []
        for s in roadmap.steps:
            all_skills.extend(s.get_skills())
        unique_skills = list(dict.fromkeys(all_skills))[:10]
        skills_text = "\n".join(f"  • {sk}" for sk in unique_skills) if unique_skills else "  • Много полезного!"
        completion_text = (
            "🏆 <b>Маршрут завершён! Поздравляю!</b>\n\n"
            "За время обучения ты освоил:\n"
            f"{skills_text}\n\n"
            "🚀 Готов к следующей цели? Нажми /newprofile"
        )
        await callback.message.answer(
            completion_text + "\n\n" + progress_text,
            reply_markup=main_menu_keyboard(),
        )
    else:
        await callback.message.answer(
            progress_text,
            reply_markup=progress_keyboard(roadmap.id, next_step_title=next_steps[0].title),
        )


@router.callback_query(F.data == "show_overview")
async def handle_show_overview(callback: CallbackQuery, session: AsyncSession) -> None:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Профиль не найден.", show_alert=True)
        return

    roadmap_repo = RoadmapRepository(session)
    roadmap = await roadmap_repo.get_active(user.id)
    if not roadmap:
        await callback.answer("Маршрут не найден.", show_alert=True)
        return

    await callback.answer()
    await callback.message.answer(
        format_roadmap_overview(roadmap),
        reply_markup=roadmap_start_keyboard(),
    )


@router.callback_query(F.data == "roadmap_adjust")
async def handle_roadmap_adjust(callback: CallbackQuery) -> None:
    await callback.answer()
    await callback.message.answer(
        "🔄 <b>Как хочешь изменить маршрут?</b>",
        reply_markup=adjustment_keyboard(),
    )


@router.callback_query(F.data == "roadmap_regenerate")
async def handle_roadmap_regenerate(callback: CallbackQuery, session: AsyncSession) -> None:
    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Профиль не найден.", show_alert=True)
        return

    await callback.answer("🔄 Запускаю...")
    await callback.message.answer("🔄 Строю новый маршрут...")
    await generate_and_show_roadmap(callback.message, session, user.id)


@router.callback_query(F.data.startswith("step_back_"))
async def handle_step_back(callback: CallbackQuery, session: AsyncSession) -> None:
    step_id = await safe_callback_int(callback, "step_back_")
    if step_id is None:
        return
    step_repo = StepRepository(session)
    step = await step_repo.get_by_id(step_id)
    if not step:
        await callback.answer()
        return

    roadmap_repo = RoadmapRepository(session)
    roadmap = await roadmap_repo.get_with_steps(step.roadmap_id)
    if roadmap:
        await callback.answer()
        await show_step(callback.message, step, roadmap.total_steps)
    else:
        await callback.answer()
