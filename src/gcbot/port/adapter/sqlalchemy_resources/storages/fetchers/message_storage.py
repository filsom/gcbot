import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from gcbot.domain.model.history import HistoryMessage


class MessageStorage:
    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def add_message(self, message: HistoryMessage) -> None:
        pass