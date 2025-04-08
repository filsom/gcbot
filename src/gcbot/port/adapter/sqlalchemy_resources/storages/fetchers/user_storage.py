import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.dialects.postgresql import insert
from gcbot.port.adapter.sqlalchemy_resources.tables import users_table, groups_table


class UserStorage:
    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def add_user(self, user_id: int, email: str):
        insert_stmt = (
            insert(users_table)
            .values(
                user_id=user_id,
                email=email
            )
        )
        # insert_stmt = insert_stmt.on_conflict_do_nothing()
        await self.connection.execute(insert_stmt)

    async def with_id_or_email(self, user_id: int, email: str):
        stmt = (
            sa.select(users_table.c.user_id)
            .where(
                sa.or_(
                    users_table.c.user_id == user_id,
                    users_table.c.email == email
                )
            )
        )
        result = (await self.connection.execute(stmt)).scalar()
        return result

    async def insert_user_in_group(self, email: str, group_id: int):
        insert_stmt = (
            sa.insert(groups_table)
            .values(
                email=email,
                group_id=group_id
            )
        )
        await self.connection.execute(insert_stmt)

    async def delete_user_from_group(self, email: str, group_id: int):
        delete_stmt = (
            sa.delete(groups_table)
            .where(groups_table.c.email == email)
            .where(groups_table.c.group_id == group_id)
        )
        await self.connection.execute(delete_stmt)

    async def update_user_with_id(self, values: dict, user_id: int):
        update_stmt = (
            self._update(values)
            .where(users_table.c.user_id == user_id)
        )
        await self.connection.execute(update_stmt)

    async def update_email_in_groups(self, values: dict, email: str):
        update_stmt = (
            sa.update(groups_table)
            .values(values)
            .where(groups_table.c.email == email)
        )
        await self.connection.execute(update_stmt)

    async def update_user_with_email(self, values: dict, email: str):
        update_stmt = (
            self._update(values)
            .where(users_table.c.email == email)
        )
        await self.connection.execute(update_stmt)

    def _update(self, values: dict):
        update_stmt = (
            sa.update(users_table)
            .values(values)
        )
        return update_stmt