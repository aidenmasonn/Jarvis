import os
import sys
import unittest.mock
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")
sys.modules['keyboard'] = unittest.mock.MagicMock()
sys.path.insert(0, "/Users/aidenmason/Desktop/Jarvis")

import jarvis
from jarvis import is_vault_reference, is_save_intent, extract_search_term


def test_vault_reference_in_my():
    assert is_vault_reference("in my Spotify conversation") is True

def test_vault_reference_fetch():
    assert is_vault_reference("fetch the recipe tool notes") is True

def test_vault_reference_remember_when():
    assert is_vault_reference("remember when we talked about algorithms") is True

def test_vault_reference_no_match():
    assert is_vault_reference("what is the capital of France") is False

def test_vault_reference_case_insensitive():
    assert is_vault_reference("In My project notes") is True

def test_save_intent_save_this():
    assert is_save_intent("save this") is True

def test_save_intent_save_conversation():
    assert is_save_intent("save the conversation") is True

def test_save_intent_no_match():
    assert is_save_intent("what time is it") is False

def test_save_intent_case_insensitive():
    assert is_save_intent("Save This please") is True

def test_extract_search_term_in_my():
    assert extract_search_term("in my Spotify conversation") == "Spotify conversation"

def test_extract_search_term_fetch():
    assert extract_search_term("fetch the recipe tool notes") == "the recipe tool notes"

def test_extract_search_term_no_match():
    assert extract_search_term("what is the capital of France") == "what is the capital of France"
