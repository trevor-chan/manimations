# Inference Rollout Animation - Implementation Plan

## Overview

This animation depicts closed-loop inference timing for a two-stage robotics model:
1. **Video Model**: Takes vision history → outputs 3-chunk video prediction
2. **Action Model**: Takes video prediction → outputs 1-chunk actions

The key visual concept: **time flows right-to-left** (elements slide left as time progresses), while the **timebar stays fixed** at center.

---

## Visual Elements

### Layer 1: Timeline Infrastructure (Static)
| Element | Description | Style |
|---------|-------------|-------|
| **TimeBar** | Vertical line at center marking "now" | Blue, with triangle marker at top |
| **ChunkMarkers** | Vertical lines dividing time into chunks | Light gray, evenly spaced |
| **TimeAxis** | Horizontal baseline | Thin gray line |

### Layer 2: Model Indicators (Move with time)
| Element | Description | Style |
|---------|-------------|-------|
| **VideoModel** | 3-chunk wide box showing when video model runs | Purple outlined, rounded corners |
| **ActionModel** | 1-chunk wide box showing when action model runs | Yellow/orange outlined, rounded corners |

### Layer 3: Data Blocks (Move with time)
| Element | Description | Style |
|---------|-------------|-------|
| **VisionHistory** | Past video frames fed to model | Solid purple fill |
| **VideoPrediction** | 3-chunk predicted future video | Purple hatched/striped |
| **ActionChunk** | 1-chunk of predicted actions | Yellow hatched/striped |

---

## Coordinate System

```
Time (chunks):  ... -3  -2  -1   0   1   2   3  ...
                          ↑
                       TimeBar (x=0, always)

Vertical layers:
  y = 2.0   Video Prediction track
  y = 1.0   Model indicators track  
  y = 0.0   TimeAxis
  y = -1.0  Vision History track
  y = -2.0  Action output track
```

### Key Formula
```python
def time_to_x(time_in_chunks, current_time):
    """Convert absolute time to screen x-coordinate."""
    return (time_in_chunks - current_time) * CHUNK_WIDTH
```

As `current_time` increases, all elements shift left.

---

## Custom Classes Needed

### 1. `HatchedRectangle(VGroup)`
Creates a rectangle with diagonal line fill pattern.

```python
class HatchedRectangle(VGroup):
    def __init__(self, width, height, color, hatch_spacing=0.1, hatch_angle=45, **kwargs):
        # Rectangle outline
        # Diagonal lines clipped to rectangle bounds
```

### 2. `TimelineElement(VGroup)`
Base class for elements that move with time.

```python
class TimelineElement(VGroup):
    def __init__(self, start_time, end_time, y_position, **kwargs):
        self.start_time = start_time
        self.end_time = end_time
        self.y_position = y_position
        
    def update_position(self, current_time):
        """Shift element based on current time."""
        x = time_to_x(self.start_time, current_time)
        self.move_to([x + self.width/2, self.y_position, 0])
```

### 3. `VisionHistory(TimelineElement)`
Solid purple block representing history.

```python
class VisionHistory(TimelineElement):
    def __init__(self, start_time, end_time, **kwargs):
        # Solid purple rectangle
        # end_time typically equals current_time
```

### 4. `VideoPrediction(TimelineElement)`
Hatched purple block (3 chunks).

```python
class VideoPrediction(TimelineElement):
    def __init__(self, start_time, **kwargs):
        # Uses HatchedRectangle
        # Width = 3 * CHUNK_WIDTH
```

### 5. `ActionChunk(TimelineElement)`
Hatched yellow block (1 chunk).

```python
class ActionChunk(TimelineElement):
    def __init__(self, start_time, **kwargs):
        # Uses HatchedRectangle  
        # Width = 1 * CHUNK_WIDTH
```

### 6. `ModelIndicator(VGroup)`
Outlined box showing model computation period.

```python
class ModelIndicator(VGroup):
    def __init__(self, width_chunks, color, label=None, **kwargs):
        # Rounded rectangle, stroke only (no fill)
```

---

## Animation Sequence

### Phase 0: Setup (t=0)
```
- Add TimeBar (static at x=0)
- Add ChunkMarkers
- Add TimeAxis
- Add VisionHistory (extends from past to timebar)
- Add VideoModel indicator (positioned for current chunk)
- Add ActionModel indicator (to the right of VideoModel)
```

### Phase 1: Vision → Video Model (Keyframes 1→2)
**Duration**: ~1 chunk of time

1. **Time progresses**: All elements slide left via updaters
2. **Vision flows into model**: 
   - Copy of vision history right edge
   - Animate: scale down + translate up-right + fade
   - Target: VideoModel indicator

```python
# Pseudo-animation
self.play(
    time_tracker.animate.increment_value(1),  # Everything shifts
    vision_copy.animate.scale(0.3).move_to(video_model).fade(),
    run_time=CHUNK_DURATION
)
```

### Phase 2: Video Prediction Appears (Keyframe 3)
**Duration**: Brief

1. **VideoPrediction** fades in at correct position
2. Starts at `current_time` and extends 3 chunks into future

