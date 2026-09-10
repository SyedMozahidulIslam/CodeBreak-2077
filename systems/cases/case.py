from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from investigation.deduction.models import ContradictionRule, Ending
from investigation.evidence.base import Evidence
from investigation.suspect import Suspect


@dataclass
class CaseBriefing:
    client: str
    incident_date: str
    summary: str = ""


@dataclass
class Case:
    case_id: str
    title: str
    tier: int
    min_rank: str
    previous_case: Optional[str]
    briefing: CaseBriefing
    suspects: list[Suspect] = field(default_factory=list)
    evidence_pool: list[Evidence] = field(default_factory=list)
    contradiction_rules: list[ContradictionRule] = field(default_factory=list)
    endings: list[Ending] = field(default_factory=list)

    def suspect(self, suspect_id: str) -> Suspect:
        for suspect in self.suspects:
            if suspect.suspect_id == suspect_id:
                return suspect
        raise KeyError(f"No suspect with id {suspect_id} in case {self.case_id}")

    def evidence(self, evidence_id: str) -> Evidence:
        for item in self.evidence_pool:
            if item.evidence_id == evidence_id:
                return item
        raise KeyError(f"No evidence with id {evidence_id} in case {self.case_id}")
