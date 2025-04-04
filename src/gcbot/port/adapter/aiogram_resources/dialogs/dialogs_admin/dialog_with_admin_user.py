from aiogram_dialog import Dialog, ShowMode, Window
from aiogram_dialog.widgets import text, kbd

from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import (
    AdminStartingDialog, 
    ContentDialog
)


admin_starting_dialog = Dialog(
    Window(
        text.Format("Приветсвую, 👋🏻\n\nПанель администратора."),
        kbd.Column(
            # kbd.Start(
            #     text.Const("Юзеры/Группы"),
            #     id="users_groups",
            #     state=UsersGroupsDialog.start,
            #     show_mode=ShowMode.EDIT,
            # ),
            kbd.Start(
                text.Const("Контент"),
                id="content",
                state=ContentDialog.start,
                show_mode=ShowMode.EDIT,
            ),
            # kbd.Start(
            #     text.Const("Рассылка"),
            #     id="mailling",
            #     state=MaillingDialog.start,
            #     show_mode=ShowMode.EDIT,
            #     data={}
            # ),
            # kbd.Start(
            #     text.Const("Разделы"),
            #     id="razdels",
            #     state=PaidStartingDialog.start,
            #     show_mode=ShowMode.EDIT,
            # ),
        ),
        state=AdminStartingDialog.start
    )
)