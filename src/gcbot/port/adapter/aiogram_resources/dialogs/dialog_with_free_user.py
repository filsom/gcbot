from aiogram import types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets import kbd, text
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import FreeStartingDialog
from gcbot.port.adapter.aiogram_resources.query_services.user_query_service import UserQueryService


@inject
async def on_click_payment_verification(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    query_service: FromDishka[UserQueryService]
):
    state = await query_service \
        .query_payment_verification(callback.from_user.id)
    if state is None:
        await dialog_manager.next()
    else:
        await dialog_manager.start(
            state,
            show_mode=ShowMode.EDIT,
            mode=StartMode.RESET_STACK
        )


@inject
async def on_click_check_access(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    query_service: FromDishka[UserQueryService]
):
    state = await query_service \
        .query_payment_verification(callback.from_user.id)
    if state is None:
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await callback.message.answer("Вас нету ни в одной группе ❌")
    else:
        await dialog_manager.start(
            state,
            show_mode=ShowMode.EDIT,
            mode=StartMode.RESET_STACK
        )


free_starting_dialog = Dialog(
    Window(
        text.Const(
            "Получите доступ ко всей базе 200+ тренировок\n"
            "и конструктору индивидуального меню,\n"
            "занимайтесь дома в удобное время и питайтесь правильно без подсчета калорий!\n\n"
            "Подробнее по ссылке https://workoutmila.ru/bot_payment"
        ),
        kbd.Column(
            kbd.Button(
                text.Const("Я оплатила"), 
                id="payment_verification", 
                on_click=on_click_payment_verification
            ),
        ),
        state=FreeStartingDialog.start,
    ),
    Window(
        text.Const(
            "Пока не вижу вашу оплату. Обычно данные обновляются в течение часа.\n"
            "Вы можете нажать кнопку ниже чуть позже, чтобы снова проверить подписку.\n"
            "Если доступ не появляется, напишите нам @Workout_mila_bot"
        ),
        kbd.Button(
            text.Const("Проверить доступ"),
            id="check_access",
            on_click=on_click_check_access
        ),
        state=FreeStartingDialog.check_access,
    ),
)
