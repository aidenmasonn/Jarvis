# Jarvis

Jarvis is a voice-first personal AI assistant CLI. You speak to it (push-to-talk via Space), it transcribes with local Whisper, talks to Claude, and can fetch from / save to an Obsidian vault.

## How to Run

**Prerequisites:**
- `brew install ffmpeg` (required by Whisper)
- Python deps: `pip install -r requirements.txt`
- `.env` file with `ANTHROPIC_API_KEY=<your-key>` (exact spelling — no typos)

```bash
python jarvis.py
```

Hold SPACE to speak. Ctrl+C to quit.

## How to Test

```bash
pytest tests/
```

24 tests across 3 files, all should pass. No API key or microphone needed — tests mock both.

## Architecture

Single file: `jarvis.py` (263 lines), four sections separated by `# ──` banners:

| Section | Lines | What it does |
|---------|-------|-------------|
| AUDIO | 39–97 | `load_whisper`, `record_audio`, `transcribe`, `speak` |
| VAULT | 99–163 | `is_vault_reference`, `is_save_intent`, `extract_search_term`, `search_vault`, `save_to_vault` |
| CLAUDE | 166–216 | `chat`, `summarize`, `SUMMARIZE_PROMPT` |
| SESSION LOOP | 219–262 | `main` — the entry point |

## Key Constants

```python
VAULT_PATH = Path("/Users/aidenmason/Desktop/obsidian_vault")  # flat .md files
SAMPLE_RATE = 16000          # Hz, matches Whisper base expectation
TRIGGER_PHRASES = [...]      # words that trigger vault search
SAVE_PHRASES = [...]         # words that trigger save-to-vault
# Claude: model="claude-sonnet-4-6", max_tokens=1024 (intentionally low for voice)
```

## Known Gotchas

- **Use `pynput`, not `keyboard`**: `keyboard` requires root/sudo on macOS and crashes. `jarvis.py` imports `from pynput import keyboard as pynput_keyboard`.
- **ffmpeg is not in requirements.txt**: Must be installed separately via `brew install ffmpeg`.
- **`.env` key spelling**: Must be exactly `ANTHROPIC_API_KEY` (with underscore between API and KEY). `ANTHROPIC_APIKEY` silently fails.
- **Whisper loads on first run**: ~10s delay on cold start, prints "Loading Whisper model..."

## Conventions

- Four-section structure with `# ── SECTION ──...` banners is intentional — keep it.
- Tests mock `pynput.keyboard` via `unittest.mock.patch` and set `ANTHROPIC_API_KEY` in env.
- `save_to_vault` slugifies the YAML `title:` field from the summary — title must be on its own line matching `^title: .+$`.
- Session state is an in-memory dict `{"messages": [], "started_at": ..., "vault_refs": []}` — not persisted between runs.

## Docs

- `docs/LESSONS.md` — bug fixes, design decisions, dead ends, open questions
- `docs/PROGRESS.md` — phase/task tracker
- `docs/superpowers/specs/` — design docs from brainstorming sessions
- `docs/superpowers/plans/` — implementation plans
