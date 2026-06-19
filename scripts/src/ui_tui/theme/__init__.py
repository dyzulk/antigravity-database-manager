"""
Theme Package — Semantic Color, Style, and Typography System.

Re-exports the complete public API for backward compatibility.
All existing imports from ``ui_tui.theme`` continue to work unchanged.
"""

# Color primitives
from .color import Color, _Ansi

# Composable styles
from .style import Style

# Palettes and style presets
from .palette import (
    Palette, PaletteHighContrast, PaletteLight,
    PALETTE, Styles, STYLES,
)

# Box-drawing borders
from .borders import (
    BoxChars,
    BORDER_THIN, BORDER_THICK, BORDER_DOUBLE, BORDER_ROUNDED, BORDER_NONE,
)

# Icons and glyphs
from .icons import Icons, Glyphs

# Gradient utilities
from .gradients import generate_gradient, gradient_bg_line, contrast_ratio_approx

__all__ = [
    # Color
    "Color", "_Ansi",
    # Style
    "Style",
    # Palette
    "Palette", "PaletteHighContrast", "PaletteLight",
    "PALETTE", "Styles", "STYLES",
    # Borders
    "BoxChars",
    "BORDER_THIN", "BORDER_THICK", "BORDER_DOUBLE", "BORDER_ROUNDED", "BORDER_NONE",
    # Icons
    "Icons", "Glyphs",
    # Gradients
    "generate_gradient", "gradient_bg_line", "contrast_ratio_approx",
]
