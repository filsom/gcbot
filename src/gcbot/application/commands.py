from dataclasses import dataclass
from decimal import Decimal as D


@dataclass
class CalculateKсalCommand:
    user_id: D
    age: D
    height: D
    weight: D 
    coefficient: D
    target_procent: D


@dataclass
class MakeMenuCommand:
    user_id: int
    recipes_ids: list[int]
    norma_kcal: D
    is_my_snack: bool