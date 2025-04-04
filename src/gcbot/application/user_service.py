from decimal import Decimal as D

from sqlalchemy.ext.asyncio import AsyncConnection

from gcbot.application import commands as cmd
from gcbot.domain.model.day_menu import adjust_recipes, present_the_menu
from gcbot.domain.model.norma_day import calculate_daily_norm
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.recipe_storage import RecipeStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_storage import UserStorage


class UserService:
    def __init__(
        self, 
        connection: AsyncConnection,
        user_storage: UserStorage,
        recipe_storage: RecipeStorage
    ):
        self.connection = connection
        self.user_storage = user_storage
        self.recipe_storage = recipe_storage

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
            return presentation

    async def create_user(self, user_id: int, email: str):
        async with self.connection.begin():
            await self.user_storage.add_user(user_id, email)
            await self.connection.commit()

    async def calculate_norma(self, command: cmd.CalculateKсalCommand) -> dict:
        async with self.connection.begin():
            norma_day = calculate_daily_norm(
                command.age,
                command.height,
                command.weight,
                command.coefficient,
                command.target_procent
            )
            await self.user_storage \
                .update_user(
                    {"norma_kcal": norma_day.kcal}, 
                    command.user_id
                )
            return norma_day.asdict()

    async def input_norma(self, user_id: int, norma_kcal: D):
        async with self.connection.begin():
            await self.user_storage \
                .update_user({"norma_kcal": norma_kcal}, user_id)
            await self.connection.commit()