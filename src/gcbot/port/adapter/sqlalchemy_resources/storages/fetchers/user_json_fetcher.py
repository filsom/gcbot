import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection

from gcbot.port.adapter.sqlalchemy_resources.tables import users_table, groups_table


class UserJsonFetcher:
    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def fetch_user_and_groups_with_id(self, user_id: int) -> dict:
        query = (
            sa.select(
                sa.func.json_build_object(
                    "user_id", users_table.c.user_id,
                    "email", users_table.c.email,
                    "norma_kcal", users_table.c.norma_kcal,
                    "groups", sa.func.json_agg(groups_table.c.group_id)
                )                 
            )
            .select_from(users_table)
            .outerjoin(
                groups_table,
                groups_table.c.email == users_table.c.email,
            )
            .group_by(
                users_table.c.user_id, 
                users_table.c.email, 
            )
            .where(users_table.c.user_id == user_id)
        )
        result = (await self.connection.execute(query)).scalar()
        if result is not None:
            if result["groups"][0] is None:
                result["groups"] = []
        return result