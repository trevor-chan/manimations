# Inference Rollout Animation - Implementation Guide

## Overview

This animation depicts closed-loop inference timing for a two-stage robotics model:
1. **Video Model** (75% of chunk): Takes vision history → outputs 3-chunk video prediction
2. **Action Model** (25% of chunk): Takes video prediction → outputs 8 action chips (1 chunk total)

The key visual concept: **time flows right-to-left** (elements slide left as time progresses), while the **timebar stays fixed** at x=0.

---

## Visual Elements

### Timeline Infrastructure (Static)
| Element | Description | Style |
|---------|-------------|-------|
| **TimeBar** | Vertical line at x=0 marking "now" | Dark gray, with triangle marker at top, z-index=100 |
| **ChunkMarkers** | Vertical lines dividing time into chunks | Gray, stroke_width=2 |

### Model Indicators (Slide with time)
| Element | Description | Style |
|---------|-------------|-------|
| **ModelContainer** | Rounded rectangle encompassing both models | Light gray fill (#E8E8E8), matches model bounds |
| **VideoModel** | 75% chunk width box | Blue outlined, rounded corners (0.12 radius) |
| **ActionModel** | 25% chunk width box | Orange outlined, rounded corners |

### Data Blocks (Slide with time)
| Element | Description | Style |
|---------|-------------|-------|
| **VisionHistory** | Past video frames | Solid blue fill, no border, opacity=1.0 |
| **VideoPrediction** | 3-chunk predicted future | Blue, fill_opacity=0.25, stroke_opacity=1.0 |
| **ActionChips** | 8 small action segments | Orange, fill_opacity=0.25, each 1/8 chunk wide |

---

## Vertical Layout

All Y positions are computed with consistent `VERTICAL_GAP = 0.15`:

```
CHUNK_MARKER_TOP ──────────────────────────────
                    (gap)
VIDEO_MODEL_Y       ████ Video Model ████
                    (gap)  
VIDEO_PRED_Y        ░░░░ Video Prediction ░░░░
                    (gap)
ACTION_MODEL_Y      ████ Action Model ████
                    (gap)
ACTION_Y            ░░░░ Action Chips ░░░░
                    (gap)
VISION_HISTORY_Y    ████ Vision History ████
                    (gap)
CHUNK_MARKER_BOTTOM ───────────────────────────
```

---

## Color Palette

Colors are imported from `../colors.py`:

| Constant | Hex | Usage |
|----------|-----|-------|
| `VISION_COLOR` | #A7D7E9 | Vision history, video model, video prediction |
| `ACTION_COLOR` | #FC670F | Action model, action chips |
| `TIMEBAR_COLOR` | #181C22 | Timebar |
| `MARKER_COLOR` | #444444 | Chunk boundary lines |
| `BG_COLOR` | #FAFAFA | Background (off-white) |
| `FILL_LIGHT_GRAY` | #E8E8E8 | Model container fill |

---

## Animation Phases

### Phase 1: Explanatory (with pauses)

**Duration**: ~15 seconds

1. **Fade In** (1s): All elements fade in from white
2. **Keyframe 1**: Initial state - vision history extends to timebar
3. **Keyframe 2**: Vision ghost animates into video model (scale + translate)
4. **Keyframe 3**: 
   - Timeline advances 75% of chunk (to video model completion)
   - Video prediction ghost expands from video model
   - Vision history grows with chip-based animation
5. **Keyframe 4**: Video prediction ghost compresses into action model
6. **Keyframe 5**:
   - Timeline advances 25% of chunk (to action model completion)
   - 8 action chips expand from action model
   - Vision history continues growing

Chip-based growth: Individual chips fade in at the leading edge, hold for 1 chip duration, then fade out as the solid history bar catches up.

### Phase 2: Continuous Loop (slow speed)

**Duration**: 4 iterations × ~0.9s each

Smooth, linear time progression using `ValueTracker` with updaters:

- **Timeline**: Progresses continuously at `rate_func=linear`
- **Ghost animations**: Complete within 1/8 chunk duration
- **Model crossfade**: Last 12.5% of chunk - old model fades out, new model fades in (both sliding)
- **Video prediction**: Fades out over first 15%, new one fades in at 75%
- **Action chips**: 8 chips, each fades out as its right edge crosses timebar
- **Vision history**: Chips fade in, hold, fade out; solid bar grows with 1-chip lag

**Soft Transition from Phase 1**: 
- Non-model elements (history, predictions, chips, markers) are instantly removed and recreated at their current positions
- Models crossfade to maintain visual continuity

### Phase 3: Fast Loop (condensed model)

**Duration**: 20 iterations × 0.45s each (~2 chunks/second)

**Simplifications**:
- No ghosting animations
- No chip visualizations
- No video prediction
- Models condensed to single horizontal line

**Condensed model transition**:
- Video model slides down to center Y
- Action model slides up to center Y  
- Container shrinks to single MODEL_HEIGHT
- Both models sit side-by-side on same row

**Fast loop behavior**:
- History bar fully caught up (right edge at x=0)
- Action bar shrinks continuously (left edge at timebar, right edge at chunk boundary)
- Simple model crossfade at chunk boundaries

### Fade Out

**Duration**: 4 chunks (~1.8s) + 1s wait

After iteration 16 of Phase 3:
- All elements continue sliding while fading out
- Fill and stroke opacity fade proportionally (preserving ratios)
- Final 1-second wait on white background

---

## Key Implementation Details

### Custom Classes

**`ModelIndicator(VGroup)`**: Rounded rectangle with optional label
- `corner_radius = 0.12`
- Stroke only, no fill

**`ModelContainer(VGroup)`**: Encompasses both models
- Dimensions calculated from VIDEO_MODEL_Y and ACTION_MODEL_Y
- Fill color matches stroke (#E8E8E8)
- z-index = -1 (renders behind models)

### Time-to-Position Conversion

```python
def time_to_x(time_in_chunks, current_time):
    """Convert absolute time to screen x-coordinate."""
    return (time_in_chunks - current_time) * CHUNK_WIDTH
```

### Sliding via Updaters

```python
def make_continuous_slide_updater(initial_x, chunk_time_tracker):
    def updater(mob):
        t = chunk_time_tracker.get_value()
        new_x = initial_x - t * CHUNK_WIDTH
        mob.move_to([new_x, mob.get_center()[1], 0])
    return updater
```

### Proportional Fade

```python
def make_fade_updater(mob):
    initial_fill = mob.get_fill_opacity()
    initial_stroke = mob.get_stroke_opacity()
    def updater(m):
        t = fade_tracker.get_value()
        m.set_fill(opacity=initial_fill * (1 - t))
        m.set_stroke(opacity=initial_stroke * (1 - t))
    return updater
```

---

## Key Constants

```python
# Dimensions
CHUNK_WIDTH = 1.5           # World units per chunk
TRACK_HEIGHT = 0.4          # Height of data blocks
MODEL_HEIGHT = 0.5          # Height of model indicators
VERTICAL_GAP = 0.15         # Gap between vertical elements

# Model timing (within a chunk)
VIDEO_MODEL_FRAC = 0.75     # Video model takes 75% of chunk
ACTION_MODEL_FRAC = 0.25    # Action model takes 25% of chunk

# Action chips
NUM_ACTION_CHIPS = 8        # 8 action chips per chunk
CHIP_WIDTH = CHUNK_WIDTH / NUM_ACTION_CHIPS

# Animation timing
EXPLANATORY_CHUNK_TIME = 2.0    # Seconds per chunk (Phase 1)
SLOW_CHUNK_TIME = 0.9           # Seconds per chunk (Phase 2)
FAST_CHUNK_TIME = 0.45          # Seconds per chunk (Phase 3)

# Ghost animation
GHOST_DURATION_FRAC = 1/8   # Ghosts complete in 1/8 of chunk
```

---

## Render Commands

```bash
# Preview (low quality, fast)
manim -pql inference_rollout.py InferenceRollout

# High quality
manim -pqh inference_rollout.py InferenceRollout

# 4K
manim -pqk inference_rollout.py InferenceRollout
```

---

## File Structure

```
inference_rollout/
├── inference_rollout.py      # Main animation (single file)
├── IMPLEMENTATION_PLAN.md    # This document
├── media/                    # Output directory
└── sketch_frames/            # Reference images
    └── 1.jpg ... 7.jpg

../colors.py                  # Shared color palette
```
