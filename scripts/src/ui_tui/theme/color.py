"""
ANSI Color Primitives.

Provides the ``Color`` dataclass and low-level ``_Ansi`` escape-code
builders used by the entire theme system.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# ==============================================================================
# ANSI ESCAPE CODE PRIMITIVES
# ==============================================================================

class _Ansi:
    """Low-level ANSI VT100 sequence builders."""

    RESET = "\x1b[0m"

    # --- Attribute codes ---
    BOLD = "\x1b[1m"
    DIM = "\x1b[2m"
    ITALIC = "\x1b[3m"
    UNDERLINE = "\x1b[4m"
    BLINK = "\x1b[5m"
    REVERSE = "\x1b[7m"
    STRIKETHROUGH = "\x1b[9m"

    @staticmethod
    def fg_256(code: int) -> str:
        """Foreground color from the 256-color palette."""
        return f"\x1b[38;5;{code}m"

    @staticmethod
    def bg_256(code: int) -> str:
        """Background color from the 256-color palette."""
        return f"\x1b[48;5;{code}m"

    @staticmethod
    def fg_rgb(r: int, g: int, b: int) -> str:
        """24-bit truecolor foreground."""
        return f"\x1b[38;2;{r};{g};{b}m"

    @staticmethod
    def bg_rgb(r: int, g: int, b: int) -> str:
        """24-bit truecolor background."""
        return f"\x1b[48;2;{r};{g};{b}m"

    @staticmethod
    def fg_basic(code: int) -> str:
        """Basic 16-color foreground (30-37, 90-97)."""
        return f"\x1b[{code}m"

    @staticmethod
    def bg_basic(code: int) -> str:
        """Basic 16-color background (40-47, 100-107)."""
        return f"\x1b[{code}m"


# ==============================================================================
# COLOR REPRESENTATION
# ==============================================================================

@dataclass(frozen=True)
class Color:
    """
    A terminal color supporting multiple encoding levels.

    Usage::

        cyan = Color(r=0, g=200, b=200, code_256=44, code_basic=36)
        seq = cyan.fg()  # Returns best available ANSI escape
    """
    r: int = 255
    g: int = 255
    b: int = 255
    code_256: Optional[int] = None
    code_basic: Optional[int] = None

    def fg(self) -> str:
        """Foreground escape sequence (truecolor preferred)."""
        return _Ansi.fg_rgb(self.r, self.g, self.b)

    def bg(self) -> str:
        """Background escape sequence (truecolor preferred)."""
        return _Ansi.bg_rgb(self.r, self.g, self.b)

    def fg_256(self) -> str:
        """Foreground via 256-color palette (fallback)."""
        if self.code_256 is not None:
            return _Ansi.fg_256(self.code_256)
        return self.fg()

    def bg_256(self) -> str:
        """Background via 256-color palette (fallback)."""
        if self.code_256 is not None:
            return _Ansi.bg_256(self.code_256)
        return self.bg()

    def fg_basic(self) -> str:
        """Foreground via basic 16-color (most compatible fallback)."""
        if self.code_basic is not None:
            return _Ansi.fg_basic(self.code_basic)
        return self.fg_256()

    def bg_basic(self) -> str:
        """Background via basic 16-color (most compatible fallback)."""
        if self.code_basic is not None:
            return _Ansi.bg_basic(self.code_basic + 10)
        return self.bg_256()

    @staticmethod
    def lerp(a: "Color", b: "Color", t: float) -> "Color":
        """
        Linear interpolation between two colors.

        ``t=0.0`` → color ``a``, ``t=1.0`` → color ``b``.
        """
        t = max(0.0, min(1.0, t))
        return Color(
            r=int(a.r + (b.r - a.r) * t),
            g=int(a.g + (b.g - a.g) * t),
            b=int(a.b + (b.b - a.b) * t),
        )

    def auto_fg(self) -> str:
        """Capability-aware foreground: truecolor → 256 → basic."""
        from ..capabilities import CAPS
        if CAPS.truecolor:
            return self.fg()
        if CAPS.colors_256:
            return self.fg_256()
        return self.fg_basic()

    def auto_bg(self) -> str:
        """Capability-aware background: truecolor → 256 → basic."""
        from ..capabilities import CAPS
        if CAPS.truecolor:
            return self.bg()
        if CAPS.colors_256:
            return self.bg_256()
        return self.bg_basic()
