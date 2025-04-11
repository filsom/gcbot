from aiogram.fsm.state import StatesGroup, State


class UsersGroupsDialog(StatesGroup):
    start = State()
    profile = State()
    inpute_email = State()
    change_email = State()
    empty_email = State()


class AddUserInGroupDialog(StatesGroup):
    start = State()


class AddVoiceDialog(StatesGroup):
    start = State()


class UploadMediaDialog(StatesGroup):
    start = State()
    text = State()
    view = State()


class NewTrainingDialog(StatesGroup):
    start = State()
    send = State()


class AddCategoryDialog(StatesGroup):
    start = State()
    confirm = State()


class DeleteCategoryDialog(StatesGroup):
    start = State()


class CategoryDialog(StatesGroup):
    start = State()


class SendMessageDialog(StatesGroup):
    start = State()