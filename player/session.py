from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Union

from database.connection import connect
from database.repositories.achievement_repository import AchievementRepository
from systems.achievements.achievement_manager import AchievementManager
from systems.core.event_bus import EventBus
from systems.economy.credit_manager import CreditManager
from systems.progression.ranks import Rank
from systems.progression.xp_tracker import XPTracker
from systems.save.save_manager import SaveManager
from systems.stats.statistics_tracker import StatisticsTracker

if TYPE_CHECKING:
    from systems.cases.case import Case


class PlayerSession:
    """Composition root: owns one EventBus and every system that needs to react
    to it, so screens never have to wire these together themselves."""

    def __init__(self, event_bus: Optional[EventBus] = None, db_path: Union[str, None] = None) -> None:
        self.event_bus = event_bus or EventBus()
        connection = connect(db_path) if db_path is not None else connect()

        self.xp_tracker = XPTracker(self.event_bus)
        self.credits = CreditManager(self.event_bus)
        self.stats = StatisticsTracker(self.event_bus)
        self.save_manager = SaveManager(self.event_bus, connection, self.xp_tracker, self.credits)

        achievement_repo = AchievementRepository(connection)
        self.achievements = AchievementManager(self.event_bus, repository=achievement_repo)

        self.active_case: Optional["Case"] = None

    @property
    def rank(self) -> Rank:
        return self.xp_tracker.rank

    def start_new_game(self, slot_index: int = 0) -> None:
        self.save_manager.save_to_slot(slot_index)
        self.achievements.set_active_slot(self.save_manager.active_slot_id)

    def load_game(self, slot_index: int) -> bool:
        slot = self.save_manager.load_from_slot(slot_index)
        if slot is None:
            return False
        self.achievements.set_active_slot(self.save_manager.active_slot_id)
        return True

    def has_completed_case(self, case_id: str) -> bool:
        if self.save_manager.active_slot_id is None:
            return False
        progress = self.save_manager.case_progress.get(self.save_manager.active_slot_id, case_id)
        return progress is not None and progress.status == "completed"
