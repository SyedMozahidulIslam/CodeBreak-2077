from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from investigation.board.board import InvestigationBoard
    from investigation.board.connection import BoardConnection


class BoardCommand(ABC):
    @abstractmethod
    def execute(self, board: InvestigationBoard) -> None: ...

    @abstractmethod
    def undo(self, board: InvestigationBoard) -> None: ...


class ConnectNodesCommand(BoardCommand):
    def __init__(self, connection_id: str, node_a_id: str, node_b_id: str) -> None:
        self.connection_id = connection_id
        self.node_a_id = node_a_id
        self.node_b_id = node_b_id

    def execute(self, board: InvestigationBoard) -> None:
        board._add_connection(self.connection_id, self.node_a_id, self.node_b_id)

    def undo(self, board: InvestigationBoard) -> None:
        board._remove_connection(self.connection_id)


class DisconnectNodesCommand(BoardCommand):
    def __init__(self, connection_id: str) -> None:
        self.connection_id = connection_id
        self._restored: Optional["BoardConnection"] = None

    def execute(self, board: InvestigationBoard) -> None:
        self._restored = board._remove_connection(self.connection_id)

    def undo(self, board: InvestigationBoard) -> None:
        if self._restored is not None:
            board._restore_connection(self._restored)
