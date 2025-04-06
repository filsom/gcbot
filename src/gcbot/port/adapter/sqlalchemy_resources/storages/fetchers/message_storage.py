import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from gcbot.domain.model.history_message import HistoryMessage
from gcbot.port.adapter.sqlalchemy_resources.tables import messages_table


class MessageStorage:
    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def add_message(self, message: HistoryMessage) -> None:
        stmt = (
            sa.insert(messages_table)
            .values(
                sender_id=message.sender_id,
                recipient_id=message.recipient_id,
                text=message.text,
                sent_to=message.sent_to
            )
        )
        await self.connection.execute(stmt)