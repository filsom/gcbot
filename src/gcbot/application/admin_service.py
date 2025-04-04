from sqlalchemy.ext.asyncio import AsyncConnection
from gspread import Worksheet

from gcbot.domain.model.day_menu import parse_recipe
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.recipe_storage import RecipeStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_storage import UserStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.workout_storage import WorkoutStorage


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