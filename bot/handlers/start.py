from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config import TOPICS, LEVELS, FORMATS, TIME_OPTIONS
from bot.keyboards.inline import topics_kb, profile_edit_kb, start_route_kb
from bot.states import ProfileForm
from recommender.engine import get_or_create_user, get_user, get_route

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = get_user(message.from_user.id)

    if user and user.topic:
        topic_label = TOPICS.get(user.topic, user.topic)
        level_label = LEVELS.get(user.level, user.level)
        format_label = FORMATS.get(user.format_pref, user.format_pref)
        time_label = TIME_OPTIONS.get(user.time_available, user.time_available)

        route = get_route(user.id)
        done = sum(1 for item, _ in route if item.status == "completed")
        total = len(route)

        await message.answer(
            f"👋 С возвращением, <b>{message.from_user.first_name}</b>!\n\n"
            f"📌 <b>Твой профиль:</b>\n"
            f"• Тема: {topic_label}\n"
            f"• Уровень: {level_label}\n"
            f"• Формат: {format_label}\n"
            f"• Время: {time_label}\n\n"
            f"📚 Прогресс по маршруту: {done}/{total} ресурсов изучено",
            parse_mode="HTML",
            reply_markup=start_route_kb() if total > 0 else profile_edit_kb(),
        )
    else:
        get_or_create_user(message.from_user.id, message.from_user.username)
        await message.answer(
            f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
            "Я — <b>ПутеводительЗнаний</b> 🧭\n\n"
            "Помогу составить персональный учебный маршрут из <b>бесплатных русскоязычных</b> "
            "ресурсов: курсов, видео и статей.\n\n"
            "Давай начнём! Выбери тему, которую хочешь освоить 👇",
            parse_mode="HTML",
            reply_markup=topics_kb(),
        )
        await state.set_state(ProfileForm.topic)
