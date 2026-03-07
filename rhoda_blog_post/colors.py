"""
Rhoda Blog Post - Unified Color Palette

Color scheme: Orange to Light/Steel Blue gradient
Based on the brand gradient shown in marketing materials.
"""

from manim import ManimColor

# =============================================================================
# PRIMARY GRADIENT COLORS (Orange → Light Blue)
# =============================================================================

# Warm end (Orange)
RHODA_ORANGE = "#FC670F"           # Primary orange (brand color)
RHODA_ORANGE_LIGHT = "#FD8A44"     # Lighter orange
RHODA_ORANGE_DARK = "#D95500"      # Deeper orange

# Cool end (Light Blue)  
RHODA_BLUE = "#A7D7E9"             # Primary light blue (brand color)
RHODA_BLUE_LIGHT = "#C5E5F0"       # Lighter blue
RHODA_BLUE_DARK = "#7DC4DD"        # Deeper blue

# Gradient midpoints (interpolated between brand colors)
RHODA_PEACH = "#FDB77C"            # Warm transition (orange → neutral)
RHODA_CREAM = "#F0D6C0"            # Neutral warm
RHODA_MIST = "#C9E1E8"             # Neutral cool (neutral → blue)

# =============================================================================
# GRADIENT STOPS (for programmatic gradients)
# =============================================================================

# Full gradient from warm to cool (left to right as shown in images)
GRADIENT_STOPS = [
    RHODA_ORANGE,
    RHODA_ORANGE_LIGHT,
    RHODA_PEACH,
    RHODA_CREAM,
    RHODA_MIST,
    RHODA_BLUE_LIGHT,
    RHODA_BLUE,
]

# Simplified 3-stop gradient
GRADIENT_SIMPLE = [RHODA_ORANGE, RHODA_CREAM, RHODA_BLUE]

# =============================================================================
# BACKGROUND COLORS
# =============================================================================

BG_WHITE = "#FFFFFF"               # Perfect white background
BG_OFFWHITE = "#FAFAFA"            # Slightly warm white
BG_DARK = "#181C22"                # Dark dark gray (brand color)
BG_CHARCOAL = "#24292E"            # Slightly lighter dark gray

# =============================================================================
# TEXT & UI COLORS
# =============================================================================

TEXT_DARK = "#181C22"              # Dark dark gray for text on light bg
TEXT_LIGHT = "#FFFFFF"             # Perfect white text on dark bg
TEXT_MUTED = "#6B6B6B"             # Gray for secondary text
MARKER_GRAY = "#444444"            # Subtle markers/gridlines

# =============================================================================
# SEMANTIC COLORS (for diagrams)
# =============================================================================

# For inference rollout diagram
VISION_COLOR = RHODA_BLUE          # Vision/video elements
ACTION_COLOR = RHODA_ORANGE        # Action elements
PREDICTION_COLOR = RHODA_PEACH     # Predictions (semi-transparent fill)
TIMEBAR_COLOR = TEXT_DARK          # Timebar indicator

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def interpolate_color(color1: str, color2: str, t: float) -> str:
    """
    Linearly interpolate between two hex colors.
    
    Args:
        color1: Starting hex color (e.g., "#FF0000")
        color2: Ending hex color
        t: Interpolation factor (0.0 = color1, 1.0 = color2)
    
    Returns:
        Interpolated hex color string
    """
    # Parse hex colors
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
    
    # Interpolate
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    
    return f"#{r:02x}{g:02x}{b:02x}"


def get_gradient_color(t: float, stops: list = None) -> str:
    """
    Get a color from the gradient at position t.
    
    Args:
        t: Position in gradient (0.0 = start, 1.0 = end)
        stops: List of hex color stops (defaults to GRADIENT_STOPS)
    
    Returns:
        Hex color string at position t
    """
    if stops is None:
        stops = GRADIENT_STOPS
    
    if t <= 0:
        return stops[0]
    if t >= 1:
        return stops[-1]
    
    # Find which segment we're in
    n_segments = len(stops) - 1
    segment_t = t * n_segments
    segment_idx = int(segment_t)
    local_t = segment_t - segment_idx
    
    # Clamp to valid range
    segment_idx = min(segment_idx, n_segments - 1)
    
    return interpolate_color(stops[segment_idx], stops[segment_idx + 1], local_t)


def create_gradient_list(n_colors: int, stops: list = None) -> list:
    """
    Create a list of n evenly-spaced colors from the gradient.
    
    Args:
        n_colors: Number of colors to generate
        stops: List of hex color stops (defaults to GRADIENT_STOPS)
    
    Returns:
        List of hex color strings
    """
    if n_colors == 1:
        return [get_gradient_color(0.5, stops)]
    
    return [get_gradient_color(i / (n_colors - 1), stops) for i in range(n_colors)]
