# CodeBreak 2077

**"Every file hides a secret. Every secret changes the truth."**

A cyberpunk cyber-investigation game built in pure Python and pygame-ce. You play a digital investigator for the Cyber Intelligence Bureau (CIB), reading emails, chat logs, CCTV footage, financial records, and phone logs to build a theory of the crime on a detective board — then submit an accusation and live with the rating you earn.

No engine, no editor, no external services. Clone it, `pip install`, and it runs.

![Investigation board with a flagged contradiction](screenshots/board_screen_phase4_demo.png)

## Status

The engine and every system underneath the game are complete and tested. All seven cases are fully written and solvable end-to-end through the deduction engine. What's *not* built yet is the player-facing UI that connects them into one continuous experience — there's no menu-to-results flow you can click through yet. See [`docs/ROADMAP.md`](docs/ROADMAP.md) for exactly what that means.

| Layer | Status |
|---|---|
| Engine (loop, state machine, event bus, config, error recovery) | Done |
| Investigation mechanics (evidence, board, contradictions, theory validation) | Done |
| Progression (XP, ranks, skills, economy) | Done |
| All 7 cases (content, suspects, evidence, endings) | Done |
| Save system + achievements + statistics | Done |
| Audio system | Done (placeholder SFX, music tracks pending) |
| Player-facing screens (menu, desktop, briefing, report submission) | Not started |

**95 automated tests, all passing.**

## Quick start

```
pip install -r requirements.txt
python main.py
```

That boots a sanity-check screen proving the engine works: press `SPACE` to fire a test event, `ESC` to open a pause overlay, `F3` to toggle an FPS counter.

To see real gameplay mechanics in action:

```
python scripts/preview_board.py
```

Click a suspect, then click an evidence card to connect them on the board — connecting the two pieces of evidence tied to Case 1's hidden contradiction turns the link red live. `U` undoes.

Run the tests:

```
pip install -r requirements-dev.txt
pytest
```

## What's actually playable right now

Nothing has a "Start Game" button yet — the screens that would give you one don't exist. What *does* exist, fully working and tested, is everything underneath where that button would be:

- All 7 cases load from real JSON content and can be solved by connecting evidence and submitting an accusation, validated end-to-end in `tests/test_report_submission.py` and `tests/test_all_cases.py`.
- A real investigation board you can click around in (`scripts/preview_board.py`).
- A full save/load/achievement/statistics pipeline reacting correctly to a real playthrough.

If you want to see the deduction engine actually solve a case, the cleanest place to look is `tests/test_report_submission.py` — it plays Case 1 twice (once getting it wrong first, once getting it right immediately) and shows every system reacting correctly.

## Tech stack

Python 3.11+, [pygame-ce](https://pyga.me/), SQLite (stdlib `sqlite3`), JSON. No other dependencies for the game itself; `pytest` is a dev-only dependency for the test suite.

## Architecture, in brief

Three layers, talking only through a central event bus — UI never imports game logic, game logic never imports persistence:

```
Presentation   (ui/)            -- screens, themes, the desktop-OS visual language
Systems        (systems/)       -- event bus, progression, economy, save, achievements, audio
Investigation  (investigation/) -- evidence, the board, the deduction engine (zero pygame imports)
Data           (cases/, data/, database/) -- JSON content + SQLite persistence
```

Full rationale, design patterns, and data schemas are in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Visual language (color tokens, typography, component specs, screen layouts) is in [`docs/UI_UX_DESIGN.md`](docs/UI_UX_DESIGN.md).

## The seven cases

| Case | Tier | Suspects | Evidence | Culprit's tell |
|---|---|---|---|---|
| The Vanishing of Aria Chen | 1 | 2 | 10 | A shell-company wire and a phone call at the exact disappearance window |
| Pulse Before Launch | 2 | 2 | 10 | EXIF metadata ties a leaked photo to one device |
| The Formulation Files | 3 | 2 | 10 | A dormant vault account and an offshore wire |
| Price of Silence | 4 | 2 | 10 | Old API credentials, never revoked, used after termination |
| The Closeout Report | 5 | 2 | 10 | A pen-tester's "all accounts deactivated" report, contradicted by the audit log |
| Ghost in the Routing | 6 | 2 | 10 | An unsigned commit forty minutes after the real patch |
| Operation Black Eclipse (finale) | 7 | 3 | 12 | Ties back to Cases 1 and 5 — the architect sells both the breach and the fix |

72 evidence pieces, 15 suspects, and 21 endings (S/B/C tiers) across all seven, every one of them loadable, solvable, and covered by tests.

## Project structure

```
CodeBreak2077/
├── main.py                 # Entry point
├── systems/                # Core engine, audio, save, achievements, progression, economy, stats, cases
├── investigation/           # Evidence, the board, the deduction engine
├── ui/                      # Screens and theme tokens
├── database/                 # SQLite models + repositories
├── cases/                    # The seven cases (JSON content)
├── config/, data/, assets/   # Settings, static reference data, fonts/audio/images
├── tests/                    # 95 tests across 19 files
├── scripts/                  # Dev preview tools
└── docs/                     # This documentation
```

Full annotated tree in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#6-folder-structure).

## Documentation

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — system design, patterns, data schemas
- [`docs/UI_UX_DESIGN.md`](docs/UI_UX_DESIGN.md) — visual language and screen specs
- [`docs/INSTALLATION.md`](docs/INSTALLATION.md) — setup in detail, troubleshooting
- [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) — what you can do with it today
- [`docs/DEVELOPER_GUIDE.md`](docs/DEVELOPER_GUIDE.md) — how to extend it (new cases, screens, achievements)
- [`docs/ROADMAP.md`](docs/ROADMAP.md) — what's left

## License

No license file is included yet, which by default means all rights are reserved. If you want this repo to be usable by others (forking, learning from it, contributing), add a `LICENSE` file — MIT is a common, permissive choice for a portfolio project.
