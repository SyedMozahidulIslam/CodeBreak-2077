from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SuspectStatus(Enum):
    UNCONFIRMED = "unconfirmed"
    ACCUSED = "accused"
    CLEARED = "cleared"


@dataclass
class Suspect:
    suspect_id: str
    name: str
    role: str
    bio: str = ""
    status: SuspectStatus = SuspectStatus.UNCONFIRMED
