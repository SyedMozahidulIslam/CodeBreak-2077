from __future__ import annotations

from typing import Optional

from investigation.board.board import InvestigationBoard
from investigation.board.node import NodeKind
from investigation.deduction.models import Ending, RatingTier, TheoryResult

_TIER_RANK = {
    RatingTier.S: 0,
    RatingTier.A: 1,
    RatingTier.B: 2,
    RatingTier.C: 3,
    RatingTier.FAIL: 4,
}


class TheoryValidator:
    def __init__(self, endings: list[Ending]) -> None:
        self._endings = sorted(endings, key=lambda ending: _TIER_RANK[ending.rating_tier])

    def validate(self, board: InvestigationBoard, accused_suspect_id: str) -> TheoryResult:
        collected_evidence_ids = {
            node_id for node_id, node in board.nodes.items() if node.kind == NodeKind.EVIDENCE
        }

        candidates = [e for e in self._endings if e.required_accusation == accused_suspect_id]

        for ending in candidates:
            missing = ending.required_evidence_ids - collected_evidence_ids
            if not missing:
                return TheoryResult(matched_ending=ending, rating_tier=ending.rating_tier)

        best_partial: Optional[Ending] = None
        smallest_gap: frozenset[str] = frozenset()
        for ending in candidates:
            missing = ending.required_evidence_ids - collected_evidence_ids
            if best_partial is None or len(missing) < len(smallest_gap):
                best_partial = ending
                smallest_gap = missing

        if best_partial is None:
            return TheoryResult(matched_ending=None, rating_tier=RatingTier.FAIL)

        return TheoryResult(matched_ending=None, rating_tier=RatingTier.FAIL, missing_evidence_ids=smallest_gap)
