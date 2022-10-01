from typing import Dict, Any, Callable

EventType = str
ValuesType = Dict[str, Any]
CallbackMethod = Callable[[ValuesType], None]
