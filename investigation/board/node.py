from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Union

from investigation.evidence.base import Evidence
from investigation.suspect import Suspect


class NodeKind(Enum):
    SUSPECT = "suspect"
    EVIDENCE = "evidence"


@dataclass
class BoardNode:
    node_id: str
    kind: NodeKind
    payload: Union[Suspect, Evidence]
    position: tuple[float, float] = (0.0, 0.0)
