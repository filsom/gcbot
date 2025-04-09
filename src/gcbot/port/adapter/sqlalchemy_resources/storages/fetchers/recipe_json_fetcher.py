import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from gcbot.domain.model.day_menu import TypeMeal
from gcbot.port.adapter.sqlalchemy_resources.tables import (
    recipes_table,
    ingredients_table
)


class RecipeJsonFetcher:
    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def fetch_partial_recipe_with_type_meal(self, type_meal: str) -> dict:
        query = (
            sa.select(
                sa.func.json_build_object(
                    "recipe_id", recipes_table.c.recipe_id,
                    "name", recipes_table.c.name,
                    "type_meal", sa.case(
                        (recipes_table.c.type_meal == TypeMeal.BREAKFAST, "завтрак"),
                        (recipes_table.c.type_meal == TypeMeal.LUNCH, "обед"),
                        (recipes_table.c.type_meal == TypeMeal.DINNER, "ужин"),
                        (recipes_table.c.type_meal == TypeMeal.SNACK, "перекус")
                    ),
                    "file_id", recipes_table.c.file_id,
                    "text_ingredients", sa.func.string_agg(
                        sa.func.concat("-", " ", ingredients_table.c.name), "\n"
                    ),
                    "is_snack", sa.case(
                        (recipes_table.c.type_meal == TypeMeal.SNACK, True),
                        else_=False
                    )
                )
            )
            .select_from(recipes_table)
            .join(
                ingredients_table,
                ingredients_table.c.recipe_id == recipes_table.c.recipe_id
            )
            .group_by(recipes_table.c.recipe_id)
            .where(recipes_table.c.type_meal == type_meal)
            .order_by(sa.func.random())
            .limit(1)
        )
        result = (await self.connection.execute(query)).scalar()
        result["view_text"] = (
            f"<b>Название рецепта: </b>{result["name"]}\n"
            f"<b>Прием пищи: </b>{result["type_meal"].title()}\n\n"
            f"<b>Ингредиенты:</b>\n{result["text_ingredients"]}\n"
        )
        return result