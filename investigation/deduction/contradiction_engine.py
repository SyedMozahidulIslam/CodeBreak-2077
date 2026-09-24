from __future__ import annotations

from typing import Optional

from investigation.board.board import InvestigationBoard
from investigation.deduction.models import ContradictionRule


class ContradictionEngine:
    def __init__(self, rules: list[ContradictionRule]) -> None:
        self._rules_by_pair: dict[frozenset[str], ContradictionRule] = {
            frozenset(rule.evidence_ids): rule for rule in rules
        }

    def check_connection(self, evidence_id_a: str, evidence_id_b: str) -> Optional[ContradictionRule]:
        return self._rules_by_pair.get(frozenset((evidence_id_a, evidence_id_b)))

    def scan_board(self, board: InvestigationBoard) -> list[tuple[str, ContradictionRule]]:
        found: list[tuple[str, ContradictionRule]] = []
        for connection in board.connections.values():
            rule = self.check_connection(connection.node_a_id, connection.node_b_id)
            if rule:
                found.append((connection.connection_id, rule))
        return found

    def apply_to_board(self, board: InvestigationBoard) -> list[tuple[str, ContradictionRule]]:
        found = self.scan_board(board)
        for connection_id, _ in found:
            board.mark_contradiction(connection_id, True)
        return found
