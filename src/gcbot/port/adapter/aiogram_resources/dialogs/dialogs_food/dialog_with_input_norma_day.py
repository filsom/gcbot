from decimal import Decimal as D

from aiogram import types as t
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets import text, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.application.user_service import UserService
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_food.dialog_state import InputNormaDayDialog
from gcbot.port.adapter.aiogram_resources.dialogs.widgets import (
    DailyNormResultWindow, 
    NormaDayTextInput,
    on_error_inpute_value
)


async def get_result_inputed_values(dialog_manager: DialogManager, **kwargs):
    return {
        "kcal": dialog_manager.find("input_kcal").get_value(),
        "protein": dialog_manager.find("input_protein").get_value(),
        "fat": dialog_manager.find("input_fat").get_value(),
        "carbs": dialog_manager.find("input_carbs").get_value()
    }


@inject
async def input_last_value(
    message: t.Message,
    button,
    dialog_manager: DialogManager,
    value,
    service: FromDishka[UserService],
    **kwargs
):
    await service.input_norma(
        message.from_user.id, 
        D(dialog_manager.find("input_kcal").get_value())
    )
    await dialog_manager.next()


input_norma_day_dialog = Dialog(
    Window(
        text.Const(
            "Напишите вашу дневную норму Калорий.\n"
            "Пришлите только цифры, например, 1650👇"
        ),
        NormaDayTextInput("input_kcal"),
        state=InputNormaDayDialog.start
    ),
    Window(
        text.Const(
            "Напишите вашу дневную норму белков.\n"
            "Пришлите только цифры, например, 120👇"
        ),
        NormaDayTextInput("input_protein"),
        state=InputNormaDayDialog.protein
    ),
    Window(
        text.Const(
            "Напишите вашу дневную норму жиров.\n"
            "Пришлите только цифры, например, 55👇"
        ),
        NormaDayTextInput("input_fat"),
        state=InputNormaDayDialog.fat
    ),
    Window(
        text.Const(
            "Напишите вашу дневную норму углеводов.\n"
            "Пришлите только цифры, например, 220👇"
        ),
        input.TextInput(
            id="input_carbs", 
            on_success=input_last_value,
            on_error=on_error_inpute_value,
            type_factory=int
        ),
        state=InputNormaDayDialog.carbs
    ),
    DailyNormResultWindow(
        InputNormaDayDialog.end,
        get_result_inputed_values
    )
)