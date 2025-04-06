from aiogram.fsm.state import StatesGroup, State


class PaidStartingDialog(StatesGroup):
    start = State()
    not_access = State()


class AnonStartingDialog(StatesGroup):
    start = State()
    confirm_email = State()
    inputed_email = State()


class FreeStartingDialog(StatesGroup):
    start = State()
    check_access = State()


class AdminStartingDialog(StatesGroup):
    start = State()


class WorkoutDialog(StatesGroup):
    start = State()
    categories = State()
    view = State()


class ContentDialog(StatesGroup):
    start = State()
    workout = State()
    upload_recipes = State()