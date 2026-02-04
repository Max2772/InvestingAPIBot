from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True, repr=False)
class LocalUser:
    telegram_id: int
    username: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    is_active_chat: bool = False