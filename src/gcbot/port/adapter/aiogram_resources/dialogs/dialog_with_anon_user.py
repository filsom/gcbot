import asyncio

from aiogram import F, Bot, types as t
from aiogram.fsm.state import State
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window, BaseDialogManager
from aiogram_dialog.widgets import kbd, text, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.application.user_service import UserService
from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import AnonStartingDialog
from gcbot.port.adapter.aiogram_resources.dialogs.widgets import get_input_email_address, input_email_address_handler
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


@inject
async def on_click_confirm_email_address(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    user_service: FromDishka[UserService],
    query_service: FromDishka[UserQueryService]
):
    try:
        await user_service.create_user(
            callback.from_user.id,
            dialog_manager.dialog_data["email"]
        )
    except ValueError:
        await callback.message.answer("Некорректный @email адресс ❌")
        await dialog_manager.back(
            show_mode=ShowMode.DELETE_AND_SEND
        )
    else:
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
            parsed_data = await query_service \
                .parse_user_data_for_admin(query_result)
            forward_data = await query_service.make_preview_text(
                parsed_data,
                callback.from_user.id,
                dialog_manager.dialog_data["email"]
            )
            builder = InlineKeyboardBuilder()
            if forward_data.get("profile", False):
                builder.button(text="Профиль", callback_data="user_profile_from_admin")
            forward_message = await bot.send_message(
                user_service.config.get("ADMIN_ID"),
                forward_data["previw_text"],
                reply_markup=builder.as_markup()
            )
            await user_service.add_history_message(
                callback.from_user.id,
                user_service.config.get("ADMIN_ID"),
                dialog_manager.dialog_data["email"],
                forward_message.message_id
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