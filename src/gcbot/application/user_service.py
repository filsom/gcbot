from datetime import datetime
from decimal import Decimal as D
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.config import Config

from gcbot.application import commands as cmd
from gcbot.domain.model.day_menu import adjust_recipes, present_the_menu
from gcbot.domain.model.history_message import HistoryMessage, make_history_message_with_norma_day, make_history_with_day_menu
from gcbot.domain.model.norma_day import InputData, calculate_daily_norm
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.message_storage import MessageStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.recipe_storage import RecipeStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_storage import UserStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.workout_storage import WorkoutStorage


class UserService:
    def __init__(
        self, 
        config: Config,
        connection: AsyncConnection,
        user_storage: UserStorage,
        recipe_storage: RecipeStorage,
        workout_storage: WorkoutStorage,
        message_storage: MessageStorage
    ) -> None:
        self.config = config
        self.connection = connection
        self.user_storage = user_storage
        self.recipe_storage = recipe_storage
        self.workout_storage = workout_storage
        self.message_storage = message_storage

    async def add_workout_to_favorites(self, user_id: int, workout_id: UUID) -> None:
        async with self.connection.begin():
            
            await self.workout_storage \
                .put_like(user_id, workout_id)
            await self.connection.commit()

    async def delete_workout_from_favorites(self, user_id: int, workout_id: UUID) -> None:
        async with self.connection.begin():
            await self.workout_storage \
                .delete_liked(user_id, workout_id)
            await self.connection.commit()

    async def make_day_menu(self, command: cmd.MakeMenuCommand) -> dict:
        async with self.connection.begin():
            recipes = await self.recipe_storage \
                .load_list_with_ids(command.recipes_ids)
            adjusted_recipes = adjust_recipes(
                command.norma_kcal,
                recipes
            )
            presentation = present_the_menu(
                command.norma_kcal,
                adjusted_recipes,
                command.is_my_snack
            )
            message = make_history_with_day_menu(
                self.config.get("ADMIN_ID"),
                command.user_id,
                adjusted_recipes,
                presentation.get("snack_kcal", None),
                self.config.get("RECIPE_URL")
            )
            await self.message_storage.add_message(message)
            await self.connection.commit()
            return presentation

    async def create_user(self, user_id: int, email: str):
        async with self.connection.begin():
            await self.user_storage.add_user(user_id, email)
            await self.connection.commit()

    async def calculate_norma(self, command: cmd.CalculateKсalCommand) -> dict:
        async with self.connection.begin():
            input_data = InputData(
                command.age,
                command.height,
                command.weight,
                command.coefficient,
                command.target_procent
            )
            norma_day = calculate_daily_norm(input_data)
            await self.user_storage \
                .update_user_with_id(
                    {"norma_kcal": norma_day.kcal}, 
                    command.user_id
                )
            message = make_history_message_with_norma_day(
                self.config.get("ADMIN_ID"),
                command.user_id,
                norma_day,
                input_data
            )
            await self.message_storage.add_message(message)
            await self.connection.commit()
            return norma_day.asdict()

    async def input_norma(self, user_id: int, norma_kcal: D):
        async with self.connection.begin():
            await self.user_storage \
                .update_user_with_id({"norma_kcal": norma_kcal}, user_id)
            await self.connection.commit()

    async def add_history_message(
        self, 
        sender_id: int, 
        recipient_id: int,
        text: str, 
        message_id: int | None = None
    ):
        message = HistoryMessage(
            sender_id,
            recipient_id,
            text,
            datetime.now(),
            message_id
        )
        await self.message_storage.add_message(message)
        await self.connection.commit()