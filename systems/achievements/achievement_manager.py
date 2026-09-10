from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from systems.achievements.conditions import CONDITION_CHECKS
from systems.core.event_bus import Event, EventBus
from systems.core.event_types import EventType

logger = logging.getLogger("codebreak.achievements")

ACHIEVEMENTS_PATH = Path("data/achievements.json")


def load_achievement_definitions(path: Path = ACHIEVEMENTS_PATH) -> list:
    if not path.exists():
        logger.warning("Achievement definitions not found at %s, using an empty list", path)
        return []
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


class AchievementManager:
    def __init__(self, event_bus: EventBus, definitions: Optional[list] = None, repository=None) -> None:
        self._event_bus = event_bus
        self._repository = repository
        self._definitions = definitions if definitions is not None else load_achievement_definitions()
        self._state: dict = {}
        self.unlocked: set = set()
        self._active_slot_id: Optional[int] = None

        for definition in self._definitions:
            event_bus.subscribe(definition["trigger_event"], self._make_handler(definition))

    def set_active_slot(self, slot_id: Optional[int]) -> None:
        self._active_slot_id = slot_id

    def _make_handler(self, definition: dict):
        def handler(event: Event) -> None:
            self._check(definition, event)
        return handler

    def _check(self, definition: dict, event: Event) -> None:
        achievement_id = definition["achievement_id"]
        if achievement_id in self.unlocked:
            return

        check = CONDITION_CHECKS.get(definition["condition"])
        if check is None:
            logger.warning("Unknown achievement condition '%s'", definition["condition"])
            return

        if check(event, definition.get("params", {}), self._state):
            self._unlock(achievement_id)

    def _unlock(self, achievement_id: str) -> None:
        self.unlocked.add(achievement_id)
        self._event_bus.publish(EventType.ACHIEVEMENT_UNLOCKED, achievement_id=achievement_id)
        if self._repository is not None and self._active_slot_id is not None:
            self._repository.unlock(self._active_slot_id, achievement_id, datetime.now(timezone.utc).isoformat())
        logger.info("Achievement unlocked: %s", achievement_id)
