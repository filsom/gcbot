import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterable

import uvicorn
from aiogram import Bot, Dispatcher
from fastapi import FastAPI
from starlette.config import Config
from dishka.integrations.fastapi import setup_dishka
from dishka import Provider, Scope, from_context, make_async_container, provide
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection

from gcbot.port.adapter.parse_gc import parse_gc
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.message_fetcher import MessageJsonFetcher
from gcbot.port.adapter.sqlalchemy_resources.tables import metadata
from gcbot.port.adapter.fastapi_resources.router import router
from gcbot.port.adapter.aiogram_resources.bot import (
    create_bot, 
    create_bot_container, 
    create_dispatcher
)


class FastApiContainer(Provider):
    bot = from_context(provides=Bot, scope=Scope.APP)
    dp = from_context(provides=Dispatcher, scope=Scope.APP)
    config = from_context(provides=Config, scope=Scope.APP)
    engine = from_context(provides=AsyncEngine, scope=Scope.APP)

    @provide(scope=Scope.REQUEST)
    async def get_connection(self, engine: AsyncEngine) -> AsyncIterable[AsyncConnection]:
        async with engine.connect() as connection:
            yield connection
            
    message_fetsher = provide(MessageJsonFetcher, scope=Scope.REQUEST)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config: Config = await app.state.dishka_container.get(Config)
    bot: Bot = await app.state.dishka_container.get(Bot)
    dp: Dispatcher = await app.state.dishka_container.get(Dispatcher)
    engine: AsyncEngine = await app.state.bot_container.get(AsyncEngine)
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
        await connection.commit()

    await bot.set_webhook(
        config.get("APP_URL_WEBHOOK").format("/webhook"),
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True
    )
    asyncio.create_task(parse_gc(engine))
    yield
    await bot.delete_webhook()
    await bot.session.close()
    await app.state.bot_container.close()
    await app.state.dishka_container.close()


def create_app():
    config = Config('../.env')
    engine = create_async_engine(config.get("DB_URL"), echo=True)
    print(config.get("DB_URL"))
    bot = create_bot(config)
    bot_container = create_bot_container(config, engine)
    dp = create_dispatcher(bot_container)
    app = FastAPI(lifespan=lifespan)
    app.include_router(router)
    app_container = make_async_container(
        FastApiContainer(),
        context={
            Bot: bot,
            Dispatcher: dp,
            Config: config,
            AsyncEngine: engine
        }
    )
    app.state.bot_container = bot_container
    setup_dishka(app_container, app)
    return app

app = create_app()