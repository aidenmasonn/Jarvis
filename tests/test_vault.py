import os
import sys
import datetime
import unittest.mock
from pathlib import Path
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
sys.modules['pynput'] = unittest.mock.MagicMock()
sys.modules['pynput.keyboard'] = unittest.mock.MagicMock()
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import jarvis
from jarvis import search_vault, save_to_vault


def _make_vault(tmp_path: Path, files: dict) -> Path:
    for name, content in files.items():
        (tmp_path / name).write_text(content)
    return tmp_path


def test_search_vault_fuzzy_filename_match(tmp_path, monkeypatch):
    _make_vault(tmp_path, {
        "2026-05-01-spotify-algorithm.md": "# Spotify\nContent about spotify algorithms",
        "2026-05-02-recipe-tool.md": "# Recipe\nContent about recipes",
    })
    monkeypatch.setattr(jarvis, "VAULT_PATH", tmp_path)
    result = search_vault("spotify algorithm")
    assert result is not None
    assert "spotify" in result.lower()


def test_search_vault_content_fallback(tmp_path, monkeypatch):
    _make_vault(tmp_path, {
        "2026-05-01-project-notes.md": "# Notes\nWe discussed reverse engineering the recommendation system",
    })
    monkeypatch.setattr(jarvis, "VAULT_PATH", tmp_path)
    result = search_vault("reverse engineering recommendation")
    assert result is not None
    assert "reverse engineering" in result.lower()


def test_search_vault_no_match_returns_none(tmp_path, monkeypatch):
    _make_vault(tmp_path, {
        "2026-05-01-cooking.md": "# Cooking\nRecipes and meal plans",
    })
    monkeypatch.setattr(jarvis, "VAULT_PATH", tmp_path)
    result = search_vault("quantum physics")
    assert result is None


def test_search_vault_prefers_filename_over_content(tmp_path, monkeypatch):
    _make_vault(tmp_path, {
        "2026-05-01-spotify.md": "# Spotify\nSpotify algorithm deep dive",
        "2026-05-02-other.md": "# Other\nMentions spotify in passing",
    })
    monkeypatch.setattr(jarvis, "VAULT_PATH", tmp_path)
    result = search_vault("spotify")
    assert result is not None
    assert "Spotify algorithm" in result


def test_save_to_vault_creates_file(tmp_path, monkeypatch):
    monkeypatch.setattr(jarvis, "VAULT_PATH", tmp_path)
    summary = """---
title: Test Conversation
date: 2026-06-04
tags: [test, jarvis]
related: []
status: in-progress
---

## Key Decisions
- Use local Whisper

## Open Questions
- None

## Learnings
- It works

## Next Steps
- Ship it
"""
    path = save_to_vault(summary)
    assert path.exists()
    assert path.suffix == ".md"
    assert path.parent == tmp_path


def test_save_to_vault_filename_contains_date(tmp_path, monkeypatch):
    monkeypatch.setattr(jarvis, "VAULT_PATH", tmp_path)
    summary = """---
title: My Test Note
date: 2026-06-04
tags: []
related: []
status: in-progress
---

## Key Decisions
- Decision one
"""
    path = save_to_vault(summary)
    today = datetime.date.today().isoformat()
    assert today in path.name


def test_save_to_vault_slugifies_title(tmp_path, monkeypatch):
    monkeypatch.setattr(jarvis, "VAULT_PATH", tmp_path)
    summary = """---
title: Spotify Algorithm Deep Dive
date: 2026-06-04
tags: []
related: []
status: in-progress
---

## Key Decisions
- Content here
"""
    path = save_to_vault(summary)
    assert "spotify-algorithm-deep-dive" in path.name.lower()
