from dataclasses import dataclass
from typing import Optional


@dataclass
class Context:
    last_message: Optional[str]
    last_step: Optional[str]


@dataclass
class User:
    id: int
    firstname: str
    lastname: Optional[str]
    username: str
    context: Context
