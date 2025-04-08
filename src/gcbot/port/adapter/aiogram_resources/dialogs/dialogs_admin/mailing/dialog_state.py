from aiogram.fsm.state import State, StatesGroup


class MaillingDialog(StatesGroup):
    start = State()
    user = State()


class SendMailingDialog(StatesGroup):
    start = State()
    text = State()
    plan_end = State()
    send_end = State()


class PlandeMaillingDialog(StatesGroup):
    start = State()
    menu = State()
    end = State()


class StatusMaillingDialog(StatesGroup):
    start = State()