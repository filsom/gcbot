from aiogram import types as t
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets import text, kbd, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.application.admin_service import AdminService
from gcbot.domain.model.content import Media
from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import ContentDialog
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.dialog_state import AddVoiceDialog


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
            kbd.Start(
                text.Const("Установить Voice"),
                id="set_voice_message",
                state=AddVoiceDialog.start
            ),
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


@inject
async def voice_handler(
    message: t.Message,
    message_input,
    dialog_manager: DialogManager,
    service: FromDishka[AdminService]
):
    await service.set_support_voice(
        Media(
            message.video_note.file_id,
            message.video_note.file_unique_id,
            message.message_id,
            ContentType.VIDEO_NOTE
        )
    )
    await message.answer(f"Успешно добавлено ✅")
    await dialog_manager.done(
        show_mode=ShowMode.DELETE_AND_SEND
    )


set_voice_dialog = Dialog(
    Window(
        text.Const("Загрузите видеосообщение"),
        input.MessageInput(
            voice_handler,
            content_types=ContentType.VIDEO_NOTE
        ),
        state=AddVoiceDialog.start
    )
)