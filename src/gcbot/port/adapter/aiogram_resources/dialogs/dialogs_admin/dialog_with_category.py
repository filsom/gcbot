import operator
from uuid import UUID
from aiogram import types as t
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets import kbd, text, input
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.application.admin_service import AdminService
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.dialog_state import AddCategoryDialog, CategoryDialog, DeleteCategoryDialog
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.workout_json_fetcher import WorkoutJsonFetcher


async def inpute_name_category_handler(
    message: t.Message,
    widget,
    dialog_manager: DialogManager,
    _
):
    await message.delete()
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    dialog_manager.dialog_data["category_name"] = message.text
    await dialog_manager.next()


@inject
async def on_add_new_сategory(
    callback: t.CallbackQuery,
    button: kbd.Select,
    dialog_manager: DialogManager,
    service: FromDishka[AdminService],
):
    await service.add_new_category(dialog_manager.dialog_data["category_name"])
    await dialog_manager.done()


async def get_input_categoty_name(
    dialog_manager: DialogManager,
    **kwargs,
):
    return {"category_name": dialog_manager.dialog_data["category_name"]}


add_new_category_dialog = Dialog(
    Window(
        text.Const("Введите название категории"),
        input.TextInput(id="add_new_cat_1", on_success=inpute_name_category_handler),
        kbd.Cancel(text.Const("⬅️ В Админ панель"), id="to_main_2"),
        state=AddCategoryDialog.start
    ),
    Window(
        text.Format("Подвтеридте создание новой категории - {category_name}"),
        kbd.Button(text.Const("Подтвредить ✅"), id="confirmed_name", on_click=on_add_new_сategory),
        kbd.Back(text.Const("Изменить название"), id="to_input"),
        kbd.Cancel(text.Const("⬅️ В Админ панель"), id="to_main_3"),
        getter=get_input_categoty_name,
        state=AddCategoryDialog.confirm
    )
)


@inject
async def on_click_category_name_for_delete(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    item_id,
    service: FromDishka[AdminService]
):
    await service.delete_category(UUID(item_id))


@inject
async def get_all_categories_names(
    dialog_manager: DialogManager, 
    query_service: FromDishka[WorkoutJsonFetcher], 
    **kwargs
):
    return await query_service.fetch_all_categories_names()
    

delete_category_dialog = Dialog(
    Window(
        text.Const("Нажмите на название категории, чтобы удалить ее 👇🏻"),
        kbd.Group(
            kbd.Select(
                id="selected_categories",
                text=text.Format("{item[0]}"),
                items="categories",
                item_id_getter=operator.itemgetter(1),
                on_click=on_click_category_name_for_delete
            ),
            width=2,
        ),
        kbd.Cancel(text.Const("⬅️ В Админ панель"), id="to_main"),
        state=DeleteCategoryDialog.start,
        getter=get_all_categories_names
    )
)


category_dialog = Dialog(
    Window(
        text.Const("Выберите действие 👇🏻"),
        kbd.Start(
            text.Const("Удалить"),
            id="delete_category",
            state=DeleteCategoryDialog.start
        ),
        kbd.Start(
            text.Const("Добавить"),
            id="add_category",
            state=AddCategoryDialog.start
        ),
        kbd.Cancel(text.Const("⬅️ В Админ панель"), id="to_main"),
        state=CategoryDialog.start
    )
)