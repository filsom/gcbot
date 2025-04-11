import asyncio
from uuid import uuid4
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from sqlalchemy.ext.asyncio import AsyncEngine
from aiogram import F, Bot, types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import text, kbd, input

from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import AdminStartingDialog
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.dialog_state import SendMailingDialog
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.mailing import StatusMailing
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.mailing_service import TelegramMailingService
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.mailing_storage import MailingStorage


@inject
async def on_click_send_now_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    storage: FromDishka[MailingStorage],
    service: FromDishka[TelegramMailingService],
    engine: FromDishka[AsyncEngine]
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    bot: Bot = dialog_manager.middleware_data["bot"]
    mailing_id = uuid4()
    if isinstance(dialog_manager.start_data["inpute_text_media"], list):
        text = dialog_manager.start_data["inpute_text_media"][0]
    else:
        text = dialog_manager.start_data["inpute_text_media"]
    await storage.add_new_mailing(
        mailing_id,
        None,
        text,
        dialog_manager.start_data["media"],
        int(dialog_manager.start_data["type_recipient"]),
        StatusMailing.AWAIT
    )
    try:
        task_mailing = await service.create_task_mailing(mailing_id)
        asyncio.create_task(task_mailing(bot=bot, engine=engine, admin_id=callback.from_user.id))
        await dialog_manager.start(
            AdminStartingDialog.start,
            show_mode=ShowMode.DELETE_AND_SEND,
        )
    except ValueError:
        dialog_manager.show_mode = ShowMode.EDIT
        dialog_manager.dialog_data["mailing_id"] = str(mailing_id)
        dialog_manager.dialog_data["mailing_is_processed"] = True


@inject
async def input_name_mailing_handler(
    message: t.Message, 
    source, 
    dialog_manager: DialogManager, 
    _,
    service: FromDishka[TelegramMailingService],
    storage: FromDishka[MailingStorage]
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    message_id = dialog_manager.current_stack().last_message_id
    await bot.delete_message(message.from_user.id, message_id)
    await message.delete()
    list_file_ids = []
    for media in dialog_manager.start_data["media"]:
        list_file_ids.append(media["file_id"])
    if dialog_manager.dialog_data.get("mailing_is_processed", None) is True:
        await service.update_name_mailing(
            dialog_manager.dialog_data["mailing_id"],
            message.text.lower()
        )
    else:
        if isinstance(dialog_manager.start_data["inpute_text_media"], list):
            text = dialog_manager.start_data["inpute_text_media"][0]
        else:
            text = dialog_manager.start_data["inpute_text_media"]
        await service.add_planed_mailing(
            uuid4(),
            message.text.lower(),
            text,
            dialog_manager.start_data["media"],
            int(dialog_manager.start_data["type_recipient"]),
            StatusMailing.AWAIT
        )
    await dialog_manager.next()


async def get_processed_mailing(
    dialog_manager: DialogManager,
    **kwrags
):
    return {"mailing_is_processed": dialog_manager.dialog_data.get("mailing_is_processed", None)}


send_mailings_dialog = Dialog(
    Window(
        text.Multi(
            text.Const("Когда запустить рассылку? 🕑", when=~F["mailing_is_processed"]),
            text.Const("Есть запущенная рассылка, запланируйте эту.", when=F["mailing_is_processed"]),
        ),
        kbd.Row(
            kbd.Button(
                text.Const("Сейчас"),
                id="now_mailing",
                on_click=on_click_send_now_mailing,
                when=~F["mailing_is_processed"]
            ),
            kbd.Button(
                text.Const("Запланировать"),
                id="plan_mailing",
                on_click=kbd.Next()
            ),
        ),
        kbd.Start(
            text.Const("⬅️ В Админ панель"),
            id="back_main_from_mailing",
            state=AdminStartingDialog.start,
            mode=StartMode.RESET_STACK
        ),
        getter=get_processed_mailing,
        state=SendMailingDialog.start
    ),
    Window(
        text.Const("Введите название рассылки (128 символов)."),
        input.TextInput(id="input_name_mailing", on_success=input_name_mailing_handler),
        state=SendMailingDialog.text
    ),
    Window(
        text.Const("Рассылка запланирована ✅"),
        kbd.Start(
            text.Const("⬅️ В Админ панель"),
            id="back_main_from_mailing",
            state=AdminStartingDialog.start,
            mode=StartMode.RESET_STACK
        ),
        state=SendMailingDialog.plan_end
    )
)