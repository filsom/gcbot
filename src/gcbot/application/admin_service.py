from enum import StrEnum, auto
from functools import partial
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection
from gspread import Worksheet
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gcbot.domain.model.content import Media
from gcbot.domain.model.day_menu import parse_recipe
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.recipe_storage import RecipeStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_storage import UserStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.workout_storage import WorkoutStorage
from gcbot.port.adapter.sqlalchemy_resources.tables import medias_table
    

class AdminService:
    def __init__(
        self, 
        connection: AsyncConnection,
        worksheet: Worksheet,
        user_storage: UserStorage,
        recipe_storage: RecipeStorage,
        workout_storage: WorkoutStorage
    ):
        self.connection = connection
        self.worksheet = worksheet
        self.user_storage = user_storage
        self.recipe_storage = recipe_storage
        self.workout_storage = workout_storage

    async def add_user_in_group(self, email: str, group_id: int) -> None:
        async with self.connection.begin():
            await self.user_storage.insert_user_in_group(email, group_id)
            await self.connection.commit()

    async def delete_user_from_group(self, email: str, group_id: int) -> None:
        async with self.connection.begin():
            await self.user_storage.delete_user_from_group(email, group_id)
            await self.connection.commit()

    async def change_user_email(self, old_email: int, new_email: str) -> None:
        async with self.connection.begin():
            await self.user_storage \
                .update_user_with_email({"email": new_email}, old_email)
            await self.user_storage \
                .update_email_in_groups({"email": new_email}, old_email)
            await self.connection.commit()

    async def unload_from_google_sheet(self) -> None:
        async with self.connection.begin():
            head = await self.recipe_storage.count()
            records = self.worksheet.get_all_records()[head:]
            if records:
                unload_recipes = []
                for record in records:
                    recipe = parse_recipe(record)
                    unload_recipes.append(recipe)
                await self.recipe_storage.add_all(unload_recipes)
            await self.connection.commit()

    async def set_support_voice(self, voice: Media) -> None:
        async with self.connection.begin():
            inset_stmt = (
                sa.insert(medias_table)
                .values(
                    media_id=uuid4(),
                    entity_id=uuid4(),
                    entity_type="support",
                    file_id=voice.file_id,
                    file_unique_id=voice.file_unique_id,
                    message_id=voice.message_id,
                    content_type=voice.content_type
                )
            )
            await self.connection.execute(inset_stmt)
            await self.connection.commit()

    async def add_new_workout(self, category_id: UUID, text: str, medias: list) -> None:
        async with self.connection.begin():
            await self.workout_storage \
                .add_workout(category_id, text, medias)
            await self.connection.commit()

    async def add_new_category(self, name: str):
        async with self.connection.begin():
            await self.workout_storage.add_category(name)
            await self.connection.commit()

    # async def create_task_mailing(self, mailing_id: UUID):
    #     async with self.session.begin():
    #         active_mailing = await self.gateway \
    #             .count_with_status(StatusMailing.PROCESS)
    #         if active_mailing:
    #             await self.session.rollback()
    #             raise ValueError
            
    #         mailing = await self.gateway \
    #             .query_mailing_with_id(mailing_id)
    #         if mailing["type_recipient"] in [
    #             RecipientMailing.FREE, RecipientMailing.TRAINING
    #         ]:
    #             is_exists = False
    #         else:
    #             is_exists = True
    #         recipiens_ids = await self.gateway \
    #             .query_all_user_id_with_role(is_exists=is_exists)
            
    #         kbd = None
    #         if mailing["type_recipient"] == RecipientMailing.TRAINING:
    #             builder = InlineKeyboardBuilder()
    #             builder.button(text="Все тренировки", callback_data="from_mailing")
    #             kbd = builder.as_markup(resize_keyboard=True)
    #         task = partial(
    #             send_mailing_message, 
    #             users_ids=recipiens_ids, 
    #             mailing_id=mailing_id,
    #             mailing_media=mailing["media"], 
    #             mailing_text=mailing["text"],
    #             kbd=kbd
    #         )
    #         await self.gateway.update_status_mailing(
    #             mailing_id, StatusMailing.PROCESS
    #         )
    #         await self.session.commit()
    #         return task