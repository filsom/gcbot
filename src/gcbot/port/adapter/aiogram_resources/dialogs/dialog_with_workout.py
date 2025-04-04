import operator
from uuid import UUID

from aiogram import F, Bot, types as t
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets import text, kbd
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from gcbot.application.user_service import UserService
from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import WorkoutDialog
from gcbot.port.adapter.aiogram_resources.dialogs.widgets import BackMain
from gcbot.port.adapter.aiogram_resources.query_services.workout_query_service import WorkoutQueryService


async def on_сlick_view_favorites_workouts(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data["from_favorites"] = True
    await dialog_manager.next()


async def on_click_category_name(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    item_id,
):
    dialog_manager.dialog_data["category_id"] = item_id
    await dialog_manager.next()


async def on_click_back_section(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    dialog_manager.dialog_data["from_favorites"] = False


@inject
async def on_click_like_training(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[UserService], 
):
    bot: Bot = dialog_manager.middleware_data["bot"]
    await service.add_workout_to_favorites(
        callback.from_user.id,
        UUID(dialog_manager.dialog_data["workout_id"])
    )
    await bot.send_message(
        callback.from_user.id,
        dialog_manager.dialog_data["text"]
    )
    dialog_manager.dialog_data.pop("text")
    dialog_manager.dialog_data["added_fovarites"] = True
    dialog_manager.dialog_data["list_messages"].clear()

@inject
async def on_click_delete_like_training(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
    service: FromDishka[UserService], 
):
    await service.delete_workout_from_favorites(
        callback.from_user.id,
        UUID(dialog_manager.dialog_data["workout_id"])
    )
    bot: Bot = dialog_manager.middleware_data["bot"]
    await bot.delete_messages(
        callback.from_user.id,
        dialog_manager.dialog_data.pop("list_messages")
    )


async def on_click_delete_history(
    callback: t.CallbackQuery,
    button,
    dialog_manager: DialogManager,
):
    if dialog_manager.dialog_data.get("list_messages"):
        bot: Bot = dialog_manager.middleware_data["bot"]
        await bot.delete_messages(
            callback.from_user.id,
            dialog_manager.dialog_data.pop("list_messages")
        )


@inject
async def get_categories_names(
    dialog_manager: DialogManager, 
    query_service: FromDishka[WorkoutQueryService], 
    **kwargs
):
    return await query_service \
        .query_categories_names(
            dialog_manager.start_data["user_id"],
            dialog_manager.dialog_data.get("from_favorites", False)
        )


@inject
async def get_workout(
    dialog_manager: DialogManager,
    query_service: FromDishka[WorkoutQueryService],
    **kwargs
):
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    query_result = await query_service \
        .query_workout(
            dialog_manager.start_data["user_id"],
            dialog_manager.dialog_data["category_id"],
            dialog_manager.dialog_data.get("from_favorites", False)
        )
    bot: Bot = dialog_manager.middleware_data["bot"]
    if not query_result.get("is_empty", False):
        if dialog_manager.dialog_data.get("added_fovarites", False):
            query_result["text"] = "Тренировка добавлена в избранное ❤️"
            dialog_manager.dialog_data.pop("added_fovarites")
            query_result["button_like"] = False 
            return query_result
        builder = MediaGroupBuilder()
        for file_id in query_result["media"]:
            builder.add_video(file_id)
        dialog_manager.dialog_data["workout_id"] = query_result["workout_id"]
        messages = await bot.send_media_group(
            dialog_manager.start_data["user_id"],
            media=builder.build()
        )
        list_messages = []
        for message in messages:
            list_messages.append(message.message_id)
        dialog_manager.dialog_data["list_messages"] = list_messages
        dialog_manager.dialog_data["text"] = query_result["text"]
        return query_result
    else:
        if dialog_manager.dialog_data.get("added_fovarites", False):
            query_result["text"] = "Тренировка добавлена в избранное ❤️"
            dialog_manager.dialog_data.pop("added_fovarites")
            query_result["button_like"] = False
        return query_result


workout_dialog = Dialog(
    Window(
        text.Const("Выберите раздел 👇🏻"),
        kbd.Button(
            text.Const("Случайная тренировка 🔎"),
            id="search_workout",
            on_click=kbd.Next()
        ),
        kbd.Button(
            text.Const("Из избраного ❤️"),
            id="search_like_workout",
            on_click=on_сlick_view_favorites_workouts
        ),
        BackMain(),
        state=WorkoutDialog.start
    ),
    Window(
        text.Multi(
            text.Const("Выберите категорию 👇🏻", when=~F["text"]),
            text.Format("{text}", when=F["text"])
        ),
        kbd.Column(
            kbd.Select(
                id="selected_categories",
                text=text.Format("{item[0]}"),
                items="categories",
                item_id_getter=operator.itemgetter(1),
                on_click=on_click_category_name
            ),
        ),
        kbd.Back(
            text.Const("⬅️ К разделам"),
            id="back_section_workout",
            on_click=on_click_back_section
        ),
        state=WorkoutDialog.categories,
        getter=get_categories_names
    ),
    Window(
        text.Format("{text}"),
        kbd.Column(
            kbd.Button(
                text.Const("Другая тренировка 🔄"), 
                id="replace",
                on_click=on_click_delete_history,
                when=~F["is_empty"]
            ),
            kbd.Button(
                text.Const("Добавить в избранное ❤️"), 
                id="like",
                when=F["button_like"],
                on_click=on_click_like_training,
            ),
            kbd.Button(
                text.Const("Удалить"), 
                id="delete",
                when=F["button_delete"],
                on_click=on_click_delete_like_training,
            ),
            kbd.Back(
                text.Const("⬅️ К категориям"),
                on_click=on_click_delete_history
            )
        ),
        state=WorkoutDialog.view,
        getter=get_workout
    )
)