from __future__ import annotations

from systems.core.event_bus import Event, EventBus
from systems.core.event_types import EventType
from systems.progression.skills import SkillId, SkillTree


class SkillManager:
    def __init__(self, event_bus: EventBus, starting_points: int = 0) -> None:
        self._event_bus = event_bus
        self.tree = SkillTree()
        self.skill_points = starting_points
        event_bus.subscribe(EventType.RANK_UP, self._on_rank_up)

    def _on_rank_up(self, event: Event) -> None:
        self.skill_points += 1

    def unlock(self, skill_id: SkillId) -> None:
        if self.skill_points <= 0:
            raise ValueError("No skill points available")
        self.tree.upgrade(skill_id)
        self.skill_points -= 1
