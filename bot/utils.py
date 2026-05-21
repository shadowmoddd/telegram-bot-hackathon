from html import escape as _escape
from typing import Optional

from aiogram.types import CallbackQuery


async def safe_callback_int(callback: CallbackQuery, prefix: str) -> Optional[int]:
    try:
        value: Optional[int] = int(callback.data.removeprefix(prefix))
    except (ValueError, AttributeError):
        value = None
    if value is None:
        await callback.answer("Неверный запрос.", show_alert=True)
    return value


def escape(text: Optional[str]) -> str:
    return _escape(text or "")
