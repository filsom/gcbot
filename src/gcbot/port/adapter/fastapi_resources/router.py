from aiogram import Bot, Dispatcher
from aiogram.types import Update
from jinja2 import PackageLoader
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from dishka.integrations.fastapi import FromDishka, inject

from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.message_fetcher import (
    MessageJsonFetcher
)


router = APIRouter()
loader = PackageLoader("gcbot.port.adapter.fastapi_resources")
templates = Jinja2Templates(directory="templates", loader=loader)


@router.post("/webhook")
@inject
async def webhook(
    bot: FromDishka[Bot],
    dp: FromDishka[Dispatcher],
    request: Request
):
    update = Update.model_validate(
        await request.json(),
        context={"bot": bot}
    )
    await dp.feed_update(bot, update)


@router.get("/history/user/{user_id}")
@inject
async def get_history_message_with_user(
    request: Request,
    user_id: int,
    message_fetcher: FromDishka[MessageJsonFetcher]
):
    history_data = await message_fetcher \
        .fetch_message_with_user(user_id)
    return templates.TemplateResponse(
        request,
        "history.html",
        context={"messages": history_data}
    )
