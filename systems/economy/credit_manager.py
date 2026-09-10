from __future__ import annotations

from systems.core.event_bus import Event, EventBus
from systems.core.event_types import EventType
from systems.core.exceptions import CodeBreakError


class InsufficientCreditsError(CodeBreakError):
    pass


class CreditManager:
    def __init__(self, event_bus: EventBus, starting_balance: int = 0) -> None:
        self._event_bus = event_bus
        self.balance = starting_balance
        event_bus.subscribe(EventType.CASE_COMPLETED, self._on_case_completed)

    def _on_case_completed(self, event: Event) -> None:
        self.add(event.data.get("credit_reward", 0))

    def add(self, amount: int) -> None:
        if amount <= 0:
            return
        self.balance += amount

    def spend(self, amount: int) -> None:
        if amount > self.balance:
            raise InsufficientCreditsError(f"Need {amount} credits, have {self.balance}")
        self.balance -= amount
