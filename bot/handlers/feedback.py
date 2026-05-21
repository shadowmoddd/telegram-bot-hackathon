from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.repository import ProfileRepository, RoadmapRepository, StepRepository, UserRepository
from bot.fsm.states import AdjustmentForm
from bot.handlers.roadmap import generate_and_show_roadmap, show_step
from bot.keyboards.inline import feedback_reason_keyboard, roadmap_start_keyboard
from bot.keyboards.reply import remove_keyboard
from bot.services.ai_service import get_ai_service
from bot.services.roadmap_service import _enrich_with_db_resources, format_roadmap_overview
from bot.utils import escape, safe_callback_int

router = Router()


@router.callback_query(F.data.startswith("step_dislike_"))
async def handle_step_dislike(callback: CallbackQuery) -> None:
    step_id = await safe_callback_int(callback, "step_dislike_")
    if step_id is None:
        return
    await callback.message.answer(
        "😕 Что именно не подходит?",
        reply_markup=feedback_reason_keyboard(step_id),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("fb_hard_"))
async def handle_feedback_hard(callback: CallbackQuery, session: AsyncSession) -> None:
    step_id = await safe_callback_int(callback, "fb_hard_")
    if step_id is None:
        return
    await _replace_step(callback, session, step_id, "too_hard", "Слишком сложно")


@router.callback_query(F.data.startswith("fb_easy_"))
async def handle_feedback_easy(callback: CallbackQuery, session: AsyncSession) -> None:
    step_id = await safe_callback_int(callback, "fb_easy_")
    if step_id is None:
        return
    await _replace_step(callback, session, step_id, "too_easy", "Слишком просто")


@router.callback_query(F.data.startswith("fb_format_"))
async def handle_feedback_format(callback: CallbackQuery, session: AsyncSession) -> None:
    step_id = await safe_callback_int(callback, "fb_format_")
    if step_id is None:
        return
    await _replace_step(callback, session, step_id, "wrong_format", "Хочу другой формат")


@router.callback_query(F.data.startswith("fb_done_"))
async def handle_feedback_done(callback: CallbackQuery, session: AsyncSession) -> None:
    step_id = await safe_callback_int(callback, "fb_done_")
    if step_id is None:
        return
    step_repo = StepRepository(session)
    await step_repo.update_status(step_id, "completed", {"reason": "already_done"})
    await callback.message.answer("✅ Шаг отмечен как пройденный! Переходим к следующему.")

    step = await step_repo.get_by_id(step_id)
    if step:
        roadmap_repo = RoadmapRepository(session)
        roadmap = await roadmap_repo.get_with_steps(step.roadmap_id)
        if roadmap:
            next_steps = [s for s in roadmap.steps if s.order_num > step.order_num and s.status == "pending"]
            if next_steps:
                next_step = next_steps[0]
                await step_repo.update_status(next_step.id, "in_progress")
                await show_step(callback.message, next_step, roadmap.total_steps)
            else:
                await callback.message.answer("🎉 Все шаги пройдены!")
    await callback.answer()


