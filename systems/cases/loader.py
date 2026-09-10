from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from investigation.deduction.models import ContradictionRule, Ending, RatingTier
from systems.cases.case import Case, CaseBriefing
from systems.cases.factories import build_evidence, build_suspect
from systems.core.exceptions import CaseLoadError, CaseValidationError

CASES_ROOT = Path("cases")

_REQUIRED_CASE_KEYS = {"case_id", "title", "tier", "briefing", "suspects", "evidence_pool", "endings"}


class CaseLoader:
    def __init__(self, cases_root: Path = CASES_ROOT) -> None:
        self._cases_root = cases_root

    def list_available_cases(self) -> list[str]:
        if not self._cases_root.exists():
            return []
        return sorted(p.parent.name for p in self._cases_root.glob("*/case.json"))

    def load(self, case_id: str) -> Case:
        case_dir = self._cases_root / case_id
        case_file = case_dir / "case.json"

        if not case_file.exists():
            raise CaseLoadError(f"No case.json found for '{case_id}' at {case_file}")

        data = self._read_json(case_file)
        self._validate_case_shape(data, case_file)

        briefing_data = data["briefing"]
        briefing = CaseBriefing(
            client=briefing_data["client"],
            incident_date=briefing_data["incident_date"],
            summary=briefing_data.get("summary", ""),
        )

        suspects = []
        for entry in data["suspects"]:
            suspect_data = self._read_json(case_dir / entry["file_ref"])
            suspects.append(build_suspect(suspect_data))

        evidence_pool = []
        for entry in data["evidence_pool"]:
            file_data = self._read_json(case_dir / entry["file_ref"])
            file_data["is_red_herring"] = entry.get("is_red_herring", False)
            evidence_pool.append(build_evidence(entry["type"], file_data))

        contradiction_rules = [
            ContradictionRule(
                rule_id=entry["id"],
                evidence_ids=tuple(entry["evidence_ids"]),
                explanation=entry["explanation_key"],
            )
            for entry in data.get("contradiction_rules", [])
        ]

        endings = [
            Ending(
                ending_id=entry["id"],
                required_accusation=entry["required_accusation"],
                required_evidence_ids=frozenset(entry["required_evidence"]),
                rating_tier=RatingTier(entry["rating_tier"]),
                xp_reward=entry.get("xp_reward", 0),
                credit_reward=entry.get("credit_reward", 0),
            )
            for entry in data["endings"]
        ]

        unlock = data.get("unlock_requirements", {})

        return Case(
            case_id=data["case_id"],
            title=data["title"],
            tier=data["tier"],
            min_rank=unlock.get("min_rank", "Intern"),
            previous_case=unlock.get("previous_case"),
            briefing=briefing,
            suspects=suspects,
            evidence_pool=evidence_pool,
            contradiction_rules=contradiction_rules,
            endings=endings,
        )

    def _read_json(self, path: Path) -> dict[str, Any]:
        try:
            with path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError as exc:
            raise CaseLoadError(f"Missing file: {path}") from exc
        except json.JSONDecodeError as exc:
            raise CaseLoadError(f"Malformed JSON in {path}: {exc}") from exc

    def _validate_case_shape(self, data: dict[str, Any], source: Path) -> None:
        missing = _REQUIRED_CASE_KEYS - data.keys()
        if missing:
            raise CaseValidationError(f"{source} is missing required keys: {sorted(missing)}")
