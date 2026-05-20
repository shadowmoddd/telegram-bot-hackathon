from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import topics_kb, levels_kb, formats_kb, time_kb, start_route_kb
from bot.states import ProfileForm
from bot.config import TOPICS, LEVELS, FORMATS, TIME_OPTIONS
from recommender.engine import update_user_profile, get_user, build_route, save_route

router = Router()


@router.callback_query(F.data.startswith("topic:"))
async def cb_topic(callback: CallbackQuery, state: FSMContext):
    topic = callback.data.split(":")[1]
    await state.update_data(topic=topic)
    await callback.message.edit_text(
        f"Тема: <b>{TOPICS[topic]}</b> ✅\n\n"
        "Теперь выбери свой <b>уровень подготовки</b>:",
        parse_mode="HTML",
        reply_markup=levels_kb(),
    )
    await state.set_state(ProfileForm.level)
    await callback.answer()


@router.callback_query(F.data.startswith("level:"))
async def cb_level(callback: CallbackQuery, state: FSMContext):
    level = callback.data.split(":")[1]
    await state.update_data(level=level)
    await callback.message.edit_text(
        f"Уровень: <b>{LEVELS[level]}</b> ✅\n\n"
        "Какой формат материалов предпочитаешь?",
        parse_mode="HTML",
        reply_markup=formats_kb(),
    )
    await state.set_state(ProfileForm.format_pref)
    await callback.answer()


@router.callback_query(F.data.startswith("format:"))
async def cb_format(callback: CallbackQuery, state: FSMContext):
    fmt = callback.data.split(":")[1]
    await state.update_data(format_pref=fmt)
    await callback.message.edit_text(
        f"Формат: <b>{FORMATS[fmt]}</b> ✅\n\n"
        "Сколько времени в неделю готов уделять обучению?",
        parse_mode="HTML",
        reply_markup=time_kb(),
    )
    await state.set_state(ProfileForm.time_available)
    await callback.answer()


@router.callback_query(F.data.startswith("time:"))
async def cb_time(callback: CallbackQuery, state: FSMContext):
    time_opt = callback.data.split(":")[1]
    data = await state.get_data()
    data["time_available"] = time_opt

    update_user_profile(
        callback.from_user.id,
        topic=data["topic"],
        level=data["level"],
        format_pref=data["format_pref"],
        time_available=time_opt,
        current_position=0,
    )

    await state.clear()
    await callback.message.edit_text(
        f"Время: <b>{TIME_OPTIONS[time_opt]}</b> ✅\n\n"
        "⏳ Составляю твой персональный маршрут...",
        parse_mode="HTML",
    )

    user = get_user(callback.from_user.id)
    resources = build_route(user)

    if not resources:
        await callback.message.edit_text(
            "😔 По твоим параметрам не нашлось ресурсов.\n\n"
            "Попробуй выбрать другую тему или формат.",
            reply_markup=topics_kb(),
        )
        await callback.answer()
        return

    save_route(user.id, resources)
    update_user_profile(callback.from_user.id, current_position=0)

    total = len(resources)
    preview = "\n".join(
        f"{i+1}. {r.title} — {r.source.capitalize()}"
        for i, r in enumerate(resources)
    )

    await callback.message.edit_text(
        f"🗺 <b>Твой учебный маршрут готов!</b>\n\n"
        f"Найдено <b>{total}</b> ресурсов по теме:\n\n"
        f"{preview}\n\n"
        "Нажми «Начать маршрут», чтобы перейти к первому материалу 👇",
        parse_mode="HTML",
        reply_markup=start_route_kb(),
    )
    await callback.answer()


@router.callback_query(F.data == "profile:edit")
async def cb_profile_edit(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "Выбери новую тему обучения:",
        reply_markup=topics_kb(),
    )
    await state.set_state(ProfileForm.topic)
    await callback.answer()
