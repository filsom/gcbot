from typing import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncConnection
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram_dialog import setup_dialogs
from dishka import AsyncContainer, make_async_container, Provider, from_context, Scope, make_async_container, provide
from dishka.integrations.aiogram import AiogramProvider, setup_dishka
from gspread import Worksheet, service_account
from starlette.config import Config

from gcbot.application.admin_service import AdminService
from gcbot.application.user_service import UserService
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_admin.mailing.mailing_service import TelegramMailingService
from gcbot.port.adapter.aiogram_resources.query_services.user_query_service import UserQueryService
from gcbot.port.adapter.aiogram_resources.query_services.workout_query_service import WorkoutQueryService
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.mailing_storage import MailingStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.message_storage import MessageStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.recipe_json_fetcher import RecipeJsonFetcher
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.recipe_storage import RecipeStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_json_fetcher import UserJsonFetcher
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_storage import UserStorage
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.workout_json_fetcher import WorkoutJsonFetcher
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.workout_storage import WorkoutStorage
from gcbot.port.adapter.aiogram_resources import starting_router


def create_bot(config: Config):
    session = AiohttpSession()
    return Bot(
        config.get("BOT_TOKEN"),
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )


def create_bot_container(
    config: Config, 
    engine: AsyncEngine
) -> AsyncContainer:
    container = make_async_container(
        TelegramBotProvider(),
        AiogramProvider(),
        context={
            AsyncEngine: engine,
            Config: config
        }
    )
    return container


def create_dispatcher(container: AsyncContainer):
    storage = MemoryStorage()
    dp = Dispatcher(
        storage=storage, 
        events_isolation=SimpleEventIsolation()
    )
    dp.include_router(starting_router)
    setup_dishka(container=container, router=dp)
    setup_dialogs(dp)
    return dp


class TelegramBotProvider(Provider):
    engine = from_context(provides=AsyncEngine, scope=Scope.APP)
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def get_worksheet(self, config: Config) -> Worksheet:
        cleint = service_account(config.get("PATH_CREDENTIALS"))
        spreadsheet = cleint.open_by_key(config.get("TABLE_KEY"))
        worksheet = spreadsheet.worksheet(config.get("TABLE_LIST"))
        return worksheet

    @provide(scope=Scope.REQUEST)
    async def get_connection(self, engine: AsyncEngine) -> AsyncIterable[AsyncConnection]:
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
    recipe_fetcher = provide(RecipeJsonFetcher, scope=Scope.REQUEST)
    admin_service = provide(AdminService, scope=Scope.REQUEST)
    message_storage = provide(MessageStorage, scope=Scope.REQUEST)
    mailing_service = provide(TelegramMailingService, scope=Scope.REQUEST)
    mailing_storage = provide(MailingStorage, scope=Scope.REQUEST)