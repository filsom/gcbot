from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal as D

from gcbot.domain.model.day_menu import Recipe
from gcbot.domain.model.norma_day import InputData, NormaDay


@dataclass
class HistoryMessage:
    sender_id: int
    recipient_id: int
    text: str
    sent_to: datetime


def make_history_message_with_norma_day(
    sender_id: int,
    recipient_id: int,
    norma_day: NormaDay,
    input_data: InputData,
) -> HistoryMessage:
    text = "{}\n{}".format(
        input_data.asmessage(),
        norma_day.asmessage()
    )
    return HistoryMessage(
        sender_id,
        recipient_id,
        text,
        datetime.now()
    )


def make_history_with_day_menu(
    sender_id: int,
    recipient_id: int,
    adjusted_recipes: list[Recipe],
    kcal_snack: D | None,
    url: str
) -> HistoryMessage:
    message = ""
    for recipe in adjusted_recipes:
        text = f"{recipe.asmessage()}\n" \
            .format(url.format(recipe.index_table))
        message += text
    if kcal_snack is not None:
        message += f"\nПользователю необходимо добрать - {kcal_snack}ККал"
    history_message = HistoryMessage(
        sender_id,
        recipient_id,
        message,
        datetime.now()
    )
    return history_message