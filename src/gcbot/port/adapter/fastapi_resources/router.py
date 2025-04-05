from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import APIRouter, Request
from dishka.integrations.fastapi import FromDishka, inject


router = APIRouter()


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