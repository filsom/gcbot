from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.mailing import StatusMailing
from gcbot.port.adapter.sqlalchemy_resources.tables import EntityType, mailing_table, medias_table


class MailingStorage:
    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def update_name(self, name: str, mailing_id: UUID) -> None:
        stmt = (
            sa.update(mailing_table)
            .values(name=name)
            .where(mailing_table.c.mailing_id == mailing_id)
        )
        await self.connection.execute(stmt)

    async def count_with_status(self, status) -> int:
        stmt = (
            sa.select(sa.func.count())
            .select_from(mailing_table)
            .where(mailing_table.c.status == status)
        )
        result = await self.connection.execute(stmt)
        count = result.scalar()
        if count is None:
            return 0
        else:
            return count
    
    async def update_status_mailing(
        self, 
        mailing_id: UUID, 
        new_status: StatusMailing
    ) -> None:
        stmt = (
            sa.update(mailing_table)
            .values(status=new_status)
            .where(mailing_table.c.mailing_id == mailing_id)
        )
        await self.connection.execute(stmt)

    async def delete(self, mailing_id: UUID) -> None:
        stmt = (
            sa.delete(mailing_table)
            .where(mailing_table.c.mailing_id == mailing_id)
        )
        await self.connection.execute(stmt)

    async def add_new_mailing(
        self,
        mailing_id: UUID,
        name_mailing: str,
        text_mailing: str,
        medias: list[dict[str, str]],
        type_recipient: int,
        status: str
    ):
        insert_mailing = (
            sa.insert(mailing_table)
            .values(
                mailing_id=mailing_id,
                text=text_mailing,
                name=name_mailing,
                type_recipient=type_recipient,
                status=status
            )
        )
        for media in medias:
            media.update({
                "media_id": uuid4(),
                "entity_id": mailing_id,
                "entity_type": EntityType.MAILING
            })
        await self.connection.execute(insert_mailing)
        insert_medias = (
            sa.insert(medias_table)
            .values(medias)
        )
        await self.connection.execute(insert_medias)

    async def query_mailing_with_id(self, mailing_id: UUID) -> dict:
        mailing_stmt = (
            sa.select(
                mailing_table.c.text,
                mailing_table.c.type_recipient.label("type_recipient")
            )
            .where(mailing_table.c.mailing_id == mailing_id)
        )
        media_stmt = (
            sa.select(
                medias_table.c.file_id,
                medias_table.c.content_type
            )
            .where(medias_table.c.entity_id == mailing_id)
        )
        mailing_rows = await self.connection.execute(mailing_stmt)
        media_rows = await self.connection.execute(media_stmt)
        list_media = []
        for media in media_rows:
            list_media.append((media[0], media[1]))
        for row in mailing_rows:
            text = row.text
            type_recipient = row.type_recipient
        return {
            "text": text,
            "type_recipient": type_recipient,
            "media": list_media
        }
    
    async def query_mailings_name(self) -> dict:
        stmt = (
            sa.select(
                mailing_table.c.name,
                mailing_table.c.mailing_id
            )
            .where(mailing_table.c.status == StatusMailing.AWAIT)
        )
        rows = await self.connection.execute(stmt)
        list_mailings_name = []
        for row in rows:
            list_mailings_name.append(row)
        return {"plan_mailings": list_mailings_name}