# Roadmap

## Complete

Everything below is built, wired together through the event bus, and covered by the test suite (95 tests, 19 files) — not partial, not stubbed.

- **Engine** — game loop, stack-based state machine, event bus, config management, exception recovery (a broken screen drops into an error screen instead of crashing), an F3 debug overlay.
- **Investigation mechanics** — seven evidence types, suspects, a board with Command-pattern undo/redo, a contradiction engine, and a theory validator that grades partial evidence chains (S/B/C tiers), not just pass/fail.
- **Progression** — XP curve, the 7-rank ladder, a 5-skill tree, credits, and a shop catalog.
- **All seven cases** — 15 suspects, 72 evidence pieces, 21 endings, each with a real (sometimes misleading) contradiction. `CaseLoader` reads them from JSON; nothing is hardcoded in Python.
- **Save system** — SQLite-backed, multiple slots, autosave on case completion, a Repository layer per table.
- **Achievements & statistics** — five achievements driven by declarative JSON conditions, a statistics tracker counting solves/mistakes/best score.
- **Audio** — three independently-volumed channels, five synthesized placeholder SFX, event-driven playback.
- **Documentation** — this set of docs.

## Not started: the player-facing experience

This is the gap between "a complete, tested engine" and "a game you can hand someone to play." None of it requires new systems — every screen below is UI work that reads from and publishes to systems that already exist and already work.

| Screen | Depends on (already built) |
|---|---|
| Boot/Splash, Main Menu | Nothing new — pure UI |
| Case Select | `CaseLoader.list_available_cases()`, `unlock_requirements` on each case, current `Rank` |
| Briefing | `Case.briefing` |
| Desktop hub (status bar, icon grid, dock) | The `GameState` stack already supports this exact layering |
| Email / Chat / Browser / Employee Database / Evidence Folder apps | `Evidence` subtypes already carry all the content these would render |
| Investigation Board (real version) | `InvestigationBoard`, `BoardScreen` exists as a proof of concept — needs drag-and-drop from trays, pan/zoom, the full visual spec from `docs/UI_UX_DESIGN.md` |
| Interrogation | Not designed in code yet — would need a dialogue-tree data shape, similar to how `Case` is structured |
| Report Submission | `submit_theory()` already does the actual work; this screen is the suspect-picker + evidence-chip UI in front of it |
| Results/Rating | `TheoryResult`, `Ending.xp_reward`/`credit_reward`, `ACHIEVEMENT_UNLOCKED` events |
| Pause, Settings, Save/Load, Achievements, Statistics Dashboard, Shop | Every underlying system exists (`ConfigManager`, `SaveManager`, `AchievementManager`, `StatisticsTracker`, `ShopManager`) — these are read/write UI in front of working logic |

## Not started: game modes

The original design called for three modes. Only the implicit "Story Mode" shape exists (one case at a time, in rank order). **Quick Case Mode** (short random investigations) and **Challenge Mode** (timed) have no code yet — they'd likely reuse the same `Case`/`InvestigationBoard`/`submit_theory` pipeline with different framing and a timer, rather than needing new systems.

## Not started: forensics tools / skill effects

`investigation/forensics_tools/` exists as an empty package, reserved since Phase 1. The 5 skills (Observation, Deduction, Digital Forensics, Interrogation, Intelligence) currently only track levels — none of them *do* anything yet. The intended shape (Strategy pattern, one class per tool) was designed but never implemented, since there's no UI yet for a player to use a tool against.

## Known gaps in what exists

- **No real fonts or music shipped.** Both fall back gracefully (this is by design, not a bug), but the visual/audio identity from `docs/UI_UX_DESIGN.md` won't be visible until real assets are added.
- **No virtual-canvas scaling/letterboxing.** The engine renders directly at whatever resolution is configured; the responsive-layout approach from the architecture doc hasn't been needed yet because there's no content-heavy screen to test it against.
- **The `no_mistakes` achievement flag and `THEORY_SUBMITTED` event are real and tested, but only `submit_theory()` produces them.** Once Report Submission exists, that's the only caller it needs.
- **`AchievementManager` and `SaveManager` each track "active slot" independently.** They're synced manually by whoever constructs them (see `tests/test_report_submission.py` for the pattern). A real composition root, once one exists, should wire this once rather than relying on every call site doing it correctly.

## Suggested order for picking this back up

1. Desktop hub + Main Menu + Case Select — gets you from boot to "looking at a case."
2. Real Investigation Board (extend `BoardScreen`, don't restart it) + Evidence Folder.
3. Report Submission + Results — closes the loop using `submit_theory()`, which is already done.
4. Everything else (Settings, Save/Load, Achievements, Statistics, Shop) — straightforward read/write UI once the above exists, in any order.
5. Real fonts, real music, Quick Case / Challenge modes, forensics tool effects.
