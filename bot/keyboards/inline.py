from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from bot.config import TOPICS, LEVELS, FORMATS, TIME_OPTIONS


def topics_kb() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=label, callback_data=f"topic:{key}")
        for key, label in TOPICS.items()
    ]
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def levels_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"level:{key}")]
        for key, label in LEVELS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def formats_kb() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text=label, callback_data=f"format:{key}")
        for key, label in FORMATS.items()
    ]
    rows = [buttons[i:i+2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def time_kb() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=label, callback_data=f"time:{key}")]
        for key, label in TIME_OPTIONS.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def route_item_kb(position: int, total: int, resource_id: int) -> InlineKeyboardMarkup:
    nav = []
    if position > 0:
        nav.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"nav:prev"))
    if position < total - 1:
        nav.append(InlineKeyboardButton(text="➡️ Далее", callback_data=f"nav:next"))

    actions = [
        InlineKeyboardButton(text="✅ Изучил", callback_data=f"item:done:{resource_id}"),
        InlineKeyboardButton(text="⏭ Пропустить", callback_data=f"item:skip:{resource_id}"),
    ]

    bottom = [
        InlineKeyboardButton(text="📋 Весь маршрут", callback_data="route:list"),
        InlineKeyboardButton(text="🔄 Новый маршрут", callback_data="route:new"),
        InlineKeyboardButton(text="✏️ Изменить профиль", callback_data="profile:edit"),
    ]

    rows = []
    if nav:
        rows.append(nav)
    rows.append(actions)
    rows.append(bottom[:2])
    rows.append([bottom[2]])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def route_list_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Новый маршрут", callback_data="route:new")],
        [InlineKeyboardButton(text="✏️ Изменить профиль", callback_data="profile:edit")],
    ])


def start_route_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Начать маршрут", callback_data="nav:start")],
        [InlineKeyboardButton(text="📋 Показать всё", callback_data="route:list")],
    ])


def profile_edit_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✏️ Изменить профиль", callback_data="profile:edit")],
        [InlineKeyboardButton(text="📋 Мой маршрут", callback_data="nav:start")],
    ])
