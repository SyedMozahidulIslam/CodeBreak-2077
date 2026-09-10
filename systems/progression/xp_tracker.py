from __future__ import annotations

import logging

from systems.core.event_bus import Event, EventBus
from systems.core.event_types import EventType
from systems.progression.ranks import rank_for_xp

logger = logging.getLogger("codebreak.progression")


class XPTracker:
    def __init__(self, event_bus: EventBus, starting_xp: int = 0) -> None:
        self._event_bus = event_bus
        self.xp = starting_xp
        self.rank = rank_for_xp(starting_xp)
        event_bus.subscribe(EventType.CASE_COMPLETED, self._on_case_completed)

    def _on_case_completed(self, event: Event) -> None:
        self.add_xp(event.data.get("xp_reward", 0))

    def add_xp(self, amount: int) -> None:
        if amount <= 0:
            return
        self.xp += amount
        self._event_bus.publish(EventType.XP_GAINED, amount=amount, total_xp=self.xp)

        new_rank = rank_for_xp(self.xp)
        if new_rank != self.rank:
            old_rank = self.rank
            self.rank = new_rank
            self._event_bus.publish(EventType.RANK_UP, old_rank=old_rank.value, new_rank=new_rank.value)
            logger.info("Rank up: %s -> %s", old_rank.value, new_rank.value)
