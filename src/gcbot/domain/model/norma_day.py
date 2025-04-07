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
    
    def to_html(self) -> str:
        return (
            f"<p><b>Бот посчитал:</b></p>"
            f"<p><b>Ккал</b> - {self.kcal}</p>"
            f"<p><b>Белки</b> - {self.macros.protein}</p>"
            f"<p><b>Жиры</b> - {self.macros.fat}</p>"
            f"<p><b>Углеводы</b> - {self.macros.carbs}</p>"
        )
    

@dataclass
class InputData:
    age: D
    height: D
    weight: D
    coefficient: D
    target_procent: D

    def to_html(self) -> str:
        return (
            f"<p><b>Пользователь ввел:</b></p>"
            f"<p><b>Возраст</b> - {self.age} лет</p>"
            f"<p><b>Рост</b> - {self.height} см</p>"
            f"<p><b>Вес</b> - {self.weight} кг</p>"
            f"<p><b>Aктивность кф.</b> - {abs(self.coefficient)}</p>"
            f"<p><b>Цель кф.</b> - {abs(self.target_procent)}</p>"
        )


def calculate_daily_norm(input_data: InputData) -> NormaDay:
    value = (D("10")*input_data.weight \
            + D("6.25")*input_data.height \
            - D("5")*input_data.age-D("161")) \
            * input_data.coefficient
    norma_kcal = abs(value*input_data.target_procent).quantize(D("1"))
    if norma_kcal < 1200:
        norma_kcal = D("1200")
    protein = (D("1.5")*input_data.weight).quantize(D("1"))
    fat = input_data.weight.quantize(D("1"))
    carbs = abs((norma_kcal-D("100")
            - (fat*D("9"))
            - (protein*D("4")))
            / D("4")).quantize(D("1"))
    return NormaDay(
        norma_kcal,
        Macros(protein, fat, carbs)
    )