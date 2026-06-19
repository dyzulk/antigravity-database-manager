"""
Box-Drawing Character Sets.

Provides ``BoxChars`` dataclass and named preset constants for
all border styles used throughout the TUI.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BoxChars:
    """
    A complete set of box-drawing characters for borders and frames.

    UX Best Practice: Consistent border style across all UI elements creates
    visual cohesion and reduces cognitive overhead.
    """
    tl: str   # top-left corner
    tr: str   # top-right corner
    bl: str   # bottom-left corner
    br: str   # bottom-right corner
    h: str    # horizontal line
    v: str    # vertical line
    t_left: str   # T-junction facing left
    t_right: str  # T-junction facing right
    t_up: str     # T-junction facing up
    t_down: str   # T-junction facing down
    cross: str    # four-way cross


# Named box-drawing presets
BORDER_THIN = BoxChars(
    tl="┌", tr="┐", bl="└", br="┘", h="─", v="│",
    t_left="┤", t_right="├", t_up="┴", t_down="┬", cross="┼",
)

BORDER_THICK = BoxChars(
    tl="┏", tr="┓", bl="┗", br="┛", h="━", v="┃",
    t_left="┫", t_right="┣", t_up="┻", t_down="┳", cross="╋",
)

BORDER_DOUBLE = BoxChars(
    tl="╔", tr="╗", bl="╚", br="╝", h="═", v="║",
    t_left="╣", t_right="╠", t_up="╩", t_down="╦", cross="╬",
)

BORDER_ROUNDED = BoxChars(
    tl="╭", tr="╮", bl="╰", br="╯", h="─", v="│",
    t_left="┤", t_right="├", t_up="┴", t_down="┬", cross="┼",
)

BORDER_NONE = BoxChars(
    tl=" ", tr=" ", bl=" ", br=" ", h=" ", v=" ",
    t_left=" ", t_right=" ", t_up=" ", t_down=" ", cross=" ",
)
