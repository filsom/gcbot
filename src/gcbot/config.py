import os
from dataclasses import dataclass


@dataclass
class Config:
    db_url: str
    bot_token: str


def load_config():
    return Config(
        db_url=os.environ.get("DB_URL"),
        bot_token=os.environ.get("BOT_TOKEN")
    )