from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔃 Перезапустить бота")]],
        resize_keyboard=True,
    )
