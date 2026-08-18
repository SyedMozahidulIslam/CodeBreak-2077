# CodeBreak 2077 — Architecture Document

**Note:** this document was rebuilt during Phase 9 after the original was accidentally deleted by an `rm -rf` during Phase 4's packaging step. This version reflects the actual final implementation across all 8 build phases, not just the original plan — a few details evolved during implementation (noted inline where relevant) and this version is authoritative.

> "Every file hides a secret. Every secret changes the truth."

---

## 1. Vision

CodeBreak 2077 is a 2D, UI-driven cyber-investigation game: the player never controls a character in a world, they control a workstation. The entire game is meant to be experienced through a simulated futuristic OS — desktop, email client, chat app, browser, employee database, evidence folder, investigation board (the Desktop hub and its apps remain unbuilt — see `docs/ROADMAP.md`). Three consequences shaped every decision below:

1. **The UI is not a layer on top of the game — the UI is the game.** `ui/` carries the same architectural weight as the gameplay logic.
2. **Content (cases) is decoupled from code.** All seven cases are pure JSON, loaded and validated by one `CaseLoader`. Adding an eighth case never requires touching engine code.
3. **The deduction logic is pure and testable.** `investigation/deduction/` has zero pygame imports. It's the intellectual core of the project and the most heavily tested part of it.

### Non-goals (still true)

No real networking, no 3D, no real cybersecurity techniques (every "forensic tool" is a fictionalized skill-check abstraction), no voice acting.

---

## 2. Architectural style — implemented as designed

Layered + event-driven, exactly as planned. The hard rule held for all 8 phases: `ui/` never imports from `investigation/`, `systems/`, or `database/`. Everything crosses layers through `EventBus.publish()`/`subscribe()`.

```
Presentation   ui/                — screens, themes (colors, spacing, typography)
Systems        systems/           — core (engine/state machine/event bus), audio, save,
                                     achievements, progression, economy, stats, cases
Investigation  investigation/     — evidence, suspect, board, deduction (zero pygame imports)
Data           cases/, data/, database/ — JSON content + SQLite persistence
```

### State flow, as built

`EngineTestScreen` and `BoardScreen` are the only two real `GameState` implementations that exist; the rest of the originally planned flow (Main Menu → Case Select → Briefing → Desktop → apps → Interrogation → Report Submission → Results) is designed but not built. `ErrorScreen` was added in Phase 8 as a safety net the original design didn't have — any unhandled exception in a screen's `update`/`draw`/`handle_event` drops the engine into it instead of crashing.

---

## 3. Design patterns — confirmed in actual use

| Pattern | Where | Confirmed by |
|---|---|---|
| State (stack-based) | `systems/core/state_machine.py` | `tests/test_state_machine.py` |
| Observer / event bus | Every cross-system interaction | All 19 test files, indirectly |
| Repository | `database/repositories/*.py` (4 of them) | `tests/test_database_repositories.py` |
| Factory method | `systems/cases/factories.py` | `tests/test_case_loader.py` |
| Strategy | `systems/achievements/conditions.py` — each achievement names a condition function | `tests/test_achievements.py` |
| Command (+ undo/redo) | `investigation/board/commands.py` | `tests/test_board.py` |
| Dependency injection | `GameContext`, passed explicitly into every state and most systems | Throughout |

ECS was deliberately not used, as planned — a few dozen typed domain objects never justified the overhead.

---

## 4. Core systems — as built

### 4.1 Core Engine (`systems/core/`)
`GameEngine` (boot sequence: logging → pygame.init → config → display → event bus/fonts/audio → context → state machine), `StateMachine` (stack; `update`/`handle_event` hit only the top, `draw` renders the whole stack — this is what lets a pause overlay dim the screen underneath instead of replacing it), `EventBus`, `GameContext`. `GameEngine._run_one_frame()` wraps update/draw/handle_event in per-call try/except, recovering into `ErrorScreen` rather than crashing (added in Phase 8, not in the original plan).

### 4.2 UI (`ui/`)
`themes/colors.py`, `spacing.py`, `typography.py` hold the literal tokens from `docs/UI_UX_DESIGN.md`. `FontBook` caches loaded fonts and falls back to pygame's default font with a once-per-role logged warning if a file is missing — true for all three font roles, since no real font files are bundled. `screens/board_screen.py` is the one real screen built against the actual visual spec (purple suspect rings, cyan evidence cards, red contradiction lines); `screens/engine_test_screen.py` and `screens/error_screen.py` are functional but not visually designed.

