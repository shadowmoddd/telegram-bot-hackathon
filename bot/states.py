from aiogram.fsm.state import State, StatesGroup


class ProfileForm(StatesGroup):
    topic = State()
    level = State()
    format_pref = State()
    time_available = State()
