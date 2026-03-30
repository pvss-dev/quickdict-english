# -*- coding: utf-8 -*-
# html_builder.py — Builds the HTML interface based on the data

from typing import Optional
import html as _html

_POS_PRIORITY = ["noun", "verb", "adjective", "adverb"]
_MAX_DEF_LENGTH = 120


def _esc(s: str) -> str:
    return _html.escape(s or "")


def generate_html(term: str, dict_data: Optional[dict], translation: Optional[str]) -> str:
    if not dict_data and not translation:
        return ""

    sections = []

    # Header: word + phonetic + audio button
    phonetic = ""
    audio_url = ""
    if dict_data:
        for ph in dict_data.get("phonetics", []):
            if not phonetic and ph.get("text"):
                phonetic = ph["text"]
            if not audio_url and ph.get("audio"):
                audio_url = ph["audio"]

    phonetic_html = f'<span class="edict-phonetic">{_esc(phonetic)}</span>' if phonetic else ""
    audio_html = (
        f'<button class="edict-audio" data-audio="{_esc(audio_url)}" aria-label="Ouvir pronúncia">▶</button>'
    ) if audio_url else ""

    sections.append(
        f'<div class="edict-header">'
        f'<span class="edict-word">{_esc(term)}</span>{phonetic_html}{audio_html}'
        f'</div>'
    )

    # Translation block
    if translation:
        sections.append(
            f'<div class="edict-section edict-translation">'
            f'<span class="edict-label">🇧🇷 Tradução</span>'
            f'<div class="edict-translation-text">{_esc(translation)}</div>'
            f'</div>'
        )

    # Best definition + synonyms
    if dict_data:

        meanings = dict_data.get("meanings", [])

        best_meaning = None
        for preferred in _POS_PRIORITY:
            for m in meanings:
                if m.get("partOfSpeech") == preferred:
                    best_meaning = m
                    break
            if best_meaning:
                break
        if not best_meaning and meanings:
            best_meaning = meanings[0]

        if best_meaning:
            part_of_speech = best_meaning.get("partOfSpeech", "")
            definitions = best_meaning.get("definitions", [])
            synonyms = list(best_meaning.get("synonyms", []))

            for defn in definitions:
                synonyms = synonyms + defn.get("synonyms", [])

            seen = set()
            unique_synonyms = []
            for s in synonyms:
                if s.lower() not in seen:
                    seen.add(s.lower())
                    unique_synonyms.append(s)
                if len(unique_synonyms) == 5:
                    break

            def_items = []
            example_used = False

            for defn in definitions[:1]:
                definition_text = defn.get("definition", "")
                if len(definition_text) > _MAX_DEF_LENGTH:
                    definition_text = definition_text[:_MAX_DEF_LENGTH].rsplit(" ", 1)[0] + "…"
                example_text = defn.get("example", "") if not example_used else ""

                item_html = '<div class="edict-def-item">'
                item_html += f'<div class="edict-def-text">{_esc(definition_text)}</div>'
                if example_text:
                    item_html += f'<div class="edict-example">"{example_text}"</div>'
                    example_used = True
                item_html += '</div>'
                def_items.append(item_html)

            synonyms_html = ""
            if unique_synonyms:
                chips = "".join(f'<span class="edict-synonym">{s}</span>' for s in unique_synonyms)
                synonyms_html = (
                    f'<div class="edict-synonyms">'
                    f'<span class="edict-synonyms-label">Sinônimos</span>'
                    f'{chips}'
                    f'</div>'
                )

            if def_items:
                pos_html = f'<span class="edict-pos">{part_of_speech}</span>' if part_of_speech else ""
                sections.append(
                    f'<div class="edict-section">'
                    f'<span class="edict-label">📖 Definição {pos_html}</span>'
                    f'{"".join(def_items)}'
                    f'{synonyms_html}'
                    f'</div>'
                )

    return f'<div class="edict-container">{"".join(sections)}</div>'
