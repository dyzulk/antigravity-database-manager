"""
Gradient and Contrast Utilities.

Provides functions for generating character-level color gradients
and WCAG-inspired contrast ratio calculation.
"""

from __future__ import annotations

from typing import Optional

from .color import Color, _Ansi


def generate_gradient(
    text: str,
    start: Color,
    end: Color,
    bg: Optional[Color] = None,
    bold: bool = False,
) -> str:
    """
    Apply a character-by-character foreground gradient to text.

    UX Best Practice: Subtle gradients add premium visual appeal without
    sacrificing readability. Use sparingly on headers and accents only.
    """
    if not text:
        return ""

    parts: list[str] = []
    n = max(len(text) - 1, 1)
    bg_seq = bg.bg() if bg else ""
    bold_seq = _Ansi.BOLD if bold else ""

    for i, ch in enumerate(text):
        t = i / n
        color = Color.lerp(start, end, t)
        parts.append(f"{color.fg()}{bg_seq}{bold_seq}{ch}")

    parts.append(_Ansi.RESET)
    return "".join(parts)


def gradient_bg_line(width: int, start: Color, end: Color) -> str:
    """
    Create a full-width background gradient bar (spaces with BG color).

    UX Best Practice: Background gradients on header bars create visual depth
    and establish clear section boundaries.
    """
    parts: list[str] = []
    n = max(width - 1, 1)
    for i in range(width):
        t = i / n
        color = Color.lerp(start, end, t)
        parts.append(f"{color.bg()} ")
    parts.append(_Ansi.RESET)
    return "".join(parts)


def contrast_ratio_approx(fg: Color, bg: Color) -> float:
    """
    Approximate contrast ratio between foreground and background.

    UX Best Practice: Text contrast should be at minimum 4.5:1 for normal
    text and 3:1 for large/bold text (WCAG AA guideline adapted for terminals).

    Returns a ratio value >= 1.0.
    """
    def relative_luminance(c: Color) -> float:
        rs = c.r / 255.0
        gs = c.g / 255.0
        bs = c.b / 255.0
        r = rs / 12.92 if rs <= 0.03928 else ((rs + 0.055) / 1.055) ** 2.4
        g = gs / 12.92 if gs <= 0.03928 else ((gs + 0.055) / 1.055) ** 2.4
        b = bs / 12.92 if bs <= 0.03928 else ((bs + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)
