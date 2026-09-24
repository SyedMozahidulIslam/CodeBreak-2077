from __future__ import annotations

import uuid
from typing import Optional

from investigation.board.commands import BoardCommand, ConnectNodesCommand, DisconnectNodesCommand
from investigation.board.connection import BoardConnection
from investigation.board.node import BoardNode, NodeKind
from investigation.evidence.base import Evidence
from investigation.suspect import Suspect
from systems.core.event_bus import EventBus
from systems.core.event_types import EventType


class InvestigationBoard:
    def __init__(self, event_bus: Optional[EventBus] = None) -> None:
        self._event_bus = event_bus
        self.nodes: dict[str, BoardNode] = {}
        self.connections: dict[str, BoardConnection] = {}
        self._undo_stack: list[BoardCommand] = []
        self._redo_stack: list[BoardCommand] = []

    def add_suspect(self, suspect: Suspect, position: tuple[float, float] = (0.0, 0.0)) -> BoardNode:
        node = BoardNode(node_id=suspect.suspect_id, kind=NodeKind.SUSPECT, payload=suspect, position=position)
        self.nodes[node.node_id] = node
        return node

    def add_evidence(self, evidence: Evidence, position: tuple[float, float] = (0.0, 0.0)) -> BoardNode:
        node = BoardNode(node_id=evidence.evidence_id, kind=NodeKind.EVIDENCE, payload=evidence, position=position)
        self.nodes[node.node_id] = node
        if self._event_bus:
            self._event_bus.publish(EventType.EVIDENCE_COLLECTED, evidence_id=evidence.evidence_id)
        return node

    def connect(self, node_a_id: str, node_b_id: str) -> str:
        if node_a_id not in self.nodes or node_b_id not in self.nodes:
            raise ValueError("Both nodes must exist on the board before connecting them")

        connection_id = str(uuid.uuid4())
        command = ConnectNodesCommand(connection_id, node_a_id, node_b_id)
        self._apply(command)
        return connection_id

    def disconnect(self, connection_id: str) -> None:
        command = DisconnectNodesCommand(connection_id)
        self._apply(command)

    def undo(self) -> None:
        if not self._undo_stack:
            return
        command = self._undo_stack.pop()
        command.undo(self)
        self._redo_stack.append(command)

    def redo(self) -> None:
        if not self._redo_stack:
            return
        command = self._redo_stack.pop()
        command.execute(self)
        self._undo_stack.append(command)

    def connections_for(self, node_id: str) -> list[BoardConnection]:
        return [c for c in self.connections.values() if c.involves(node_id)]

    def mark_contradiction(self, connection_id: str, is_contradiction: bool = True) -> None:
        connection = self.connections.get(connection_id)
        if connection is None:
            return
        connection.is_contradiction = is_contradiction
        if self._event_bus and is_contradiction:
            self._event_bus.publish(EventType.CONTRADICTION_FOUND, connection_id=connection_id)

    def _apply(self, command: BoardCommand) -> None:
        command.execute(self)
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def _add_connection(self, connection_id: str, node_a_id: str, node_b_id: str) -> None:
        self.connections[connection_id] = BoardConnection(connection_id, node_a_id, node_b_id)

    def _remove_connection(self, connection_id: str) -> Optional[BoardConnection]:
        return self.connections.pop(connection_id, None)

    def _restore_connection(self, connection: BoardConnection) -> None:
        self.connections[connection.connection_id] = connection
