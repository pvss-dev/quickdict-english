# -*- coding: utf-8 -*-
# dictionary.py — Orchestrates cache, APIs, and HTML generation

from concurrent.futures import ThreadPoolExecutor
from .core.cache_mgr import cache_get, cache_set
from .core.api import fetch_dictionary, fetch_translation
from .core.html_builder import generate_html

def build_tooltip_html(term: str) -> str:
    """The main function called by reviewer.py to return the HTML."""
    
    cached = cache_get(term)
    if cached:
        dict_data = cached.get("dict_data")
        translation = cached.get("translation")
    else:
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_dict = executor.submit(fetch_dictionary, term)
            future_trans = executor.submit(fetch_translation, term)
            dict_data = future_dict.result()
            translation = future_trans.result()

        cache_set(term, dict_data, translation)

    return generate_html(term, dict_data, translation)