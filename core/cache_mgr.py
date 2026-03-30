# -*- coding: utf-8 -*-
# cache_mgr.py — Local disk cache management

import json
import time
from pathlib import Path
from typing import Optional
import threading

_lock = threading.Lock()

CACHE_FILE = Path(__file__).parent.parent / "cache.json"
CACHE_MAX = 500


def _load_cache() -> dict:
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_cache(cache: dict) -> None:
    try:
        if len(cache) > CACHE_MAX:
            sorted_keys = sorted(cache, key=lambda k: cache[k].get("ts", 0))
            for key in sorted_keys[:len(cache) - CACHE_MAX]:
                del cache[key]
        CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False), encoding="utf-8")
    except Exception:
        pass


_cache_memory: dict = {}


def cache_get(term: str) -> Optional[dict]:
    with _lock:
        return _cache_memory.get(term.lower())


def load_memory_from_disk() -> None:
    global _cache_memory
    _cache_memory = _load_cache()


def cache_set(term: str, dict_data: Optional[dict], translation: Optional[str]) -> None:
    with _lock:
        _cache_memory[term.lower()] = {
            "ts": time.time(),
            "dict_data": dict_data,
            "translation": translation,
        }
        _save_cache(_cache_memory)
