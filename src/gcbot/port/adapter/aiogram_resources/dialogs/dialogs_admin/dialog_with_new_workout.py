import asyncio
import operator
from uuid import UUID

from aiogram import types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import kbd, text
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.application.admin_service import AdminService
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.dialog_state import (
    NewTrainingDialog, 
    UploadMediaDialog
)
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.dialog_state import SendMailingDialog
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.mailing import RecipientMailing
from gcbot.port.adapter.aiogram_resources.query_services.workout_query_service import (
    WorkoutQueryService
)


async def on_click_category_name(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    item_id,
):
    dialog_manager.dialog_data["category_id"] = str(item_id)
    dialog_manager.dialog_data["user_id"] = callback.from_user.id
    await dialog_manager.start(
        UploadMediaDialog.start,
        show_mode=ShowMode.EDIT,
        data={"from_training": True}
    )


@inject
async def get_categories_name(
    dialog_manager: DialogManager, 
    service: FromDishka[WorkoutQueryService], 
    **kwargs
):
    return await service.query_categories_names()


async def on_click_free_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        SendMailingDialog.start,
        data={
            "user_id": callback.from_user.id, 
            "media": dialog_manager.dialog_data["media"],
            "inpute_text_media": dialog_manager.dialog_data["inpute_text_media"],
            "type_recipient": RecipientMailing.FREE
        },
        mode=StartMode.NORMAL,
        show_mode=ShowMode.EDIT
    )


@inject
async def process_result_add_workout(
    start_data,
    result,
    dialog_manager: DialogManager,
    service: FromDishka[AdminService]
):
    if result:
        dialog_manager.dialog_data["media"] = result["media"]
        dialog_manager.dialog_data["inpute_text_media"] = result["inpute_text_media"]
        await service.add_new_workout(
            UUID(dialog_manager.dialog_data["category_id"]),
            result["inpute_text_media"],
            result["media"]
        )
        await dialog_manager.next()


new_workout_dialog = Dialog(
    Window(
        text.Const("Выберите категорию тренировки!"),
        kbd.Column(
            kbd.Select(
                id='id_name_category_1',
                text=text.Format("{item[0]}"),
                items="categories",
                item_id_getter=operator.itemgetter(1),
                on_click=on_click_category_name
            ),
        ),
        kbd.Cancel(text.Const("⬅️ В Админ панель"), id="to_main"),
        state=NewTrainingDialog.start,
        getter=get_categories_name,
        on_process_result=process_result_add_workout
    ),
    Window(
        text.Const(
            "Тренировка успешно сохранена ✅\nРазослать бесплатным пользователям?"
        ),
        kbd.Row(
            kbd.Button(
                text.Const("Да"),
                id="yes_mailing_1",
                on_click=on_click_free_mailing
            ),
            kbd.Cancel(text.Const("Нет"))
        ),
        state=NewTrainingDialog.send,
    )
)