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


# ── CLAUDE ─────────────────────────────────────────────────────────────────


# ── SESSION LOOP ───────────────────────────────────────────────────────────

def main():
    pass


if __name__ == "__main__":
    main()
