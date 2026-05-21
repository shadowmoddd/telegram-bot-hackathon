import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.fsm.states import ProfileForm
from bot.keyboards.inline import (
    formats_keyboard,
    learn_style_keyboard,
    profile_confirm_keyboard,
    time_keyboard,
    total_hours_keyboard,
)
from bot.services.goal_classifier import classify_goal
from bot.services.profile_service import (
    format_profile_summary,
    get_or_create_user,
    save_profile,
)
from bot.services.quiz_service import evaluate_quiz, generate_quiz

router = Router()

_LEVEL_LABELS = {
    "beginner": "Новичок",
    "elementary": "Есть база",
    "intermediate": "Средний уровень",
    "advanced": "Продвинутый",
}


@router.message(ProfileForm.goal)
async def process_goal(message: Message, state: FSMContext) -> None:
    if not message.text or len(message.text.strip()) < 3:
        await message.answer("Пожалуйста, опиши свою цель подробнее (минимум 3 символа).")
        return

    goal = message.text.strip()
    await state.update_data(goal=goal)

    loading = await message.answer("🔍 Подбираю вопросы для оценки уровня...")

    questions = []
    try:
        questions = await generate_quiz(goal)
    except Exception as e:
        logger.error(f"[Quiz] Generation failed: {e}")

    try:
        await loading.delete()
    except Exception:
        pass

    if questions:
        await state.update_data(quiz_questions=questions, quiz_answers=[])
        await state.set_state(ProfileForm.quiz)
        await message.answer(
            f"🎯 Задам пару вопросов, чтобы понять твой текущий уровень.\n\n"
            f"<b>Вопрос:</b> {questions[0]['q']}",
        )
    else:
        hit = classify_goal(goal)
        await state.update_data(
            sphere=hit["sphere"] or "other",
            specialization=(hit["specs"] or [None])[0],
            level="beginner",
        )
        await state.set_state(ProfileForm.time_per_week)
        await message.answer(
            "⏰ <b>Вопрос 2 из 5</b>\n\nСколько времени в неделю готов уделять обучению?",
            reply_markup=time_keyboard(),
        )


@router.message(ProfileForm.quiz)
async def process_quiz_answer(message: Message, state: FSMContext) -> None:
    if not message.text:
        return

    data = await state.get_data()
    questions = data.get("quiz_questions", [])
    answers = data.get("quiz_answers", [])
    index = len(answers)

    if index >= len(questions):
        return

    current_q = questions[index]
    user_answer = message.text.strip()

    hints = current_q.get("hints", [])
    is_correct = bool(hints) and any(h.lower() in user_answer.lower() for h in hints)
    feedback = "✅ Правильно!" if is_correct else "💡 Понял."

    answers.append({"q": current_q["q"], "a": user_answer, "correct": is_correct})
    await state.update_data(quiz_answers=answers)

    next_index = index + 1
    if next_index < len(questions):
        next_q = questions[next_index]
        await message.answer(
            f"{feedback}\n\n<b>Следующий вопрос:</b> {next_q['q']}",
        )
    else:
        await message.answer(f"{feedback}\n\n🔄 Оцениваю твои знания...")

        try:
            evaluation = await evaluate_quiz(data["goal"], answers)
        except Exception as e:
            logger.error(f"[Quiz] Evaluation failed: {e}")
            evaluation = {}

        level = evaluation.get("level", "beginner")
        sphere = evaluation.get("sphere") or classify_goal(data["goal"])["sphere"] or "other"
        spec = evaluation.get("specialization")
        learning_gaps = evaluation.get("learning_gaps", [])
        strong_points = evaluation.get("strong_points", [])

        if spec in ("none", "", None):
            spec = None

        await state.update_data(
            level=level,
            sphere=sphere,
            specialization=spec,
            learning_gaps=learning_gaps,
            strong_points=strong_points,
        )

        level_text = _LEVEL_LABELS.get(level, level)
        await message.answer(
            f"📊 Определил твой уровень: <b>{level_text}</b>\n\nПродолжаем!",
        )

        await state.set_state(ProfileForm.time_per_week)
        await message.answer(
            "⏰ <b>Вопрос 2 из 5</b>\n\nСколько времени в неделю готов уделять обучению?",
            reply_markup=time_keyboard(),
        )