@router.callback_query(F.data == "fb_change_goal")
async def handle_feedback_change_goal(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(AdjustmentForm.new_goal)
    await callback.message.answer("🎯 Напиши новую цель обучения:", reply_markup=remove_keyboard())
    await callback.answer()


async def _replace_step(
    callback: CallbackQuery,
    session: AsyncSession,
    step_id: int,
    adjustment_type: str,
    reason: str,
) -> None:
    await callback.message.answer(f"🔄 Подбираю альтернативу... ({reason})")

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

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Профиль не найден.", show_alert=True)
        return

    profile_repo = ProfileRepository(session)
    profile = await profile_repo.get_by_user_id(user.id)
    if not profile:
        await callback.answer("Профиль не найден.", show_alert=True)
        return

    try:
        ai = get_ai_service()
        alternative = await ai.suggest_alternative_step(step, reason, profile)

        await step_repo.update_status(step_id, "skipped", {"reason": adjustment_type, "replaced": True})

        new_step = await step_repo.create(roadmap.id, alternative, step.order_num)
        new_step.status = "in_progress"
        await session.commit()

        await callback.message.answer("✅ Нашёл замену! Вот альтернативный шаг:")
        await show_step(callback.message, new_step, roadmap.total_steps)

    except Exception as e:
        logger.error(f"Error getting alternative step: {e}")
        await callback.message.answer(
            "😔 Не удалось найти альтернативу. Попробуй изменить маршрут целиком через «🔄 Изменить маршрут»."
        )
    await callback.answer()


@router.callback_query(F.data.startswith("adj_"))
async def handle_adjustment(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    action = callback.data.replace("adj_", "")

    if action == "cancel":
        await callback.message.answer("Отменено.")
        await callback.answer()
        return

    if action == "change_goal":
        await state.set_state(AdjustmentForm.new_goal)
        await callback.message.answer("🎯 Напиши новую цель обучения:", reply_markup=remove_keyboard())
        await callback.answer()
        return

    adjustment_map = {
        "harder": ("too_hard", "Хочу сложнее"),
        "easier": ("too_easy", "Хочу проще"),
        "more_video": ("wrong_format", "Хочу больше видео"),
        "more_articles": ("wrong_format", "Хочу больше статей"),
    }

    if action not in adjustment_map:
        await callback.answer()
        return

    adjustment_type, reason = adjustment_map[action]

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(callback.from_user.id)
    if not user:
        await callback.answer("Профиль не найден.", show_alert=True)
        return

    await callback.answer("🔄 Перестраиваю...")
    await callback.message.answer(f"🔄 Перестраиваю маршрут... ({reason})")

    roadmap_repo = RoadmapRepository(session)
    roadmap = await roadmap_repo.get_active(user.id)
    if not roadmap:
        return

    roadmap_with_steps = await roadmap_repo.get_with_steps(roadmap.id)
    profile_repo = ProfileRepository(session)
    profile = await profile_repo.get_by_user_id(user.id)

    try:
        ai = get_ai_service()
        new_data = await ai.adjust_roadmap(roadmap_with_steps, roadmap_with_steps.steps, reason, adjustment_type)

        if profile:
            new_data = _enrich_with_db_resources(new_data, profile)

        await roadmap_repo.abandon_active(user.id)

        new_roadmap = await roadmap_repo.create(
            user_id=user.id,
            title=new_data.get("title", roadmap.title),
            description=new_data.get("description", ""),
            total_steps=len(new_data.get("steps", [])),
            estimated_weeks=new_data.get("estimated_weeks", 0),
        )

        step_repo = StepRepository(session)
        await step_repo.create_bulk(new_roadmap.id, new_data.get("steps", []))

        updated = await roadmap_repo.get_with_steps(new_roadmap.id)
        if updated:
            overview = format_roadmap_overview(updated)
            await callback.message.answer(
                "✅ Маршрут обновлён!\n\n" + overview,
                reply_markup=roadmap_start_keyboard(),
            )

    except Exception as e:
        logger.error(f"Error adjusting roadmap: {e}")
        if "429" in str(e) or "rate_limit" in str(e).lower():
            await callback.message.answer(
                "⏳ Сервис временно перегружен. Попробуй через 1–2 часа."
            )
        else:
            await callback.message.answer("😔 Не удалось скорректировать маршрут. Попробуй позже.")


@router.message(AdjustmentForm.new_goal)
async def process_new_goal(message: Message, state: FSMContext, session: AsyncSession) -> None:
    new_goal = message.text.strip() if message.text else ""
    if not new_goal:
        await message.answer("Пожалуйста, напиши новую цель.")
        return

    await state.clear()

    user_repo = UserRepository(session)
    user = await user_repo.get_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Профиль не найден.")
        return

    profile_repo = ProfileRepository(session)
    await profile_repo.upsert(user.id, {"goal": new_goal})

    await message.answer(
        f"✅ Цель обновлена: <b>{escape(new_goal)}</b>\n\n🔄 Строю новый маршрут...",
    )

    await generate_and_show_roadmap(message, session, user.id)
