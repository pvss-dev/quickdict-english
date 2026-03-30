# -*- coding: utf-8 -*-
# web.py — Registers web assets and injects them into the Anki reviewer

from aqt import mw

ADDON_MODULE = mw.addonManager.addonFromModule(__name__)

# We have now loaded all the modular files
popup_integrator = f"""
<link rel="stylesheet" href="/_addons/{ADDON_MODULE}/web/css/tokens.css">
<link rel="stylesheet" href="/_addons/{ADDON_MODULE}/web/css/layout.css">
<link rel="stylesheet" href="/_addons/{ADDON_MODULE}/web/css/components.css">
<script src="/_addons/{ADDON_MODULE}/web/js/ui.js"></script>
<script src="/_addons/{ADDON_MODULE}/web/js/events.js"></script>
"""

def initialize_web():
    mw.addonManager.setWebExports(__name__, r"web/.*\.(js|css)")