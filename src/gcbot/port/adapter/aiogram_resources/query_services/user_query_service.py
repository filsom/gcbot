from aiogram.fsm.state import State

from gcbot.domain.model.day_menu import TypeMeal
from gcbot.port.adapter.aiogram_resources.dialogs.dialog_state import (
    AdminStartingDialog, 
    AnonStartingDialog,
    DayMenuDialog,
    FoodDialog, 
    FreeStartingDialog, 
    PaidStartingDialog,
    WorkoutDialog
)
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.recipe_json_fetcher import RecipeJsonFetcher
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.user_json_fetcher import UserJsonFetcher
from gcbot.port.adapter.sqlalchemy_resources.storages.fetchers.workout_json_fetcher import WorkoutJsonFetcher


class Group(object):
    ADMIN = 1
    WORKOUT = 2315673
    FOOD = 3088338


class UserQueryService:
    def __init__(
        self, 
        user_fetcher: UserJsonFetcher,
        workout_fetcher: WorkoutJsonFetcher,
        recipe_fetcher: RecipeJsonFetcher
    ) -> None:
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
        print(user_data)
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