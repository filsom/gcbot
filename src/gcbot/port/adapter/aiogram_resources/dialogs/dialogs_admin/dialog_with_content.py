from aiogram import types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets import text, kbd
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.application.admin_service import AdminService
from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import ContentDialog


@inject
async def on_click_unload_from_google_sheet(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[AdminService],
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await service.unload_from_google_sheet()
    callback.message.answer("Рецепты успешно выгружены ✅")


content_dialog = Dialog(
    Window(
        text.Const("Управление контентом бота ⭐️"),
        kbd.Column(
            # kbd.Button(
            #     text.Const("Добавить тренировку"),
            #     id="add_training",
            #     on_click=Clicker.on_add_training,
            # ),
            # kbd.Start(
            #     text.Const("Добавить категорию"),
            #     id="add_category",
            #     state=AddCategoryDialog.start,
            #     show_mode=ShowMode.EDIT,
            # ),
            kbd.Button(
                text.Const("Выгрузить с Exele"),
                id="upload",
                on_click=on_click_unload_from_google_sheet,
            ),
            kbd.Cancel(
                text.Const("⬅️ В Админ панель"),
                id="back_main_from_content",
            ),
        ),
        state=ContentDialog.start
    )
)