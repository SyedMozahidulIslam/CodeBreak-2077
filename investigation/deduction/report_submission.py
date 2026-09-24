from __future__ import annotations

from investigation.board.board import InvestigationBoard
from investigation.deduction.models import Ending, TheoryResult
from investigation.deduction.theory_validator import TheoryValidator
from systems.core.event_bus import EventBus
from systems.core.event_types import EventType


def submit_theory(
    event_bus: EventBus,
    board: InvestigationBoard,
    case_id: str,
    endings: list,
    accused_suspect_id: str,
    attempt_number: int = 1,
) -> TheoryResult:
    result = TheoryValidator(endings).validate(board, accused_suspect_id)

    event_bus.publish(
        EventType.THEORY_SUBMITTED,
        case_id=case_id,
        accused_suspect_id=accused_suspect_id,
        rating_tier=result.rating_tier.value,
        missing_evidence_ids=sorted(result.missing_evidence_ids),
    )

    if result.matched_ending is not None:
        event_bus.publish(
            EventType.CASE_COMPLETED,
            case_id=case_id,
            ending_id=result.matched_ending.ending_id,
            rating_tier=result.matched_ending.rating_tier.value,
            xp_reward=result.matched_ending.xp_reward,
            credit_reward=result.matched_ending.credit_reward,
            no_mistakes=(attempt_number == 1),
        )

    return result
