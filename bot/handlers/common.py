from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config import TOPICS, LEVELS, FORMATS, TIME_OPTIONS
from bot.keyboards.inline import topics_kb, profile_edit_kb, start_route_kb
from bot.states import ProfileForm
from recommender.engine import get_user, get_route, get_or_create_user

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "🧭 <b>ПутеводительЗнаний — команды:</b>\n\n"
        "/start — начать или вернуться к профилю\n"
        "/route — показать текущий маршрут\n"
        "/profile — посмотреть профиль\n"
        "/restart — начать заново\n"
        "/help — эта справка\n\n"
        "📚 Бот подбирает бесплатные русскоязычные курсы, видео и статьи "
        "с Stepik, YouTube и Habr.",
        parse_mode="HTML",
    )


@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user = get_user(message.from_user.id)
    if not user or not user.topic:
        await message.answer("Профиль не заполнен. Напиши /start чтобы начать.")
        return

    route = get_route(user.id)
    done = sum(1 for item, _ in route if item.status == "completed")
    total = len(route)

    await message.answer(
        f"👤 <b>Твой профиль:</b>\n\n"
        f"• Тема: {TOPICS.get(user.topic, user.topic)}\n"
        f"• Уровень: {LEVELS.get(user.level, user.level)}\n"
        f"• Формат: {FORMATS.get(user.format_pref, user.format_pref)}\n"
        f"• Время: {TIME_OPTIONS.get(user.time_available, user.time_available)}\n\n"
        f"📊 Прогресс: {done}/{total} ресурсов изучено",
        parse_mode="HTML",
        reply_markup=profile_edit_kb(),
    )


@router.message(Command("restart"))
async def cmd_restart(message: Message, state: FSMContext):
    await state.clear()
    get_or_create_user(message.from_user.id, message.from_user.username)
    await message.answer(
        "🔄 Начинаем сначала! Выбери тему:",
        reply_markup=topics_kb(),
    )
    await state.set_state(ProfileForm.topic)
