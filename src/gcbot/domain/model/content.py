from dataclasses import dataclass


@dataclass
class Media:
    file_id: str
    file_unique_id: str
    message_id: str
    content_type: str