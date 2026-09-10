from __future__ import annotations

from enum import Enum
from typing import Optional


class Rank(Enum):
    INTERN = "Intern"
    ANALYST = "Analyst"
    INVESTIGATOR = "Investigator"
    SENIOR_INVESTIGATOR = "Senior Investigator"
    CYBER_DETECTIVE = "Cyber Detective"
    CHIEF_ANALYST = "Chief Analyst"
    CYBER_DIRECTOR = "Cyber Director"


RANK_ORDER = [
    Rank.INTERN,
    Rank.ANALYST,
    Rank.INVESTIGATOR,
    Rank.SENIOR_INVESTIGATOR,
    Rank.CYBER_DETECTIVE,
    Rank.CHIEF_ANALYST,
    Rank.CYBER_DIRECTOR,
]

RANK_XP_THRESHOLDS = {
    Rank.INTERN: 0,
    Rank.ANALYST: 500,
    Rank.INVESTIGATOR: 1500,
    Rank.SENIOR_INVESTIGATOR: 3500,
    Rank.CYBER_DETECTIVE: 7000,
    Rank.CHIEF_ANALYST: 12000,
    Rank.CYBER_DIRECTOR: 20000,
}


def rank_for_xp(xp: int) -> Rank:
    current = Rank.INTERN
    for rank in RANK_ORDER:
        if xp >= RANK_XP_THRESHOLDS[rank]:
            current = rank
    return current


def xp_for_next_rank(xp: int) -> Optional[int]:
    current = rank_for_xp(xp)
    index = RANK_ORDER.index(current)
    if index + 1 >= len(RANK_ORDER):
        return None
    next_rank = RANK_ORDER[index + 1]
    return RANK_XP_THRESHOLDS[next_rank] - xp
