from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BoardConnection:
    connection_id: str
    node_a_id: str
    node_b_id: str
    is_contradiction: bool = False

    def involves(self, node_id: str) -> bool:
        return node_id in (self.node_a_id, self.node_b_id)

    def other_end(self, node_id: str) -> str:
        return self.node_b_id if node_id == self.node_a_id else self.node_a_id
