from typing import Dict, Any, Callable

EventType = str
ValuesType = Dict[str, Any]
CallbackMethod = Callable[[EventType, ValuesType], None]
