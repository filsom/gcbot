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
                sent_to=message.sent_to,
                message_id=message.message_id
            )
        )
        await self.connection.execute(stmt)

    async def get_recipient_id_by_message_id(self, message_id) -> HistoryMessage:
        stmt = (
            sa.select(messages_table.c.sender_id)
            .where(messages_table.c.message_id == message_id)
        )
        row = (await self.connection.execute(stmt)).scalar()
        return row