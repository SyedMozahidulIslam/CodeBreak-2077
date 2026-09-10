from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import pygame

from config.config_manager import ConfigManager
from systems.audio.audio_manager import AudioManager
from systems.core.event_bus import EventBus
from ui.themes.typography import FontBook

if TYPE_CHECKING:
    from player.session import PlayerSession
    from systems.core.state_machine import StateMachine


@dataclass
class GameContext:
    screen: pygame.Surface
    event_bus: EventBus
    config: ConfigManager
    fonts: FontBook
    audio: AudioManager | None = None
    session: "PlayerSession | None" = None
    state_machine: StateMachine | None = None
