from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class Event:
    type: str
    data: dict[str, Any] = field(default_factory=dict)


EventHandler = Callable[[Event], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        handlers = self._handlers.get(event_type)
        if handlers and handler in handlers:
            handlers.remove(handler)

    def publish(self, event_type: str, **data: Any) -> None:
        event = Event(type=event_type, data=data)
        for handler in list(self._handlers.get(event_type, ())):
            handler(event)

    def clear(self) -> None:
        self._handlers.clear()
