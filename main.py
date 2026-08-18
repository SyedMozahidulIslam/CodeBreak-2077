from systems.core.engine import GameEngine
from ui.screens.main_menu_screen import MainMenuScreen


def main() -> None:
    engine = GameEngine()
    engine.run(MainMenuScreen())


if __name__ == "__main__":
    main()
