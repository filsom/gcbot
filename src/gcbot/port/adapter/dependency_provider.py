from typing import AsyncIterable

from dishka import Provider, from_context, Scope, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncConnection

from gcbot.application.user_service import UserService
from gcbot.config import Config
from gcbot.port.adapter.aiogram_resources.query_services.user_query_service import UserQueryService
from gcbot.port.adapter.aiogram_resources.query_services.workout_query_service import WorkoutQueryService
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.recipe_storage import RecipeStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_json_fetchers import UserJsonFetcher
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_storage import UserStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.workout_json_fetcher import WorkoutJsonFetcher
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.workout_storage import WorkoutStorage


class DependencyProvider(Provider):
    engine = from_context(provides=AsyncEngine, scope=Scope.APP)
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_connection(
        self, 
        engine: AsyncEngine
    ) -> AsyncIterable[AsyncConnection]:
        async with engine.connect() as connection:
            yield connection

    user_service = provide(UserService, scope=Scope.REQUEST)
    user_query_service = provide(UserQueryService, scope=Scope.REQUEST)
    user_storage = provide(UserStorage, scope=Scope.REQUEST)
    user_fetcher = provide(UserJsonFetcher, scope=Scope.REQUEST)
    recipe_storage = provide(RecipeStorage, scope=Scope.REQUEST)
    workout_fetcher = provide(WorkoutJsonFetcher, scope=Scope.REQUEST)
    workout_storage = provide(WorkoutStorage, scope=Scope.REQUEST)
    workout_query_service = provide(WorkoutQueryService, scope=Scope.REQUEST)