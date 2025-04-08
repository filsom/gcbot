import asyncio
from functools import partial
from uuid import UUID

from aiogram import Bot
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncConnection

from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.mailing import RecipientMailing, StatusMailing
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.mailing_storage import MailingStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_storage import UserStorage


async def bot_send_message(bot, user_id, media, text, kbd):
    await bot.send_media_group(user_id, media)
    await bot.send_message(user_id, text, reply_markup=kbd)


async def send_mailing_message(
    users_ids: list[int],
    mailing_id: UUID,
    mailing_media: list[dict],
    mailing_text: str,
    kbd,
    bot: Bot,
    engine: AsyncEngine,
    admin_id
):
    builder = MediaGroupBuilder()
    content_type = mailing_media[0][1]
    for media in mailing_media:
        builder.add(
            type=content_type,
            media=media[0]
        )
    media_messages = builder.build()
    if not users_ids:
        async with engine.connect() as connection:
            gateway = MailingStorage(connection)
            await gateway.update_status_mailing(mailing_id, StatusMailing.DONE)
            await connection.commit()
        return
    tasks = []
    total_users = len(users_ids)
    processed_users = 0
    for user_id in users_ids:
        tasks.append(
            bot_send_message(
                bot,
                user_id,
                media_messages,
                mailing_text,
                kbd
            )
        )
    message = f"Прогресс: 0% ({processed_users}/{total_users})"
    message_a = await bot.send_message(admin_id, message)
    while tasks:
        slice_tasks = tasks[:7]
        current_batch = len(slice_tasks)
        processed_users += current_batch
        progress = (processed_users / total_users) * 100        
        message = f"Прогресс: {progress:.0f}% ({processed_users}/{total_users})"
        await asyncio.gather(*slice_tasks, return_exceptions=True)
        del tasks[:7]
        await message_a.edit_text(message)
        if tasks:
            await asyncio.sleep(1)
        
    async with engine.connect() as connection:
        gateway = MailingStorage(connection)
        await gateway.update_status_mailing(
            mailing_id, 
            StatusMailing.DONE
        )
        await connection.commit()
    await message_a.edit_text("Рассылка выполнена ✅")
    await asyncio.sleep(2)
    await message_a.delete()



class TelegramMailingService:
    def __init__(
        self, 
        connection: AsyncConnection,
        user_storage: UserStorage,
        mailing_storage: MailingStorage
    ):
        self.connection = connection
        self.user_storage = user_storage
        self.mailing_storage = mailing_storage

    async def create_task_mailing(self, mailing_id: UUID):
        active_mailing = await self.mailing_storage \
            .count_with_status(StatusMailing.PROCESS)
        if active_mailing:
            await self.connection.rollback()
            raise ValueError
        
        mailing = await self.mailing_storage \
            .query_mailing_with_id(mailing_id)
        if int(mailing["type_recipient"]) in [
            RecipientMailing.FREE, RecipientMailing.TRAINING
        ]:
            is_exists = False
        else:
            is_exists = True
        recipiens_ids = await self.user_storage \
            .all_user_id(is_exists=is_exists)
        
        kbd = None
        if mailing["type_recipient"] == RecipientMailing.TRAINING:
            builder = InlineKeyboardBuilder()
            builder.button(text="Все тренировки", callback_data="from_mailing")
            kbd = builder.as_markup(resize_keyboard=True)
        task = partial(
            send_mailing_message, 
            users_ids=recipiens_ids, 
            mailing_id=mailing_id,
            mailing_media=mailing["media"], 
            mailing_text=mailing["text"],
            kbd=kbd
        )
        await self.mailing_storage.update_status_mailing(
            mailing_id, StatusMailing.PROCESS
        )
        await self.connection.commit()
        return task
        
    async def update_name_mailing(self, mailing_id: UUID, name: str) -> None:
        async with self.connection.begin():
            await self.mailing_storage.update_name(name, mailing_id)
            await self.connection.commit()

    async def delete_mailing(self, mailing_id: UUID) -> None:
        async with self.connection.begin():
            await self.mailing_storage.delete(mailing_id)
            await self.connection.commit()


    async def add_planed_mailing(
        self,
        mailing_id: UUID,
        name_mailing: str,
        text_mailing: str,
        medias: list[dict[str, str]],
        type_recipient: int,
        status: str
    ):
        async with self.connection.begin():
            await self.mailing_storage.add_new_mailing(
                mailing_id,
                name_mailing,
                text_mailing,
                medias,
                type_recipient,
                status
            )
            await self.connection.commit()