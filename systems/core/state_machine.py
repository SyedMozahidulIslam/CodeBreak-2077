from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import pygame

from systems.core.event_types import EventType

if TYPE_CHECKING:
    from systems.core.context import GameContext
    from systems.core.state import GameState

logger = logging.getLogger("codebreak.state_machine")


class StateMachine:
    def __init__(self, context: GameContext) -> None:
        self._context = context
        self._stack: list[GameState] = []

    @property
    def current(self) -> GameState | None:
        return self._stack[-1] if self._stack else None

    def push_state(self, state: GameState) -> None:
        self._stack.append(state)
        state.on_enter(self._context)
        self._context.event_bus.publish(EventType.STATE_CHANGED, state=type(state).__name__)
        logger.debug("Entered %s", type(state).__name__)

    def pop_state(self) -> None:
        if not self._stack:
            return
        state = self._stack.pop()
        state.on_exit()
        logger.debug("Exited %s", type(state).__name__)
        if self._stack:
            self._context.event_bus.publish(EventType.STATE_CHANGED, state=type(self._stack[-1]).__name__)

    def change_state(self, state: GameState) -> None:
        while self._stack:
            self.pop_state()
        self.push_state(state)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.current:
            self.current.handle_event(event)

    def update(self, dt: float) -> None:
        if self.current:
            self.current.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        for state in self._stack:
            state.draw(surface)
