# Data Circles Figure

Animated visualization comparing training data sizes across different robotics models. Circles have areas proportional to hours of training data, with a camera that pans and zooms to reveal each circle at consistent visual scale.

## Overview

The animation shows four models with dramatically different training data sizes:
- **OXE**: 4,000 hours
- **π₀**: 10,000 hours  
- **GEN-0**: 270,000 hours
- **Rhoda**: 100 hours

The camera starts zoomed in on OXE, then progressively pans right and zooms out to reveal larger circles. For Rhoda (the smallest), it zooms way in, showing GEN-0 as a massive arc in the background.

## Render Commands

```bash
# Quick preview (low quality, fast)
manim -pql data_circles_figure.py DataCirclesFigure

# High quality (1080p @ 60fps)
manim -pqh data_circles_figure.py DataCirclesFigure

# 4K quality
manim -pqk data_circles_figure.py DataCirclesFigure

# Static version (all circles visible at once)
manim -pql data_circles_figure.py DataCirclesFigureStatic
```

## Key Parameters

### Data Configuration
```python
data = [
    ("OXE", 4000),
    (r"\pi_0", 10000),
    ("GEN-0", 270000),
    ("Rhoda", 100),
]
```
- First element: display name (use `r"\pi_0"` for Greek letters via Unicode conversion)
- Second element: hours of training data (determines circle area)

### Aspect Ratio
```python
config.pixel_width = 1920
config.pixel_height = 960
config.frame_width = 16
config.frame_height = 8
```
Currently set to **2:1 aspect ratio**. Adjust these values together to change output dimensions.

### Circle Sizing
```python
scale_factor = 0.012
```
Controls overall circle size. Radius = `sqrt(hours) * scale_factor`.

### Circle Spacing
```python
gap_multipliers = [0.8, 0.1, -0.35]  # OXE→π₀, π₀→GEN-0, GEN-0→Rhoda
```
- Positive values: gap between circles (as fraction of larger radius)
- Negative values: circles overlap (GEN-0 "looms" over Rhoda)

### Camera Zoom
```python
initial_frame_height = radii[0] * 4.5  # Base zoom level
```
Lower values = more zoomed in. Each subsequent circle scales proportionally.

```python
frame_height_3 = radii[3] * 16  # Rhoda-specific zoom
```
Rhoda has custom zoom to show both Rhoda and GEN-0's arc.

### Camera Vertical Position
```python
camera_y_offset = 0.35  # Fraction of frame height above baseline
```
Controls where baseline appears in frame. Higher = baseline lower in frame.

### Label Positioning
```python
label_offset = camera_height * 0.20  # Distance from circle top to label
gap = camera_height * 0.02           # Gap at line endpoints
```

### Connector Line Weight
```python
base_line_weight = 0.5  # Weight for first circle (OXE)
```
Line weight scales proportionally with circle radius. Minimum weight of 0.1 enforced, doubled for very small circles.

### Stroke Widths
```python
baseline_stroke_width = 1
circle_stroke_width = 1
```
Baseline is offset to account for both stroke widths so circles sit flush.

### Font
```python
sans_font = get_preferred_font()  # Returns "Open Sans" if available, else "Arial"
```
Name labels use `SEMIBOLD` weight; hours labels use regular weight.

### Animation Timing
| Phase | Duration |
|-------|----------|
| Circle reveal | 1.5s |
| Wait after reveal | 1s |
| Camera pan (OXE→π₀) | 2s |
| Camera pan (π₀→GEN-0) | 2.5s |
| Camera zoom (GEN-0→Rhoda) | 2.5s |
| Wait on Rhoda | 4s |
| Fade out | 2s (fade) / 4s (camera) |
| Final wait (baseline only) | 2s |

### Fade Out (Loop Preparation)
```python
# Fade takes 2s, camera zoom takes 4s (both start together)
self.play(
    *[FadeOut(c, run_time=2) for c in circles],
    self.camera.frame.animate(run_time=4).set_height(initial_frame_height),
)
```
Camera zooms back to initial scale (Y position reset, X position maintained) for seamless looping.

## Scene Classes

### `DataCirclesFigure` (Main)
Animated version with camera panning/zooming through each circle sequentially.

### `DataCirclesFigureStatic`
Static version showing all circles at once (useful for reference/debugging).

## File Structure
```
data_circles_figure/
├── data_circles_figure.py   # Main animation code
├── README.md                # This file
└── media/                   # Generated output (gitignored)
    └── videos/
        └── data_circles_figure/
            └── 960p60/
                └── DataCirclesFigure.mp4
```
