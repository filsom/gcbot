from typing import Any
from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.dialects.postgresql import aggregate_order_by

from gcbot.port.adapter.sqlalchemy_resources.tables import (
    medias_table,
    workouts_table,
    like_workouts_table,
    categories_table
)


class WorkoutJsonFetcher:
    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def fetch_favorites_categories_names(self, user_id: int):
        sub_query = (
            sa.select(workouts_table.c.category_id)
            .select_from(workouts_table)
            .join(
                like_workouts_table,
                like_workouts_table.c.workout_id == workouts_table.c.workout_id
            )
            .where(like_workouts_table.c.user_id == user_id)
        )
        query = (
            sa.select(
                categories_table.c.name, 
                sa.cast(categories_table.c.category_id, sa.String)
                )
            .select_from(categories_table)
            .where(categories_table.c.category_id.in_(sub_query))
        )
        rows = (await self.connection.execute(query))
        name_categories = []
        for row in rows:
            name_categories.append(row)
        text = None
        if not name_categories:
            text = "Избранные категории с тренировками отсутствуют 🤷🏻"
        return {
            "categories": name_categories,
            "text": text
        }
    
    async def fetch_all_categories_names(self):
        query = (
            sa.select(
                categories_table.c.name, 
                sa.cast(categories_table.c.category_id, sa.String)
            )
        )
        rows = await self.connection.execute(query)
        name_categories = []
        for row in rows:
            name_categories.append(row)
        return {"categories": name_categories}
    
    async def fetch_not_empty_categories_names(self):
        query = (
            sa.select(
                categories_table.c.name, 
                sa.cast(categories_table.c.category_id, sa.String)
            )
            .where(sa.exists(
                sa.select(1)
                .where(workouts_table.c.category_id == categories_table.c.category_id)
            ))
        )
        rows = await self.connection.execute(query)
        name_categories = []
        for row in rows:
            name_categories.append(row)
        return {"categories": name_categories}
    
    async def fetch_last_workout(self) -> dict:
        query = (
            self._select_json_workout()
            .select_from(workouts_table)
            .join(
                medias_table, 
                sa.and_(
                    medias_table.c.entity_id == workouts_table.c.workout_id,
                    medias_table.c.entity_type == workouts_table.c.entity_type,
                )
            )
            .group_by(
                workouts_table.c.workout_id,
                workouts_table.c.text
            )
            .order_by(sa.desc(workouts_table.c.created_at))
            .limit(1)
        )
        result = (await self.connection.execute(query)).scalar()
        return result
    
    async def fetch_favorite_workout_with_category_id(
        self, 
        category_id: UUID, 
        user_id: int, 
    ):
        query = (
            self._select_workout(category_id, user_id)
            .order_by(sa.func.random())
        )
        result = (await self.connection.execute(query)).scalar()
        if result is None:
            return None
        result["button_like"] = False
        result["button_delete"] = True
        return result
    
    async def fetch_random_workout_with_category_id(
        self, 
        category_id: UUID, 
        user_id: int, 
    ):
        query = (
            self._select_workout(category_id, user_id, isouter=True)
            .order_by(sa.func.random())
        )
        result = (await self.connection.execute(query)).scalar()
        if result is None:
            return None
        result["button_like"] = True
        result["button_delete"] = False
        return result
    
    def _select_workout(self, category_id: UUID, user_id: int, isouter=False):
        print(user_id, "r")
        liked = (
            sa.select(
                like_workouts_table.c.workout_id.label("workout_id")
            )
            .select_from(like_workouts_table)
            .where(like_workouts_table.c.user_id == user_id)
        ).cte("liked")
        query = (
            self._select_json_workout()
            .select_from(workouts_table)
            .join(
                medias_table, 
                sa.and_(
                    medias_table.c.entity_id == workouts_table.c.workout_id,
                    medias_table.c.entity_type == workouts_table.c.entity_type,
                )
            )
            .join(
                liked, 
                liked.c.workout_id == workouts_table.c.workout_id, isouter=isouter
            )
            .group_by(
                workouts_table.c.workout_id, 
                workouts_table.c.text
            )
            .where(workouts_table.c.category_id == category_id)
            .limit(1)
        )
        if isouter is True:
            query = query.where(liked.c.workout_id == None)
        return query

    def _select_json_workout(self) -> sa.Select[tuple[Any]]:
        select = (
            sa.select(
                sa.func.json_build_object(
                    "workout_id", workouts_table.c.workout_id,
                    "media", sa.func.json_agg(
                        aggregate_order_by(
                            medias_table.c.file_id, 
                            medias_table.c.message_id
                        )
                    ),
                    "text", workouts_table.c.text
                )
            )
        )
        return select