### 4.3 Audio (`systems/audio/`)
`AudioManager`, added in Phase 8. Three independently-volumed channels (master/music/sfx, read from `config/settings.json`). Reacts to `CASE_COMPLETED` (success), `THEORY_SUBMITTED` with a `fail` tier (failure), `NOTIFICATION_REQUESTED`/`ACHIEVEMENT_UNLOCKED` (notification blip). Five SFX exist as synthesized placeholder `.wav` files (pure stdlib sine-wave generation — no external assets); music tracks are referenced but not bundled, since a synthesized ambient loop wouldn't represent real composition work.

### 4.4 Cases (`systems/cases/`)
Added in Phase 6 — missing from the original folder tree's text but not its diagram, an inconsistency caught and fixed during implementation. `CaseLoader.load(case_id)` reads `case.json`, follows `file_ref` pointers to suspect/evidence files, and builds typed objects via `factories.py`. `list_available_cases()` was added in Phase 8 as a small Case-Select-screen enabler.

### 4.5 Evidence (`investigation/evidence/`)
`Evidence` base + 7 subtypes exactly as planned (Email, ChatLog, CCTV, PhoneRecord, Financial, Image, Document), all plain dataclasses.

### 4.6 Suspect (`investigation/suspect.py`)
A single module directly under `investigation/`, not a subpackage — it never had a planned home in the original folder tree; one small dataclass didn't justify one.

### 4.7 Board (`investigation/board/`)
`InvestigationBoard`, `BoardNode`/`NodeKind`, `BoardConnection`, and the Command pattern (`ConnectNodesCommand`/`DisconnectNodesCommand`) backing real undo/redo. Publishes `EVIDENCE_COLLECTED` on `add_evidence()` and `CONTRADICTION_FOUND` on `mark_contradiction()`.

### 4.8 Deduction (`investigation/deduction/`)
`ContradictionEngine` (pair lookup against case-defined rules), `TheoryValidator` (sorts endings best-tier-first, returns the best fully-satisfied one, or the closest partial match with the specific missing evidence IDs). `report_submission.py`'s `submit_theory()` was added in Phase 8 — it's the one function that finally ties `TheoryValidator`'s pure result to `THEORY_SUBMITTED`/`CASE_COMPLETED` events, closing a gap that existed from Phase 4 through Phase 7.

### 4.9 Progression (`systems/progression/`)
`Rank` (7-tier enum + XP thresholds as plain Python constants — deliberately not JSON, since rank balance is core design, not swappable content), `XPTracker` (self-subscribes to `CASE_COMPLETED`), `SkillTree`/`SkillManager` (5 skills, max level 3, one skill point per rank-up).

