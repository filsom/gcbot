from decimal import Decimal

from aiogram import F, Bot, types as t
from aiogram.enums import ContentType
from aiogram_dialog import Dialog, DialogManager, ShowMode, StartMode, Window
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets import text, kbd
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.application import commands as cmd
from gcbot.application.user_service import UserService
from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import DayMenuDialog, PaidStartingDialog
from gcbot.port.adapter.aiogram_resources.query_services.user_query_service import UserQueryService


def BackMain():
    return kbd.Button(
        text.Const("⬅️ На главную"),
        id="back_main_from_day_menu",
        on_click=on_click_back_main
    )


async def get_missing_quantity_kcal(
    dialog_manager: DialogManager,
    **kwargs
):
    return {"kcal": dialog_manager.dialog_data.get("snack_kcal")}


@inject
async def get_recipe(
    dialog_manager: DialogManager,
    query_service: FromDishka[UserQueryService],
    **kwargs
):
    query_result = await query_service \
        .query_recipe_with_type_meal(
            dialog_manager.start_data["type_meal"][0]
        )
    dialog_manager.dialog_data["temporal_recipes"] = query_result
    return {
        **query_result, 
        "photo": MediaAttachment(
            ContentType.PHOTO, 
            file_id=MediaId(query_result["file_id"])
        )
    }


@inject
async def on_click_select_recipe(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[UserService]
):
    dialog_manager.start_data["type_meal"].pop(0)
    like_recipe = dialog_manager.dialog_data["temporal_recipes"]
    bot: Bot = dialog_manager.middleware_data["bot"]
    message_photo = await bot.send_photo(callback.from_user.id, like_recipe["file_id"])
    message = await bot.send_message(callback.from_user.id, like_recipe["view_text"])
    dialog_manager.start_data["dirty_photos"].append(message_photo.message_id)
    dialog_manager.start_data["recipes"].update({
        like_recipe["recipe_id"]: message.message_id,
    })
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    if not dialog_manager.start_data["type_meal"]:
        list_recipes_ids = []
        for recipe_id in dialog_manager.start_data["recipes"]:
            list_recipes_ids.append(int(recipe_id))
        day_menu = await service.make_day_menu(
            cmd.MakeMenuCommand(
                list_recipes_ids,
                Decimal(dialog_manager.start_data["norma_kcal"]),
                False
            )
        )
        for recipe_id in day_menu:
            message_id = dialog_manager.start_data["recipes"].get(recipe_id)
            if message_id is not None:
                await bot.edit_message_text(
                    day_menu[recipe_id],
                    chat_id=callback.from_user.id,
                    message_id=message_id
                )
        dialog_manager.start_data["dirty_photos"].clear()
        dialog_manager.start_data["recipes"].clear()
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.next()


@inject
async def on_click_my_snack(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[UserService]
):
    dialog_manager.start_data["type_meal"].clear()
    bot: Bot = dialog_manager.middleware_data["bot"]
    list_recipes_ids = []
    for recipe_id in dialog_manager.start_data["recipes"]:
        list_recipes_ids.append(int(recipe_id))
    
    day_menu = await service.make_day_menu(
        cmd.MakeMenuCommand(
            list_recipes_ids,
            Decimal(dialog_manager.start_data["norma_kcal"]),
            True
        )
    )
    for recipe_id in day_menu:
        message_id = dialog_manager.start_data["recipes"].get(recipe_id)
        if message_id is not None:
            await bot.edit_message_text(
                day_menu[recipe_id],
                chat_id=callback.from_user.id,
                message_id=message_id
            )
    dialog_manager.start_data["dirty_photos"].clear()
    dialog_manager.dialog_data["snack_kcal"] = day_menu["snack_kcal"]
    dialog_manager.start_data["recipes"].clear()
    await dialog_manager.next()


async def on_click_back_main(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    if dialog_manager.start_data["recipes"]:
        bot: Bot = dialog_manager.middleware_data["bot"]
        list_delete_messages = []
        for message_id in dialog_manager.start_data["recipes"].values():
            if message_id is not None:
                list_delete_messages.append(message_id)
        list_delete_messages.extend(dialog_manager.start_data["dirty_photos"])
        await bot.delete_messages(callback.from_user.id, list_delete_messages)
    await dialog_manager.start(
        PaidStartingDialog.start,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT
    )


day_menu_dialog = Dialog(
    Window(
        DynamicMedia("photo"),
        text.Format(
            "{view_text}\n"
            "Выберите все блюда на день, и я напишу рецепты\n"
            "Нравится этот {type_meal} или прислать другой?"
        ),
        kbd.Button(
            text.Format("Этот {type_meal}"),
            id="selected_meal",
            on_click=on_click_select_recipe
        ),
        kbd.Button(
            text.Format("Другой {type_meal}"),
            id="next_meal",
        ),
        kbd.Button(
            text.Format("Cвой {type_meal}"),
            id="my_snack",
            on_click=on_click_my_snack,
            when=F["is_snack"]
        ),
        BackMain(),
        state=DayMenuDialog.start,
        getter=get_recipe
    ),
    Window(
        text.Multi(
            text.Format(
                "Готовые рецепты с количеством ингредиентов выше 👆\n"
                "Вам нужно добавить любой перекус, чтобы постараться добрать.\n\n"
                "Калорий - {kcal}",
                when=F["kcal"]
            ),
            text.Const(
                "Готовые рецепты с количеством ингредиентов выше 👆",
                when=~F["kcal"]
            ),
        ),
        BackMain(),
        state=DayMenuDialog.view,
        getter=get_missing_quantity_kcal
    ),
)