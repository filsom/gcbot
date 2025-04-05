from uuid import UUID
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.workout_json_fetcher import (
    WorkoutJsonFetcher
)


class WorkoutQueryService:
    def __init__(
        self, 
        workout_fetcher: WorkoutJsonFetcher
    ) -> None:
        self.workout_fetcher = workout_fetcher

    async def query_categories_names(
        self, 
        user_id: int, 
        from_favorites: bool
    ) -> dict:
        if from_favorites:
            return await self.workout_fetcher \
                .fetch_favorites_categories_names(user_id)
        else:
            return await self.workout_fetcher \
                .fetch_all_categories_names()
        
    async def query_workout(
        self,
        user_id: int, 
        category_id: UUID,
        from_favorites: bool
    ) -> dict:
        if from_favorites:
            data_workout = await self.workout_fetcher \
                .fetch_favorite_workout_with_category_id(category_id, user_id)
        else:
            data_workout = await self.workout_fetcher \
                .fetch_random_workout_with_category_id(category_id, user_id)
        if data_workout is None:
            data_workout = {}
            if from_favorites:
                text = "Избранные видео с тренировками в данной категории отсутсвуют 🤷🏻"
            else:
                text = "Все тренировки данной категории добавлены в избранное ❤️"
            data_workout["text"] = text
            data_workout["is_empty"] = True
        print(data_workout)
        return data_workout