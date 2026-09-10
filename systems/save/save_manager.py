from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Optional

from database.models.records import CaseProgressRecord, SaveSlotRecord
from database.repositories.case_progress_repository import CaseProgressRepository
from database.repositories.save_slot_repository import SaveSlotRepository
from systems.core.event_bus import Event, EventBus
from systems.core.event_types import EventType
from systems.economy.credit_manager import CreditManager
from systems.progression.ranks import Rank
from systems.progression.xp_tracker import XPTracker

logger = logging.getLogger("codebreak.save")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class SaveManager:
    def __init__(
        self,
        event_bus: EventBus,
        connection,
        xp_tracker: XPTracker,
        credit_manager: CreditManager,
        player_id: int = 1,
    ) -> None:
        self._event_bus = event_bus
        self._conn = connection
        self._xp_tracker = xp_tracker
        self._credit_manager = credit_manager
        self._player_id = player_id
        self.save_slots = SaveSlotRepository(connection)
        self.case_progress = CaseProgressRepository(connection)
        self._active_slot_id: Optional[int] = None

        self._ensure_player_exists()
        event_bus.subscribe(EventType.CASE_COMPLETED, self._on_case_completed)
        event_bus.subscribe(EventType.CASE_STARTED, self._on_case_started)

    def _ensure_player_exists(self) -> None:
        row = self._conn.execute("SELECT 1 FROM players WHERE player_id = ?", (self._player_id,)).fetchone()
        if row is None:
            self._conn.execute(
                "INSERT INTO players (player_id, display_name, created_at) VALUES (?, ?, ?)",
                (self._player_id, "Player", _now()),
            )
            self._conn.commit()

    @property
    def active_slot_id(self) -> Optional[int]:
        return self._active_slot_id

    def list_slots(self) -> list[SaveSlotRecord]:
        return self.save_slots.list()

    def save_to_slot(self, slot_index: int) -> SaveSlotRecord:
        existing = self._find_by_index(slot_index)
        record = SaveSlotRecord(
            slot_id=existing.slot_id if existing else None,
            player_id=self._player_id,
            slot_index=slot_index,
            rank=self._xp_tracker.rank.value,
            xp=self._xp_tracker.xp,
            credits=self._credit_manager.balance,
            updated_at=_now(),
        )
        saved = self.save_slots.save(record)
        self._active_slot_id = saved.slot_id
        self._event_bus.publish(EventType.SAVE_COMPLETED, slot_index=slot_index, slot_id=saved.slot_id)
        logger.info("Saved to slot %s", slot_index)
        return saved

    def load_from_slot(self, slot_index: int) -> Optional[SaveSlotRecord]:
        slot = self._find_by_index(slot_index)
        if slot is None:
            return None
        self._active_slot_id = slot.slot_id
        self._xp_tracker.xp = slot.xp
        self._xp_tracker.rank = Rank(slot.rank)
        self._credit_manager.balance = slot.credits
        return slot

    def record_case_completion(self, case_id: str, ending_id: Optional[str], rating_tier: Optional[str]) -> None:
        if self._active_slot_id is None:
            return
        self.case_progress.upsert(CaseProgressRecord(
            slot_id=self._active_slot_id, case_id=case_id, status="completed",
            ending_id=ending_id, rating_tier=rating_tier,
        ))

    def _on_case_completed(self, event: Event) -> None:
        if self._active_slot_id is None:
            return

        case_id = event.data.get("case_id")
        if case_id:
            self.record_case_completion(case_id, event.data.get("ending_id"), event.data.get("rating_tier"))

        active_slot = self._find_by_id(self._active_slot_id)
        if active_slot:
            self.save_to_slot(active_slot.slot_index)

    def _on_case_started(self, event: Event) -> None:
        if self._active_slot_id is None:
            return
        case_id = event.data.get("case_id")
        if not case_id:
            return
        existing = self.case_progress.get(self._active_slot_id, case_id)
        if existing and existing.status == "completed":
            return
        self.case_progress.upsert(CaseProgressRecord(
            slot_id=self._active_slot_id, case_id=case_id, status="in_progress",
        ))

    def _find_by_index(self, slot_index: int) -> Optional[SaveSlotRecord]:
        return next((s for s in self.save_slots.list() if s.slot_index == slot_index), None)

    def _find_by_id(self, slot_id: int) -> Optional[SaveSlotRecord]:
        return next((s for s in self.save_slots.list() if s.slot_id == slot_id), None)
