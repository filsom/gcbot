from aiogram import F
from aiogram_dialog import Dialog, ShowMode, StartMode, Window
from aiogram_dialog.widgets import text, kbd

from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import (
    CalculateNormaDayDialog, 
    FoodDialog, 
    InputNormaDayDialog, 
    PaidStartingDialog
)


food_dialog = Dialog(
    Window(
        text.Const(
            "У меня нет ваших данных КБЖУ.\n"
            "Хотите посчитать или ввести свои данные",
            when=~F["kkal"]
        ),
        text.Const(
            "Вот что можем сделать:",
            when=F["kkal"]
        ),
        kbd.Start(
            text.Const("Расчет КБЖУ"),
            id="cal_kbju",
            state=CalculateNormaDayDialog.start
        ),
        kbd.Start(
            text.Const("Ввести КБЖУ"),
            id="input_kbju",
            state=InputNormaDayDialog.start,
        ),
        kbd.Button(
            text.Const("Меню на день"),
            id="day_menu",
            when=F["kkal"],
            on_click=...
        ),
        kbd.Start(
            text.Const("⬅️ На главную"),
            id="back_to_main_1",
            state=PaidStartingDialog.start,
            show_mode=ShowMode.EDIT,
            mode=StartMode.RESET_STACK
        ),
        state=FoodDialog.start,
        getter=...
    ),
)