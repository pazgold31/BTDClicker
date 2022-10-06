from typing import Optional


def increment_if_set(value: Optional[int]) -> Optional[int]:
    return None if value is None else value + 1
