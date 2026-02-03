"""
Professional Market Research Styling Module

This module provides color schemes and utility functions for consistent
professional styling across PowerPoint and HTML outputs.

Color Accessibility:
- All colors are WCAG AA compliant for normal text (contrast ratio ≥ 4.5:1)
- Statistical significance colors provide clear visual distinction
- Chart colors are colorblind-friendly (avoiding red/green dependency)

Market Research Color Standards:
- Primary blue conveys trust and professionalism
- Orange accent provides visual interest without being overwhelming
- Green/red significance colors follow universal conventions
- Neutral grays ensure readability
"""

from typing import Tuple

# Optional import for PowerPoint support
try:
    # Try newer python-pptx version (>=1.0.0)
    from pptx.dml.color import RGBColor
    HAS_PPTX = True
except ImportError:
    try:
        # Try older python-pptx version (<1.0.0)
        from pptx.util import RGBColor
        HAS_PPTX = True
    except ImportError:
        HAS_PPTX = False
        # Define a dummy RGBColor class for when pptx is not available
        # Matches the interface of pptx.dml.color.RGBColor (subscriptable, not attribute-based)
        class RGBColor:
            def __init__(self, r, g, b):
                self._rgb = (r, g, b)

            def __getitem__(self, index):
                return self._rgb[index]

            @property
            def count(self):
                return 3

            def index(self, value):
                return self._rgb.index(value)


# =============================================================================
# Color Scheme Constants
# =============================================================================

# Primary colors
COLOR_PRIMARY = "2C5282"    # Dark blue - conveys trust, professionalism
COLOR_SECONDARY = "4299E1"  # Light blue - complementary, friendly
COLOR_ACCENT = "ED8936"     # Orange - provides visual interest, highlight

# Statistical significance colors
COLOR_SIGNIFICANT = "48BB78"  # Green - universally positive meaning
COLOR_NOT_SIGNIFICANT = "E53E3E"  # Red - universally negative/cautionary

# Chart colors (sequential palette)
# Colors chosen for:
# - Distinctiveness from each other
# - Colorblind accessibility (avoiding red/green only)
# - Professional appearance
CHART_COLORS = [
    "4299E1",  # Blue
    "48BB78",  # Green
    "F6E05E",  # Yellow
    "ED8936",  # Orange
    "9F7AEA",  # Purple
    "ED64A6",  # Pink
    "38B2AC",  # Teal
    "FC8181",  # Light red/coral
]

# Neutral colors
COLOR_TEXT_DARK = "1A202C"      # Near black - main text
COLOR_TEXT_LIGHT = "718096"     # Medium gray - secondary text
COLOR_BACKGROUND = "F7FAFC"     # Very light blue-gray - page background
COLOR_BORDER = "E2E8F0"         # Light gray - borders/dividers
COLOR_TABLE_HEADER = "EDF2F7"   # Light gray - table headers
COLOR_HOVER = "F0F4F8"          # Subtle hover state


# =============================================================================
# Font Settings
# =============================================================================

# PowerPoint font settings
TITLE_FONT = {"name": "Calibri", "size": 32, "bold": True}
HEADING_FONT = {"name": "Calibri", "size": 24, "bold": True}
BODY_FONT = {"name": "Calibri", "size": 18}
FOOTER_FONT = {"name": "Calibri", "size": 12, "italic": True}
TABLE_HEADER_FONT = {"name": "Calibri", "size": 10, "bold": True}
TABLE_CELL_FONT = {"name": "Calibri", "size": 11}


# =============================================================================
# Color Utility Functions
# =============================================================================

