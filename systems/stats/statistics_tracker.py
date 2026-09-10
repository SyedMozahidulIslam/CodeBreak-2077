from __future__ import annotations

from database.models.records import StatisticsRecord
from systems.core.event_bus import Event, EventBus
from systems.core.event_types import EventType

_TIER_SCORES = {"S": 100, "A": 85, "B": 70, "C": 50, "fail": 0}


class StatisticsTracker:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus
        self.cases_solved = 0
        self.mistakes_made = 0
        self.time_played_sec = 0
        self.best_score = 0

        event_bus.subscribe(EventType.CASE_COMPLETED, self._on_case_completed)
        event_bus.subscribe(EventType.THEORY_SUBMITTED, self._on_theory_submitted)

    def _on_case_completed(self, event: Event) -> None:
        self.cases_solved += 1
        score = _TIER_SCORES.get(event.data.get("rating_tier", ""), 0)
        self.best_score = max(self.best_score, score)

    def _on_theory_submitted(self, event: Event) -> None:
        if event.data.get("rating_tier") == "fail":
            self.mistakes_made += 1

    def add_play_time(self, seconds: float) -> None:
        self.time_played_sec += int(seconds)

    def snapshot(self, slot_id: int) -> StatisticsRecord:
        return StatisticsRecord(
            slot_id=slot_id,
            cases_solved=self.cases_solved,
            mistakes_made=self.mistakes_made,
            time_played_sec=self.time_played_sec,
            best_score=self.best_score,
        )
