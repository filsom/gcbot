from aiogram import F, Bot, types as t
from aiogram_dialog import DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import text, kbd, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from email_validator import validate_email, EmailNotValidError

from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import PaidStartingDialog
from gcbot.port.adapter.aiogram_resources.query_services.user_query_service import UserQueryService


async def input_email_address_handler(
    message: t.Message,
    button,
    dialog_manager: DialogManager,
    value,
    **kwargs
):  
    try:
        await message.delete()
        dialog_manager.show_mode = ShowMode.EDIT
        email_info = validate_email(value)
        dialog_manager.dialog_data["email"] = email_info.normalized.lower()
        await dialog_manager.next()
    except EmailNotValidError:
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await message.answer("Некорректный @email адрес ❌")


async def get_input_email_address(dialog_manager: DialogManager, **kwargs):
    return {"email": dialog_manager.dialog_data.get("email", None)}


@inject
async def on_click_day_meny(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    query_service: FromDishka[UserQueryService]
):
    query_result = await query_service \
        .query_day_menu(callback.from_user.id)
    await dialog_manager.start(
        query_result["dialog_state"],
        data=query_result["data"],
        show_mode=ShowMode.DELETE_AND_SEND
    )


async def on_click_back_main(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    await dialog_manager.start(
        PaidStartingDialog.start,
        data={"user_id": callback.from_user.id},
        show_mode=ShowMode.EDIT,
        mode=StartMode.RESET_STACK
    )


def BackAdminPanel(when_key=None):
    if when_key is not None:
        when_key = ~F[when_key]
    return kbd.Cancel(
        text.Const("⬅️ В Админ панель"),
        id="back_admin_panel",
        when=when_key
    )


def BackMain():
    return kbd.Button(
        text.Const("⬅️ На главную"), 
        id="back_main", 
        on_click=on_click_back_main
    )


def NormaDayTextInput(id: str) -> input.TextInput:
    return input.TextInput(
        id,
        on_success=kbd.Next(),
        on_error=on_error_inpute_value,
        type_factory=int
    )


async def on_error_inpute_value(
    message: t.Message,
    dialog_,
    dialog_manager: DialogManager,
    error_: ValueError
):
    await message.answer("Некорректный ввод, значение должно быть целым числом ❌")


def DailyNormResultWindow(state, getter) -> Window:
    return Window(
        text.Format(
            "Итак, необходимо ежедневно:\n\n"
            "ККал - <b>{kcal}</b>\n"
            "Белки - <b>{protein}</b>\n"
            "Жиры - <b>{fat}</b>\n"
            "Углеводы - <b>{carbs}</b>\n\n"
            "Дальше я буду подбирать вам рецепты ежедневно, чтобы уложиться в эти цифры."
            "Вы также можете ввести свои КБЖУ в первом разделе питания, "
            "если хотите, и я буду подбирать рецепты под них."
        ),
        kbd.Button(
            text.Const("Меню на день"),
            id="day_menu",
            on_click=on_click_day_meny
        ),
        BackMain(),
        state=state,
        getter=getter
    )