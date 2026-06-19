"""
Terminal Capability Detection.

Probes the runtime environment to determine which visual features the
terminal supports, then exposes a singleton ``CAPS`` object that the rest
of the TUI can query.

Detected features:
  - Truecolor (24-bit) RGB support
  - 256-color palette support
  - Basic 16-color support
  - Unicode box-drawing / emoji rendering
  - Mouse reporting (SGR mode)
  - Bracketed paste mode
  - Light vs dark background heuristic

UX Best Practice: Graceful degradation ensures the TUI looks good on
every terminal — from modern GPU-accelerated emulators to SSH over tmux.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass


# ==============================================================================
# CAPABILITY DETECTION
# ==============================================================================

@dataclass
class TerminalCapabilities:
    """
    Runtime terminal feature flags.

    Populated once at startup via ``detect()``.  Other modules read these
    flags to choose the best rendering path (e.g., truecolor gradients
    vs plain bold text).
    """
    truecolor: bool = False       # 24-bit RGB (16 million colors)
    colors_256: bool = False      # 8-bit palette (256 colors)
    colors_basic: bool = True     # 4-bit palette (16 colors) — always available
    unicode_box: bool = True      # Box-drawing and block-element characters
    unicode_emoji: bool = False   # Full emoji rendering (🗄📁 etc.)
    mouse_sgr: bool = False       # SGR mouse event protocol
    bracketed_paste: bool = False # Bracketed-paste safe input
    light_bg: bool = False        # Terminal has a light background
    reduce_motion: bool = False   # User prefers reduced motion


def detect() -> TerminalCapabilities:
    """
    Probe the runtime environment and return a populated capabilities object.

    Detection heuristics (ordered by confidence):
      1. ``COLORTERM`` env var (``truecolor`` or ``24bit``)
      2. ``TERM_PROGRAM`` env var (known modern emulators)
      3. ``TERM`` env var (xterm-256color, etc.)
      4. Windows 10+ conhost / Windows Terminal (VT support)
      5. ``NO_COLOR`` convention (https://no-color.org)
      6. ``AGMERCIUM_REDUCE_MOTION`` env var
    """
    caps = TerminalCapabilities()

    # --- NO_COLOR convention ---
    if os.environ.get("NO_COLOR") is not None:
        caps.truecolor = False
        caps.colors_256 = False
        caps.colors_basic = True
        caps.unicode_box = True
        caps.unicode_emoji = False
        return caps

    # --- Truecolor detection ---
    colorterm = os.environ.get("COLORTERM", "").lower()
    if colorterm in ("truecolor", "24bit"):
        caps.truecolor = True
        caps.colors_256 = True

    # Known truecolor terminal emulators
    term_program = os.environ.get("TERM_PROGRAM", "").lower()
    truecolor_programs = {
        "iterm.app", "hyper", "wezterm", "alacritty", "kitty",
        "vscode", "ghostty", "contour", "rio", "warp",
    }
    if term_program in truecolor_programs:
        caps.truecolor = True
        caps.colors_256 = True

    # Windows Terminal always supports truecolor
    if os.environ.get("WT_SESSION") or os.environ.get("WT_PROFILE_ID"):
        caps.truecolor = True
        caps.colors_256 = True

    # --- 256-color fallback ---
    term = os.environ.get("TERM", "").lower()
    if "256color" in term:
        caps.colors_256 = True
    if not caps.colors_256 and not caps.truecolor:
        # Windows 10+ conhost supports 256 colors via VT
        if sys.platform == "win32":
            caps.colors_256 = True  # Conservative default for Win10+

    # --- Unicode detection ---
    # Most modern terminals support box-drawing characters
    caps.unicode_box = True
    # Emoji support is less universal
    if caps.truecolor or term_program in truecolor_programs:
        caps.unicode_emoji = True
    if sys.platform == "win32" and not os.environ.get("WT_SESSION"):
        caps.unicode_emoji = False  # Classic conhost has mixed emoji support

    # --- Mouse support ---
    # SGR mouse is available in most modern terminals
    if caps.truecolor or term_program in truecolor_programs:
        caps.mouse_sgr = True
    if os.environ.get("TERM_PROGRAM") == "Apple_Terminal":
        caps.mouse_sgr = False  # Apple Terminal has poor mouse support
    # Disable mouse in screen/tmux by default (they intercept events)
    if "screen" in term or "tmux" in term:
        caps.mouse_sgr = False

    # --- Bracketed paste ---
    caps.bracketed_paste = caps.truecolor or caps.colors_256

    # --- Light background heuristic ---
    colorfgbg = os.environ.get("COLORFGBG", "")
    if colorfgbg:
        parts = colorfgbg.split(";")
        if len(parts) >= 2:
            try:
                bg_code = int(parts[-1])
                # Colors 0-6 and 8 are dark, 7 and 9-15 are light
                caps.light_bg = bg_code in (7, 9, 10, 11, 12, 13, 14, 15)
            except ValueError:
                pass
    if term_program == "apple_terminal":
        caps.light_bg = True  # Default Apple Terminal is light

    # --- Reduce motion ---
    if os.environ.get("AGMERCIUM_REDUCE_MOTION", "").lower() in ("1", "true", "yes"):
        caps.reduce_motion = True
    # Respect macOS accessibility setting
    if os.environ.get("REDUCE_MOTION", "").lower() in ("1", "true"):
        caps.reduce_motion = True

    return caps


# ==============================================================================
# SINGLETON — Detect once at import time
# ==============================================================================

CAPS = detect()


def color_mode_label() -> str:
    """Human-readable label for the current color mode (for debug/status)."""
    if CAPS.truecolor:
        return "Truecolor (24-bit)"
    if CAPS.colors_256:
        return "256-color"
    return "Basic (16-color)"
