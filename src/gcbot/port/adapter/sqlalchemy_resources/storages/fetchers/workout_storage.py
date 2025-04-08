from datetime import datetime
from uuid import UUID, uuid4

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.dialects.postgresql import insert

from gcbot.port.adapter.sqlalchemy_resources.tables import (
    EntityType,
    like_workouts_table, 
    workouts_table, 
    medias_table
)


class WorkoutStorage:
    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def put_like(self, user_id: int, workout_id: UUID):
        insert_stmt = (
            insert(like_workouts_table)
            .values(
                user_id=user_id,
                workout_id=workout_id
            )
        )
        insert_stmt = insert_stmt.on_conflict_do_nothing()
        await self.connection.execute(insert_stmt)

    async def delete_liked(self, user_id: int, workout_id: UUID):
        delete_stmt = (
            sa.delete(like_workouts_table)
            .where(sa.and_(
                like_workouts_table.c.user_id == user_id,
                like_workouts_table.c.workout_id == workout_id
            ))
        )
        await self.connection.execute(delete_stmt)

    async def add_training(
        self,
        category_id: UUID,
        text: str,
        medias: list
    ):
        workout_id = uuid4()
        insert_training = (
            sa.insert(workouts_table)
            .values(
                workout_id=workout_id,
                entity_type=EntityType.WORKOUT,
                category_id=category_id,
                text=text,
                created_at=datetime.now()
            )
        )
        await self.connection.execute(insert_training)
        for media in medias:
            media.update({
                "media_id": uuid4(),
                "entity_id": workout_id,
                "entity_type": EntityType.WORKOUT
            })
        insert_medias = (
            sa.insert(medias_table)
            .values(medias)
        )
        await self.connection.execute(insert_medias)