```python
video_pred = VideoPrediction(start_time=current_time)
self.play(FadeIn(video_pred))
```

### Phase 3: Video → Action Model (Keyframes 3→4)
**Duration**: Brief

1. **Video prediction flows into ActionModel**:
   - Copy portion of video prediction
   - Animate: translate down to action model indicator

### Phase 4: Action Chunk Appears (Keyframe 5)
**Duration**: Brief

1. **ActionChunk** fades in
2. Positioned for next chunk (chunk 1-2 relative to when computation started)

### Phase 5: Chunk Transition (Keyframe 6)
**Duration**: ~1 chunk

1. **Time progresses** another chunk
2. All elements slide left
3. Previous elements shift/fade as needed
4. New vision history extends to new "now"

### Phase 6: Actions → Vision History (Keyframe 7)
**Duration**: Continuous during inference

1. **Incremental conversion**: Every 1/8 chunk:
   - Small piece of ActionChunk fades out
   - Corresponding piece appears as VisionHistory extension

```python
# Using updater or stepped animation
for i in range(8):
    action_slice = action_chunk.get_slice(i)
    vision_extension = create_vision_slice(action_slice.position)
    self.play(
        FadeOut(action_slice),
        FadeIn(vision_extension),
        run_time=CHUNK_DURATION/8
    )
```

---

## Key Technical Challenges

### 1. Smooth Time Progression
Use `ValueTracker` + updaters:

```python
time_tracker = ValueTracker(0)

def update_element(mob):
    current_time = time_tracker.get_value()
    x = time_to_x(mob.start_time, current_time)
    mob.move_to([x + mob.width/2, mob.y_position, 0])

element.add_updater(update_element)
```

### 2. Hatched Fill Pattern
Option A: Diagonal lines clipped with `intersection`:
```python
lines = VGroup(*[Line(...) for angle in range(n)])
hatched = Intersection(rect, lines)
```

Option B: Use SVG pattern (more complex)

Option C: Many thin rectangles at angle (simpler):
```python
for i in range(n_lines):
    line = Line(start, end, stroke_width=1)
    line.rotate(45*DEGREES)
```

### 3. Element Lifecycle Management
Elements need to be created/destroyed as they enter/exit view:
- Create elements when they're about to enter frame
- Remove elements when they exit left side of frame
- Use `always_redraw` or careful updater management

### 4. Looping Animation
For seamless looping:
- End state should match start state (offset by N chunks)
- Fade out/in at loop point

---

## File Structure

```
inference_rollout/
├── inference_rollout.py      # Main animation
├── timeline_elements.py      # Custom Mobject classes
├── constants.py              # Timing, colors, dimensions
├── README.md                 # Documentation
└── sketch_frames/            # Reference images
    ├── 1.jpg ... 7.jpg
```

---

## Constants to Define

```python
# Timing
CHUNK_DURATION = 1.0          # Seconds per chunk in animation
VIDEO_MODEL_CHUNKS = 1        # How long video model takes
ACTION_MODEL_CHUNKS = 0.5     # How long action model takes

# Dimensions  
CHUNK_WIDTH = 1.5             # World units per chunk
TRACK_HEIGHT = 0.6            # Height of data blocks
TRACK_SPACING = 1.2           # Vertical spacing between tracks

# Colors
VISION_COLOR = "#9B7BB8"      # Purple
VIDEO_PRED_COLOR = "#9B7BB8"  # Purple (hatched)
ACTION_COLOR = "#F5A623"      # Yellow/orange
TIMEBAR_COLOR = "#4A90D9"     # Blue

# Hatching
HATCH_SPACING = 0.15
HATCH_ANGLE = 45 * DEGREES
```

---

## Suggested Implementation Order

1. **Constants & Utilities** (`constants.py`)
   - Define all constants
   - `time_to_x()` function

2. **Basic Elements** (`timeline_elements.py`)
   - `HatchedRectangle` 
   - `TimelineElement` base class
   - `VisionHistory`
   - `ModelIndicator`

3. **Static Scene Test**
   - Render keyframe 1 as static image
   - Verify positioning and styling

4. **Time Progression**
   - Add `ValueTracker`
   - Add updaters to elements
   - Test smooth sliding

5. **Flow Animations**
   - Vision → VideoModel flow effect
   - VideoPrediction → ActionModel flow effect

6. **Output Elements**
   - `VideoPrediction` appearance
   - `ActionChunk` appearance

7. **Full Cycle**
   - Chain all phases together
   - Add chunk transition

8. **Action→Vision Conversion**
   - Incremental slice conversion
   - Smooth visual effect

9. **Polish**
   - Timing adjustments
   - Easing curves
   - Loop preparation

---

## Questions to Resolve

1. **How many chunks of history to show?** (Looks like ~4 in sketches)
2. **Should models slide left too, or stay fixed?** (Sketches show them moving)
3. **Exact timing**: How long does each model computation take in real time vs animation time?
4. **Loop point**: After how many chunks should animation loop?
5. **Labels**: Should models be labeled with text?
