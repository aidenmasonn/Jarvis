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

_whisper_model = None


def load_whisper():
    global _whisper_model
    print("Loading Whisper model (first run may take a moment)...")
    _whisper_model = whisper.load_model("base")
    print("Whisper ready.")


def record_audio() -> Path:
    print("\nHold SPACE to speak...", end="", flush=True)
    while not keyboard.is_pressed("space"):
        pass
    print(" Recording...", end="", flush=True)
    frames = []
    with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype="int16") as stream:
        while keyboard.is_pressed("space"):
            data, _ = stream.read(1024)
            frames.append(data.copy())
    print(" Done.")
    audio = np.concatenate(frames, axis=0)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    wav_write(tmp.name, SAMPLE_RATE, audio)
    return Path(tmp.name)


def transcribe(wav_path: Path) -> str:
    result = _whisper_model.transcribe(str(wav_path))
    wav_path.unlink(missing_ok=True)
    return result["text"].strip()


def speak(text: str) -> None:
    subprocess.run(["say", text])


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


def save_to_vault(summary: str) -> Path:
    title_match = re.search(r"^title:\s*(.+)$", summary, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "untitled"
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "untitled"
    today = datetime.date.today().isoformat()
    filename = f"{today}-{slug}.md"
    path = VAULT_PATH / filename
    path.write_text(summary, encoding="utf-8")
    return path


# ── CLAUDE ─────────────────────────────────────────────────────────────────

def chat(session: dict, user_text: str, vault_context: str | None = None) -> str:
    content = user_text
    if vault_context:
        content = f"[Vault context]\n{vault_context}\n\n{user_text}"
    session["messages"].append({"role": "user", "content": content})
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,  # intentionally low for voice — bump to 2048 if answers get cut off
        system=SYSTEM_PROMPT,
        messages=session["messages"],
    )
    reply = response.content[0].text
    session["messages"].append({"role": "assistant", "content": reply})
    return reply


SUMMARIZE_PROMPT = """Please summarize our conversation as a structured Obsidian note. Return ONLY the markdown content, nothing else. Use this exact format:

---
title: [concise title for this conversation]
date: {date}
tags: [comma-separated relevant tags]
related: [any [[wikilinks]] to related topics mentioned, or empty list]
status: in-progress
---

## Key Decisions
- [bullet points]

## Open Questions
- [bullet points]

## Learnings
- [bullet points]

## Next Steps
- [bullet points]
""".format(date=datetime.date.today().isoformat())


def summarize(session: dict) -> str:
    messages = session["messages"] + [{"role": "user", "content": SUMMARIZE_PROMPT}]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text


# ── SESSION LOOP ───────────────────────────────────────────────────────────

def main():
    pass


if __name__ == "__main__":
    main()
