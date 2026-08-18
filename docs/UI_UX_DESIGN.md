# CodeBreak 2077 — UI/UX Design Document

**Note:** rebuilt during Phase 9 after the original was accidentally deleted by an `rm -rf` during Phase 4's packaging step. The color, typography, and spacing tokens below are copied directly from the actual source files (`ui/themes/`), so they're exact, not reconstructed from memory. The screen specs reflect the original design intent; only the Investigation Board has actually been built against them — see the status note in each section.

---

## 1. Visual identity

Cyberpunk detective theme. Near-black backgrounds, two disciplined neon accents — cyan for primary/active, purple for secondary/suspect-related — and nothing else competes with them.

## 2. Color palette (`ui/themes/colors.py`, verified against source)

| Token | RGB | Hex | Used for |
|---|---|---|---|
| `BG_VOID` | (4, 5, 10) | `#04050A` | Deepest background, letterbox bars, splash |
| `BG_APP` | (10, 14, 27) | `#0A0E1B` | Desktop wallpaper, app backgrounds |
| `BG_SURFACE` | (17, 22, 42) | `#11162A` | Window bodies, panels |
| `BG_SURFACE_RAISED` | (26, 33, 64) | `#1A2140` | Cards, input fields, list rows, board nodes |
| `BORDER_SOFT` | (40, 51, 87) | `#283357` | Default borders |
| `BORDER_STRONG` | (62, 76, 130) | `#3E4C82` | Hover/focus borders |
| `TEXT_PRIMARY` | (234, 239, 252) | `#EAEFFC` | Main text |
| `TEXT_SECONDARY` | (151, 163, 199) | `#97A3C7` | Labels, metadata |
| `TEXT_DISABLED` | (90, 100, 133) | `#5A6485` | Disabled states |
| `CYAN_500` | (47, 230, 224) | `#2FE6E0` | Primary accent, evidence node rings |
| `CYAN_700` | (14, 124, 130) | `#0E7C82` | Glow base, muted cyan fills |
| `PURPLE_500` | (163, 92, 255) | `#A35CFF` | Secondary accent, suspect node rings |
| `PURPLE_700` | (90, 46, 153) | `#5A2E99` | Glow base, muted purple fills |
| `SUCCESS` | (54, 226, 154) | `#36E29A` | Verified evidence, correct deduction, FPS overlay |
| `DANGER` | (255, 79, 109) | `#FF4F6D` | Contradictions, wrong accusations |
| `WARNING` | (255, 182, 72) | `#FFB648` | Red-herring risk, caution |

**Status: fully implemented and in active use** — `BoardScreen` and `ErrorScreen` both render with these exact tokens, not approximations.

## 3. Typography (`ui/themes/typography.py`, verified against source)

| Role | Font file expected | Size constants (`FontSize`) |
|---|---|---|
| `display` | `Orbitron-Bold.ttf` | `DISPLAY = 56` |
| `heading` | `Rajdhani-SemiBold.ttf` | `H1 = 32`, `H2 = 24` |
| `body` | `Rajdhani-Regular.ttf` | `H3 = 18`, `BODY = 16`, `CAPTION = 13` |
| `mono` | `ShareTechMono-Regular.ttf` | `MONO = 14` |

**Status: the role/size system is fully implemented; no font files are bundled.** `FontBook.get(role, size)` falls back to pygame's default font with a once-per-role logged warning. Every screenshot in `screenshots/` was taken without real fonts — what you see there is the *fallback* look, not the designed one.

## 4. Spacing (`ui/themes/spacing.py`, verified against source)

`XS=4, SM=8, MD=16, LG=24, XL=32, XXL=48, XXXL=64, HUGE=96`. Defined and available; not yet consistently applied since most screens that would use a real layout grid don't exist yet.

## 5. Window chrome — designed, not built

The glow technique (2-3 progressively larger, lower-opacity copies of a window's border, offset outward) and the 40px title bar with square neon control chips are fully specified but have no implementation — there's no `Window` component yet, since no screen has needed window-in-window layering. `BoardScreen` renders full-screen, not inside a window.

## 6. Component library

| Component | Status |
|---|---|
| Buttons (primary/secondary/ghost/danger) | Designed, not implemented — no screen has needed a button yet |
| Panels/cards | Designed, not implemented |
| Toasts | Designed, not implemented — `NOTIFICATION_REQUESTED` exists and is wired to audio, but nothing renders a toast on screen yet |
| List rows, tabs, input fields | Designed, not implemented |
| Progress/XP bars (cyan-to-purple gradient) | Designed, not implemented — `XPTracker` has the data, nothing renders it |
| **Investigation board nodes & connections** | **Implemented exactly as designed**: 64px circular suspect nodes ringed `PURPLE_500`, 96×64 evidence cards ringed `CYAN_500`, connections at `CYAN_500`/60% opacity that switch to `DANGER` red and thicken when `ContradictionEngine` flags them |

## 7. Motion language — designed, mostly not built

The full timing table (220ms window open, 150ms tab cross-fade, 1.6s glow pulse, etc.) is unchanged from the original design intent. None of it is implemented yet, since there's no window/tab system to animate. The one thing that *is* real: the pulsing glow circle in `EngineTestScreen` uses accumulated delta-time (not frame count) for its sine-wave opacity — proving the frame-rate-independent animation approach works, even though it's not a "real" UI element.

## 8. Screen layouts — design intent, build status

All 20 screens from the original design (Boot/Splash, Main Menu, Case Select, Briefing, Desktop, Email, Chat, Browser, Employee Database, Evidence Folder, Investigation Board, Interrogation, Report Submission, Results, Pause, Settings, Save/Load, Achievements, Statistics Dashboard, Shop) remain valid design targets. **Only the Investigation Board has an implementation** (`ui/screens/board_screen.py`), and it's a simplified version: click-to-connect rather than drag-from-tray, no suspect/evidence trays, no pan/zoom, full-screen rather than windowed. The other 19 are unchanged from the original spec — see `docs/ROADMAP.md` for what each one needs to get built.

## 9. Accessibility — unchanged from original intent

Color pairings target WCAG AA contrast; status is never color-only by design (contradictions get both red *and* a dashed/thickened line). No accessibility settings UI exists yet to let a player toggle reduced motion or high contrast — there's no Settings screen at all yet.

## 10. What to read next

`docs/ROADMAP.md` for the build order; `docs/DEVELOPER_GUIDE.md` for how to add a new screen against these tokens without hardcoding values.
