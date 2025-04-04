from aiogram import F, Router, types as t
from aiogram import filters as f
from aiogram_dialog import DialogManager, ShowMode, StartMode
from dishka.integrations.aiogram import FromDishka, inject

from gcbot.port.adapter.aiogram_resources.query_services.user_query_service import UserQueryService


starting_router = Router()


@starting_router.message(f.CommandStart())
@inject
async def start(
    message: t.Message, 
    dialog_manager: DialogManager,
    query_service: FromDishka[UserQueryService]
):
    await message.delete()
    state = await query_service \
        .query_command_start(message.from_user.id)
    await dialog_manager.start(
        state,
        mode=StartMode.RESET_STACK,
        show_mode=ShowMode.EDIT
    )