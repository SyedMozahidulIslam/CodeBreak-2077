# Installation Guide

## Requirements

- Python 3.11 or later
- `pip`
- A display (any OS with a screen works; see the headless note at the bottom if you don't have one)

No GPU, no internet connection at runtime, no external services.

## 1. Get the code

Clone or download the repository, then move into it:

```
cd CodeBreak2077
```

## 2. (Recommended) Create a virtual environment

```
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

This keeps `pygame-ce` isolated from anything else on your system. Not required, but it avoids version conflicts with other Python projects.

## 3. Install dependencies

```
pip install -r requirements.txt
```

This installs `pygame-ce` — a community-maintained, drop-in-compatible fork of `pygame`. If you'd rather use upstream `pygame`, it should work identically; the codebase only uses standard `pygame` APIs.

For running the test suite, also install the dev dependency:

```
pip install -r requirements-dev.txt
```

## 4. Run it

```
python main.py
```

This opens a window and boots `EngineTestScreen` — a sanity-check screen, not the game itself (there's no menu or case-select yet; see `docs/ROADMAP.md`). You should see "CodeBreak 2077 - Engine Online" with a pulsing cyan dot. Press `SPACE`, `ESC`, and `F3` to confirm input, the pause overlay, and the debug FPS counter all work.

To see the investigation mechanics instead:

```
python scripts/preview_board.py
```

## 5. Run the tests

```
pytest
```

You should see `95 passed`. If pygame complains about a display, see the headless note below — the tests are designed to run without a real screen.

## Fonts and music (optional, not required to run)

The game references three font roles (`display`, `heading`, `body`, `mono`) and two music tracks. None of the files are bundled — `FontBook` and `AudioManager` both fall back gracefully (a logged warning, not a crash) when they're missing, using pygame's default font and silence respectively.

If you want the real visual/audio design from `docs/UI_UX_DESIGN.md`:

- **Fonts** (SIL Open Font License, free): Orbitron, Rajdhani, Share Tech Mono — available from Google Fonts. Drop the `.ttf` files into `assets/fonts/` using the filenames in `ui/themes/typography.py`'s `FONT_FILES` dict.
- **Music**: `assets/audio/music/menu_theme.ogg` and `investigation_ambient.ogg` — source these yourself (royalty-free or licensed); nothing is synthesized for music since a procedurally generated ambient loop wouldn't represent real composition work. The five SFX (`success`, `failure`, `notification`, `click`, `connect`) already exist as synthesized placeholders in `assets/audio/sfx/`.

## Troubleshooting

**"No available video device" or similar SDL error.** You're in a headless environment (a container, CI, SSH session with no display). Set the dummy driver before running:

```
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy python main.py
```

You won't see anything on screen, but the engine will run and you can confirm it doesn't crash via the logs in `saves/logs/game.log`.

**Warnings about missing fonts/music in the console.** Expected — see the section above. The game runs correctly; it just looks plainer than the design doc until you add real assets.

**`ModuleNotFoundError: No module named 'systems'` when running pytest from somewhere other than the repo root.** `pytest.ini` sets `pythonpath = .`, which assumes pytest is invoked from the project root. Run `pytest` from `CodeBreak2077/`, not from inside a subfolder.

**Saves and logs not appearing where expected.** `config/settings.json`, `saves/codebreak.db`, and `saves/logs/game.log` are all written relative to the current working directory, not the location of `main.py`. Always run from the project root.
