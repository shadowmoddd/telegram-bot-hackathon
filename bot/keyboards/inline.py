from aiogram.types import InlineKeyboardMarkup, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.config import settings


def _miniapp_url() -> str:
    return settings.MINIAPP_URL


def time_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⏱ Меньше 1 часа", callback_data="time_lt1")
    builder.button(text="⏰ 1–2 часа", callback_data="time_1to2")
    builder.button(text="🕐 3–5 часов", callback_data="time_3to5")
    builder.button(text="💪 5+ часов", callback_data="time_gt5")
    builder.adjust(2)
    return builder.as_markup()


def learn_style_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 Теория + практика вместе", callback_data="lstyle_theory_practice")
    builder.button(text="🛠 Только практика, минимум теории", callback_data="lstyle_practice")
    builder.button(text="👀 Смотрю примеры и повторяю", callback_data="lstyle_examples")
    builder.button(text="📝 Структурированный курс с заданиями", callback_data="lstyle_structured")
    builder.adjust(1)
    return builder.as_markup()


def total_hours_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⚡ До 10 часов", callback_data="hours_10")
    builder.button(text="📘 10–20 часов", callback_data="hours_20")
    builder.button(text="🎯 20–40 часов", callback_data="hours_40")
    builder.button(text="🔥 40–80 часов", callback_data="hours_80")
    builder.button(text="🚀 80+ часов", callback_data="hours_80plus")
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def profile_confirm_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Всё верно, строим маршрут!", callback_data="profile_confirm")
    builder.button(text="✏️ Изменить", callback_data="profile_edit")
    builder.adjust(1)
    return builder.as_markup()


def formats_keyboard(selected: list[str] | None = None) -> InlineKeyboardMarkup:
    if selected is None:
        selected = []
    formats = [
        ("📺 Видео", "fmt_video"),
        ("📰 Статьи", "fmt_article"),
        ("🎓 Курсы", "fmt_course"),
        ("🎙 Лекции", "fmt_lecture"),
        ("📚 Книги", "fmt_book"),
    ]
    builder = InlineKeyboardBuilder()
    for text, callback in formats:
        check = "✅ " if callback.replace("fmt_", "") in selected else ""
        builder.button(text=f"{check}{text}", callback_data=f"toggle_{callback}")
    builder.button(text="➡️ Далее", callback_data="formats_done")
    builder.adjust(2, 2, 1, 1)
    return builder.as_markup()


def step_actions_keyboard(step_id: int, has_next: bool = True) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Завершить шаг", callback_data=f"step_complete_{step_id}")
    if has_next:
        builder.button(text="📚 Следующий шаг", callback_data=f"step_next_{step_id}")
    builder.button(text="👎 Не подходит", callback_data=f"step_dislike_{step_id}")
    builder.button(text="🔄 Изменить маршрут", callback_data="roadmap_adjust")
    builder.adjust(2, 2)
    return builder.as_markup()


def feedback_reason_keyboard(step_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="😰 Слишком сложно", callback_data=f"fb_hard_{step_id}")
    builder.button(text="😴 Слишком просто", callback_data=f"fb_easy_{step_id}")
    builder.button(text="📺 Другой формат", callback_data=f"fb_format_{step_id}")
    builder.button(text="✅ Уже прошёл", callback_data=f"fb_done_{step_id}")
    builder.button(text="🎯 Изменить цель", callback_data="fb_change_goal")
    builder.button(text="◀️ Назад", callback_data=f"step_back_{step_id}")
    builder.adjust(2)
    return builder.as_markup()


def adjustment_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📈 Сделать сложнее", callback_data="adj_harder")
    builder.button(text="📉 Сделать проще", callback_data="adj_easier")
    builder.button(text="🎬 Больше видео", callback_data="adj_more_video")
    builder.button(text="📖 Больше статей", callback_data="adj_more_articles")
    builder.button(text="🎯 Изменить цель", callback_data="adj_change_goal")
    builder.button(text="◀️ Отмена", callback_data="adj_cancel")
    builder.adjust(2)
    return builder.as_markup()


def roadmap_start_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🚀 Открыть приложение", web_app=WebAppInfo(url=_miniapp_url()))
    builder.adjust(1)
    return builder.as_markup()


def progress_keyboard(roadmap_id: int, next_step_title: str = "") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📊 Мой прогресс", callback_data=f"progress_{roadmap_id}")
    label = f"▶️ {next_step_title[:28]}..." if len(next_step_title) > 28 else f"▶️ {next_step_title}" if next_step_title else "▶️ Продолжить"
    builder.button(text=label, callback_data="roadmap_continue")
    builder.adjust(1, 1)
    return builder.as_markup()
