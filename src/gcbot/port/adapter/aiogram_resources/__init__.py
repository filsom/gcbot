from .router import starting_router
from .dialogs.dialog_with_anon_user import anon_starting_dialog
from .dialogs.dialog_with_free_user import free_starting_dialog
from .dialogs.dialog_with_paid_user import paid_starting_dialog
from .dialogs.dialogs_food.dialog_with_food import food_dialog
from .dialogs.dialogs_food.dialog_with_input_norma_day import input_norma_day_dialog
from .dialogs.dialogs_food.dialog_with_calculate_norma_day import calculate_norma_day_dialog
from .dialogs.dialog_with_workout import workout_dialog
from .dialogs.dialogs_food.dialog_with_day_menu import day_menu_dialog
from .dialogs.dialogs_admin.dialog_with_admin_user import (
    admin_starting_dialog, 
)
from .dialogs.dialogs_admin.dialog_with_content import content_dialog
from .dialogs.dialogs_admin.dialog_with_users_groups import (
    users_groups_dialog, 
    add_user_group_dialog
)


starting_router.include_router(anon_starting_dialog)
starting_router.include_router(free_starting_dialog)
starting_router.include_router(paid_starting_dialog)
starting_router.include_router(food_dialog)
starting_router.include_router(input_norma_day_dialog)
starting_router.include_router(calculate_norma_day_dialog)
starting_router.include_router(workout_dialog)
starting_router.include_router(day_menu_dialog)
starting_router.include_router(admin_starting_dialog)
starting_router.include_router(content_dialog)
starting_router.include_router(users_groups_dialog)
starting_router.include_router(add_user_group_dialog)
