from typing import Dict, Any, Callable

EventType = str
ValuesType = dict[str, Any]
CallbackMethod = Callable[[ValuesType], None]
