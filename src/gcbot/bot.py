import asyncio

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage, SimpleEventIsolation
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram_dialog import setup_dialogs

from dishka import make_async_container
from dishka.integrations.aiogram import AiogramProvider, setup_dishka

from gcbot.config import load_config
from gcbot.port.adapter.aiogram_resources import starting_router
from gcbot.port.adapter.dependency_provider import DependencyProvider
from gcbot.port.adapter.sqlalchemy_resources.tables import metadata


async def main():
    config = load_config()
    engine = create_async_engine(
        config.db_url,
        echo=True
    )
    storage = MemoryStorage()
    bot = Bot(
        config.bot_token, 
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(
        storage=storage, 
        events_isolation=SimpleEventIsolation()
    )
    dp.include_router(starting_router)
    container = make_async_container(
        DependencyProvider(),
        AiogramProvider(),
        context={AsyncEngine: engine}
    )
    setup_dishka(container=container, router=dp)
    setup_dialogs(dp)

    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
        await connection.commit()

    try:
        await dp.start_polling(bot)
    finally:
        await container.close()
        await bot.session.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())