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

    raw_dict = data[0]

    clean_dict = {
        "phonetics": [],
        "meanings": []
    }

    for ph in raw_dict.get("phonetics", []):
        clean_ph = {}
        if ph.get("text"):
            clean_ph["text"] = ph["text"]
        if ph.get("audio"):
            clean_ph["audio"] = ph["audio"]

        if clean_ph:
            clean_dict["phonetics"].append(clean_ph)

    for m in raw_dict.get("meanings", []):
        clean_m = {
            "partOfSpeech": m.get("partOfSpeech")
        }

        if m.get("synonyms"):
            clean_m["synonyms"] = m.get("synonyms")

        clean_m["definitions"] = []

        for d in m.get("definitions", [])[:2]:
            clean_d = {"definition": d.get("definition")}

            if d.get("example"):
                clean_d["example"] = d["example"]
            if d.get("synonyms"):
                clean_d["synonyms"] = d["synonyms"]

            clean_m["definitions"].append(clean_d)

        clean_dict["meanings"].append(clean_m)

    return clean_dict


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
