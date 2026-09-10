import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from systems.core.engine import GameEngine
from ui.screens.board_screen import BoardScreen


def main() -> None:
    engine = GameEngine()
    engine.run(BoardScreen())


if __name__ == "__main__":
    main()
