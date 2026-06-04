import os
import sys
import datetime
import unittest.mock
from pathlib import Path
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
sys.modules['pynput'] = unittest.mock.MagicMock()
sys.modules['pynput.keyboard'] = unittest.mock.MagicMock()
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from unittest.mock import patch, MagicMock
import jarvis
from jarvis import chat, summarize


def _make_session():
    return {"messages": [], "started_at": datetime.datetime.now(), "vault_refs": []}


def test_chat_appends_user_message():
    session = _make_session()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Hello there")]
    with patch.object(jarvis.client.messages, "create", return_value=mock_response):
        chat(session, "Hello")
    assert session["messages"][0] == {"role": "user", "content": "Hello"}


def test_chat_appends_assistant_message():
    session = _make_session()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="I am Jarvis")]
    with patch.object(jarvis.client.messages, "create", return_value=mock_response):
        reply = chat(session, "Who are you?")
    assert reply == "I am Jarvis"
    assert session["messages"][1] == {"role": "assistant", "content": "I am Jarvis"}


def test_chat_prepends_vault_context():
    session = _make_session()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Based on your notes...")]
    with patch.object(jarvis.client.messages, "create", return_value=mock_response) as mock_create:
        chat(session, "Tell me more", vault_context="# Spotify\nContent here")
    call_messages = mock_create.call_args.kwargs["messages"]
    assert "[Vault context]" in call_messages[0]["content"]
    assert "# Spotify" in call_messages[0]["content"]


def test_chat_without_vault_context_sends_plain_text():
    session = _make_session()
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="Sure")]
    with patch.object(jarvis.client.messages, "create", return_value=mock_response) as mock_create:
        chat(session, "What time is it?")
    call_messages = mock_create.call_args.kwargs["messages"]
    assert call_messages[0]["content"] == "What time is it?"


def test_summarize_sends_all_messages():
    session = _make_session()
    session["messages"] = [
        {"role": "user", "content": "Tell me about Spotify"},
        {"role": "assistant", "content": "Spotify uses collaborative filtering"},
    ]
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="---\ntitle: Spotify\n---\n## Key Decisions\n- CF")]
    with patch.object(jarvis.client.messages, "create", return_value=mock_response) as mock_create:
        result = summarize(session)
    call_messages = mock_create.call_args.kwargs["messages"]
    assert len(call_messages) == 3  # 2 history + 1 summarize request
    assert "summarize" in call_messages[-1]["content"].lower() or "summary" in call_messages[-1]["content"].lower()
    assert result == "---\ntitle: Spotify\n---\n## Key Decisions\n- CF"
