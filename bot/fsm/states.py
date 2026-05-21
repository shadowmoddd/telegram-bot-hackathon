from aiogram.fsm.state import State, StatesGroup


class ProfileForm(StatesGroup):
    goal = State()
    quiz = State()
    time_per_week = State()
    total_hours = State()
    formats = State()
    learn_style = State()
    confirm = State()


class AdjustmentForm(StatesGroup):
    new_goal = State()
