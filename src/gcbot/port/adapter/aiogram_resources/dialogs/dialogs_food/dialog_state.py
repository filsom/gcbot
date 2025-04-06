from aiogram.fsm.state import StatesGroup, State


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
    

class DayMenuDialog(StatesGroup):
    start = State()
    view = State()