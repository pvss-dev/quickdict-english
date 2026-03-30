# -*- coding: utf-8 -*-
# reviewer.py — Hooks into Anki's reviewer to handle JS <-> Python communication

from typing import Any, Optional, Tuple

from aqt import mw
from aqt.reviewer import Reviewer
from aqt.previewer import Previewer
from aqt.qt import QMenu, QApplication

from .dictionary import build_tooltip_html
from .web import popup_integrator
from .core.cache_mgr import load_memory_from_disk

PYCMD_IDENTIFIER = "englishDict"


def on_webview_will_show_context_menu(webview: Any, menu: QMenu):
    if hasattr(webview, "title"):
        if webview.title not in ("main webview", "previewer"):
            return

    window = QApplication.activeWindow()
    if mw.state != "review" and not isinstance(window, Previewer):
        return
    if not webview.selectedText():
        return

    action = menu.addAction("Look up in English Dictionary...")
    action.triggered.connect(_lookup_selected)


def _lookup_selected():
    """Triggers a lookup for the currently selected text via JS."""
    window = QApplication.activeWindow()
    js = "invokeEnglishDict();"
    if isinstance(window, Previewer):
        window._web.eval(js)
    else:
        mw.reviewer.web.eval(js)


# JS <-> Python bridge
def handle_message(message: str) -> Optional[str]:
    """Receives pycmd messages from JS and returns HTML content."""
    if not message.startswith(PYCMD_IDENTIFIER + ":"):
        return None

    term = message[len(PYCMD_IDENTIFIER) + 1:].strip()
    if not term:
        return None

    return build_tooltip_html(term)


# Anki hooks
def on_webview_will_set_content(web_content: Any, context: Any):
    if not isinstance(context, (Reviewer, Previewer)):
        return
    web_content.body += popup_integrator


def on_webview_did_receive_js_message(
        handled: Tuple[bool, Any], message: str, context: Any
) -> Tuple[bool, Any]:
    if not isinstance(context, (Reviewer, Previewer)):
        return handled
    if not message.startswith(PYCMD_IDENTIFIER):
        return handled

    result = handle_message(message) or ""
    return True, result


_patched = False


def patch_reviewer():
    global _patched
    if _patched:
        return

    from aqt.gui_hooks import (
        webview_will_set_content,
        webview_did_receive_js_message,
    )

    webview_will_set_content.append(on_webview_will_set_content)
    webview_did_receive_js_message.append(on_webview_did_receive_js_message)
    _patched = True


def initialize_reviewer():
    from aqt.gui_hooks import profile_did_open, webview_will_show_context_menu

    profile_did_open.append(patch_reviewer)
    profile_did_open.append(load_memory_from_disk)
    webview_will_show_context_menu.append(on_webview_will_show_context_menu)
