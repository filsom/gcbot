from decimal import Decimal as D
import operator

from aiogram import Bot, types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets import text, kbd
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.application import commands as cmd
from gcbot.application.user_service import UserService
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_food.dialog_state import CalculateNormaDayDialog
from gcbot.port.adapter.aiogram_resources.dialogs.widgets import (
    DailyNormResultWindow, 
    NormaDayTextInput
)
from gcbot.port.adapter.aiogram_resources.query_services.user_query_service import UserQueryService


async def get_data_targets(**kwargs):
    target_types = [
        ("Быстро похудеть", "-0.8"),
        ("Плавно похудеть", "-0.9"),
        ("Поддержание веса", "1"),
        ("Плавный набор", "1.1"),
        ("Быстрый набор", "1.2"),
    ]
    return {"targets": target_types}


async def get_data_coefficients(**kwargs):
    activity_types = [
        ("Минимальная", "1.2"),
        ("Слабая", "1.375"),
        ("Средняя", "1.55"),
        ("Высокая", "1.725"),
        ("Не знаю 😔", "1"),
    ]
    return {"coefficients": activity_types}


@inject
async def selected_target(
    callback: t.CallbackQuery, 
    widget, 
    dialog_manager: DialogManager, 
    item_id,
    service: FromDishka[UserService] 
):
    calculate_result = await service \
        .calculate_norma(
            cmd.CalculateKсalCommand(
                callback.from_user.id,
                D(dialog_manager.find("input_age").get_value()),
                D(dialog_manager.find("input_hieght").get_value()),
                D(dialog_manager.find("input_weight").get_value()),
                D(dialog_manager.dialog_data["coefficient"]),
                D(item_id)
            )
        )
    dialog_manager.dialog_data.update(calculate_result)
    await dialog_manager.next()


async def get_result_calculated_values(dialog_manager: DialogManager, **kwargs):
    return dialog_manager.dialog_data["norma_day"]


@inject
async def selected_coefficient(
    callback: t.CallbackQuery, 
    widget, 
    dialog_manager: DialogManager, 
    item_id,
    query_service: FromDishka[UserQueryService]
):
    if item_id == "1":
        file_id = await query_service.query_video_note()
        await callback.message.answer_video_note(file_id)
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    else:
        dialog_manager.dialog_data["coefficient"] = item_id
        await dialog_manager.next()


calculate_norma_day_dialog = Dialog(
    Window(
        text.Const(
            "Напишите ваш текущий вес в кг.\n"
            "Пришлите только цифры, например, 72👇"
        ),
        NormaDayTextInput("input_weight"),
        state=CalculateNormaDayDialog.start
    ),
    Window(
        text.Const(
            "Введите ваш рост в см.\n"
            "Пришлите только цифры, например, 165👇"
        ),
        NormaDayTextInput("input_hieght"),
        state=CalculateNormaDayDialog.hieght
    ),
    Window(
        text.Const(
            "Напишите ваш возраст (лет).\n"
            "Пришлите только цифры, например, 35👇"
        ),
        NormaDayTextInput("input_age"),
        state=CalculateNormaDayDialog.age
    ),
    Window(
        text.Const("Выберите Ваш уровень активности:"),
        kbd.Column(
            kbd.Select(
                text.Format("{item[0]}"),
                id="selected_coefficient",
                item_id_getter=operator.itemgetter(1),
                items="coefficients",
                on_click=selected_coefficient
            )
        ),
        state=CalculateNormaDayDialog.activity,
        getter=get_data_coefficients
    ),
    Window(
        text.Const("Выберите цель меню:"),
        kbd.Column(
            kbd.Select(
                text.Format("{item[0]}"),
                id="selected_target",
                item_id_getter=operator.itemgetter(1),
                items="targets",
                on_click=selected_target
            )
        ),
        state=CalculateNormaDayDialog.target,
        getter=get_data_targets
    ),
    DailyNormResultWindow(
        CalculateNormaDayDialog.end, 
        get_result_calculated_values
    )
)