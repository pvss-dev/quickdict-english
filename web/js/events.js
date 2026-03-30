// events.js — Monitors mouse events and calls Python
window.Edict = window.Edict || {};

window.Edict.Events = (function () {
  "use strict";

  window.Edict.lastMouseX = 0;
  window.Edict.lastMouseY = 0;

  var clickCount = 0,
    clickTimer = null;
  var mouseDownX = 0,
    mouseDownY = 0;
  var isDoubleClick = false;
  var DRAG_THRESHOLD = 6;

  // Track cursor position
  document.addEventListener("mousemove", function (e) {
    window.Edict.lastMouseX = e.clientX;
    window.Edict.lastMouseY = e.clientY;
  });

  document.addEventListener("mousedown", function (e) {
    var qa = document.getElementById("qa");
    if (!qa || !qa.contains(e.target) || e.button !== 0) return;

    mouseDownX = e.clientX;
    mouseDownY = e.clientY;
    isDoubleClick = false;

    clickCount++;
    if (clickTimer) clearTimeout(clickTimer);
    clickTimer = setTimeout(function () {
      clickCount = 0;
    }, 400);

    // Double-click: wait for mouseup to read the selection
    if (clickCount === 2) {
      clickCount = 0;
      isDoubleClick = true;
      clearTimeout(clickTimer);
      document.addEventListener(
        "mouseup",
        function onMouseUp(e) {
          document.removeEventListener("mouseup", onMouseUp);
          handleSelection(e.clientX, e.clientY);
        },
        { once: true },
      );
    }
  });

  // Drag-select: trigger lookup only if pointer moved enough
  document.addEventListener("mouseup", function (e) {
    if (isDoubleClick || e.button !== 0) return;
    var qa = document.getElementById("qa");
    if (!qa || !qa.contains(e.target)) return;
    var dist = Math.sqrt(
        Math.pow(e.clientX - mouseDownX, 2) + Math.pow(e.clientY - mouseDownY, 2)
    );
    if (dist >= DRAG_THRESHOLD) handleSelection(e.clientX, e.clientY);
  });

  function handleSelection(x, y) {
    var selection = window.getSelection();
    if (!selection) return;
    var term = selection.toString().trim();
    if (term.length >= 2 && term.length <= 60 && /[a-zA-Z]/.test(term)) {
      handleLookup(term, x, y);
    }
  }

  function escapeHtml(str) {
    return str
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function handleLookup(term, x, y) {
    window.Edict.UI.showLoading(x, y);
    pycmd("englishDict:" + term, function (html) {
      if (!html) {
        window.Edict.UI.showTooltipAt(
          x,
          y,
          '<div class="edict-container"><div class="edict-not-found">No results for <em>' +
            escapeHtml(term) +
            "</em></div></div>",
          null,
        );
      } else {
        window.Edict.UI.showTooltipAt(x, y, html, term);
      }
    });
  }

  // Called by the right-click context menu action (via reviewer.py)
  window.invokeEnglishDict = function () {
    handleSelection(window.Edict.lastMouseX, window.Edict.lastMouseY);
  };

  return { handleLookup: handleLookup };
})();