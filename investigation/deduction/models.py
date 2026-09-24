from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class RatingTier(Enum):
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    FAIL = "fail"


@dataclass
class ContradictionRule:
    rule_id: str
    evidence_ids: tuple[str, str]
    explanation: str


@dataclass
class Ending:
    ending_id: str
    required_accusation: str
    required_evidence_ids: frozenset[str]
    rating_tier: RatingTier
    xp_reward: int = 0
    credit_reward: int = 0


@dataclass
class TheoryResult:
    matched_ending: Optional[Ending]
    rating_tier: RatingTier
    missing_evidence_ids: frozenset[str] = field(default_factory=frozenset)
