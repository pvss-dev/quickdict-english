# -*- coding: utf-8 -*-
# api.py — Fetches data from Free Dictionary API and MyMemory

import json
import urllib.request
import urllib.parse
from typing import Optional
import sys
import urllib.error


def _get(url: str, timeout: int = 5) -> Optional[dict]:
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "AnkiEnglishDictionary/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"[EnglishDict] API error: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"[EnglishDict] API error: {e}", file=sys.stderr)
        return None


def fetch_dictionary(word: str) -> Optional[dict]:
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(word)}"
    data = _get(url)
    if not data or not isinstance(data, list):
        return None
    return data[0]


def fetch_translation(word: str) -> Optional[str]:
    encoded = urllib.parse.quote(word)
    url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair=en|pt-BR"
    data = _get(url)
    if not data:
        return None
    try:
        translation = data["responseData"]["translatedText"]
        if translation.lower() == word.lower():
            return None
        return translation
    except (KeyError, TypeError):
        return None
