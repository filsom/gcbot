import asyncio

from email_validator import validate_email, EmailNotValidError
from aiogram import F, Bot, types as t
from aiogram.fsm.state import State
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window, BaseDialogManager
from aiogram_dialog.widgets import kbd, text, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.application.user_service import UserService
from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import AnonStartingDialog
from gcbot.port.adapter.aiogram_resources.query_services.user_query_service import UserQueryService


async def send_last_workout(
    user_id: int,
    state: State,
    bg: BaseDialogManager,
    bot: Bot,
    last_workout: dict
):
    await asyncio.sleep(4)
    caption = None
    if len(last_workout["text"]) < 1024:
        caption = last_workout["text"]
    builder = MediaGroupBuilder(caption=caption)
    print(last_workout)
    for media in last_workout["media"]:
        builder.add_video(media)
    if builder.caption is not None:
        await bot.send_media_group(user_id, media=builder.build())
    else:
        await bot.send_media_group(user_id, media=builder.build())
        await bot.send_message(user_id, last_workout["text"])
    await asyncio.sleep(4)
    await bg.start(
        state,
        show_mode=ShowMode.DELETE_AND_SEND,
        mode=StartMode.RESET_STACK
    )

async def get_input_email_address(dialog_manager: DialogManager, **kwargs):
    return {"email": dialog_manager.dialog_data.get("email", None)}


async def input_email_address_handler(
    message: t.Message,
    button,
    dialog_manager: DialogManager,
    value,
    **kwargs
):  
    try:
        email_info = validate_email(value)
        dialog_manager.dialog_data["email"] = email_info.normalized.lower()
        await dialog_manager.next()
    except EmailNotValidError:
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await message.answer("Некорректный @email адрес ❌")


@inject
async def on_click_confirm_email_address(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    query_service: FromDishka[UserQueryService]
):
    await user_service.create_user(
        callback.from_user.id,
        dialog_manager.dialog_data["email"]
    )
    query_result = await query_service \
        .query_confirm_email_address(callback.from_user.id)
    workout = query_result.get("workout")
    if workout is not None:
        bot: Bot = dialog_manager.middleware_data["bot"]
        bg_manager = dialog_manager.bg(user_id=callback.from_user.id)
        asyncio.create_task(
            send_last_workout(
                callback.from_user.id,
                query_result["dialog_state"],
                bg_manager,
                bot,
                workout
            )
        )
        await dialog_manager.next()
    else:
        await dialog_manager.start(
            query_result["dialog_state"],
            mode=StartMode.RESET_STACK,
            show_mode=ShowMode.EDIT
        )
    

anon_starting_dialog = Dialog(
    Window(
        text.Const("Здравствуйте. Пожалуйста, введите Ваш @email 👇🏻"),
        input.TextInput(id="input_email_address", on_success=input_email_address_handler),
        state=AnonStartingDialog.start,
    ),
    Window(
        text.Format("Подтвeрдите введенный @email - {email}"),
        kbd.Button(
            text.Const("Подтвeрдить"),
            id="confirm_email_address",
            on_click=on_click_confirm_email_address
        ),
        state=AnonStartingDialog.confirm_email,
        getter=get_input_email_address
    ),
    Window(
        text.Format(
            "Приветсвую 👋🏻\n\nВаш @email - {email}\n"
            "Активирована бесплатная подписка.\n\nВам будут приходить новые тренировки в этот чат, когда Мила их будет записывать ❤️\n\nВот самая свежая 👇🏻",
            when=F["email"]
        ),
        getter=get_input_email_address,
        state=AnonStartingDialog.inputed_email
    )
)