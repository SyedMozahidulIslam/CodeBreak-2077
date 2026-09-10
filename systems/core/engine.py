from __future__ import annotations

import logging

import pygame

from config.config_manager import ConfigManager
from player.session import PlayerSession
from systems.audio.audio_manager import AudioManager
from systems.core.context import GameContext
from systems.core.event_bus import EventBus
from systems.core.logger import setup_logging
from systems.core.state import GameState
from systems.core.state_machine import StateMachine
from ui.screens.error_screen import ErrorScreen
from ui.themes.colors import Color
from ui.themes.typography import FontBook, FontSize

logger = logging.getLogger("codebreak.engine")


class GameEngine:
    def __init__(self) -> None:
        setup_logging()
        pygame.init()

        self.config = ConfigManager()
        width, height = self.config.get("resolution", [1280, 720])
        flags = pygame.FULLSCREEN if self.config.get("fullscreen") else 0
        self.screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption("CodeBreak 2077")

        self.clock = pygame.time.Clock()
        self.event_bus = EventBus()
        self.fonts = FontBook()
        self.audio = AudioManager(self.event_bus, self.config)
        self.session = PlayerSession(self.event_bus)

        self.context = GameContext(
            screen=self.screen,
            event_bus=self.event_bus,
            config=self.config,
            fonts=self.fonts,
            audio=self.audio,
            session=self.session,
        )
        self.state_machine = StateMachine(self.context)
        self.context.state_machine = self.state_machine

        self._running = False
        self._show_debug_overlay = False

    def run(self, initial_state: GameState) -> None:
        self.state_machine.push_state(initial_state)
        self._running = True
        logger.info("CodeBreak 2077 engine started")

        while self._running:
            dt = self.clock.tick(60) / 1000.0
            self._run_one_frame(dt)

        self.shutdown()

    def _run_one_frame(self, dt: float) -> None:
        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                self._running = False
                return
            if pygame_event.type == pygame.KEYDOWN and pygame_event.key == pygame.K_F3:
                self._show_debug_overlay = not self._show_debug_overlay
                continue
            self._safe_handle_event(pygame_event)

        self._safe_update(dt)
        self._safe_draw()
        pygame.display.flip()

    def _safe_handle_event(self, pygame_event: pygame.event.Event) -> None:
        try:
            self.state_machine.handle_event(pygame_event)
        except Exception as exc:
            self._recover_from_error(exc)

    def _safe_update(self, dt: float) -> None:
        try:
            self.state_machine.update(dt)
        except Exception as exc:
            self._recover_from_error(exc)

    def _safe_draw(self) -> None:
        try:
            self.screen.fill(Color.BG_VOID)
            self.state_machine.draw(self.screen)
        except Exception as exc:
            self._recover_from_error(exc)
            self.screen.fill(Color.BG_VOID)
            self.state_machine.draw(self.screen)

        if self._show_debug_overlay:
            self._draw_debug_overlay()

    def _recover_from_error(self, exc: Exception) -> None:
        logger.exception("Unhandled error in game loop, switching to the error screen")
        self.state_machine.change_state(ErrorScreen(str(exc)))

    def _draw_debug_overlay(self) -> None:
        font = self.fonts.get("mono", FontSize.CAPTION)
        fps_text = font.render(f"FPS: {self.clock.get_fps():.1f}", True, Color.SUCCESS)
        self.screen.blit(fps_text, (self.screen.get_width() - fps_text.get_width() - 12, 8))

    def shutdown(self) -> None:
        logger.info("Shutting down")
        pygame.quit()
