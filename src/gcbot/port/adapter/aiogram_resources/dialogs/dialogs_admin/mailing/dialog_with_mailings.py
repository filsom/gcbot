import operator

from aiogram import types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets import text, kbd

from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.dialog_state import UploadMediaDialog
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.dialog_state import (
    MaillingDialog, 
    PlandeMaillingDialog, 
    SendMailingDialog
)
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.mailing import RecipientMailing


async def on_click_name_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    item_id,
):
    await dialog_manager.start(
        SendMailingDialog.start,
        data={
            "media": dialog_manager.dialog_data["media"],
            "inpute_text_media": dialog_manager.dialog_data["inpute_text_media"],
            "type_recipient": item_id
        },
        show_mode=ShowMode.EDIT
    )


async def get_data_mailings(
   dialog_manager: DialogManager,
   **kwargs 
):
    name_mailings = [
        ("Бесплатные", RecipientMailing.FREE),
        ("Платные", RecipientMailing.PAID)
    ]
    return {"mailings": name_mailings}


async def on_click_new_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        UploadMediaDialog.start,
        show_mode=ShowMode.EDIT,
        data={}
    )


async def process_result_add_new_mailing(
    start_data,
    result,
    dialog_manager: DialogManager,
):
    if result:
        dialog_manager.dialog_data["media"] = *result["media"],
        dialog_manager.dialog_data["inpute_text_media"] = result["inpute_text_media"],
        await dialog_manager.next(ShowMode.EDIT)


mailing_dialog = Dialog(
    Window(
        text.Const("Меню рассылки"),
        kbd.Button(
            text.Const("Новая рассылка"), 
            id="new_mailing", 
            on_click=on_click_new_mailing
        ),
        kbd.Start(
            text.Const("Запланированные"),
            id="planed_mailing",
            state=PlandeMaillingDialog.start,
            show_mode=ShowMode.EDIT,
        ),
        kbd.Cancel(
            text.Const("⬅️ На главную"),
            id="back_main_from_mailling_menu",
        ),
        on_process_result=process_result_add_new_mailing,
        state=MaillingDialog.start
    ),
    Window(
        text.Const("Выберите категорию пользователей для рассылки."),
        kbd.Select(
            text.Format("{item[0]}"),
            id="s_name_mailing",
            item_id_getter=operator.itemgetter(1),
            items="mailings",
            on_click=on_click_name_mailing
        ),
        kbd.Cancel(
            text.Const("⬅️ На главную"),
            id="back_main_from_mailling_menu",
        ),
        getter=get_data_mailings,
        state=MaillingDialog.user
    )
)