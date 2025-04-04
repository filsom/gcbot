from dataclasses import asdict, dataclass
from decimal import Decimal as D


@dataclass
class Macros:
    protein: D
    fat: D
    carbs: D

    def repr(self) -> str:
        return (
            f"Белки - {self.protein}\n"
            f"Жиры - {self.fat}\n"
            f"Углеводы - {self.carbs}"
        )
    

@dataclass
class NormaDay:
    kcal: D
    macros: Macros

    def repr(self) -> str:
        return f"Ккал - {self.kcal}\n{self.macros.repr()}"

    def asdict(self) -> dict:
        norma_day = {}
        norma_day.setdefault("norma_day", {})
        norma_day["norma_day"].update({"kcal": str(self.kcal)})
        macros = asdict(self.macros)
        for key in macros.keys():
            norma_day["norma_day"].update({key: str(macros[key])})
        return norma_day
    

def calculate_daily_norm(
    age: D,
    height: D,
    weight: D,
    coefficient: D,
    target_procent: D
) -> NormaDay:
    value = (D("10")*weight \
            + D("6.25")*height \
            - D("5")*age-D("161")) \
            * coefficient
    norma_kcal = abs(value*target_procent).quantize(D("1"))
    if norma_kcal < 1200:
        norma_kcal = D("1200")
    protein = (D("1.5")*weight).quantize(D("1"))
    fat = weight.quantize(D("1"))
    carbs = abs((norma_kcal-D("100")
            - (fat*D("9"))
            - (protein*D("4")))
            / D("4")).quantize(D("1"))
    return NormaDay(
        norma_kcal,
        Macros(protein, fat, carbs)
    )