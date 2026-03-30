// ui.js — Manages the dictionary visual interface
window.Edict = window.Edict || {};

window.Edict.UI = (function () {
  "use strict";

  var tooltipEl = null;
  var tooltipVisible = false;
  var currentAudio = null;

  function createTooltipEl() {
    var el = document.createElement("div");
    el.id = "edict-tooltip";
    el.style.display = "none";
    document.body.appendChild(el);

    // Close tooltip when clicking outside of it
    document.addEventListener("mousedown", function (e) {
      if (tooltipVisible && !el.contains(e.target)) hideTooltip();
    });

    // Close tooltip on Escape key
    document.addEventListener("keydown", function (e) {
      if (tooltipVisible && e.key === "Escape") hideTooltip();
    });

    return el;
  }

  function copyText(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.style.cssText = "position:fixed;opacity:0;pointer-events:none;";
    document.body.appendChild(ta);
    ta.focus();
    ta.select();
    try {
      document.execCommand("copy");
    } catch (_) {}
    document.body.removeChild(ta);
  }

  function positionTooltip(x, y) {
    var vw = window.innerWidth,
      vh = window.innerHeight;
    var tw = tooltipEl.offsetWidth,
      th = tooltipEl.offsetHeight;
    var left = x + 12,
      top = y + 12;

    if (left + tw > vw - 10) left = x - tw - 12;
    if (top + th > vh - 10) top = y - th - 12;

    tooltipEl.style.left = Math.max(10, left) + "px";
    tooltipEl.style.top = Math.max(10, top) + "px";
  }

  function buildTooltip(html, word) {
    tooltipEl.innerHTML = html;
    var container = tooltipEl.querySelector(".edict-container");
    if (!container) return;

    // Header buttons (copy, close)
    var header = container.querySelector(".edict-header");
    if (header) {
      if (word) {
        var copyBtn = document.createElement("button");
        copyBtn.className = "edict-copy";
        copyBtn.textContent = "⎘ Copy";
        copyBtn.addEventListener("click", function () {
          copyText(word);
          copyBtn.textContent = "✓ Copied";
          copyBtn.classList.add("copied");
          setTimeout(function () {
            copyBtn.textContent = "⎘ Copy";
            copyBtn.classList.remove("copied");
          }, 1500);
        });
        header.appendChild(copyBtn);
      }

      var closeBtn = document.createElement("button");
      closeBtn.className = "edict-close";
      closeBtn.textContent = "✕";
      closeBtn.addEventListener("click", hideTooltip);
      header.appendChild(closeBtn);
    }

    // Audio button
    var audioBtn = container.querySelector(".edict-audio");
    if (audioBtn) {
      var audioUrl = audioBtn.getAttribute("data-audio");
      audioBtn.addEventListener("click", function () {
        if (currentAudio) {
          currentAudio.pause();
          currentAudio.currentTime = 0;
        }
        currentAudio = new Audio(audioUrl);
        currentAudio.play();
        audioBtn.classList.add("playing");
        currentAudio.addEventListener("ended", function () {
          audioBtn.classList.remove("playing");
        });
      });
    }

    // Synonym chips
    var chips = container.querySelectorAll(".edict-synonym");
    chips.forEach(function (chip) {
      // Make chips keyboard-accessible (pairs with CSS :focus style)
      chip.setAttribute("role", "button");
      chip.setAttribute("tabindex", "0");

      function lookupSynonym() {
        var synonymTerm = chip.textContent.trim();
        if (window.Edict.Events && window.Edict.Events.handleLookup) {
          window.Edict.Events.handleLookup(
            synonymTerm,
            window.Edict.lastMouseX,
            window.Edict.lastMouseY,
          );
        }
      }

      chip.addEventListener("click", lookupSynonym);
      chip.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          lookupSynonym();
        }
      });
    });
  }

  function showTooltipAt(x, y, html, word) {
    if (!tooltipEl) tooltipEl = createTooltipEl();
    buildTooltip(html, word);

    // Force reflow to restart the fade-in animation
    tooltipEl.style.animation = "none";
    tooltipEl.style.display = "block";
    void tooltipEl.offsetWidth;
    tooltipEl.style.animation = "";

    positionTooltip(x, y);
    tooltipVisible = true;
  }

  function showLoading(x, y) {
    if (!tooltipEl) tooltipEl = createTooltipEl();
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }
    tooltipEl.innerHTML =
      '<div class="edict-loading"><span class="edict-spinner"></span>Looking up...</div>';
    tooltipEl.style.display = "block";
    tooltipEl.style.left = x + 12 + "px";
    tooltipEl.style.top = y + 12 + "px";
    tooltipVisible = true;
  }

  function hideTooltip() {
    if (currentAudio) {
      currentAudio.pause();
      currentAudio = null;
    }
    if (tooltipEl) tooltipEl.style.display = "none";
    tooltipVisible = false;
  }

  // Public API consumed by events.js
  return {
    showTooltipAt: showTooltipAt,
    showLoading: showLoading,
    hideTooltip: hideTooltip,
  };
})();
