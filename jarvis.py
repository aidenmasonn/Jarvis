import os
import re
import difflib
import subprocess
import tempfile
import datetime
from pathlib import Path

import anthropic
import keyboard
import sounddevice as sd
import whisper
import numpy as np
from scipy.io.wavfile import write as wav_write
from dotenv import load_dotenv

load_dotenv()

VAULT_PATH = Path("/Users/aidenmason/Desktop/obsidian_vault")
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]

SAMPLE_RATE = 16000

TRIGGER_PHRASES = ["in my", "fetch", "remember when", "refer to", "from my", "look up", "pull up"]
SAVE_PHRASES = ["save this", "save the conversation", "save this conversation"]

SYSTEM_PROMPT = (
    "You are Jarvis, a concise voice assistant. "
    "The user speaks to you and your responses are read aloud, so keep answers short and conversational — "
    "two to four sentences max unless the user asks for detail. "
    "You have access to the user's Obsidian knowledge vault. "
    "When vault context is provided, use it to inform your answer."
)

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


# ── AUDIO ──────────────────────────────────────────────────────────────────


# ── VAULT ──────────────────────────────────────────────────────────────────

def is_vault_reference(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in TRIGGER_PHRASES)


def is_save_intent(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in SAVE_PHRASES)


def extract_search_term(text: str) -> str:
    t = text.lower()
    for phrase in TRIGGER_PHRASES:
        idx = t.find(phrase)
        if idx != -1:
            return text[idx + len(phrase):].strip()
    return text


def search_vault(text: str) -> str | None:
    term = extract_search_term(text)
    md_files = list(VAULT_PATH.glob("*.md"))
    if not md_files:
        return None

    # Stage 1: fuzzy filename match
    stems = [f.stem for f in md_files]
    matches = difflib.get_close_matches(term.lower(), [s.lower() for s in stems], n=1, cutoff=0.3)
    if matches:
        matched_stem = matches[0]
        for f in md_files:
            if f.stem.lower() == matched_stem:
                return f.read_text()

    # Stage 2: full-text grep fallback (exact phrase takes priority over all-words)
    term_lower = term.lower()
    words = [w for w in term_lower.split() if len(w) > 2]
    exact_hits = []
    allwords_hits = []
    for f in md_files:
        content = f.read_text(errors="ignore")
        content_lower = content.lower()
        if term_lower in content_lower:
            exact_hits.append(content)
        elif words and all(w in content_lower for w in words):
            allwords_hits.append(content)
    if exact_hits:
        return exact_hits[0]
    if allwords_hits:
        return allwords_hits[0]

    return None


# ── CLAUDE ─────────────────────────────────────────────────────────────────


# ── SESSION LOOP ───────────────────────────────────────────────────────────

def main():
    pass


if __name__ == "__main__":
    main()
