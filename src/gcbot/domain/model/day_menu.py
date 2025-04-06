from __future__ import annotations
import re
from dataclasses import dataclass
from decimal import Decimal as D


class TypeMeal(object):
    BREAKFAST = 1
    LUNCH = 2
    DINNER = 3
    SNACK= 4


@dataclass
class Ingredient:
    name: str
    value: D
    unit: str


@dataclass
class Recipe:
    recipe_id: int
    name: str
    text: str
    file_id: str
    amount_kcal: D
    type_meal: TypeMeal
    ingredients: list[Ingredient]

    def adjust(self, meal_kcal: D) -> Recipe:        
        scale = meal_kcal/self.amount_kcal
        adjusted_ingredients = []
        for ingredient in self.ingredients:
            adjusted_amount = round(ingredient.value * scale)
            adjusted_amount = str(adjusted_amount)
            value = D(adjusted_amount).quantize(D("1"))
            if value == 0:
                value = D("1")
            adjusted_ingredients.append(
                Ingredient(
                    ingredient.name, 
                    value, 
                    ingredient.unit
                )
            )
        return Recipe(
            self.recipe_id, 
            self.name,
            self.text,
            self.file_id,
            meal_kcal, 
            self.type_meal,
            adjusted_ingredients
        )

    def partial_repr(self) -> str:
        TRANSlATION_MAP = {
            TypeMeal.BREAKFAST: "Завтрак",
            TypeMeal.LUNCH: "Обед",
            TypeMeal.DINNER: "Ужин",
            TypeMeal.SNACK: "Перекус"
        }
        text = ""
        for ingredient in self.ingredients:
            text += f"- {ingredient.name.title()} <b>{ingredient.value}{ingredient.unit}</b>\n"
        return (
            f"<b>Прием пищи:</b> {TRANSlATION_MAP.get(self.type_meal)}\n"
            f"<b>Название рецепта:</b> {self.name.title()}\n\n"
            f"<b>Ингредиенты:</b>:\n{text}\n"
        )
    
    def full_repr(self) -> str:
        return f"{self.partial_repr()}{self.text}"
    
    def asmessage(self) -> str:
        return (
            "<b>Ссылка:</b> {}\n"
            f"{self.partial_repr()}"
        )
    
    @property
    def index_table(self) -> str:
        return f"{self.recipe_id+1}:{self.recipe_id+1}"
    

def present_the_menu(
    user_norma_kcal: D, 
    adjusted_recipes: list[Recipe], 
    is_snack: bool
) -> dict:
    sum_kcal = D("0")
    menu = {}
    for recipe in adjusted_recipes:
        sum_kcal += recipe.amount_kcal
        menu.update({recipe.recipe_id: recipe.full_repr()})
    snack_kcal = None
    if is_snack:
        snack_kcal = str((user_norma_kcal-sum_kcal).quantize(D("1")))
    menu.update({"snack_kcal": snack_kcal})
    return menu


def adjust_recipes(
    user_norma_kcal: D, 
    recipes: list[Recipe]
) -> list[Recipe]:
    RATIO_MAP = {
        TypeMeal.BREAKFAST: D("0.3"),
        TypeMeal.LUNCH: D("0.3"),
        TypeMeal.SNACK: D("0.15"),
        TypeMeal.DINNER: D("0.25")
    }
    adjusted_recipes = []
    for recipe in recipes:
        difference = user_norma_kcal*(1-RATIO_MAP.get(recipe.type_meal))
        meal_kcal = user_norma_kcal - difference
        adjusted_recipe = recipe.adjust(meal_kcal)
        adjusted_recipes.append(adjusted_recipe)
    return adjusted_recipes
    

def parse_recipe(data: dict[str, str]):
    TYPE_MAP = {
        "завтрак": TypeMeal.BREAKFAST,
        "обед": TypeMeal.LUNCH,
        "ужин": TypeMeal.DINNER,
        "перекус": TypeMeal.SNACK
    }
    return Recipe(
        data["id"],
        data["name"].strip()[0].title(),
        data["recipe"].strip(),
        data["photo"],
        data["kkal"],
        TYPE_MAP.get(data["type"].lower()),
        normalize_ingredients(data["ingred"])
    )


def normalize_ingredients(text: str) -> Ingredient:
    normal_ingredients = []
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        result = parse_ingredient(line)
        ingredient = Ingredient(
            result["name"],
            result["value"],
            result["unit"]
        )
        normal_ingredients.append(ingredient)
    return normal_ingredients


def parse_ingredient(text: str):
    text = text.replace('\n', ' ').strip()
    pattern = r'^(\d+)_([^_\s]*)\s*(.*)$'
    match = re.match(pattern, text)
    
    if not match:
        return {
            'value': None,
            'unit': 'г',
            'name': text,
            'error': 'Некорректный формат, установлены значения по умолчанию'
        }
    
    quantity = int(match.group(1))
    raw_unit = match.group(2).strip()
    raw_name = match.group(3).strip()
    
    unit = raw_unit.lower().replace('.', '') if raw_unit else 'г'
    UNIT_MAP = {
        'гр': 'г',
        'грамм': 'г',
        'гм': 'г',
        'ml': 'мл',
        'миллилитр': 'мл',
        'л': 'л',
        'литр': 'л',
        'шт': 'шт',
        'штука': 'шт',
        'ст': 'ст',
        'стакан': 'ст',
        'чайнл': 'ч.л',
        'столл': 'ст.л',
        'чл': 'ч.л',
        'сл': 'ст.л'
    }
    unit = UNIT_MAP.get(unit, unit)
    
    name = re.sub(r'\.+$', '', raw_name).strip()
    name = name if name else 'Не указано название'
    
    return {
        'value': quantity,
        'unit': unit,
        'name': name.title()
    }