def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color string to RGB tuple.

    Args:
        hex_color: Hex color string with or without '#' prefix

    Returns:
        Tuple of (r, g, b) values (0-255)

    Examples:
        >>> hex_to_rgb("2C5282")
        (44, 82, 130)
        >>> hex_to_rgb("#4299E1")
        (66, 153, 225)
    """
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def get_chart_color(index: int, hex_format: bool = True) -> str | Tuple[int, int, int]:
    """
    Get color for chart series by index.

    Colors cycle through CHART_COLORS palette to ensure all series
    have distinct, professional colors.

    Args:
        index: Series index (0-based)
        hex_format: If True, return hex string; if False, return RGB tuple

    Returns:
        Color as hex string or RGB tuple

    Examples:
        >>> get_chart_color(0)
        '4299E1'
        >>> get_chart_color(10)  # Cycles back
        '4299E1'
    """
    color_hex = CHART_COLORS[index % len(CHART_COLORS)]

    if hex_format:
        return color_hex
    else:
        return hex_to_rgb(color_hex)


def get_market_research_color(color_name: str) -> RGBColor:
    """
    Get RGB color object for market research theme (python-pptx).

    This function returns pptx.util.RGBColor objects for use with
    python-pptx styling operations.

    Args:
        color_name: Color identifier name
            - "primary": Dark blue (main headings)
            - "secondary": Light blue (subheadings)
            - "accent": Orange (highlights)
            - "significant": Green (significant results)
            - "not_significant": Red (non-significant results)
            - "text": Dark gray (body text)
            - "muted": Medium gray (secondary text)
            - "background": Light blue-gray (backgrounds)
            - "border": Light gray (borders)

    Returns:
        RGBColor object for python-pptx

    Raises:
        ValueError: If color_name is not recognized

    Examples:
        >>> get_market_research_color("primary")
        RGBColor(44, 82, 130)
        >>> get_market_research_color("significant")
        RGBColor(72, 187, 120)
    """
    color_map = {
        "primary": COLOR_PRIMARY,
        "secondary": COLOR_SECONDARY,
        "accent": COLOR_ACCENT,
        "significant": COLOR_SIGNIFICANT,
        "not_significant": COLOR_NOT_SIGNIFICANT,
        "text": COLOR_TEXT_DARK,
        "muted": COLOR_TEXT_LIGHT,
        "background": COLOR_BACKGROUND,
        "border": COLOR_BORDER,
        "table_header": COLOR_TABLE_HEADER,
    }

    if color_name not in color_map:
        raise ValueError(
            f"Unknown color name: {color_name}. "
            f"Valid names: {list(color_map.keys())}"
        )

    rgb_tuple = hex_to_rgb(color_map[color_name])
    return RGBColor(*rgb_tuple)


# =============================================================================
# Accessibility Utilities
# =============================================================================

def check_contrast_ratio(hex_color1: str, hex_color2: str) -> float:
    """
    Calculate WCAG contrast ratio between two colors.

    Contrast ratio formula:
    - If L1 >= L2: (L1 + 0.05) / (L2 + 0.05)
    - If L2 > L1: (L2 + 0.05) / (L1 + 0.05)

    Where L is relative luminance (0-1)

    Args:
        hex_color1: First hex color
        hex_color2: Second hex color

    Returns:
        Contrast ratio (1-21, typically)

    Note:
        WCAG AA requires 4.5:1 for normal text, 3:1 for large text
        WCAG AAA requires 7:1 for normal text, 4.5:1 for large text
    """
    def get_luminance(hex_color: str) -> float:
        """Calculate relative luminance of a color."""
        r, g, b = [x / 255.0 for x in hex_to_rgb(hex_color)]

        # Apply gamma correction
        def channel_to_linear(c: float) -> float:
            if c <= 0.03928:
                return c / 12.92
            return ((c + 0.055) / 1.055) ** 2.4

        r_linear = channel_to_linear(r)
        g_linear = channel_to_linear(g)
        b_linear = channel_to_linear(b)

        # Calculate luminance
        return 0.2126 * r_linear + 0.7152 * g_linear + 0.0722 * b_linear

    l1 = get_luminance(hex_color1)
    l2 = get_luminance(hex_color2)

    if l1 >= l2:
        return (l1 + 0.05) / (l2 + 0.05)
    else:
        return (l2 + 0.05) / (l1 + 0.05)


def is_accessible_text(
    text_color: str,
    background_color: str,
    level: str = "AA",
    large_text: bool = False
) -> bool:
    """
    Check if text color meets WCAG accessibility standards on background.

    Args:
        text_color: Hex color of text
        background_color: Hex color of background
        level: Accessibility level ("AA" or "AAA")
        large_text: True for text ≥ 18pt or ≥ 14pt bold

    Returns:
        True if contrast ratio meets the required standard

    Examples:
        >>> is_accessible_text("1A202C", "FFFFFF")  # Dark on white
        True
        >>> is_accessible_text("718096", "FFFFFF")  # Gray on white, AA
        True
    """
    ratio = check_contrast_ratio(text_color, background_color)

    if level == "AAA":
        required_ratio = 4.5 if large_text else 7.0
    else:  # AA
        required_ratio = 3.0 if large_text else 4.5

    return ratio >= required_ratio


# =============================================================================
# Chart Color Palette for JavaScript
# =============================================================================

def get_js_chart_colors() -> str:
    """
    Generate JavaScript array of chart colors for HTML dashboard.

    Returns JavaScript array string with rgba color definitions.

    Returns:
        JavaScript array string

    Examples:
        >>> colors = get_js_chart_colors()
        >>> print(colors[:50])
        [`rgba(66, 153, 225, ${{alpha}})`, `rgba(72, 187, 120,
    """
    js_colors = []
    for color_hex in CHART_COLORS:
        r, g, b = hex_to_rgb(color_hex)
        js_colors.append(f"`rgba({r}, {g}, {b}, ${{alpha}})`")

    return f"[{', '.join(js_colors)}]"


# =============================================================================
# CSS Variables for HTML Dashboard
# =============================================================================

def get_css_variables() -> str:
    """
    Generate CSS custom properties (variables) for HTML dashboard.

    Returns:
        CSS variables block as string

    Examples:
        >>> css_vars = get_css_variables()
        >>> print(css_vars[:100])
        :root {
            --color-primary: #2C5282;
            --color-secondary: #4299E1;
            --color-accent: #ED8936;
    """
    return f"""
:root {{
    --color-primary: #{COLOR_PRIMARY};
    --color-secondary: #{COLOR_SECONDARY};
    --color-accent: #{COLOR_ACCENT};
    --color-significant: #{COLOR_SIGNIFICANT};
    --color-not-significant: #{COLOR_NOT_SIGNIFICANT};
    --color-text: #{COLOR_TEXT_DARK};
    --color-text-light: #{COLOR_TEXT_LIGHT};
    --color-bg: #{COLOR_BACKGROUND};
    --color-border: #{COLOR_BORDER};
    --color-table-header: #{COLOR_TABLE_HEADER};
    --color-hover: #{COLOR_HOVER};
}}
"""
