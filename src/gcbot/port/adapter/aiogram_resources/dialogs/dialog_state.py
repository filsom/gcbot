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


class FoodDialog(StatesGroup):
    start = State()


class InputNormaDayDialog(StatesGroup):
    start = State()
    protein = State()
    fat = State()
    carbs = State()
    end = State()


class CalculateNormaDayDialog(StatesGroup):
    start = State()
    hieght = State()
    age = State()
    activity = State()
    target = State()
    end = State()


class WorkoutDialog(StatesGroup):
    start = State()
    categories = State()
    view = State()


class DayMenuDialog(StatesGroup):
    start = State()
    view = State()


class WorkoutDialog(StatesGroup):
    start = State()
    categories = State()
    view = State()


class DayMenuDialog(StatesGroup):
    start = State()
    view = State()


class ContentDialog(StatesGroup):
    start = State()
    workout = State()
    upload_recipes = State()