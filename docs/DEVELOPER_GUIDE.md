# Developer Guide

This is the practical companion to `docs/ARCHITECTURE.md` — that document explains *why* things are shaped this way, this one is a checklist for actually changing the code without breaking the rules that keep it maintainable.

## The one rule that matters most

**`ui/` never imports from `investigation/`, `systems/`, or `database/`, and those never import `ui/` either.** Everything crosses layers through `EventBus.publish()`/`subscribe()`. If you find yourself wanting a screen to call a system method directly, or a system to reach into a screen, that's a sign the right tool is an event, not a function call. The one sanctioned exception is `GameContext`, which carries read-only references (`fonts`, `audio`, `config`) into screens for rendering — it never flows the other direction.

## Running tests while you work

```
pytest -q
```

95 tests, all of them fast (no real display needed — they run under `SDL_VIDEODRIVER=dummy`). If you're writing a test that touches `GameEngine` or anything pygame-related, set the dummy driver at the top of the file before importing pygame:

```python
import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
```

Tests that touch the filesystem (`ConfigManager`, `SaveManager`'s SQLite file, logs) should use `monkeypatch.chdir(tmp_path)` so they don't pollute the real project directory. `database.connect(":memory:")` avoids touching disk entirely for repository/save tests.

## Adding a new event type

1. Add the constant to `systems/core/event_types.py`.
2. Document who publishes it and who's expected to subscribe — this project has no central event registry beyond that file's naming, so a stray typo'd string just silently never fires anything. Test the publish/subscribe pair explicitly.

## Adding a new screen

1. Create `ui/screens/your_screen.py`, subclass `GameState`, implement `handle_event`, `update`, `draw` (and `on_enter`/`on_exit` if you need setup/teardown).
2. Use `ui/themes/colors.py`, `spacing.py`, `typography.py` for anything visual — don't hardcode hex values or font sizes.
3. If it needs audio, guard the call: `if context.audio: context.audio.play_sfx(...)` — `audio` is `Optional` on `GameContext` for backward compatibility with lightweight test contexts.
4. Push it with `state_machine.push_state(YourScreen())`, or swap entirely with `change_state()`.
5. Write a smoke test following `tests/test_board_screen_smoke.py` or `tests/test_engine_smoke.py` as a template — boot a real `GameEngine`, push your screen, simulate input, assert on the result.

## Adding a new evidence type

Only do this if an existing type (`EmailEvidence`, `ChatLogEvidence`, `CCTVEvidence`, `PhoneRecordEvidence`, `FinancialEvidence`, `ImageEvidence`, `DocumentEvidence`) genuinely doesn't fit.

1. Add the value to `EvidenceType` in `investigation/evidence/base.py`.
2. Add the dataclass to `investigation/evidence/types.py`, subclassing `Evidence`, with its own fields (all with defaults, since dataclass inheritance requires that).
3. Register it in `_EVIDENCE_CLASSES` in `systems/cases/factories.py` so `CaseLoader` knows how to build it from JSON.
4. Re-export it from `investigation/evidence/__init__.py`.

## Adding a new case

Case 1 (`cases/case_01_missing_employee/`) is the reference template. The shape:

```
cases/case_XX_name/
├── case.json              # index: metadata, suspect/evidence refs, contradiction rules, endings
├── suspects/
│   └── sus_00N.json        # {suspect_id, name, role, bio}
└── evidence/
    ├── emails/ev_NNN.json
    ├── chats/ev_NNN.json
    ├── cctv/ev_NNN.json
    ├── financial/ev_NNN.json
    ├── phone/ev_NNN.json
    ├── documents/ev_NNN.json
    └── images/ev_NNN.json
```

Each evidence file holds only the type-specific payload (`sender`/`recipient`/`body` for an email, etc.) plus the universal fields (`evidence_id`, `title`, `timestamp`, `source`) — **not** `is_red_herring`, which lives in `case.json`'s `evidence_pool` index and gets merged in by the loader.

`case.json` itself needs: `case_id`, `title`, `tier`, `unlock_requirements` (`min_rank`, `previous_case`), `briefing` (`client`, `incident_date`, `summary`), `suspects` (id + `file_ref`), `evidence_pool` (id, `type`, `file_ref`, `is_red_herring`), `contradiction_rules` (id, `evidence_ids` pair, `explanation_key`), and `endings` (id, `required_accusation`, `required_evidence`, `rating_tier`, `xp_reward`, `credit_reward`).

After writing it, add it to `EXPECTED_CULPRITS` in `tests/test_all_cases.py` so it's covered by the same generic load/contradiction/playthrough/wrong-accusation checks every other case gets for free.

## Adding an achievement

No code change needed for most cases — add an entry to `data/achievements.json` referencing one of the existing condition strategies in `systems/achievements/conditions.py` (`rating_tier_at_least`, `event_count_at_least`, `field_equals`, `rating_tier_count_at_least`, `flagged_perfect`). Only write a new condition function if none of those shapes fit; register it in `CONDITION_CHECKS`.

## Adding a shop item

Add an entry to `data/shop_items.json`: `item_id`, `name`, `cost`, `category`. No code change.

## A subtle gotcha: event subscription order

`SaveManager.save_to_slot()` reads `XPTracker.xp` and `CreditManager.balance` *at the moment it's called*. When `CASE_COMPLETED` triggers an autosave, that works correctly only because `XPTracker` and `CreditManager` were constructed (and therefore subscribed) *before* `SaveManager` — `EventBus` calls handlers in subscription order, so by the time `SaveManager`'s handler runs, the values it reads are already updated. If you ever reorder system construction in a composition root, double check this still holds, or better, make the dependency explicit rather than relying on ordering. This is documented here because it's exactly the kind of thing that works fine for months and then breaks mysteriously when someone reorders an unrelated import.

## Style

- PEP 8, type hints on public functions, `from __future__ import annotations` everywhere for forward-reference-friendly typing.
- `dataclasses` for plain data (`Evidence`, `Suspect`, `Ending`, database records) — not classes with manual `__init__`.
- Minimal inline comments. If code needs a comment to be understood, prefer renaming things until it doesn't; reserve comments for genuinely non-obvious *why*, not *what*.
- Exceptions: raise from the hierarchy in `systems/core/exceptions.py` (`CaseLoadError`, `CaseValidationError`, `ConfigError`, etc.), not bare `Exception`.

## What's intentionally not built yet

See `docs/ROADMAP.md` for the full list, but the short version: every backend system is done and tested; the screens that would let a player actually click through a menu, pick a case, read a briefing, work through a real Desktop UI, and submit a report don't exist yet. `BoardScreen` and `EngineTestScreen` are deliberately disposable proof-of-concept screens, not the final UI.
