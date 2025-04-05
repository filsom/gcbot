from contextlib import asynccontextmanager

import uvicorn
from aiogram import Bot, Dispatcher
from fastapi import FastAPI
from starlette.config import Config
from dishka.integrations.fastapi import setup_dishka
from dishka import Provider, Scope, from_context, make_async_container
from sqlalchemy.ext.asyncio import create_async_engine

from gcbot.port.adapter.fastapi_resources.router import router
from gcbot.port.adapter.aiogram_resources.bot import (
    create_bot, 
    create_bot_container, 
    create_dispatcher
)


class WebAppContainer(Provider):
    bot = from_context(provides=Bot, scope=Scope.APP)
    dp = from_context(provides=Dispatcher, scope=Scope.APP)
    config = from_context(provides=Config, scope=Scope.APP)


@asynccontextmanager
async def lifespan(app: FastAPI):
    config: Config = await app.state.dishka_container.get(Config)
    bot: Bot = await app.state.dishka_container.get(Bot)
    dp: Dispatcher = await app.state.dishka_container.get(Dispatcher)
    await bot.set_webhook(
        config.get("APP_URL_WEBHOOK"),
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=False
    )
    yield
    await bot.delete_webhook()
    await bot.session.close()
    await app.state.bot_container.close()
    await app.state.dishka_container.close()


def create_web_app():
    config = Config('../.env')
    engine = create_async_engine(config.get("DB_URL"), echo=True)
    bot = create_bot(config)
    bot_container = create_bot_container(config, engine)
    dp = create_dispatcher(bot_container)

    web_app = FastAPI(lifespan=lifespan)
    web_app.include_router(router)
    web_app_container = make_async_container(
        WebAppContainer(),
        context={
            Bot: bot,
            Dispatcher: dp,
            Config: config
        }
    )
    web_app.state.bot_container = bot_container
    setup_dishka(web_app_container, web_app)
    return web_app


if __name__ == "__main__":
    uvicorn.run(create_web_app(), port=8000, lifespan="on")