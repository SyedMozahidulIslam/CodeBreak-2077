# User Guide

This guide covers what you can actually do with CodeBreak 2077 today. Read `docs/ROADMAP.md` alongside this if you want the gap between "what exists" and "the finished game" spelled out.

## Running the engine sanity screen

```
python main.py
```

This isn't gameplay — it's a minimal screen that proves the engine, event bus, theming, and state stack all work together. Useful if you're checking out the repo and want to confirm it runs before reading any code.

| Input | Effect |
|---|---|
| `SPACE` | Publishes a test event through the real event bus; a counter on screen increments |
| `ESC` | Pushes a pause overlay on top (the screen underneath stays visible, dimmed) |
| `ESC` (again, while paused) | Pops the overlay, returns to the screen underneath |
| `F3` | Toggles an FPS counter in the corner (works in any screen, including the one below) |
| Closing the window | Shuts down cleanly, flushing logs |

## Playing with the investigation board

```
python scripts/preview_board.py
```

This loads a small two-evidence, one-suspect scenario built from Case 1's actual contradiction (an email and a financial record that don't add up).

| Input | Effect |
|---|---|
| Click a node | Selects it (its border highlights) |
| Click a second node | Connects it to the first with a line |
| Click the same node twice | Deselects without connecting |
| `U` | Undoes the last connection |

If you connect the two evidence cards specifically, the line turns red immediately — that's the contradiction engine catching it live, not a scripted animation.

This is a developer preview, not the real board screen: there's no drag-and-drop from a tray, no pan/zoom, and no suspect tray/evidence tray UI yet. It exists to prove the board's logic and rendering work together correctly.

## How a real case actually works (today, in code)

There's no menu that lets you pick a case yet, but every case is fully real and solvable. Here's what "playing" Case 1 looks like at the code level — this is exactly what `tests/test_report_submission.py` does, just without test assertions:

```python
from investigation.board import InvestigationBoard
from investigation.deduction import submit_theory
from systems.cases.loader import CaseLoader
from systems.core.event_bus import EventBus

bus = EventBus()
case = CaseLoader().load("case_01_missing_employee")

board = InvestigationBoard(event_bus=bus)
for evidence in case.evidence_pool:
    board.add_evidence(evidence)
for suspect in case.suspects:
    board.add_suspect(suspect)

# Accuse the wrong person first.
result = submit_theory(bus, board, case.case_id, case.endings, "sus_001", attempt_number=1)
print(result.rating_tier)  # RatingTier.FAIL

# Accuse the right one.
result = submit_theory(bus, board, case.case_id, case.endings, "sus_002", attempt_number=2)
print(result.rating_tier)  # RatingTier.S
```

Every one of the seven cases works this way. If you want to see all of them solved correctly in one pass, `tests/test_all_cases.py` does exactly that, case by case.

## What a case actually contains

Each case (`cases/case_XX_name/case.json`) has:

- **2-3 suspects**, one of whom is the real culprit.
- **8-12 pieces of evidence** across seven types (emails, chat logs, CCTV stills, financial records, phone records, documents, images), some of which are red herrings that look suspicious but lead nowhere.
- **One real contradiction** — two pieces of evidence that don't add up, which may or may not directly implicate the culprit (sometimes it clears an innocent suspect of something embarrassing instead).
- **Three endings** (S/B/A/C-tier), each requiring a specific subset of evidence connected to the right suspect. More evidence in your case file means a better rating, not just a pass/fail.

## Progression, in code

Ranks (Intern through Cyber Director), XP, skills, and credits all exist and are fully tested (`tests/test_progression.py`, `tests/test_economy.py`), but nothing surfaces them visually yet — there's no HUD, skill tree screen, or shop screen. They react correctly to the same `CASE_COMPLETED` event a real case completion publishes, so once those screens exist, no system code needs to change — only the rendering.

## Settings

`config/settings.json` is created automatically on first run with defaults (1280x720, windowed, 80% master volume). Edit it directly for now — there's no in-game Settings screen yet. Keys: `resolution`, `fullscreen`, `master_volume`, `music_volume`, `sfx_volume`, `keybindings`.

## Save data

A SQLite database is created at `saves/codebreak.db` the first time `SaveManager` is used. There's no Save/Load screen yet, so this only gets populated if you write code that exercises `SaveManager` directly (as the tests do) — running `main.py` alone won't create it.
