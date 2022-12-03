from typing import Optional, Union, List


def increment_if_set(value: Optional[int]) -> Optional[int]:
    return None if value is None else value + 1


def get_last_if_list(value: Union[list[int], int]) -> int:
    return value[-1] if isinstance(value, list) else value
