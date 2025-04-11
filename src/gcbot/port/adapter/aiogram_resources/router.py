import asyncio
from aiogram import F, Bot, Router, types as t
from aiogram import filters as f
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, ShowMode, StartMode
from dishka.integrations.aiogram import FromDishka, inject
from starlette.config import Config
from gcbot.application.user_service import UserService
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.dialog_state import UsersGroupsDialog
from gcbot.port.adapter.aiogram_resources.query_services.user_query_service import UserQueryService
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.message_storage import MessageStorage


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
        show_mode=ShowMode.DELETE_AND_SEND
    )


async def _send_expiring_notification(message: t.Message):
    notify_message = await message.answer("Сообщение отправлено ✅")
    await message.delete()
    await asyncio.sleep(2.0)
    await notify_message.delete()

# 
class HistoryMessageFilter(f.Filter):
    @inject
    async def __call__(
        self, 
        message: t.Message, 
        config: FromDishka[Config]
    ) -> bool:
        if message.text is None:
            return False
        if message.text.startswith("/"):
            return False
        entities = message.entities or message.caption_entities
        if entities is not None:
            if entities[-1].type == "email":
                list_words = message.text.split(" ")
                if len(list_words) == 1:
                    return False
                
        if message.from_user.id == int(config.get("ADMIN_ID")) or message.from_user.id == 987956844:
            return False
        try:
            int(message.text)
            return False
        except ValueError:
            return True
        
# 
class HistoryMessageAnswer(f.Filter):
    @inject
    async def __call__(self, message: t.Message, config: FromDishka[Config]):
        if message.from_user.id == int(config.get("ADMIN_ID")) or message.from_user.id == 987956844:
            if message.reply_to_message is None:
                return False
            elif F.reply_to_message:
                return True
        return False    
        


@starting_router.message(HistoryMessageAnswer())
@inject
async def reply_to_user(
    message: t.Message, 
    service: FromDishka[UserService], 
    storage: FromDishka[MessageStorage]
):
    recipient_id = await storage \
        .get_recipient_id_by_message_id(
            message.reply_to_message.message_id
        )
    await service.add_history_message(
        service.config.get("ADMIN_ID"),
        recipient_id,
        message.text,
        message.message_id
    )
    await message.copy_to(recipient_id)
    # await message.reply_to_message.delete()
    # await message.delete()


@starting_router.message(HistoryMessageFilter())
@inject
async def handle_any_message(
    message: t.Message,
    bot: Bot,
    service: FromDishka[UserService],
    query_service: FromDishka[UserQueryService]
):
    data = await query_service \
        .query_forwarding_data(
            message.from_user.id,
            message.text
        )
    builder = InlineKeyboardBuilder()
    if data.get("profile", False):
        builder.button(text="Профиль", callback_data="user_profile_from_admin")
    admin_message = await bot.send_message(
        service.config.get("ADMIN_ID"),
        data["previw_text"],
        reply_markup=builder.as_markup()
    )
    await service.add_history_message(
        message.from_user.id,
        service.config.get("ADMIN_ID"),
        message.text,
        admin_message.message_id
    )
    # asyncio.create_task(_send_expiring_notification(message))


@starting_router.callback_query(F.data == "user_profile_from_admin")
@inject
async def callback_user_profile(
    callback: t.CallbackQuery, 
    dialog_manager: DialogManager,
    storage: FromDishka[MessageStorage]
):
    recipient_id = await storage \
        .get_recipient_id_by_message_id(
            callback.message.message_id
        )
    await callback.answer("Открыт профиль")
    await dialog_manager.start(
        UsersGroupsDialog.profile,
        show_mode=ShowMode.SEND,
        data={
            "user_id": recipient_id,
            "open_from_message": True,
            "message_id": callback.message.message_id
        }
    )