from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EvidenceType(Enum):
    EMAIL = "email"
    CHAT_LOG = "chat_log"
    CCTV = "cctv"
    PHONE_RECORD = "phone_record"
    FINANCIAL = "financial"
    IMAGE = "image"
    DOCUMENT = "document"


@dataclass
class Evidence:
    evidence_id: str
    title: str
    timestamp: str
    source: str
    is_red_herring: bool = False

    @property
    def evidence_type(self) -> EvidenceType:
        raise NotImplementedError("Subclasses must define evidence_type")