### 4.10 Economy (`systems/economy/`)
`CreditManager` (mirrors `XPTracker`'s self-subscription pattern), `ShopManager` with its catalog loaded from `data/shop_items.json` (unlike ranks, a catalog is exactly the kind of content worth editing without touching code) — same missing-file fallback pattern as `FontBook`/`ConfigManager`.

### 4.11 Save (`systems/save/`)
`SaveManager`, backed by `database/repositories`. Holds direct references to `XPTracker`/`CreditManager` (a snapshot needs current state, not a change stream) but reacts to `CASE_COMPLETED` via the event bus to autosave. Ensures its own `players` row exists on construction — a real foreign-key bug caught and fixed during Phase 7's own test run.

### 4.12 Achievements (`systems/achievements/`)
`AchievementManager` + `conditions.py`. Each achievement definition names a condition strategy; the manager doesn't interpret any of them itself. Five achievements ship in `data/achievements.json`; one (`perfect_investigation`) depends on a `no_mistakes` flag that only `submit_theory()` currently produces.

### 4.13 Statistics (`systems/stats/`)
`StatisticsTracker`, deliberately unaware of SQL — it counts, and hands a `StatisticsRecord` snapshot to whoever wants to persist it.

### Event catalog (`systems/core/event_types.py`), as actually used

`CASE_STARTED`, `CASE_COMPLETED`, `EVIDENCE_COLLECTED`, `CONTRADICTION_FOUND`, `THEORY_SUBMITTED`, `XP_GAINED`, `RANK_UP`, `ACHIEVEMENT_UNLOCKED`, `PURCHASE_MADE`, `SAVE_REQUESTED`, `SAVE_COMPLETED`, `SETTINGS_CHANGED`, `NOTIFICATION_REQUESTED`, `STATE_CHANGED`. `CASE_STARTED` and `SAVE_REQUESTED` are defined but have no publisher yet — they're reserved for the Briefing and Pause/Settings screens respectively.

---

## 5. Data architecture — as implemented

JSON for designer-authored content (`cases/`, `data/achievements.json`, `data/shop_items.json`); SQLite for player state, behind the Repository layer. This split held exactly as planned, with one refinement: rank thresholds and skill definitions stayed as Python constants rather than moving to `data/ranks.json`/`data/skills.json` as the original plan suggested — they're core balance, not editable content, and a JSON-loading layer for them would have added file I/O at import time for no real benefit.

### Case schema (implemented exactly as `cases/case_01_missing_employee/case.json` shows)

```json
{
  "case_id": "case_01_missing_employee",
  "title": "...", "tier": 1,
  "unlock_requirements": { "min_rank": "Intern", "previous_case": null },
  "briefing": { "client": "...", "incident_date": "...", "summary": "..." },
  "suspects": [{ "suspect_id": "sus_001", "file_ref": "suspects/sus_001_marcus_voss.json" }],
  "evidence_pool": [{ "id": "ev_001", "type": "email", "file_ref": "evidence/emails/ev_001.json", "is_red_herring": false }],
  "contradiction_rules": [{ "id": "rule_01", "evidence_ids": ["ev_002", "ev_009"], "explanation_key": "..." }],
  "endings": [{ "id": "ending_true", "required_accusation": "sus_002", "required_evidence": [...], "rating_tier": "S", "xp_reward": 400, "credit_reward": 250 }]
}
```

`is_red_herring` lives only in the index entry, not the evidence file itself — the loader merges it in. `xp_reward`/`credit_reward` on endings were added during Phase 6 to feed Phase 5's progression events; they weren't in the original Phase 1 schema sketch.

### SQLite schema (`database/connection.py`, implemented exactly as planned)

`players`, `save_slots`, `case_progress`, `achievements_unlocked`, `statistics` — five tables, `CREATE TABLE IF NOT EXISTS` run on every connection, foreign keys enforced (`PRAGMA foreign_keys = ON`).

---

## 6. Folder structure — actual, final

```
CodeBreak2077/
├── main.py
├── requirements.txt, requirements-dev.txt, pytest.ini, .gitignore
│
├── assets/
│   ├── audio/{music (empty),sfx (5 synthesized .wav files),voice (empty)}/
│   ├── images/{ui,backgrounds,characters,evidence}/ (empty - no art yet)
│   └── fonts/ (empty - no real fonts bundled)
│
├── saves/                       # SQLite db + logs, created at runtime
├── data/                        # achievements.json, shop_items.json
├── cases/                       # all 7 cases, fully written
│
├── ui/
│   ├── screens/                  # engine_test_screen.py, board_screen.py, error_screen.py
│   └── themes/                   # colors.py, spacing.py, typography.py
│   # components/, animations/ exist as empty packages - no reusable widgets built yet
│
├── systems/
│   ├── core/                      # engine, state_machine, state, context, event_bus,
│   │                                event_types, exceptions, logger
│   ├── audio/                     # audio_manager.py
│   ├── save/                      # save_manager.py
│   ├── achievements/               # achievement_manager.py, conditions.py
│   ├── progression/                 # ranks.py, xp_tracker.py, skills.py, skill_manager.py
│   ├── economy/                     # credit_manager.py, shop.py
│   ├── stats/                       # statistics_tracker.py
│   └── cases/                       # case.py, factories.py, loader.py
│
├── investigation/
│   ├── board/                     # board.py, node.py, connection.py, commands.py
│   ├── evidence/                  # base.py, types.py
│   ├── deduction/                  # models.py, contradiction_engine.py,
│   │                                 theory_validator.py, report_submission.py
│   ├── forensics_tools/            # empty package, reserved
│   └── suspect.py
│
├── player/                       # empty package, reserved
├── database/
│   ├── models/                    # records.py
│   └── repositories/               # one file per table, 4 total
├── config/                        # config_manager.py, settings.json
├── docs/                          # this set of documents
├── screenshots/                    # 2 real screenshots from Phases 4 and 8
├── scripts/                        # preview_board.py (not in the original plan -
│                                       added in Phase 3 as a dev convenience)
└── tests/                         # 19 files, 95 tests
```

---

## 7. Engineering standards — as implemented

Exception hierarchy (`systems/core/exceptions.py`): `CodeBreakError` base, `CaseLoadError`, `CaseValidationError`, `SaveCorruptionError` (defined, not yet triggered by any code path), `AssetLoadError` (defined, not yet used), `ConfigError`. Logging via `RotatingFileHandler` to `saves/logs/game.log`. `ConfigManager` merges loaded JSON over defaults (`{**DEFAULTS, **loaded}`) for forward compatibility. Testing: 95 tests, all running headless under `SDL_VIDEODRIVER=dummy`, using `:memory:` SQLite and `tmp_path`/`monkeypatch.chdir` for filesystem isolation.

## 8. What's not built

See `docs/ROADMAP.md` for the full breakdown — in short, every system above is real and tested; the screens that would let a player navigate between them are not.
