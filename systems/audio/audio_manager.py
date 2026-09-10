from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import pygame

from config.config_manager import ConfigManager
from systems.core.event_bus import Event, EventBus
from systems.core.event_types import EventType

logger = logging.getLogger("codebreak.audio")

MUSIC_DIR = Path("assets/audio/music")
SFX_DIR = Path("assets/audio/sfx")

MUSIC_FILES = {
    "main_menu": "menu_theme.ogg",
    "investigation": "investigation_ambient.ogg",
}

SFX_FILES = {
    "success": "success.wav",
    "failure": "failure.wav",
    "notification": "notification.wav",
    "click": "click.wav",
    "connect": "connect.wav",
}


class AudioManager:
    def __init__(self, event_bus: EventBus, config: ConfigManager) -> None:
        self._event_bus = event_bus
        self._config = config
        self._sfx_cache: dict = {}
        self._missing_warned: set = set()
        self._current_music: Optional[str] = None
        self._mixer_ready = self._init_mixer()

        event_bus.subscribe(EventType.CASE_COMPLETED, self._on_case_completed)
        event_bus.subscribe(EventType.THEORY_SUBMITTED, self._on_theory_submitted)
        event_bus.subscribe(EventType.NOTIFICATION_REQUESTED, self._on_notification)
        event_bus.subscribe(EventType.ACHIEVEMENT_UNLOCKED, self._on_achievement_unlocked)
        event_bus.subscribe(EventType.SETTINGS_CHANGED, self._on_settings_changed)

    def _init_mixer(self) -> bool:
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            return True
        except pygame.error as exc:
            logger.warning("Audio mixer unavailable (%s); audio will be silently skipped", exc)
            return False

    def play_music(self, track: str, loop: bool = True) -> None:
        if not self._mixer_ready or track == self._current_music:
            return

        self._current_music = track
        path = MUSIC_DIR / MUSIC_FILES.get(track, "")
        if not path.exists():
            self._warn_once(f"music:{track}", f"Music track '{track}' not found at {path}")
            return

        try:
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.set_volume(self._volume("music_volume"))
            pygame.mixer.music.play(-1 if loop else 0)
        except pygame.error as exc:
            logger.warning("Could not play music '%s': %s", track, exc)

    def play_sfx(self, name: str) -> None:
        if not self._mixer_ready:
            return
        sound = self._load_sfx(name)
        if sound is not None:
            sound.set_volume(self._volume("sfx_volume"))
            sound.play()

    def _load_sfx(self, name: str):
        if name in self._sfx_cache:
            return self._sfx_cache[name]

        path = SFX_DIR / SFX_FILES.get(name, "")
        sound = None
        if path.exists():
            try:
                sound = pygame.mixer.Sound(str(path))
            except pygame.error as exc:
                logger.warning("Could not load sound '%s': %s", name, exc)
        else:
            self._warn_once(f"sfx:{name}", f"Sound effect '{name}' not found at {path}")

        self._sfx_cache[name] = sound
        return sound

    def _volume(self, key: str) -> float:
        master = float(self._config.get("master_volume", 1.0))
        channel = float(self._config.get(key, 1.0))
        return max(0.0, min(1.0, master * channel))

    def _warn_once(self, key: str, message: str) -> None:
        if key not in self._missing_warned:
            logger.warning(message)
            self._missing_warned.add(key)

    def _on_case_completed(self, event: Event) -> None:
        self.play_sfx("success")

    def _on_theory_submitted(self, event: Event) -> None:
        if event.data.get("rating_tier") == "fail":
            self.play_sfx("failure")

    def _on_notification(self, event: Event) -> None:
        self.play_sfx("notification")

    def _on_achievement_unlocked(self, event: Event) -> None:
        self.play_sfx("notification")

    def _on_settings_changed(self, event: Event) -> None:
        if self._mixer_ready and pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self._volume("music_volume"))
