from __future__ import annotations

from typing import Any

from investigation.evidence.base import Evidence, EvidenceType
from investigation.evidence.types import (
    CCTVEvidence,
    ChatLogEvidence,
    DocumentEvidence,
    EmailEvidence,
    FinancialEvidence,
    ImageEvidence,
    PhoneRecordEvidence,
)
from investigation.suspect import Suspect
from systems.core.exceptions import CaseValidationError

_EVIDENCE_CLASSES = {
    EvidenceType.EMAIL.value: EmailEvidence,
    EvidenceType.CHAT_LOG.value: ChatLogEvidence,
    EvidenceType.CCTV.value: CCTVEvidence,
    EvidenceType.PHONE_RECORD.value: PhoneRecordEvidence,
    EvidenceType.FINANCIAL.value: FinancialEvidence,
    EvidenceType.IMAGE.value: ImageEvidence,
    EvidenceType.DOCUMENT.value: DocumentEvidence,
}


def build_evidence(evidence_type: str, data: dict[str, Any]) -> Evidence:
    evidence_class = _EVIDENCE_CLASSES.get(evidence_type)
    if evidence_class is None:
        raise CaseValidationError(f"Unknown evidence type '{evidence_type}'")

    common = {
        "evidence_id": data["evidence_id"],
        "title": data["title"],
        "timestamp": data["timestamp"],
        "source": data["source"],
        "is_red_herring": data.get("is_red_herring", False),
    }
    extra = {k: v for k, v in data.items() if k not in common and k != "type"}
    return evidence_class(**common, **extra)


def build_suspect(data: dict[str, Any]) -> Suspect:
    return Suspect(
        suspect_id=data["suspect_id"],
        name=data["name"],
        role=data["role"],
        bio=data.get("bio", ""),
    )
