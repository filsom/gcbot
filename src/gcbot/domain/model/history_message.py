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
    message_id: int | None = None

    def text_for_preview_forward(self, username: str | None) -> str:
        text = (
            f"👤 id {self.sender_id}\n"
            "{}\n"
            f"Сообщение:\n{self.text}"
        )
        if username is not None:
            text.format(f"@{username}")
        else:
            text.format("@username скрыт")
        return text


def make_history_message_with_norma_day(
    sender_id: int,
    recipient_id: int,
    norma_day: NormaDay,
    input_data: InputData,
) -> HistoryMessage:
    text = "{}\n{}".format(
        input_data.to_html(),
        norma_day.to_html()
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
    text = "\n".join(recipe.to_html(url) for recipe in adjusted_recipes)
    if kcal_snack is not None:
        text += (
            f"<p><b>Пользователю необходимо добрать -</b> {kcal_snack} ККал</p>"
        )
    history_message = HistoryMessage(
        sender_id,
        recipient_id,
        text,
        datetime.now()
    )
    return history_message