@router.callback_query(ProfileForm.time_per_week, F.data.startswith("time_"))
async def process_time(callback: CallbackQuery, state: FSMContext) -> None:
    time_key = callback.data.replace("time_", "")
    await state.update_data(time_per_week=time_key)
    await state.set_state(ProfileForm.total_hours)
    await callback.message.answer(
        "🕐 <b>Вопрос 3 из 5</b>\n\n"
        "Сколько часов суммарно ты готов потратить на весь маршрут?\n\n"
        "<i>Это поможет подобрать маршрут нужной глубины</i>",
        reply_markup=total_hours_keyboard(),
    )
    await callback.answer()


@router.callback_query(ProfileForm.total_hours, F.data.startswith("hours_"))
async def process_total_hours(callback: CallbackQuery, state: FSMContext) -> None:
    hours_key = callback.data.replace("hours_", "")
    await state.update_data(total_hours=hours_key)
    await state.update_data(formats=[])
    await state.set_state(ProfileForm.formats)
    await callback.message.answer(
        "🎬 <b>Вопрос 4 из 5</b>\n\n"
        "Какие форматы обучения тебе подходят?\n"
        "<i>Можно выбрать несколько. Нажми «Далее» когда выберешь.</i>",
        reply_markup=formats_keyboard([]),
    )
    await callback.answer()


@router.callback_query(ProfileForm.formats, F.data.startswith("toggle_fmt_"))
async def toggle_format(callback: CallbackQuery, state: FSMContext) -> None:
    fmt = callback.data.replace("toggle_fmt_", "")
    data = await state.get_data()
    selected: list[str] = data.get("formats", [])

    if fmt in selected:
        selected.remove(fmt)
    else:
        selected.append(fmt)

    await state.update_data(formats=selected)
    await callback.message.edit_reply_markup(reply_markup=formats_keyboard(selected))
    await callback.answer()


@router.callback_query(ProfileForm.formats, F.data == "formats_done")
async def process_formats_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    formats = data.get("formats", [])
    if not formats:
        await callback.answer("Выбери хотя бы один формат!", show_alert=True)
        return

    await state.set_state(ProfileForm.learn_style)
    await callback.message.answer(
        "🎓 <b>Вопрос 5 из 5</b>\n\nКак тебе лучше всего учиться?",
        reply_markup=learn_style_keyboard(),
    )
    await callback.answer()


@router.callback_query(ProfileForm.learn_style, F.data.startswith("lstyle_"))
async def process_learn_style(callback: CallbackQuery, state: FSMContext) -> None:
    learn_style = callback.data.replace("lstyle_", "")
    await state.update_data(learn_style=learn_style)
    await _show_confirm(callback.message, state)
    await callback.answer()


async def _show_confirm(message: Message, state: FSMContext) -> None:
    await state.set_state(ProfileForm.confirm)
    data = await state.get_data()
    summary = format_profile_summary(data)
    await message.answer(
        f"{summary}\n\nВсё верно?",
        reply_markup=profile_confirm_keyboard(),
    )


@router.callback_query(ProfileForm.confirm, F.data == "profile_confirm")
async def confirm_profile(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    user = await get_or_create_user(session, callback.from_user.id, callback.from_user.username, callback.from_user.first_name)
    await save_profile(session, user.id, data)
    logger.info(f"Profile saved for user_id={user.id}")

    await state.clear()
    loading_msg = await callback.message.answer("✨ Подбираю материалы для маршрута...")
    await callback.answer()

    anim_task = asyncio.create_task(_loading_animation(loading_msg))
    try:
        from bot.handlers.roadmap import generate_and_show_roadmap
        await generate_and_show_roadmap(callback.message, session, user.id)
    finally:
        anim_task.cancel()
        try:
            await loading_msg.delete()
        except Exception:
            pass


async def _loading_animation(msg: Message) -> None:
    stages = [
        "🔍 Подбираю материалы...",
        "🗺 Строю маршрут...",
        "✅ Проверяю ссылки...",
        "⚡ Почти готово...",
    ]
    try:
        for stage in stages:
            await asyncio.sleep(7)
            await msg.edit_text(stage)
    except asyncio.CancelledError:
        pass
    except Exception:
        pass


@router.callback_query(ProfileForm.confirm, F.data == "profile_edit")
async def edit_profile(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(ProfileForm.goal)
    await callback.message.answer(
        "🔄 Начнём заново.\n\n"
        "🎯 <b>Вопрос 1 из 5</b>\n\nЧего хочешь достичь?\n\n"
        "✏️ <i>Например: «стать Python-разработчиком», «освоить UI/UX дизайн», «монтировать видео»</i>",
    )
    await callback.answer()
