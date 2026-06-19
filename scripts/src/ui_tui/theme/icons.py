"""
Icon and Symbol Sets.

Provides ``Icons`` (semantic UI symbols) and ``Glyphs`` (block-element
characters for data visualization).
"""

from __future__ import annotations


class Icons:
    """
    Curated Unicode symbols for semantic UI indicators.

    UX Best Practice: Consistent iconography provides instant visual meaning
    without requiring the user to read text labels.
    """
    # Navigation
    POINTER     = "▸"
    POINTER_DBL = "▶"
    ARROW_UP    = "↑"
    ARROW_DOWN  = "↓"
    ARROW_LEFT  = "←"
    ARROW_RIGHT = "→"
    CHEVRON_R   = "›"
    CHEVRON_D   = "▾"

    # Status
    CHECK       = "✓"
    CROSS       = "✗"
    WARNING     = "⚠"
    INFO        = "ℹ"
    CIRCLE_FILL = "●"
    CIRCLE_OPEN = "○"
    DIAMOND     = "◆"

    # Progress
    BLOCK_FULL  = "█"
    BLOCK_3_4   = "▓"
    BLOCK_HALF  = "▒"
    BLOCK_1_4   = "░"

    # Data
    FOLDER      = "📁"
    FILE        = "📄"
    DATABASE    = "🗄"
    KEY         = "🔑"
    LOCK        = "🔒"
    UNLOCK      = "🔓"

    # Spinners (frame sequences)
    SPINNER_DOTS    = ("⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷")
    SPINNER_LINE    = ("—", "\\", "|", "/")
    SPINNER_ARC     = ("◜", "◠", "◝", "◞", "◡", "◟")
    SPINNER_BRAILLE = ("⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏")
    SPINNER_PULSE   = ("○", "◔", "◑", "◕", "●", "◕", "◑", "◔")
    SPINNER_BOUNCE  = ("⠁", "⠂", "⠄", "⡀", "⢀", "⠠", "⠐", "⠈")


class Glyphs:
    """
    Block-element characters for gauges, bar charts, and meters.

    UX Best Practice: Using block elements instead of plain text for
    data visualization provides instant visual meaning.
    """
    # Horizontal bar (8 levels)
    BAR_H = (" ", "▏", "▎", "▍", "▌", "▋", "▊", "▉", "█")
    # Vertical bar (8 levels)
    BAR_V = (" ", "▁", "▂", "▃", "▄", "▅", "▆", "▇", "█")
    # Gauge segments
    GAUGE_EMPTY   = "○"
    GAUGE_QUARTER = "◔"
    GAUGE_HALF    = "◑"
    GAUGE_THREE_Q = "◕"
    GAUGE_FULL    = "●"
    # Scrollbar
    SCROLL_TRACK  = "│"
    SCROLL_THUMB  = "┃"
    SCROLL_UP     = "▲"
    SCROLL_DOWN   = "▼"
    # Separators
    THIN_H        = "─"
    THICK_H       = "━"
    DOUBLE_H      = "═"
    # Toggle
    TOGGLE_ON     = "◉"
    TOGGLE_OFF    = "○"
