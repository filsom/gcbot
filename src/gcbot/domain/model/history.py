from dataclasses import dataclass
from datetime import datetime


@dataclass
class HistoryMessage:
    sender_id: int
    recipient_id: int
    text: str
    sent_to: datetime