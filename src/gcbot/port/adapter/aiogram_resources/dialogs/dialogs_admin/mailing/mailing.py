from enum import StrEnum, auto


class StatusMailing(StrEnum):
    AWAIT = auto()
    PROCESS = auto()
    DONE = auto()


class RecipientMailing(object):
    TRAINING = 1
    FREE = 2
    PAID = 3