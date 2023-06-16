from dataclasses import dataclass, field
from typing import Optional
import datetime


@dataclass
class Message:
    is_command: bool = False
    text: str = ""


@dataclass
class Step:
    top_level: bool = True
    is_command: bool = False
    code: str = ""
    data: dict = field(default_factory=dict)


@dataclass
class Context:
    last_message: Optional[Message] = None
    last_step: Optional[Step] = None


@dataclass
class User:
    id: int
    firstname: str
    lastname: Optional[str]
    username: str
    context: Context


@dataclass
class Key:
    key: str
    value: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    reminders: int
    reminders_failed: int
    reminders_succeded: int
    next_reminder: datetime.datetime


@dataclass
class Reminder:
    id: str
    key: str
    value: str
    expire: datetime.datetime
    username: str
    chat_id: int
