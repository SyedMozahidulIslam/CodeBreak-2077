from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SkillId(Enum):
    OBSERVATION = "observation"
    DEDUCTION = "deduction"
    DIGITAL_FORENSICS = "digital_forensics"
    INTERROGATION = "interrogation"
    INTELLIGENCE = "intelligence"


SKILL_NAMES = {
    SkillId.OBSERVATION: "Observation",
    SkillId.DEDUCTION: "Deduction",
    SkillId.DIGITAL_FORENSICS: "Digital Forensics",
    SkillId.INTERROGATION: "Interrogation",
    SkillId.INTELLIGENCE: "Intelligence",
}

MAX_SKILL_LEVEL = 3


@dataclass
class SkillTree:
    levels: dict[SkillId, int] = field(default_factory=lambda: {skill: 0 for skill in SkillId})

    def level_of(self, skill_id: SkillId) -> int:
        return self.levels.get(skill_id, 0)

    def can_upgrade(self, skill_id: SkillId) -> bool:
        return self.level_of(skill_id) < MAX_SKILL_LEVEL

    def upgrade(self, skill_id: SkillId) -> None:
        if not self.can_upgrade(skill_id):
            raise ValueError(f"{SKILL_NAMES[skill_id]} is already at max level")
        self.levels[skill_id] = self.level_of(skill_id) + 1
