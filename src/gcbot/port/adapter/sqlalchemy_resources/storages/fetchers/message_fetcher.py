import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection
from starlette.config import Config
from sqlalchemy.dialects.postgresql import aggregate_order_by

from gcbot.port.adapter.sqlalchemy_resources.tables import messages_table


class MessageJsonFetcher:
    def __init__(
        self, 
        config: Config,
        connection: AsyncConnection
    ) -> None:
        self.config = config
        self.connection = connection

    async def fetch_message_with_user(self, user_id: int) -> dict:
        query = (
            sa.select(
                sa.func.json_agg(
                    aggregate_order_by(
                        sa.func.json_build_object(
                            "user", sa.case(
                                (messages_table.c.sender_id == int(self.config("ADMIN_ID")), "admin"),
                                else_="user"
                            ),
                            "time", sa.func.to_char(messages_table.c.sent_to, 'YYYY-MM-DD"T"HH24:MI:SS'),
                            "text", messages_table.c.text,
                            "sent_to", messages_table.c.sent_to,
                        ),
                        sa.asc(messages_table.c.sent_to)
                    )
                )
            )
            .where(
                sa.or_(
                    sa.and_(
                        messages_table.c.sender_id == int(self.config("ADMIN_ID")),
                        messages_table.c.recipient_id == user_id
                    ),
                    sa.and_(
                        messages_table.c.sender_id == user_id,
                        messages_table.c.recipient_id == int(self.config("ADMIN_ID"))
                    )
                )
            )
        )
        result = (await self.connection.execute(query)).scalar()
        return result