import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from gcbot.domain.model.day_menu import Ingredient, Recipe
from gcbot.port.adapter.sqlalchemy_resources.tables import (
    recipes_table,
    ingredients_table
)


class RecipeStorage:
    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def load_list_with_ids(self, recipes_ids: list) -> list:
        stmt = (
            sa.select(
                recipes_table.c.recipe_id,
                recipes_table.c.name,
                recipes_table.c.text,
                recipes_table.c.file_id,
                recipes_table.c.amount_kcal,
                recipes_table.c.type_meal,
                ingredients_table.c.name.label("ingredient_name"),
                ingredients_table.c.value,
                ingredients_table.c.unit
            )
            .join(
                ingredients_table,
                ingredients_table.c.recipe_id == recipes_table.c.recipe_id,
            )
            .where(recipes_table.c.recipe_id.in_(recipes_ids))
        )
        rows = (await self.connection.execute(stmt)).mappings().all()
        recipes_dict = {}
        for row in rows:
            recipe_id = row['recipe_id']
            if recipe_id not in recipes_dict:
                recipes_dict[recipe_id] = {
                    'recipe': Recipe(
                        recipe_id=row['recipe_id'],
                        name=row['name'],
                        text=row['text'],
                        file_id=row['file_id'],
                        amount_kcal=row['amount_kcal'],
                        type_meal=row['type_meal'],
                        ingredients=[]
                    ),
                    'ingredients': []
                }
            if row['ingredient_name']:
                recipes_dict[recipe_id]['ingredients'].append(
                    Ingredient(
                        name=row['ingredient_name'],
                        value=row['value'],
                        unit=row['unit']
                    )
                )
        recipes = []
        for recipe_data in recipes_dict.values():
            recipe = recipe_data['recipe']
            recipe.ingredients = recipe_data['ingredients']
            recipes.append(recipe)

        return recipes

    async def add_all(self, recipes: list[Recipe]) -> None:
        data_recipes = []
        data_ingredients = []
        for recipe in recipes:
            data_recipes.append({
                "recipe_id": recipe.recipe_id,
                "name": recipe.name,
                "text": recipe.text,
                "file_id": recipe.file_id,
                "amount_kcal": recipe.amount_kcal,
                "type_meal": recipe.type_meal
            })
            for ingredient in recipe.ingredients:
                data_ingredients.append({
                    "recipe_id": recipe.recipe_id,
                    "name": ingredient.name,
                    "value": ingredient.value,
                    "unit": ingredient.unit
                })
        insert_recipes_stmt = (
            sa.insert(recipes_table)
            .values(data_recipes)
        )
        insert_ingredients_stmt = (
            sa.insert(ingredients_table)
            .values(data_ingredients)
        )
        await self.connection.execute(insert_recipes_stmt)
        await self.connection.execute(insert_ingredients_stmt)
        
    async def count(self) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(recipes_table)
        )
        result = (await self.connection.execute(stmt)).scalar()
        if result is None:
            return 0
        return result