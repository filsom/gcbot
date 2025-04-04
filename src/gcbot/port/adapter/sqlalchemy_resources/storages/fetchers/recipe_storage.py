from sqlalchemy.ext.asyncio import AsyncConnection

from gcbot.domain.model.day_menu import Recipe


class RecipeStorage:
    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def load_list_with_ids(self, recipes_ids: list) -> list[Recipe]:
        pass

    async def add_all(self, recipes: list[Recipe]) -> None:
        pass

    async def count(self):
        pass