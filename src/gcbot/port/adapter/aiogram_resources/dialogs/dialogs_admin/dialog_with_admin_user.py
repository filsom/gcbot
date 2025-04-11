from aiogram import Bot, types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets import text, kbd, input
from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import (
    AdminStartingDialog, 
    ContentDialog,
    PaidStartingDialog
)
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.dialog_state import UsersGroupsDialog
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.dialog_state import MaillingDialog


async def photo_handler(
    message: t.Message,
    message_input,
    dialog_manager: DialogManager,
):
    last_id = dialog_manager.current_stack().last_message_id
    bot: Bot = dialog_manager.middleware_data["bot"]
    await bot.delete_message(message.from_user.id, last_id)
    await message.delete()
    await message.answer(message.photo[-1].file_id)


admin_starting_dialog = Dialog(
    Window(
        text.Format("Приветсвую, 👋🏻\n\nПанель администратора."),
        input.MessageInput(photo_handler, content_types="photo"),
        kbd.Column(
            kbd.Start(
                text.Const("Юзеры/Группы"),
                id="users_groups",
                state=UsersGroupsDialog.start,
                show_mode=ShowMode.EDIT,
            ),
            kbd.Start(
                text.Const("Контент"),
                id="content",
                state=ContentDialog.start,
                show_mode=ShowMode.EDIT,
            ),
            kbd.Start(
                text.Const("Рассылка"),
                id="mailling",
                state=MaillingDialog.start,
                show_mode=ShowMode.EDIT,
                # data={}
            ),
            kbd.Start(
                text.Const("Разделы"),
                id="razdels",
                state=PaidStartingDialog.start,
                show_mode=ShowMode.EDIT,
            ),
        ),
        state=AdminStartingDialog.start,
    )
)