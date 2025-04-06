from aiogram.fsm.state import StatesGroup, State


class UsersGroupsDialog(StatesGroup):
    start = State()
    profile = State()
    inpute_email = State()
    change_email = State()
    empty_email = State()


class AddUserInGroupDialog(StatesGroup):
    start = State()