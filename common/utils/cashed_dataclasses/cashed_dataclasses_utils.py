import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import TypeVar, Type, Any

from pydantic import parse_raw_as
from pydantic.json import pydantic_encoder

T = TypeVar("T")


def load_cached_dataclass(path: Path, output_type: Type[T], update_time: timedelta) -> T:
    if datetime.now() - datetime.fromtimestamp(path.stat().st_mtime) < update_time:
        with path.open("r") as of:
            return parse_raw_as(output_type, of.read())


def save_dataclass_to_cache(path: Path, info_data: Any):
    with path.open("w") as of:
        json.dump(info_data, of, default=pydantic_encoder)
