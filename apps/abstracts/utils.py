# Python
from typing import Any
from datetime import (
    datetime,
    timedelta
)


def get_eta_time(seconds: int) -> Any:
    return datetime.utcnow() + timedelta(seconds=seconds)