# Lessons Learned

Running log of bugs, decisions, dead ends, and open questions from Jarvis development.
Most recent entries first within each section.

---

## Bug Fixes

### 2026-06-03 — `keyboard` library crashes on macOS
**What happened:** The `keyboard` library (used for push-to-talk) requires root/sudo or accessibility permissions on macOS and raises a permission error at import time.
**Fix:** Replaced with `pynput`. Both libraries detect keypresses but `pynput` works without elevated permissions on macOS.
**Lesson:** On macOS, always check whether a keyboard/input library requires accessibility permissions before committing to it.

### 2026-06-03 — `.env` key missing underscore
**What happened:** `.env` had `ANTHROPIC_APIKEY=...` (missing underscore). `os.environ["ANTHROPIC_API_KEY"]` raised `KeyError` silently swallowed by dotenv.
**Fix:** Rename key to `ANTHROPIC_API_KEY` in `.env`.
**Lesson:** Double-check exact env var names — `python-dotenv` loads whatever keys are present without warning about mismatches.

### 2026-06-03 — Empty frames / unloaded model guard
**What happened:** `record_audio()` could return an empty list if the user released Space before any audio was captured. `transcribe()` could be called before `load_whisper()` if main() was bypassed in tests.
**Fix:** Added `if not frames: raise RuntimeError(...)` in `record_audio` and `if _whisper_model is None: raise RuntimeError(...)` in `transcribe`.
**Lesson:** Guard module-level state (lazy-loaded models) at every entry point, not just in the happy path.

### 2026-06-03 — `extract_search_term` called twice in main loop
**What happened:** `main()` called `search_vault(text)` (which internally calls `extract_search_term`) and then called `extract_search_term(text)` again to print the term. Duplicate work, and the two calls could theoretically diverge.
**Fix:** Call `extract_search_term(text)` once and pass the result to both `search_vault` and the log print.
**Lesson:** When a function is a pure extraction with no side effects, avoid calling it twice — extract once to a variable.

### 2026-06-03 — Exact-phrase match must take priority over all-words match
**What happened:** Full-text vault search had two strategies: exact phrase match and all-words match. Without explicit priority, a file matching all individual words could be returned over one matching the full phrase.
**Fix:** Collect `exact_hits` and `allwords_hits` in separate lists; return `exact_hits[0]` before falling back to `allwords_hits[0]`.
**Lesson:** When combining search strategies, always be explicit about priority — implicit ordering creates subtle relevance bugs.

### 2026-06-03 — UTF-8 encoding and empty-slug fallback in `save_to_vault`
**What happened:** `path.write_text(summary)` used the system default encoding, which could fail on non-ASCII vault content. Titles with only special characters produced an empty slug after regex substitution.
**Fix:** Explicit `encoding="utf-8"` in `write_text`. Added `or "untitled"` fallback: `slug = ... or "untitled"`.
**Lesson:** Always specify encoding explicitly for file writes. Always guard against empty strings after sanitization.

---

## Design Decisions

### Single-file architecture (`jarvis.py`)
**Decision:** Keep all code in one file for the MVP.
**Why:** Reduces import complexity and makes the whole system readable in one scroll. The four-section banner structure provides enough organization. Split into modules when a section exceeds ~150 lines or needs independent testing.

### Push-to-talk via Space key
**Decision:** Hold Space to record, release to stop.
**Why:** Always-listening requires VAD (voice activity detection) and background threads — more complex and harder to test. Push-to-talk is predictable and works reliably in a CLI context.

### Local Whisper base model
**Decision:** Use OpenAI Whisper `base` model running locally.
**Why:** No cloud dependency, no per-request cost, works offline. Base model is 74MB and runs on CPU in ~1-2s for short utterances. Accuracy is sufficient for conversational commands.

### Two-stage vault search (filename → full-text)
**Decision:** Try fuzzy filename match first, fall back to full-text grep.
**Why:** Most vault lookups are by note name ("my Spotify conversation"). Filename match is fast (difflib, no I/O). Full-text grep is the fallback for content-based queries.

### 1024 max_tokens for chat
**Decision:** Cap Claude responses at 1024 tokens in `chat()`.
**Why:** Responses are read aloud via `say`. Long responses make for bad voice UX. `summarize()` uses 2048 since it generates a structured document, not spoken text.

### macOS `say` for TTS
**Decision:** Use the built-in `say` command for text-to-speech.
**Why:** Zero dependencies, works out of the box on macOS, synchronous (blocks until speech is done, which is what we want in a turn-based voice loop).

### In-memory session only
**Decision:** Session history (`messages`, `vault_refs`) lives in a dict for the duration of one `python jarvis.py` run and is not persisted.
**Why:** Simplest possible state management for MVP. Explicit saves via "save this conversation" are the persistence mechanism.

---

## Dead Ends

### `keyboard` library
**What we tried:** Used `keyboard` for push-to-talk (detecting Space keypress).
**Why it failed:** `keyboard` on macOS requires root/sudo or Accessibility permissions granted in System Preferences. Raises `ImportError` or permission error at runtime in a normal terminal. Also requires the terminal app to have accessibility access, which is a per-machine manual setup step.
**What replaced it:** `pynput` — same API surface for key detection, works without elevated permissions on macOS.

---

## Open Questions & Next Steps

### Pending: Task 8 — End-to-end manual verification
The final task from Phase 1 (run `python jarvis.py`, test vault reference, test save, verify Obsidian graph) was blocked by the `.env` key typo. The typo is now fixed. This should be the next thing to do: run the app and verify the full voice loop end-to-end.

### Future: Persistent session history
Currently each run starts with an empty `messages` list. Consider persisting the last N messages to a JSON file so Jarvis has continuity across sessions.

### Future: Multi-vault support
`VAULT_PATH` is hardcoded. Could be moved to `.env` or a config file to support multiple vaults or different machines.

### Future: Always-listening mode
Push-to-talk is deliberate and simple, but an always-listening mode with silence detection would feel more natural. Requires VAD (e.g., `webrtcvad`) and a background recording thread.
