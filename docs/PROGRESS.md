# Progress

Phase-by-task tracker for Jarvis development.

---

## Phase 1 — Jarvis MVP

**Status: 7/8 complete**

- [x] Task 1: Project scaffold — `jarvis.py` with imports, constants, `.env`, `requirements.txt`, `.gitignore`
- [x] Task 2: Intent detection — `is_vault_reference`, `is_save_intent`, `extract_search_term` (12 tests)
- [x] Task 3: Vault search — `search_vault` with two-stage fuzzy + grep (7 tests)
- [x] Task 4: Vault save — `save_to_vault` with YAML frontmatter slugification (part of test_vault.py)
- [x] Task 5: Claude integration — `chat`, `summarize` with session history (5 tests)
- [x] Task 6: Audio — `load_whisper`, `record_audio`, `transcribe`, `speak`
- [x] Task 7: Main session loop — `main()` wiring all sections together
- [ ] Task 8: End-to-end manual verification — run `python jarvis.py`, test vault reference, test save, check Obsidian

**Total tests:** 24 (all passing as of 2026-06-03)

---

## Phase 2 — TBD

Next features to decide on:
- Persistent session history across runs
- Multi-vault / configurable vault path
- Always-listening mode with VAD
- Web UI or menu bar app wrapper

---

## How to Add a Phase

When starting a new phase:
1. Add a `## Phase N — Name` section above this one
2. List tasks as `- [ ] Task N: Description`
3. Check off tasks as they complete
4. Update **Status** line when the phase is done
