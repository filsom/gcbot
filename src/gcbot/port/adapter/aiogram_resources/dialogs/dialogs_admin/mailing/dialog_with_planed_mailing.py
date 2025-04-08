import asyncio
import operator

from typing import AsyncGenerator
from aiogram import Bot, types as t
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets import text, kbd
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from sqlalchemy.ext.asyncio import AsyncEngine

from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.dialog_state import PlandeMaillingDialog
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.mailing import StatusMailing
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.mailing_service import TelegramMailingService
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.mailing_storage import MailingStorage


@inject
async def on_click_process_sending(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    storage: FromDishka[MailingStorage], 
):
    await storage.update_status_mailing(
        dialog_manager.dialog_data["mailing_id"],
        StatusMailing.PROCESS
    )


@inject
async def on_click_delete_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[TelegramMailingService], 
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    await service.delete_mailing(
        dialog_manager.dialog_data["mailing_id"]
    )
    await bot.delete_messages(
        callback.from_user.id,
        dialog_manager.dialog_data["preview_plan_mailing"]
    )
    await dialog_manager.done()


@inject
async def on_click_start_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[TelegramMailingService], 
    engine: FromDishka[AsyncEngine]
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    try:
        mailing_task = await service.create_task_mailing(
            dialog_manager.dialog_data["mailing_id"]
        )
        _ = asyncio.create_task(mailing_task(bot=bot, engine=engine, admin_id=callback.from_user.id))
        if dialog_manager.dialog_data.get("preview_plan_mailing", None) is not None:
            await bot.delete_messages(
                callback.from_user.id,
                dialog_manager.dialog_data["preview_plan_mailing"]
            )
        dialog_manager.dialog_data["result_text"] = "Рассылка успещно запущена."
    except ValueError:
            dialog_manager.dialog_data["result_text"] = "Не удалось запустить рассылку, так как есть рассылка в процессе выполнения."
    await dialog_manager.next()


async def get_result_text(
    dialog_manager: DialogManager,
    **kwargs
):
    return {
        "result_text": dialog_manager.dialog_data.get("result_text", None)
    }


async def on_click_cancel_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    if dialog_manager.dialog_data.get("preview_plan_mailing", None) is not None:
        await bot.delete_messages(
            callback.from_user.id,
            dialog_manager.dialog_data["preview_plan_mailing"]
        )


@inject
async def on_click_name_plan_mailing(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    item_id,
    storage: FromDishka[MailingStorage], 
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    bot: Bot = dialog_manager.middleware_data["bot"]
    dialog_manager.dialog_data["mailing_id"] = str(item_id)
    data_mailing = await storage.query_mailing_with_id(item_id)
    dialog_manager.dialog_data["data_mailing"] = data_mailing
    builder = MediaGroupBuilder()
    for media in data_mailing["media"]:
        builder.add(type=media[1], media=media[0])
    media_messages = await bot.send_media_group(
        callback.from_user.id,
        media=builder.build()
    )
    list_delete_media = []
    for media_message in media_messages:
        list_delete_media.append(media_message.message_id)
    message = await bot.send_message(
        callback.from_user.id,
        data_mailing["text"]
    )
    list_delete_media.append(message.message_id)
    dialog_manager.dialog_data["preview_plan_mailing"] = list_delete_media
    await dialog_manager.next() 


@inject
async def get_name_mailings(
    dialog_manager: DialogManager,
    storage: FromDishka[MailingStorage], 
    **kwargs
):
    return await storage.query_mailings_name()


planed_mailling_dialog = Dialog(
    Window(
        text.Const("Выберите запланированную рассылку 👇🏻"),
        kbd.Column(kbd.Select(
            text.Format("{item[0]}"),
            id="s_planed_mailling",
            item_id_getter=operator.itemgetter(1),
            items="plan_mailings",
            on_click=on_click_name_plan_mailing
        )),
        kbd.Cancel(
            text.Const("⬅️ В Админ панель"),
            id="to_main_from_planed_mailling",
        ),
        getter=get_name_mailings,
        state=PlandeMaillingDialog.start
    ),
    Window(
        text.Const("Сообщение для рассылки 👆🏻"),
        kbd.Row(
            kbd.Button(
                text.Const("Удалить"),
                id="process_delete",
                on_click=on_click_delete_mailing
            ),
            kbd.Button(
                text.Const("Запустить 🔔"),
                id="process_sending",
                on_click=on_click_start_mailing
            ),
        ),
        kbd.Cancel(
            text.Const("⬅️ В Админ панель"),
            id="to_main_from_planed_mailling_1",
            on_click=on_click_cancel_mailing
        ),
        getter=get_name_mailings,
        state=PlandeMaillingDialog.menu
    ),
    Window(
        text.Format("{result_text}"),
        kbd.Cancel(
            text.Const("⬅️ В Админ панель"),
            id="to_main_from_planed_mailling_1",
            on_click=on_click_cancel_mailing
        ),
        getter=get_result_text,
        state=PlandeMaillingDialog.end
    )  
)