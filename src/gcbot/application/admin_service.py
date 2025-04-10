from enum import StrEnum, auto
from functools import partial
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection
from gspread import Worksheet
from aiogram.utils.keyboard import InlineKeyboardBuilder

from gcbot.domain.model.content import Media
from gcbot.domain.model.day_menu import parse_recipe
from gcbot.domain.model.history_message import HistoryMessage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.message_storage import MessageStorage
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
        workout_storage: WorkoutStorage,
        message_storage: MessageStorage,
    ):
        self.connection = connection
        self.worksheet = worksheet
        self.user_storage = user_storage
        self.recipe_storage = recipe_storage
        self.workout_storage = workout_storage
        self.message_storage = message_storage

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

    async def delete_category(self, category_id: UUID):
        async with self.connection.begin():
            await self.workout_storage.delete_category(category_id)
            await self.connection.commit()


    async def add_history_message(self, message: HistoryMessage):
        async with self.connection.begin():
            await self.message_storage.add_message(message)
            await self.connection.commit()