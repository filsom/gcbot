import operator

from aiogram import F, types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets import text, input, kbd
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.application.admin_service import AdminService
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.dialog_state import (
    AddUserInGroupDialog, 
    UsersGroupsDialog
)
from gcbot.port.adapter.aiogram_resources.dialogs.widgets import (
    BackAdminPanel, 
    get_input_email_address,
    input_email_address_handler, 
)
from gcbot.port.adapter.aiogram_resources.query_services.user_query_service import UserQueryService


@inject
async def get_user_data_for_admin(
    dialog_manager: DialogManager,
    query_service: FromDishka[UserQueryService],
    **kwargs
):  
    try:
        query_result = await query_service \
            .query_user_for_admin_with_email(
                dialog_manager.dialog_data["email"]
            )
    except KeyError:
        query_result = await query_service \
            .query_user_for_admin_with_id(
                dialog_manager.start_data["user_id"]
            )
    dialog_manager.dialog_data.update(**query_result)
    return query_result


async def get_user_groups(
    dialog_manager: DialogManager,
    **kwargs
):
    return {"groups": dialog_manager.start_data["groups"]}


async def on_click_add_user_in_groups(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):  
    await dialog_manager.start(
        state=AddUserInGroupDialog.start,
        data={
            "current_email": dialog_manager.dialog_data["current_email"],
            "groups": dialog_manager.dialog_data["select_groups"],
        },
        show_mode=ShowMode.EDIT,
    )


@inject
async def on_click_selected_group(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    item_id,
    service: FromDishka[AdminService]
):  
    await service.add_user_in_group(
        dialog_manager.start_data["current_email"],
        int(item_id)
    )
    await dialog_manager.done()


@inject
async def on_click_save_changed_email_address(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[AdminService]
):
    await service.change_user_email(
        dialog_manager.dialog_data["current_email"],
        dialog_manager.find("input_user_new_email_address").get_value()
    )
    if dialog_manager.start_data is not None:
        if dialog_manager.start_data.get("open_from_message", False):
            await dialog_manager.switch_to(UsersGroupsDialog.profile)
    else:
        await dialog_manager.done(show_mode=ShowMode.DELETE_AND_SEND)


async def get_open_status(dialog_manager: DialogManager, **kwargs):
    if dialog_manager.start_data is not None:
        return {"open_from_message": dialog_manager.start_data.get("open_from_message", False)}
    return {}


@inject
async def on_click_close_profile_from_message(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    await dialog_manager.done()
    await callback.message.delete()


users_groups_dialog = Dialog(
    Window(
        text.Const("Введите @email пользователя 🔎"),
        input.TextInput(
            id="input_user_email_address",
            on_success=input_email_address_handler
        ),
        BackAdminPanel(),
        state=UsersGroupsDialog.start,
    ),
    Window(
        text.Const("Пользователь не найден!", when=~F["user_id"]),
        text.Format(
            "👤 id {user_id}\n"
            "📧 @email: {current_email}\n"
            "👥 GC группы: {alias_groups}\n",
            when=F["user_id"]
        ),
        kbd.Url(
            text.Const("История сообщений"),
            text.Format("{url}"),
            id="history_message",
            when=F["url"]
        ),
        kbd.Button(
            text.Const("Добавить в группу"),
            id="add_user_in_group",
            on_click=on_click_add_user_in_groups,
            when=F["select_groups"]
        ),
        kbd.Button(
            text.Const("Изменить @email"),
            id="change_user_email_address",
            on_click=kbd.Next(),
            when=F["user_id"]
        ),
        kbd.Button(
            text.Const("Закрыть"), 
            id="close_and_delete", 
            when=F["open_from_message"], 
            on_click=on_click_close_profile_from_message
        ),
        BackAdminPanel("open_from_message"),
        state=UsersGroupsDialog.profile,
        getter=[get_user_data_for_admin]
    ),
    Window(
        text.Const("Введите новый @email пользователя 🔎"),
        input.TextInput(
            id="input_user_new_email_address",
            on_success=input_email_address_handler
        ),
        kbd.Button(
            text.Const("Закрыть"), 
            id="close_and_delete", 
            when=F["open_from_message"], 
            on_click=on_click_close_profile_from_message
        ),
        BackAdminPanel("open_from_message"),
        state=UsersGroupsDialog.inpute_email
    ),
    Window(
        text.Format("Проверьте правильность ввода @email - {email}"),
        kbd.Button(
            text.Const("Сохранить изменения"),
            id="save_change_email",
            on_click=on_click_save_changed_email_address
        ),
        kbd.Back(text.Const("Ввести заново")),
        state=UsersGroupsDialog.change_email,
        getter=get_input_email_address
    ),
    getter=get_open_status
)


add_user_group_dialog = Dialog(
    Window(
        text.Const("Выберите группу для открытия доступа"),
        kbd.Column(
            kbd.Select(
                text.Format("{item[0]}"),
                id="user_groups",
                item_id_getter=operator.itemgetter(1),
                items="groups",
                on_click=on_click_selected_group,
            ),
        ),
        BackAdminPanel(),
        state=AddUserInGroupDialog.start,
        getter=get_user_groups
    )
)