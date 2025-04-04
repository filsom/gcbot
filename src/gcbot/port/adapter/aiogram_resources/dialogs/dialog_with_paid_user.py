from aiogram import F, types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets import text, kbd
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.domain.model.group import Group
from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import PaidStartingDialog
from gcbot.port.adapter.aiogram_resources.query_services.user_query_service import UserQueryService


async def get_button_status(dialog_manager: DialogManager, **kwargs):         
    return {
        "button_workout": dialog_manager.dialog_data["button_workout"],
        "button_food": dialog_manager.dialog_data["button_food"]
    }


async def on_click_section(
    user_id: int,
    group_id: int,
    dialog_manager: DialogManager,
    query_service: UserQueryService
):
    query_result = await query_service \
        .query_user_section(user_id, group_id)
    if query_result.get("dialog_state", None) is not None:
        await dialog_manager.start(
            query_result.get("dialog_state"),
            show_mode=ShowMode.EDIT,
        )
    else:
        dialog_manager.dialog_data.update(
            query_result["button_status"]
        )
        await dialog_manager.next()


@inject
async def on_сlick_workout_section(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    query_service: FromDishka[UserQueryService]
):
    await on_click_section(
        callback.from_user.id,
        Group.WORKOUT,
        dialog_manager,
        query_service
    )


@inject
async def on_сlick_food_section(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    query_service: FromDishka[UserQueryService]
):
    await on_click_section(
        callback.from_user.id,
        Group.FOOD,
        dialog_manager,
        query_service
    )
        

paid_starting_dialog = Dialog(
    Window(
        text.Const("Что будем делать? 👇🏻"),
        kbd.Column(
            kbd.Button(
                text.Const("Тренироваться"),
                id="workout",
                on_click=on_сlick_workout_section,
            ),
            kbd.Button(
                text.Const("Кушать"),
                id="food",
                on_click=on_сlick_food_section,
            ),
        ),
        state=PaidStartingDialog.start
    ),
    Window(
        text.Format("Вам недоступен этот раздел.\nВыберите другой 👇🏻"),
        kbd.Column(
            kbd.Button(
                text.Const("Тренироваться"), 
                id="workout_section", 
                when=F["button_workout"],
                on_click=on_сlick_workout_section
            ),
            kbd.Button(
                text.Const("Кушать"), 
                id="food_section", 
                when=F["button_food"],
                on_click=on_сlick_food_section,
            ),
            kbd.Back(
                text.Const("⬅️ На главную"), 
                id="back_main"
            ),
        ),
        state=PaidStartingDialog.not_access,
        getter=get_button_status
    ),
)