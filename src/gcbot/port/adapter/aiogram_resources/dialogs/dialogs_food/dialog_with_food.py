from aiogram import F
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import text, kbd
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import (
    CalculateNormaDayDialog, 
    FoodDialog, 
    InputNormaDayDialog, 
    PaidStartingDialog
)
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_food.widgets import on_click_day_meny
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_json_fetchers import UserJsonFetcher


@inject
async def get_user_data(
    dialog_manager: DialogManager, 
    user_fentcher: FromDishka[UserJsonFetcher],
    **kwargs
):
    return await user_fentcher \
        .fetch_user_and_groups_with_id(
            dialog_manager.start_data["user_id"]
        )


food_dialog = Dialog(
    Window(
        text.Const(
            "У меня нет ваших данных КБЖУ.\n"
            "Хотите посчитать или ввести свои данные",
            when=~F["norma_kcal"]
        ),
        text.Const(
            "Вот что можем сделать:",
            when=F["norma_kcal"]
        ),
        kbd.Start(
            text.Const("Расчет КБЖУ"),
            id="calculate_norma_day",
            state=CalculateNormaDayDialog.start
        ),
        kbd.Start(
            text.Const("Ввести КБЖУ"),
            id="input_norma_day",
            state=InputNormaDayDialog.start,
        ),
        kbd.Button(
            text.Const("Меню на день"),
            id="day_menu",
            when=F["norma_kcal"],
            on_click=on_click_day_meny
        ),
        kbd.Start(
            text.Const("⬅️ На главную"),
            id="back_main_from_food",
            state=PaidStartingDialog.start,
            show_mode=ShowMode.EDIT,
            mode=StartMode.RESET_STACK
        ),
        state=FoodDialog.start,
        getter=get_user_data
    ),
)