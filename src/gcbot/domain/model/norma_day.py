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
    
    def asmessage(self) -> str:
        return f"Бoт расчитал:\n{self.repr()}"
    

@dataclass
class InputData:
    age: D
    height: D
    weight: D
    coefficient: D
    target_procent: D

    def asmessage(self) -> str:
        return (
            f"Пользователь ввел:\n"
            f"Возраст - {self.age} лет\n"
            f"Рост - {self.height} см\n"
            f"Вес - {self.weight} кг\n"
            f"Aктивность - {self.coefficient}\n"
            f"Цель - {self.target_procent}\n"
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