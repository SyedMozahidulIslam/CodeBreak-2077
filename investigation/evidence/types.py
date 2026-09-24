from __future__ import annotations

from dataclasses import dataclass, field

from investigation.evidence.base import Evidence, EvidenceType


@dataclass
class EmailEvidence(Evidence):
    sender: str = ""
    recipient: str = ""
    body: str = ""

    @property
    def evidence_type(self) -> EvidenceType:
        return EvidenceType.EMAIL


@dataclass
class ChatLogEvidence(Evidence):
    participants: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)

    @property
    def evidence_type(self) -> EvidenceType:
        return EvidenceType.CHAT_LOG


@dataclass
class CCTVEvidence(Evidence):
    location: str = ""
    description: str = ""

    @property
    def evidence_type(self) -> EvidenceType:
        return EvidenceType.CCTV


@dataclass
class PhoneRecordEvidence(Evidence):
    caller: str = ""
    receiver: str = ""
    duration_seconds: int = 0

    @property
    def evidence_type(self) -> EvidenceType:
        return EvidenceType.PHONE_RECORD


@dataclass
class FinancialEvidence(Evidence):
    account_from: str = ""
    account_to: str = ""
    amount: float = 0.0

    @property
    def evidence_type(self) -> EvidenceType:
        return EvidenceType.FINANCIAL


@dataclass
class ImageEvidence(Evidence):
    image_path: str = ""
    description: str = ""

    @property
    def evidence_type(self) -> EvidenceType:
        return EvidenceType.IMAGE


@dataclass
class DocumentEvidence(Evidence):
    document_path: str = ""
    summary: str = ""

    @property
    def evidence_type(self) -> EvidenceType:
        return EvidenceType.DOCUMENT
