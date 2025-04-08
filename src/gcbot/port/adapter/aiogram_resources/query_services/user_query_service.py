import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncConnection
from aiogram.fsm.state import State
from starlette.config import Config

from gcbot.domain.model.day_menu import TypeMeal
from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import (
    AdminStartingDialog, 
    AnonStartingDialog,
    FreeStartingDialog, 
    PaidStartingDialog,
    WorkoutDialog
)
from gcbot.port.adapter.aiogram_resources.dialogs.dialogs_food.dialog_state import DayMenuDialog, FoodDialog
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.recipe_json_fetcher import RecipeJsonFetcher
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_json_fetcher import UserJsonFetcher
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.workout_json_fetcher import WorkoutJsonFetcher
from gcbot.port.adapter.sqlalchemy_resources.tables import medias_table


class Group(object):
    ADMIN = 1
    WORKOUT = 2315673
    FOOD = 3088338


class UserQueryService:
    def __init__(
        self, 
        config: Config,
        connection: AsyncConnection,
        user_fetcher: UserJsonFetcher,
        workout_fetcher: WorkoutJsonFetcher,
        recipe_fetcher: RecipeJsonFetcher
    ) -> None:
        self.config = config
        self.connection = connection
        self.user_fetcher = user_fetcher
        self.workout_fetcher = workout_fetcher
        self.recipe_fetcher = recipe_fetcher

    async def query_command_start(self, user_id: int) -> State:
        user_data = await self.user_fetcher \
            .fetch_user_and_groups_with_id(user_id)
        if user_data is None:
            dialog_state = AnonStartingDialog.start
        else:
            if Group.ADMIN in user_data["groups"]:
                dialog_state = AdminStartingDialog.start
            elif user_data["groups"]:
                dialog_state = PaidStartingDialog.start
            else:
                dialog_state = FreeStartingDialog.check_access
        return dialog_state
    
    async def query_confirm_email_address(self, user_id: int) -> dict:
        user_data = await self.user_fetcher \
            .fetch_user_and_groups_with_id(user_id)
        if user_data["groups"]:
            if Group.ADMIN in user_data["groups"]:
                user_data.update({"dialog_state": AdminStartingDialog.start})
            else:
                user_data.update({"dialog_state": PaidStartingDialog.start})
        else:
            last_workout = await self.workout_fetcher \
                .fetch_last_workout()
            user_data.update({"dialog_state": FreeStartingDialog.start})
            user_data.update({"workout": last_workout})
        return user_data
    
    async def query_payment_verification(self, user_id: int) -> State | None:
        user_data = await self.user_fetcher \
            .fetch_user_and_groups_with_id(user_id)
        if user_data["groups"]:
            dialog_state = PaidStartingDialog.start
        else:
            dialog_state = None
        return dialog_state
    
    async def query_user_section(self, user_id: int, group_id: int) -> dict:
        user_data = await self.user_fetcher \
            .fetch_user_and_groups_with_id(user_id)
        if group_id in user_data["groups"] or Group.ADMIN in user_data["groups"]:
            if group_id == Group.FOOD:
                dialog_state = FoodDialog.start
            elif group_id == Group.WORKOUT:
                dialog_state = WorkoutDialog.start
            user_data.update({"dialog_state": dialog_state})
        else:
            button_status = {}
            if group_id == Group.FOOD:
                button_status.update({
                    "button_workout": True,
                    "button_food": False
                })
            else:
                button_status.update({
                    "button_workout": False,
                    "button_food": True
                })
            user_data.update({"button_status": button_status})
        return user_data
    
    async def query_day_menu(self, user_id: int) -> dict:
        user_data = await self.user_fetcher \
            .fetch_user_and_groups_with_id(user_id)
        user_data.setdefault("data", {})
        user_data["data"].update({
            "type_meal": [
                TypeMeal.BREAKFAST,
                TypeMeal.LUNCH,
                TypeMeal.DINNER,
                TypeMeal.SNACK
            ],
            "recipes": {},
            "dirty_photos": [],
            "norma_kcal": str(user_data.get("norma_kcal"))
        })
        user_data.update({"dialog_state": DayMenuDialog.start})
        return user_data
    
    async def query_recipe_with_type_meal(self, type_meal: str) -> dict:
        return await self.recipe_fetcher \
            .fetch_partial_recipe_with_type_meal(type_meal)
    
    async def query_user_for_admin_with_email(self, email: str) -> dict:
        user_data = await self.user_fetcher \
            .fetch_user_and_groups_with_email(email)
        return await self.parse_user_data_for_admin(user_data)
    
    async def query_user_for_admin_with_id(self, user_id) -> dict:
        user_data = await self.user_fetcher \
            .fetch_user_and_groups_with_id(user_id)
        return await self.parse_user_data_for_admin(user_data)
    
    async def query_forwarding_data(self, user_id: int, text_message: str) -> dict:
        user_data = await self.query_user_for_admin_with_id(user_id)
        return await self.make_preview_text(user_data, user_id, text_message)
    
    async def make_preview_text(self, user_data: dict, user_id: int, text_message: str) -> dict:
        forwarding_data = {}
        if not user_data:
            text = (
                f"👤 id {user_id}\n"
                f"Сообщение:\n{text_message}"
            )
        else:
            text = (
                f"👤 id {user_id}\n"
                f"📧 @email: {user_data["current_email"]}\n"
                f"👥 GC группы: {user_data["alias_groups"]}\n"
                f"Сообщение:\n{text_message}"
            )
            forwarding_data.update({"profile": True})
        forwarding_data.update({"previw_text": text})
        return forwarding_data

    async def parse_user_data_for_admin(self, user_data: dict | None) -> dict:
        if user_data is None:
            return {}
        email = user_data.pop("email")
        user_data.update({"current_email": email})
        user_data["url"] = self.config.get("APP_URL_WEBHOOK") \
            .format(f"/history/user/{user_data["user_id"]}")
        select_group = [
            ("К еде", Group.FOOD),
            ("К тренировкам", Group.WORKOUT)
        ]
        if Group.ADMIN in user_data["groups"]:
            alias = "Администратор"
            user_data.pop("url")
        elif not user_data["groups"]:
            alias = "🤷🏻"
            user_data.update({"select_groups": select_group})
        else:
            alias = []
            for group in user_data["groups"]:
                if group == Group.FOOD:
                    alias.append("Еда")
                    select_group.remove(("К еде", group))
                if group == Group.WORKOUT:
                    alias.append("Тренировки")
                    select_group.remove(("К тренировкам", group))
            alias = ", ".join(alias)
            user_data.update({"select_groups": select_group})
        user_data.update({
            "alias_groups": alias,
        }) 
        return user_data
    
    async def query_video_note(self) -> str:
        query = (
            sa.select(medias_table.c.file_id)
            .where(medias_table.c.content_type == "video_note")
            .order_by(sa.desc(medias_table.c.message_id))
            .limit(1)
        )
        result = (await self.connection.execute(query)).scalar()
        return result