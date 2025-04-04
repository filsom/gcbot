import os
from dataclasses import dataclass


@dataclass
class Config:
    db_url: str
    bot_token: str
    path_credentials: str
    table_key: str
    table_list: str


def load_config():
    return Config(
        db_url=os.environ.get("DB_URL"),
        bot_token=os.environ.get("BOT_TOKEN"),
        path_credentials=os.environ.get("PATH_CREDENTIALS"),
        table_key=os.environ.get("TABLE_KEY"),
        table_list=os.environ.get("TABLE_LIST")
    )