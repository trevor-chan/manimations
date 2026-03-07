"""
Inference Rollout Animation - Closed-loop inference timing visualization

Shows the flow and timing of a two-stage robotics model:
1. Video Model: vision history → 3-chunk video prediction
2. Action Model: video prediction → 1-chunk actions
"""

from manim import *
import math

# =============================================================================
# CONFIGURATION
# =============================================================================

# Aspect ratio (2:1)
config.pixel_width = 1920
config.pixel_height = 960
config.frame_width = 16
config.frame_height = 8

# =============================================================================
# CONSTANTS
# =============================================================================

# Dimensions
CHUNK_WIDTH = 2.6             # World units per chunk (stretched horizontally)
NUM_ACTION_CHIPS = 8          # Number of action chips per chunk
CHIP_WIDTH = CHUNK_WIDTH / NUM_ACTION_CHIPS  # Width of each action chip

# Model positioning within a chunk (no margins - models span full chunk)
MODEL_GAP = 0      # Small gap between video and action model

# Calculate model widths (both fit within one chunk, no margins)
# Video model gets 75% (6 chips), action model gets 25% (2 chips)
AVAILABLE_MODEL_WIDTH = CHUNK_WIDTH - MODEL_GAP
VIDEO_MODEL_WIDTH = AVAILABLE_MODEL_WIDTH * 0.75
ACTION_MODEL_WIDTH = AVAILABLE_MODEL_WIDTH * 0.25

# Vertical positioning - computed for consistent gaps
# Elements (top to bottom): video model, video pred, action model, action pred, vision history
TRACK_HEIGHT = 0.5            # Height of data blocks (predictions, history, actions)
MODEL_HEIGHT = 0.7            # Height of model indicator boxes
VERTICAL_GAP = 0.35           # Consistent gap between all elements
MARKER_MARGIN = 0.1           # Margin from chunk markers to outermost elements

# Compute Y positions from top to bottom
_video_model_top = 0  # Will offset everything to center around y=0
_video_model_bottom = _video_model_top - MODEL_HEIGHT
_video_pred_top = _video_model_bottom - VERTICAL_GAP
_video_pred_bottom = _video_pred_top - TRACK_HEIGHT
_action_model_top = _video_pred_bottom - VERTICAL_GAP
_action_model_bottom = _action_model_top - MODEL_HEIGHT
_action_pred_top = _action_model_bottom - VERTICAL_GAP
_action_pred_bottom = _action_pred_top - TRACK_HEIGHT
_vision_history_top = _action_pred_bottom - VERTICAL_GAP
_vision_history_bottom = _vision_history_top - TRACK_HEIGHT

# Total height and centering offset
_total_height = _video_model_top - _vision_history_bottom
_center_offset = _total_height / 2  # Shift to center around y=0

# Final Y positions (centers)
VIDEO_MODEL_Y = (_video_model_top + _video_model_bottom) / 2 + _center_offset
VIDEO_PRED_Y = (_video_pred_top + _video_pred_bottom) / 2 + _center_offset
ACTION_MODEL_Y = (_action_model_top + _action_model_bottom) / 2 + _center_offset
ACTION_Y = (_action_pred_top + _action_pred_bottom) / 2 + _center_offset
VISION_HISTORY_Y = (_vision_history_top + _vision_history_bottom) / 2 + _center_offset

# Chunk marker extents (with margin)
CHUNK_MARKER_TOP = _video_model_top + _center_offset + MARKER_MARGIN
CHUNK_MARKER_BOTTOM = _vision_history_bottom + _center_offset - MARKER_MARGIN

# Colors (all white for now - will be revised later)
VISION_COLOR = WHITE
ACTION_COLOR = WHITE
TIMEBAR_COLOR = WHITE
MARKER_COLOR = "#444444"      # Slightly lighter gray for chunk markers
BG_COLOR = BLACK              # Black background

# Hatching
HATCH_SPACING = 0.25          # Spacing between diagonal hatch lines
HATCH_ANGLE = 45 * DEGREES

# Timing (animation durations in seconds)
EXPLANATORY_CHUNK_TIME = 4.0  # Slow explanatory phase
SLOW_CHUNK_TIME = 2.0         # Slow continuous phase
FAST_CHUNK_TIME = 0.25        # Real-time phase (4 chunks/sec)

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def time_to_x(time_in_chunks, current_time):
    """Convert absolute chunk time to screen x-coordinate.
    
    Timebar is always at x=0 (current_time).
    Past (time < current_time) is to the left (negative x).
    Future (time > current_time) is to the right (positive x).
    """
    return (time_in_chunks - current_time) * CHUNK_WIDTH


# =============================================================================
# CUSTOM MOBJECTS
# =============================================================================

class HatchedRectangle(VGroup):
    """Rectangle with diagonal hatching pattern."""
    
    def __init__(self, width, height, color, hatch_spacing=HATCH_SPACING, 
                 hatch_angle=HATCH_ANGLE, stroke_width=2, fill_opacity=0.15, **kwargs):
        super().__init__(**kwargs)
        
        # Main rectangle (outline + light fill)
        self.rect = Rectangle(width=width, height=height)
        self.rect.set_stroke(color, width=stroke_width)
        self.rect.set_fill(color, opacity=fill_opacity)
        self.add(self.rect)
        
        # Create diagonal hatch lines at specified angle
        # We'll create lines and clip them to the rectangle bounds
        
        cos_a = math.cos(hatch_angle)
        sin_a = math.sin(hatch_angle)
        
        # Rectangle bounds
        left = -width / 2
        right = width / 2
        bottom = -height / 2
        top = height / 2
        
        # Calculate the range of offsets needed to cover the rectangle
        # Project rectangle corners onto perpendicular direction
        corners = [(left, bottom), (right, bottom), (left, top), (right, top)]
        perpendicular_offsets = [(-sin_a * x + cos_a * y) for x, y in corners]
        min_offset = min(perpendicular_offsets)
        max_offset = max(perpendicular_offsets)
        
        # Create lines at regular spacing
        offset = min_offset
        while offset <= max_offset:
            # Line passes through point (offset * -sin_a, offset * cos_a) in direction (cos_a, sin_a)
            # Find intersections with rectangle edges
            intersections = []
            
            # Parametric line: (offset * -sin_a + t * cos_a, offset * cos_a + t * sin_a)
            # Check intersection with each edge
            
            # Left edge: x = left
            if abs(cos_a) > 1e-10:
                t = (left - offset * (-sin_a)) / cos_a
                y = offset * cos_a + t * sin_a
                if bottom <= y <= top:
                    intersections.append((left, y))
            
            # Right edge: x = right
            if abs(cos_a) > 1e-10:
                t = (right - offset * (-sin_a)) / cos_a
                y = offset * cos_a + t * sin_a
                if bottom <= y <= top:
                    intersections.append((right, y))
            
            # Bottom edge: y = bottom
            if abs(sin_a) > 1e-10:
                t = (bottom - offset * cos_a) / sin_a
                x = offset * (-sin_a) + t * cos_a
                if left <= x <= right:
                    intersections.append((x, bottom))
            
            # Top edge: y = top
            if abs(sin_a) > 1e-10:
                t = (top - offset * cos_a) / sin_a
                x = offset * (-sin_a) + t * cos_a
                if left <= x <= right:
                    intersections.append((x, top))
            
            # Remove duplicates and ensure we have 2 points
            unique_intersections = []
            for pt in intersections:
                is_dup = False
                for existing in unique_intersections:
                    if abs(pt[0] - existing[0]) < 1e-10 and abs(pt[1] - existing[1]) < 1e-10:
                        is_dup = True
                        break
                if not is_dup:
                    unique_intersections.append(pt)
            
            if len(unique_intersections) >= 2:
                p1, p2 = unique_intersections[0], unique_intersections[1]
                line = Line(
                    start=[p1[0], p1[1], 0],
                    end=[p2[0], p2[1], 0],
                    stroke_width=1.5,
                    color=color
                )
                self.add(line)
            
            offset += hatch_spacing
    
    def get_width(self):
        return self.rect.get_width()
    
    def get_height(self):
        return self.rect.get_height()


class ModelIndicator(VGroup):
    """Rounded rectangle representing a model computation block."""
    
    def __init__(self, width, color, label_text=None, **kwargs):
        super().__init__(**kwargs)
        
        # Rounded rectangle outline
        self.box = RoundedRectangle(
            width=width,
            height=MODEL_HEIGHT,
            corner_radius=0.12,
            stroke_width=3,
            stroke_color=color,
            fill_opacity=0
        )
        self.add(self.box)
        
        # Label inside the box (optional)
        if label_text:
            self.label = Text(
                label_text,
                font="Arial",
                font_size=16,
                color=color
            )
            self.label.move_to(self.box.get_center())
            self.add(self.label)
    
    def get_width(self):
        return self.box.get_width()


# =============================================================================
# MAIN SCENE
# =============================================================================

class InferenceRollout(Scene):
    def construct(self):
        # Set background
        self.camera.background_color = BG_COLOR
        
        # =====================================================================
        # STATIC INFRASTRUCTURE
        # =====================================================================
        
        # Timebar - vertical line at x=0 with triangle marker
        timebar = Line(
            start=[0, CHUNK_MARKER_BOTTOM - 0.3, 0],
            end=[0, CHUNK_MARKER_TOP + 0.5, 0],
            stroke_width=3,
            color=TIMEBAR_COLOR
        )
        timebar_marker = Triangle(
            fill_color=TIMEBAR_COLOR,
            fill_opacity=1,
            stroke_width=0
        ).scale(0.15).rotate(PI).move_to([0, CHUNK_MARKER_TOP + 0.5, 0])
        timebar_group = VGroup(timebar, timebar_marker)
        timebar_group.set_z_index(100)  # Ensure timebar always renders on top
        
        # Chunk markers - vertical lines at each chunk boundary (including t=0)
        chunk_markers = VGroup()
        for i in range(-4, 6):
            marker = Line(
                start=[i * CHUNK_WIDTH, CHUNK_MARKER_BOTTOM, 0],
                end=[i * CHUNK_WIDTH, CHUNK_MARKER_TOP, 0],
                stroke_width=2,
                color=MARKER_COLOR
            )
            chunk_markers.add(marker)
        
        # =====================================================================
        # KEYFRAME 1: Initial state
        # =====================================================================
        
        # Current time tracker (starts at 0)
        current_time = 0
        
        # Vision History: solid purple block extending from past to present
        # History extends off screen to the left
        history_start = -4  # Far off screen to the left
        history_end = 0      # Up to current time
        history_width = (history_end - history_start) * CHUNK_WIDTH
        
        vision_history = Rectangle(
            width=history_width,
            height=TRACK_HEIGHT,
            fill_color=VISION_COLOR,
            fill_opacity=1.0,
            stroke_width=0  # Solid fill, no border
        )
        # Position: left edge at history_start, centered at VISION_HISTORY_Y
        vision_history.move_to([
            time_to_x(history_start, current_time) + history_width/2,
            VISION_HISTORY_Y,
            0
        ])
        
        # Both models fit within one chunk, starting at timebar
        # Layout: |--margin--|--video--|--gap--|--action--|--margin--|
        
        # Video Model indicator
        video_model = ModelIndicator(
            width=VIDEO_MODEL_WIDTH,
            color=VISION_COLOR
        )
        # Position: left edge at timebar (no margin)
        video_model_x = time_to_x(0, current_time) + VIDEO_MODEL_WIDTH/2
        video_model.move_to([video_model_x, VIDEO_MODEL_Y, 0])
        
        # Action Model indicator: immediately after video model with small gap
        action_model = ModelIndicator(
            width=ACTION_MODEL_WIDTH,
            color=ACTION_COLOR
        )
        # Position: left edge at video model right edge + gap
        action_model_x = video_model_x + VIDEO_MODEL_WIDTH/2 + MODEL_GAP + ACTION_MODEL_WIDTH/2
        action_model.move_to([action_model_x, ACTION_MODEL_Y, 0])
        
        # =====================================================================
        # ADD ELEMENTS TO SCENE
        # =====================================================================
        
        # Add infrastructure first
        self.add(chunk_markers)
        self.add(timebar_group)
        
        # Add main elements
        self.add(vision_history)
        self.add(video_model)
        self.add(action_model)
        
        # Hold for viewing keyframe 1
        self.wait(1)
        
        # =====================================================================
        # KEYFRAME 2: Vision flows into Video Model (no time progression)
        # =====================================================================
        
        # Create a ghost copy of vision history to animate flowing into model
        vision_ghost = vision_history.copy()
        vision_ghost.set_opacity(0.6)
        self.add(vision_ghost)
        
        # Target: video model's center position
        video_model_center = video_model.get_center()
        
        # Animate ghost flowing into video model
        # Timeline stays static - no time elapses during model input
        # Scale width (dim=0) more aggressively than height (dim=1)
        self.play(
            vision_ghost.animate.stretch(0.15, dim=0).stretch(0.6, dim=1).move_to(video_model_center).set_opacity(0),
            run_time=1.0
        )
        
        # Clean up ghost
        self.remove(vision_ghost)
        
        self.wait(0.5)
        
        # =====================================================================
        # KEYFRAME 3: Time progresses through Video Model, Video Prediction appears
        # =====================================================================
        
        # Time progresses through video model computation
        # Video model width as fraction of chunk
        video_model_time = VIDEO_MODEL_WIDTH / CHUNK_WIDTH
        
        # Use ValueTracker to smoothly progress time
        time_tracker = ValueTracker(0)
        
        # Elements that slide left as time progresses (excluding vision_history which grows)
        sliding_elements = [video_model, action_model, chunk_markers]
        
        # Store initial positions
        initial_positions = {id(mob): mob.get_center()[0] for mob in sliding_elements}
        
        def make_slide_updater(initial_x):
            """Create a slide updater with captured initial position."""
            def updater(mob):
                dt = time_tracker.get_value()
                new_x = initial_x - dt * CHUNK_WIDTH
                mob.move_to([new_x, mob.get_center()[1], 0])
            return updater
        
        # Add updaters to sliding elements
        for mob in sliding_elements:
            mob.add_updater(make_slide_updater(initial_positions[id(mob)]))
        
        # Create history chips for phase 1 (same style as phase 2)
        initial_history_width = vision_history.get_width()
        history_lag_phase1 = 1 * CHIP_WIDTH
        
        # Create initial gap chip to fill the lag (starts fully visible)
        phase1_gap_chip = Rectangle(
            width=CHIP_WIDTH,
            height=TRACK_HEIGHT,
            fill_color=VISION_COLOR,
            fill_opacity=1.0,
        )
        phase1_gap_chip.set_stroke(width=0, opacity=0)
        phase1_gap_chip.move_to([-CHIP_WIDTH/2, VISION_HISTORY_Y, 0])
        self.add(phase1_gap_chip)
        
        # Create chips that will fade in during this time segment
        phase1_history_chips = []
        # Calculate how many chips we need for video_model_time duration
        chips_needed = int(np.ceil(video_model_time * NUM_ACTION_CHIPS)) + 2
        for i in range(chips_needed):
            chip = Rectangle(
                width=CHIP_WIDTH,
                height=TRACK_HEIGHT,
                fill_color=VISION_COLOR,
                fill_opacity=0,
            )
            chip.set_stroke(width=0, opacity=0)
            chip_x = CHIP_WIDTH / 2 + i * CHIP_WIDTH
            chip.move_to([chip_x, VISION_HISTORY_Y, 0])
            self.add(chip)
            phase1_history_chips.append(chip)
        
        # Chip updaters: fade in, hold, fade out (based on absolute chunk time)
        # Each chip spans 1/NUM_ACTION_CHIPS of a chunk in time
        chip_duration = 1.0 / NUM_ACTION_CHIPS  # Duration of each chip phase in chunk units
        
        def make_phase1_chip_updater(chip_index, initial_chip_x):
            def updater(mob):
                dt = time_tracker.get_value()  # dt is in chunk units (0 to video_model_time)
                
                # Slide with timeline
                new_x = initial_chip_x - dt * CHUNK_WIDTH
                mob.move_to([new_x, VISION_HISTORY_Y, 0])
                
                # Fade timing based on absolute chunk time
                # Each chip phase (fade in, hold, fade out) lasts chip_duration
                chip_start_t = chip_index * chip_duration
                chip_end_t = (chip_index + 1) * chip_duration      # End of fade in
                hold_end_t = (chip_index + 2) * chip_duration      # End of hold
                fade_out_end_t = (chip_index + 3) * chip_duration  # End of fade out
                
                if dt < chip_start_t:
                    mob.set_fill(opacity=0)
                elif dt < chip_end_t:
                    fade_in_progress = (dt - chip_start_t) / chip_duration
                    mob.set_fill(opacity=1.0 * fade_in_progress)
                elif dt < hold_end_t:
                    mob.set_fill(opacity=1.0)
                elif dt < fade_out_end_t:
                    fade_out_progress = (dt - hold_end_t) / chip_duration
                    mob.set_fill(opacity=1.0 * (1 - fade_out_progress))
                else:
                    mob.set_fill(opacity=0)
            return updater
        
        for i, chip in enumerate(phase1_history_chips):
            chip_initial_x = chip.get_center()[0]
            chip.add_updater(make_phase1_chip_updater(i, chip_initial_x))
        
        # Main history grows with lag
        def history_grow_updater(mob):
            dt = time_tracker.get_value()
            new_width = initial_history_width + dt * CHUNK_WIDTH
            mob.stretch_to_fit_width(new_width)
            # Position with right edge behind timebar by history_lag
            mob.move_to([-history_lag_phase1 - new_width/2, VISION_HISTORY_Y, 0])
        
        vision_history.add_updater(history_grow_updater)
        
        # Slide updater for gap chip
        gap_chip_initial_x = phase1_gap_chip.get_center()[0]
        def gap_chip_slide(mob):
            dt = time_tracker.get_value()
            new_x = gap_chip_initial_x - dt * CHUNK_WIDTH
            mob.move_to([new_x, VISION_HISTORY_Y, 0])
        phase1_gap_chip.add_updater(gap_chip_slide)
        
        # Animate time progression through video model
        self.play(
            time_tracker.animate.set_value(video_model_time),
            run_time=1.5
        )
        
        # Remove updaters and clean up chips
        for mob in sliding_elements:
            mob.clear_updaters()
        vision_history.clear_updaters()
        for chip in phase1_history_chips:
            chip.clear_updaters()
            self.remove(chip)
        phase1_gap_chip.clear_updaters()
        self.remove(phase1_gap_chip)
        
        # Extend history to current position (remove lag)
        current_width = vision_history.get_width()
        vision_history.move_to([-current_width/2, VISION_HISTORY_Y, 0])
        
        # Create Video Prediction: hatched rectangle, 3 chunks long
        # Starts at the beginning of the chunk (which has shifted left)
        video_pred_width = 3 * CHUNK_WIDTH
        
        # The chunk boundary started at x=0 but has shifted left by video_model_time * CHUNK_WIDTH
        chunk_start_x = -video_model_time * CHUNK_WIDTH
        
        # Final position for video prediction
        video_pred_final_x = chunk_start_x + video_pred_width / 2
        video_pred_final_y = VIDEO_PRED_Y
        
        # Create a simple rectangle ghost that expands from video model
        # (no hatching during animation to avoid artifacts)
        video_model_current_pos = video_model.get_center()
        
        pred_ghost = Rectangle(
            width=VIDEO_MODEL_WIDTH,  # Start at video model width
            height=TRACK_HEIGHT,
            fill_color=VISION_COLOR,
            fill_opacity=0.25,  # Match video_prediction opacity
            stroke_color=VISION_COLOR,
            stroke_width=2
        )
        pred_ghost.move_to(video_model_current_pos)
        
        self.add(pred_ghost)
        
        # Animate ghost expanding from video model to final prediction position
        self.play(
            pred_ghost.animate.stretch(video_pred_width / VIDEO_MODEL_WIDTH, dim=0).move_to([video_pred_final_x, video_pred_final_y, 0]),
            run_time=0.8
        )
        
        # Create the final video prediction and instant swap with ghost
        video_prediction = Rectangle(
            width=video_pred_width,
            height=TRACK_HEIGHT,
            fill_color=VISION_COLOR,
            fill_opacity=0.25,  # 25% fill (more transparent than history)
            stroke_color=VISION_COLOR,
            stroke_width=2
        )
        video_prediction.move_to([video_pred_final_x, video_pred_final_y, 0])
        
        # Instant swap: remove ghost, add prediction (same frame)
        self.remove(pred_ghost)
        self.add(video_prediction)
        
        self.wait(0.5)
        
        # =====================================================================
        # KEYFRAME 4: Video Prediction flows into Action Model
        # =====================================================================
        
        # Create a ghost of video prediction to animate into action model
        pred_ghost_2 = video_prediction.copy()
        pred_ghost_2.set_fill(opacity=0.25)
        self.add(pred_ghost_2)
        
        # Target: action model's current position
        action_model_pos = action_model.get_center()
        
        # Animate ghost compressing and moving down into action model
        self.play(
            pred_ghost_2.animate.stretch(ACTION_MODEL_WIDTH / video_pred_width, dim=0).move_to(action_model_pos).set_opacity(0),
            run_time=1.0
        )
        
        # Clean up ghost
        self.remove(pred_ghost_2)
        
        self.wait(0.3)
        
        # =====================================================================
        # KEYFRAME 5 (Part 1): Time progresses through Action Model
        # =====================================================================
        
        # Time progresses through action model computation
        action_model_time = ACTION_MODEL_WIDTH / CHUNK_WIDTH
        
        # Use ValueTracker to smoothly progress time
        time_tracker_2 = ValueTracker(0)
        
        # Elements that slide left (excluding vision_history which grows)
        sliding_elements_2 = [video_model, action_model, chunk_markers, video_prediction]
        
        # Store initial positions
        initial_positions_2 = {id(mob): mob.get_center()[0] for mob in sliding_elements_2}
        
        def make_slide_updater_2(initial_x):
            def updater(mob):
                dt = time_tracker_2.get_value()
                new_x = initial_x - dt * CHUNK_WIDTH
                mob.move_to([new_x, mob.get_center()[1], 0])
            return updater
        
        # Add updaters
        for mob in sliding_elements_2:
            mob.add_updater(make_slide_updater_2(initial_positions_2[id(mob)]))
        
        # Create history chips for action model phase
        initial_history_width_2 = vision_history.get_width()
        
        # Create initial gap chip for this segment
        phase1_gap_chip_2 = Rectangle(
            width=CHIP_WIDTH,
            height=TRACK_HEIGHT,
            fill_color=VISION_COLOR,
            fill_opacity=1.0,
        )
        phase1_gap_chip_2.set_stroke(width=0, opacity=0)
        phase1_gap_chip_2.move_to([-CHIP_WIDTH/2, VISION_HISTORY_Y, 0])
        self.add(phase1_gap_chip_2)
        
        # Create chips for this time segment
        phase1_history_chips_2 = []
        chips_needed_2 = int(np.ceil(action_model_time * NUM_ACTION_CHIPS)) + 2
        for i in range(chips_needed_2):
            chip = Rectangle(
                width=CHIP_WIDTH,
                height=TRACK_HEIGHT,
                fill_color=VISION_COLOR,
                fill_opacity=0,
            )
            chip.set_stroke(width=0, opacity=0)
            chip_x = CHIP_WIDTH / 2 + i * CHIP_WIDTH
            chip.move_to([chip_x, VISION_HISTORY_Y, 0])
            self.add(chip)
            phase1_history_chips_2.append(chip)
        
        # Chip updaters (based on absolute chunk time)
        chip_duration_2 = 1.0 / NUM_ACTION_CHIPS
        
        def make_phase1_chip_updater_2(chip_index, initial_chip_x):
            def updater(mob):
                dt = time_tracker_2.get_value()  # dt is in chunk units
                
                new_x = initial_chip_x - dt * CHUNK_WIDTH
                mob.move_to([new_x, VISION_HISTORY_Y, 0])
                
                # Fade timing based on absolute chunk time
                chip_start_t = chip_index * chip_duration_2
                chip_end_t = (chip_index + 1) * chip_duration_2
                hold_end_t = (chip_index + 2) * chip_duration_2
                fade_out_end_t = (chip_index + 3) * chip_duration_2
                
                if dt < chip_start_t:
                    mob.set_fill(opacity=0)
                elif dt < chip_end_t:
                    fade_in_progress = (dt - chip_start_t) / chip_duration_2
                    mob.set_fill(opacity=1.0 * fade_in_progress)
                elif dt < hold_end_t:
                    mob.set_fill(opacity=1.0)
                elif dt < fade_out_end_t:
                    fade_out_progress = (dt - hold_end_t) / chip_duration_2
                    mob.set_fill(opacity=1.0 * (1 - fade_out_progress))
                else:
                    mob.set_fill(opacity=0)
            return updater
        
        for i, chip in enumerate(phase1_history_chips_2):
            chip_initial_x = chip.get_center()[0]
            chip.add_updater(make_phase1_chip_updater_2(i, chip_initial_x))
        
        # Main history grows with lag
        def history_grow_updater_2(mob):
            dt = time_tracker_2.get_value()
            new_width = initial_history_width_2 + dt * CHUNK_WIDTH
            mob.stretch_to_fit_width(new_width)
            mob.move_to([-history_lag_phase1 - new_width/2, VISION_HISTORY_Y, 0])
        
        vision_history.add_updater(history_grow_updater_2)
        
        # Slide updater for gap chip
        gap_chip_2_initial_x = phase1_gap_chip_2.get_center()[0]
        def gap_chip_2_slide(mob):
            dt = time_tracker_2.get_value()
            new_x = gap_chip_2_initial_x - dt * CHUNK_WIDTH
            mob.move_to([new_x, VISION_HISTORY_Y, 0])
        phase1_gap_chip_2.add_updater(gap_chip_2_slide)
        
        # Animate time progression through action model
        self.play(
            time_tracker_2.animate.set_value(action_model_time),
            run_time=1.0
        )
        
        # Remove updaters and clean up chips
        for mob in sliding_elements_2:
            mob.clear_updaters()
        for chip in phase1_history_chips_2:
            chip.clear_updaters()
            self.remove(chip)
        phase1_gap_chip_2.clear_updaters()
        self.remove(phase1_gap_chip_2)
        
        # Extend history to current position
        current_width_2 = vision_history.get_width()
        vision_history.move_to([-current_width_2/2, VISION_HISTORY_Y, 0])
        vision_history.clear_updaters()
        
        # =====================================================================
        # KEYFRAME 5 (Part 2): Action chips appear from Action Model
        # =====================================================================
        
        # Create ghost chips from action model that expand to action chip positions
        action_model_current_pos = action_model.get_center()
        
        action_ghosts = []
        action_chips = []
        for i in range(NUM_ACTION_CHIPS):
            # Ghost starts at action model
            ghost = Rectangle(
                width=ACTION_MODEL_WIDTH * 0.1,  # Start very narrow
                height=TRACK_HEIGHT,
                fill_color=ACTION_COLOR,
                fill_opacity=0.25,
                stroke_color=ACTION_COLOR,
                stroke_width=1
            )
            ghost.move_to(action_model_current_pos)
            self.add(ghost)
            action_ghosts.append(ghost)
            
            # Final chip position
            chip_x = CHIP_WIDTH / 2 + i * CHIP_WIDTH
            chip = Rectangle(
                width=CHIP_WIDTH,
                height=TRACK_HEIGHT,
                fill_color=ACTION_COLOR,
                fill_opacity=0.25,
                stroke_color=ACTION_COLOR,
                stroke_width=1
            )
            chip.move_to([chip_x, ACTION_Y, 0])
            action_chips.append(chip)
        
        # Animate all ghosts expanding from action model to their chip positions
        self.play(
            *[
                ghost.animate.stretch_to_fit_width(CHIP_WIDTH).move_to([CHIP_WIDTH / 2 + i * CHIP_WIDTH, ACTION_Y, 0])
                for i, ghost in enumerate(action_ghosts)
            ],
            run_time=0.8
        )
        
        # Instant swap ghosts for final chips
        for ghost in action_ghosts:
            self.remove(ghost)
        for chip in action_chips:
            self.add(chip)
        
        self.wait(0.5)
        
        # =====================================================================
        # TRANSITION: Keep visuals, only fade models to new position
        # =====================================================================
        
        loop_time = SLOW_CHUNK_TIME * 2  # 2x slower
        video_model_frac = VIDEO_MODEL_WIDTH / CHUNK_WIDTH
        action_model_frac = ACTION_MODEL_WIDTH / CHUNK_WIDTH
        ghost_duration_frac = 1/8  # Ghost animations complete in 1/8 chunk
        
        # Get current positions of phase 1 objects
        phase1_video_model_pos = video_model.get_center()
        phase1_action_model_pos = action_model.get_center()
        phase1_video_pred_pos = video_prediction.get_center()
        phase1_chunk_markers_pos = chunk_markers.get_center()
        phase1_history_width = vision_history.get_width()
        phase1_history_pos = vision_history.get_center()
        
        # --- Instant wipe and remake for non-model objects ---
        
        # Remove old objects (not models)
        self.remove(vision_history)
        self.remove(video_prediction)
        self.remove(chunk_markers)
        for chip in action_chips:
            self.remove(chip)
        
        # Create new loop versions at the SAME positions
        
        # Chunk markers at current position
        # Calculate how much the original markers shifted
        # Original markers ranged from -4 to 5, center was at 0.5*CHUNK_WIDTH
        original_center_x = 0.5 * CHUNK_WIDTH
        shift_amount = original_center_x - phase1_chunk_markers_pos[0]
        
        loop_chunk_markers = VGroup()
        for i in range(-5, 12):  # Extended range for more markers to the right
            marker = Line(
                start=[i * CHUNK_WIDTH - shift_amount, CHUNK_MARKER_BOTTOM, 0],
                end=[i * CHUNK_WIDTH - shift_amount, CHUNK_MARKER_TOP, 0],
                stroke_color=MARKER_COLOR,
                stroke_width=2
            )
            loop_chunk_markers.add(marker)
        self.add(loop_chunk_markers)
        
        # Bring timebar to front so it renders on top of chunk markers
        self.bring_to_front(timebar_group)
        
        # Vision history at current position
        loop_vision_history = Rectangle(
            width=phase1_history_width,
            height=TRACK_HEIGHT,
            fill_color=VISION_COLOR,
            fill_opacity=1.0,
            stroke_width=0
        )
        loop_vision_history.move_to(phase1_history_pos)
        self.add(loop_vision_history)
        
        # Video prediction at current position
        loop_video_pred_width = 3 * CHUNK_WIDTH
        loop_video_prediction = Rectangle(
            width=loop_video_pred_width,
            height=TRACK_HEIGHT,
            fill_color=VISION_COLOR,
            fill_opacity=0.25,
            stroke_color=VISION_COLOR,
            stroke_width=2
        )
        loop_video_prediction.move_to(phase1_video_pred_pos)
        self.add(loop_video_prediction)
        
        # Action chips at current positions
        loop_action_chips = []
        for i, old_chip in enumerate(action_chips):
            chip = Rectangle(
                width=CHIP_WIDTH,
                height=TRACK_HEIGHT,
                fill_color=ACTION_COLOR,
                fill_opacity=0.25,
                stroke_color=ACTION_COLOR,
                stroke_width=1
            )
            chip.move_to(old_chip.get_center())
            self.add(chip)
            loop_action_chips.append(chip)
        
        # Create initial gap chip (at current time position, will slide left)
        history_lag_init = 1 * CHIP_WIDTH
        initial_fade_gap_chips = []
        gap_chip = Rectangle(
            width=CHIP_WIDTH,
            height=TRACK_HEIGHT,
            fill_color=VISION_COLOR,
            fill_opacity=1.0,
        )
        gap_chip.set_stroke(width=0, opacity=0)
        gap_chip.move_to([-CHIP_WIDTH/2, VISION_HISTORY_Y, 0])
        self.add(gap_chip)
        initial_fade_gap_chips.append(gap_chip)
        
        # --- Create new models at NEXT chunk position ---
        loop_video_model = ModelIndicator(width=VIDEO_MODEL_WIDTH, color=VISION_COLOR)
        loop_video_model.move_to([VIDEO_MODEL_WIDTH / 2, VIDEO_MODEL_Y, 0])
        loop_video_model.set_stroke(opacity=0)  # Start invisible
        self.add(loop_video_model)
        
        loop_action_model = ModelIndicator(width=ACTION_MODEL_WIDTH, color=ACTION_COLOR)
        loop_action_model.move_to([VIDEO_MODEL_WIDTH / 2 + VIDEO_MODEL_WIDTH/2 + MODEL_GAP + ACTION_MODEL_WIDTH/2, ACTION_MODEL_Y, 0])
        loop_action_model.set_stroke(opacity=0)  # Start invisible
        self.add(loop_action_model)
        
        # Fade out old models, fade in new models simultaneously
        self.play(
            video_model.animate.set_stroke(opacity=0),
            action_model.animate.set_stroke(opacity=0),
            loop_video_model.animate.set_stroke(opacity=1),
            loop_action_model.animate.set_stroke(opacity=1),
            run_time=0.5
        )
        
        # Remove old models
        self.remove(video_model)
        self.remove(action_model)
        
        for loop_iteration in range(4):  # Run loop 2 times
            
            # Single time tracker for entire chunk (0 to 1)
            chunk_time = ValueTracker(0)
            
            # Create new models for the NEXT chunk (will fade in at end of this chunk)
            new_video_model = ModelIndicator(width=VIDEO_MODEL_WIDTH, color=VISION_COLOR)
            new_video_model.move_to([VIDEO_MODEL_WIDTH / 2, VIDEO_MODEL_Y, 0])
            new_video_model.set_stroke(opacity=0)  # Start invisible
            
            new_action_model = ModelIndicator(width=ACTION_MODEL_WIDTH, color=ACTION_COLOR)
            new_action_model.move_to([VIDEO_MODEL_WIDTH / 2 + VIDEO_MODEL_WIDTH/2 + MODEL_GAP + ACTION_MODEL_WIDTH/2, ACTION_MODEL_Y, 0])
            new_action_model.set_stroke(opacity=0)  # Start invisible
            
            self.add(new_video_model, new_action_model)
            
            # Model crossfade updaters - current models fade out, new models fade in at END
            model_fade_start_t = 1 - ghost_duration_frac
            
            def make_model_fade_out(fade_start):
                def updater(mob):
                    t = chunk_time.get_value()
                    if t < fade_start:
                        return
                    fade_progress = min((t - fade_start) / ghost_duration_frac, 1.0)
                    mob.set_stroke(opacity=1 - fade_progress)
                return updater
            
            def make_model_fade_in(fade_start):
                def updater(mob):
                    t = chunk_time.get_value()
                    if t < fade_start:
                        return
                    fade_progress = min((t - fade_start) / ghost_duration_frac, 1.0)
                    mob.set_stroke(opacity=fade_progress)
                return updater
            
            loop_video_model.add_updater(make_model_fade_out(model_fade_start_t))
            loop_action_model.add_updater(make_model_fade_out(model_fade_start_t))
            new_video_model.add_updater(make_model_fade_in(model_fade_start_t))
            new_action_model.add_updater(make_model_fade_in(model_fade_start_t))
            
            # All elements that slide left continuously
            sliding_elements_loop = [
                loop_video_model, loop_action_model, loop_chunk_markers, 
                loop_video_prediction
            ] + loop_action_chips
            initial_positions_loop = {id(mob): mob.get_center()[0] for mob in sliding_elements_loop}
            
            # New models also slide (so they move while fading in)
            new_video_model_initial_x = new_video_model.get_center()[0]
            new_action_model_initial_x = new_action_model.get_center()[0]
            
            def make_continuous_slide_updater(initial_x):
                def updater(mob):
                    t = chunk_time.get_value()
                    new_x = initial_x - t * CHUNK_WIDTH
                    mob.move_to([new_x, mob.get_center()[1], 0])
                return updater
            
            for mob in sliding_elements_loop:
                mob.add_updater(make_continuous_slide_updater(initial_positions_loop[id(mob)]))
            
            # Add slide updaters to new models
            new_video_model.add_updater(make_continuous_slide_updater(new_video_model_initial_x))
            new_action_model.add_updater(make_continuous_slide_updater(new_action_model_initial_x))
            
            # Action chips fade out as they reach the timebar (x=0)
            def make_chip_fade_updater(chip_initial_x):
                def updater(mob):
                    t = chunk_time.get_value()
                    current_x = chip_initial_x - t * CHUNK_WIDTH
                    chip_right_edge = current_x + CHIP_WIDTH / 2
                    
                    # Fade out as the chip crosses the timebar
                    if chip_right_edge <= 0:
                        # Fully past timebar
                        mob.set_opacity(0)
                    elif chip_right_edge <= CHIP_WIDTH:
                        # Fading out (chip is crossing the timebar)
                        fade_progress = 1 - (chip_right_edge / CHIP_WIDTH)
                        mob.set_fill(opacity=0.25 * (1 - fade_progress))
                        mob.set_stroke(opacity=1 - fade_progress)
                    else:
                        # Not yet at timebar
                        mob.set_fill(opacity=0.25)
                        mob.set_stroke(opacity=1)
                return updater
            
            for chip in loop_action_chips:
                chip_initial_x = chip.get_center()[0]
                chip.add_updater(make_chip_fade_updater(chip_initial_x))
            
            # Vision history grows via chips that fade in sequentially
            initial_history_width_loop = loop_vision_history.get_width()
            
            # Use pre-created gap chips for iteration 0, create new ones for others
            if loop_iteration == 0:
                # Use the chips that were faded in with the loop
                initial_gap_chips = initial_fade_gap_chips
            else:
                # Create fresh gap chips for subsequent iterations
                initial_gap_chips = []
                gap_chip = Rectangle(
                    width=CHIP_WIDTH,
                    height=TRACK_HEIGHT,
                    fill_color=VISION_COLOR,
                    fill_opacity=1.0,  # Start fully visible to fill the gap
                )
                gap_chip.set_stroke(width=0, opacity=0)
                gap_chip.move_to([-CHIP_WIDTH/2, VISION_HISTORY_Y, 0])
                self.add(gap_chip)
                initial_gap_chips.append(gap_chip)
            
            # Create history chips that appear at full opacity and fade OUT
            history_chips = []
            for i in range(NUM_ACTION_CHIPS):
                chip = Rectangle(
                    width=CHIP_WIDTH,
                    height=TRACK_HEIGHT,
                    fill_color=VISION_COLOR,
                    fill_opacity=0,  # Start invisible, appear when it's their turn
                )
                chip.set_stroke(width=0, opacity=0)  # No border
                # Position each chip at the leading edge
                chip_x = CHIP_WIDTH / 2 + i * CHIP_WIDTH
                chip.move_to([chip_x, VISION_HISTORY_Y, 0])
                self.add(chip)
                history_chips.append(chip)
            
            # Updater: chips slide left, fade IN, HOLD at full opacity, then fade OUT
            def make_history_chip_updater(chip_index, initial_chip_x):
                def updater(mob):
                    t = chunk_time.get_value()
                    # Slide with timeline
                    new_x = initial_chip_x - t * CHUNK_WIDTH
                    mob.move_to([new_x, VISION_HISTORY_Y, 0])
                    
                    # Chip timing: fade in -> hold -> fade out (1 chip each)
                    chip_start_t = chip_index / NUM_ACTION_CHIPS
                    chip_end_t = (chip_index + 1) / NUM_ACTION_CHIPS      # End of fade in
                    hold_end_t = (chip_index + 2) / NUM_ACTION_CHIPS      # End of hold (1 chip duration)
                    fade_out_end_t = (chip_index + 3) / NUM_ACTION_CHIPS  # End of fade out
                    
                    if t < chip_start_t:
                        # Not yet visible
                        mob.set_fill(opacity=0)
                    elif t < chip_end_t:
                        # Fading IN
                        fade_in_progress = (t - chip_start_t) / (chip_end_t - chip_start_t)
                        mob.set_fill(opacity=1.0 * fade_in_progress)
                    elif t < hold_end_t:
                        # HOLD at full opacity
                        mob.set_fill(opacity=1.0)
                    elif t < fade_out_end_t:
                        # Fading out (history is catching up)
                        fade_out_progress = (t - hold_end_t) / (fade_out_end_t - hold_end_t)
                        mob.set_fill(opacity=1.0 * (1 - fade_out_progress))
                    else:
                        # Fully faded out (absorbed into history)
                        mob.set_fill(opacity=0)
                return updater
            
            for i, chip in enumerate(history_chips):
                chip_initial_x = chip.get_center()[0]
                chip.add_updater(make_history_chip_updater(i, chip_initial_x))
            
            # Updater for initial gap chip (just slide, stay visible)
            def make_gap_chip_updater(initial_gap_x):
                def updater(mob):
                    t = chunk_time.get_value()
                    # Slide with timeline, stay fully visible
                    new_x = initial_gap_x - t * CHUNK_WIDTH
                    mob.move_to([new_x, VISION_HISTORY_Y, 0])
                return updater
            
            for gap_chip in initial_gap_chips:
                gap_chip_initial_x = gap_chip.get_center()[0]
                gap_chip.add_updater(make_gap_chip_updater(gap_chip_initial_x))
            
            # Main history grows but stays 2 chips behind the current time
            # (chips fade in over 1 slot, then fade out over the next slot)
            history_lag = 1 * CHIP_WIDTH  # Right edge stays this far behind timebar
            def history_grow_delayed(mob):
                t = chunk_time.get_value()
                # History grows continuously but right edge stays behind timebar
                new_width = initial_history_width_loop + t * CHUNK_WIDTH
                mob.stretch_to_fit_width(new_width)
                # Position so right edge is at -history_lag (behind timebar)
                right_edge = -history_lag
                center_x = right_edge - new_width/2
                mob.move_to([center_x, VISION_HISTORY_Y, 0])
            loop_vision_history.add_updater(history_grow_delayed)
            
            # Old video prediction fades out (completes in first 15% of chunk)
            old_video_pred_initial_opacity = loop_video_prediction.get_fill_opacity()
            def old_video_pred_fade(mob):
                t = chunk_time.get_value()
                fade_progress = min(t / 0.15, 1.0)
                mob.set_fill(opacity=old_video_pred_initial_opacity * (1 - fade_progress))
                mob.set_stroke(opacity=1 - fade_progress)
            loop_video_prediction.add_updater(old_video_pred_fade)
            
            # --- Vision ghost flows INTO video model ---
            vision_ghost_loop = loop_vision_history.copy()
            vision_ghost_loop.set_opacity(0.6)
            vision_ghost_loop.clear_updaters()
            self.add(vision_ghost_loop)
            
            video_model_initial_x = loop_video_model.get_center()[0]
            def ghost_track_model(mob):
                t = chunk_time.get_value()
                ghost_progress = min(t / ghost_duration_frac, 1.0)
                target_x = video_model_initial_x - t * CHUNK_WIDTH
                
                if not hasattr(mob, '_start_x'):
                    mob._start_x = mob.get_center()[0]
                    mob._start_width = mob.get_width()
                    mob._start_height = mob.get_height()
                
                current_x = mob._start_x + (target_x - mob._start_x) * ghost_progress
                current_y = VISION_HISTORY_Y + (VIDEO_MODEL_Y - VISION_HISTORY_Y) * ghost_progress
                mob.move_to([current_x, current_y, 0])
                
                target_width = VIDEO_MODEL_WIDTH * 0.8
                target_height = MODEL_HEIGHT * 0.6
                new_width = mob._start_width + (target_width - mob._start_width) * ghost_progress
                new_height = mob._start_height + (target_height - mob._start_height) * ghost_progress
                mob.stretch_to_fit_width(new_width)
                mob.stretch_to_fit_height(new_height)
                mob.set_opacity(0.6 * (1 - ghost_progress))
            
            vision_ghost_loop.add_updater(ghost_track_model)
            
            # --- Video prediction ghost OUT of video model ---
            video_pred_width_loop = 3 * CHUNK_WIDTH
            video_pred_ghost_out = Rectangle(
                width=VIDEO_MODEL_WIDTH * 0.8,
                height=TRACK_HEIGHT,
                fill_color=VISION_COLOR,
                fill_opacity=0.0,
                stroke_color=VISION_COLOR,
                stroke_width=2
            )
            video_pred_ghost_out.set_stroke(opacity=0)
            self.add(video_pred_ghost_out)
            
            video_pred_out_start_t = max(video_model_frac - ghost_duration_frac, 0)
            def video_pred_ghost_out_updater(mob):
                t = chunk_time.get_value()
                if t < video_pred_out_start_t:
                    return
                
                ghost_dur = video_model_frac - video_pred_out_start_t
                ghost_progress = min((t - video_pred_out_start_t) / ghost_dur, 1.0) if ghost_dur > 0 else 1.0
                
                video_model_current_x = video_model_initial_x - t * CHUNK_WIDTH
                current_chunk_start = -t * CHUNK_WIDTH
                video_pred_final_x = current_chunk_start + video_pred_width_loop / 2
                
                current_x = video_model_current_x + (video_pred_final_x - video_model_current_x) * ghost_progress
                current_y = VIDEO_MODEL_Y + (VIDEO_PRED_Y - VIDEO_MODEL_Y) * ghost_progress
                mob.move_to([current_x, current_y, 0])
                
                start_width = VIDEO_MODEL_WIDTH * 0.8
                new_width = start_width + (video_pred_width_loop - start_width) * ghost_progress
                mob.stretch_to_fit_width(new_width)
                
                mob.set_fill(VISION_COLOR, opacity=0.25 * ghost_progress)
                mob.set_stroke(VISION_COLOR, opacity=ghost_progress)
            
            video_pred_ghost_out.add_updater(video_pred_ghost_out_updater)
            
            # Animate through video model phase
            self.play(
                chunk_time.animate(rate_func=linear).set_value(video_model_frac),
                run_time=loop_time * video_model_frac
            )
            
            # Cleanup video model phase ghosts
            vision_ghost_loop.clear_updaters()
            self.remove(vision_ghost_loop)
            video_pred_ghost_out.clear_updaters()
            self.remove(video_pred_ghost_out)
            
            # Remove old video prediction, create new one
            loop_video_prediction.clear_updaters()
            self.remove(loop_video_prediction)
            
            current_chunk_start = -video_model_frac * CHUNK_WIDTH
            video_pred_x = current_chunk_start + video_pred_width_loop / 2
            
            new_video_prediction = Rectangle(
                width=video_pred_width_loop,
                height=TRACK_HEIGHT,
                fill_color=VISION_COLOR,
                fill_opacity=0.25,
                stroke_color=VISION_COLOR,
                stroke_width=2
            )
            new_video_prediction.move_to([video_pred_x, VIDEO_PRED_Y, 0])
            
            video_pred_initial_x = video_pred_x
            def video_pred_slide(mob):
                t = chunk_time.get_value()
                new_x = video_pred_initial_x - (t - video_model_frac) * CHUNK_WIDTH
                mob.move_to([new_x, mob.get_center()[1], 0])
            new_video_prediction.add_updater(video_pred_slide)
            self.add(new_video_prediction)
            loop_video_prediction = new_video_prediction
            
            # --- Phase 2: Action model computation ---
            
            # Prediction ghost flows INTO action model
            pred_ghost_in = Rectangle(
                width=video_pred_width_loop,
                height=TRACK_HEIGHT,
                fill_color=VISION_COLOR,
                fill_opacity=0.25,
                stroke_color=VISION_COLOR,
                stroke_width=2
            )
            pred_ghost_in.move_to(loop_video_prediction.get_center())
            self.add(pred_ghost_in)
            
            action_model_initial_x = loop_action_model.get_center()[0]
            
            def pred_ghost_in_updater(mob):
                t = chunk_time.get_value()
                if t < video_model_frac:
                    return
                
                ghost_progress = min((t - video_model_frac) / ghost_duration_frac, 1.0)
                target_x = action_model_initial_x - (t - video_model_frac) * CHUNK_WIDTH
                
                if not hasattr(mob, '_pred_start_x'):
                    mob._pred_start_x = mob.get_center()[0]
                
                current_x = mob._pred_start_x + (target_x - mob._pred_start_x) * ghost_progress
                current_y = VIDEO_PRED_Y + (ACTION_MODEL_Y - VIDEO_PRED_Y) * ghost_progress
                mob.move_to([current_x, current_y, 0])
                
                new_width = video_pred_width_loop + (ACTION_MODEL_WIDTH - video_pred_width_loop) * ghost_progress
                mob.stretch_to_fit_width(new_width)
                mob.set_opacity(0.25 * (1 - ghost_progress))
            
            pred_ghost_in.add_updater(pred_ghost_in_updater)
            
            # Action chips ghost OUT of action model - create 8 chips
            action_chips_out = []
            for i in range(NUM_ACTION_CHIPS):
                chip_ghost = Rectangle(
                    width=ACTION_MODEL_WIDTH * 0.1,  # Start very narrow
                    height=TRACK_HEIGHT,
                    fill_color=ACTION_COLOR,
                    fill_opacity=0.0,
                    stroke_color=ACTION_COLOR,
                    stroke_width=1
                )
                chip_ghost.set_stroke(opacity=0)
                self.add(chip_ghost)
                action_chips_out.append(chip_ghost)
            
            action_out_start_t = 1 - ghost_duration_frac
            
            def make_chip_ghost_out_updater(chip_index, mob):
                # Each chip goes to a different final position
                final_chip_x = CHIP_WIDTH / 2 + chip_index * CHIP_WIDTH
                
                def updater(m):
                    t = chunk_time.get_value()
                    if t < action_out_start_t:
                        return
                    
                    ghost_progress = min((t - action_out_start_t) / ghost_duration_frac, 1.0)
                    
                    action_model_current_x = action_model_initial_x - (t - video_model_frac) * CHUNK_WIDTH
                    
                    current_x = action_model_current_x + (final_chip_x - action_model_current_x) * ghost_progress
                    current_y = ACTION_MODEL_Y + (ACTION_Y - ACTION_MODEL_Y) * ghost_progress
                    m.move_to([current_x, current_y, 0])
                    
                    start_width = ACTION_MODEL_WIDTH * 0.1
                    new_width = start_width + (CHIP_WIDTH - start_width) * ghost_progress
                    m.stretch_to_fit_width(new_width)
                    
                    m.set_fill(ACTION_COLOR, opacity=0.25 * ghost_progress)
                    m.set_stroke(ACTION_COLOR, opacity=ghost_progress)
                return updater
            
            for i, chip_ghost in enumerate(action_chips_out):
                chip_ghost.add_updater(make_chip_ghost_out_updater(i, chip_ghost))
            
            # Animate through action model phase
            self.play(
                chunk_time.animate(rate_func=linear).set_value(1.0),
                run_time=loop_time * action_model_frac
            )
            
            # Cleanup action model phase
            pred_ghost_in.clear_updaters()
            self.remove(pred_ghost_in)
            
            # Clear and remove all chip ghosts
            for chip_ghost in action_chips_out:
                chip_ghost.clear_updaters()
                self.remove(chip_ghost)
            
            # Remove old chips that have faded out
            for chip in loop_action_chips:
                chip.clear_updaters()
                self.remove(chip)
            
            # Create new action chips for the next chunk
            loop_action_chips = []
            for i in range(NUM_ACTION_CHIPS):
                chip = Rectangle(
                    width=CHIP_WIDTH,
                    height=TRACK_HEIGHT,
                    fill_color=ACTION_COLOR,
                    fill_opacity=0.25,
                    stroke_color=ACTION_COLOR,
                    stroke_width=1
                )
                chip_x = CHIP_WIDTH / 2 + i * CHIP_WIDTH
                chip.move_to([chip_x, ACTION_Y, 0])
                self.add(chip)
                loop_action_chips.append(chip)
            
            # Clear all updaters
            for mob in sliding_elements_loop:
                mob.clear_updaters()
            loop_vision_history.clear_updaters()
            loop_video_prediction.clear_updaters()
            
            # Clean up history chips and extend main history
            for chip in history_chips:
                chip.clear_updaters()
                self.remove(chip)
            
            # Clean up initial gap chips
            for gap_chip in initial_gap_chips:
                gap_chip.clear_updaters()
                self.remove(gap_chip)
            
            # Extend the main history to include the new chunk
            new_history_width = initial_history_width_loop + CHUNK_WIDTH
            loop_vision_history.stretch_to_fit_width(new_history_width)
            # Position with right edge 2 chips behind timebar
            history_lag_cleanup = 1 * CHIP_WIDTH  # Match the updater value
            loop_vision_history.move_to([-history_lag_cleanup - new_history_width/2, VISION_HISTORY_Y, 0])
            
            # Swap to new models
            loop_video_model.clear_updaters()
            loop_action_model.clear_updaters()
            new_video_model.clear_updaters()
            new_action_model.clear_updaters()
            
            self.remove(loop_video_model, loop_action_model)
            new_video_model.set_stroke(opacity=1)
            new_action_model.set_stroke(opacity=1)
            
            # Reset new models to correct position for next iteration
            new_video_model.move_to([VIDEO_MODEL_WIDTH / 2, VIDEO_MODEL_Y, 0])
            new_action_model.move_to([VIDEO_MODEL_WIDTH / 2 + VIDEO_MODEL_WIDTH/2 + MODEL_GAP + ACTION_MODEL_WIDTH/2, ACTION_MODEL_Y, 0])
            
            loop_video_model = new_video_model
            loop_action_model = new_action_model
        
        # =====================================================================
        # PHASE 3: Fast continuous loop (2 chunks per second) - SIMPLIFIED
        # No ghosting, no chips - just simple bars that update continuously
        # =====================================================================
        
        fast_loop_time = 0.45  # 2 chunks per second
        
        # Remove chip-based elements from phase 2, replace with simple bars
        for chip in loop_action_chips:
            self.remove(chip)
        
        # Create simple action bar (spans from current time to next chunk boundary)
        # At t=0, full chunk wide. At t=1, width=0
        fast_action_bar = Rectangle(
            width=CHUNK_WIDTH,
            height=TRACK_HEIGHT,
            fill_color=ACTION_COLOR,
            fill_opacity=0.25,
            stroke_color=ACTION_COLOR,
            stroke_width=1
        )
        # Left edge at timebar (x=0), so center is at CHUNK_WIDTH/2
        fast_action_bar.move_to([CHUNK_WIDTH / 2, ACTION_Y, 0])
        self.add(fast_action_bar)
        
        # Extend history to be fully caught up (right edge at x=0)
        current_history_width = loop_vision_history.get_width()
        loop_vision_history.move_to([-current_history_width / 2, VISION_HISTORY_Y, 0])
        
        for loop_iteration in range(10):  # More iterations at fast speed
            
            # Single time tracker for entire chunk (0 to 1)
            chunk_time = ValueTracker(0)
            
            # Capture initial widths/positions for this iteration
            initial_history_width_p3 = loop_vision_history.get_width()
            
            # Simple slide updater
            def make_slide_p3(initial_x):
                def updater(mob):
                    t = chunk_time.get_value()
                    new_x = initial_x - t * CHUNK_WIDTH
                    mob.move_to([new_x, mob.get_center()[1], 0])
                return updater
            
            # History grows and stays caught up with timebar (right edge at x=0)
            def history_grow_p3(mob):
                t = chunk_time.get_value()
                new_width = initial_history_width_p3 + t * CHUNK_WIDTH
                mob.stretch_to_fit_width(new_width)
                mob.move_to([-new_width / 2, VISION_HISTORY_Y, 0])
            
            # Action bar shrinks as time progresses (left edge stays at timebar x=0)
            def action_bar_shrink_p3(mob):
                t = chunk_time.get_value()
                # Width shrinks from CHUNK_WIDTH to 0 as time progresses
                new_width = max(CHUNK_WIDTH * (1 - t), 0.01)  # Avoid zero width
                mob.stretch_to_fit_width(new_width)
                # Left edge stays at x=0 (timebar), right edge shrinks inward
                mob.move_to([new_width / 2, ACTION_Y, 0])
            
            # Model crossfade (simple instant swap at end)
            model_fade_frac = 0.15  # Last 15% of chunk
            model_fade_start = 1 - model_fade_frac
            
            def make_model_fade_out_p3(fade_start):
                def updater(mob):
                    t = chunk_time.get_value()
                    if t < fade_start:
                        return
                    fade_progress = min((t - fade_start) / model_fade_frac, 1.0)
                    mob.set_stroke(opacity=1 - fade_progress)
                return updater
            
            def make_model_fade_in_p3(fade_start):
                def updater(mob):
                    t = chunk_time.get_value()
                    if t < fade_start:
                        return
                    fade_progress = min((t - fade_start) / model_fade_frac, 1.0)
                    mob.set_stroke(opacity=fade_progress)
                return updater
            
            # Video prediction fades out over the first part of chunk
            video_pred_initial_opacity = loop_video_prediction.get_fill_opacity()
            def video_pred_fade_out_p3(mob):
                t = chunk_time.get_value()
                # Start fading immediately, fully faded by 60%
                fade_end = 0.6
                if t < fade_end:
                    fade_progress = t / fade_end
                    mob.set_fill(opacity=video_pred_initial_opacity * (1 - fade_progress))
                    mob.set_stroke(opacity=1 - fade_progress)
                else:
                    mob.set_fill(opacity=0)
                    mob.set_stroke(opacity=0)
            
            # Create new video prediction that appears at 75% (when video model finishes)
            video_model_end_frac = 0.75  # Video model takes 75% of chunk
            new_video_prediction = Rectangle(
                width=3 * CHUNK_WIDTH,
                height=TRACK_HEIGHT,
                fill_color=VISION_COLOR,
                fill_opacity=0,  # Starts invisible
                stroke_color=VISION_COLOR,
                stroke_width=2
            )
            new_video_prediction.set_stroke(opacity=0)
            # Position: starts at chunk boundary (x=0), extends 3 chunks to the right
            new_video_prediction.move_to([3 * CHUNK_WIDTH / 2, VIDEO_PRED_Y, 0])
            self.add(new_video_prediction)
            
            new_video_pred_x = new_video_prediction.get_center()[0]
            
            def new_video_pred_fade_in_p3(mob):
                t = chunk_time.get_value()
                if t < video_model_end_frac:
                    return  # Still invisible
                # Fade in over 15% of chunk
                fade_duration = 0.15
                fade_progress = min((t - video_model_end_frac) / fade_duration, 1.0)
                mob.set_fill(opacity=0.25 * fade_progress)
                mob.set_stroke(opacity=fade_progress)
            
            # Create new models for next chunk
            new_video_model = ModelIndicator(width=VIDEO_MODEL_WIDTH, color=VISION_COLOR)
            new_video_model.move_to([VIDEO_MODEL_WIDTH / 2, VIDEO_MODEL_Y, 0])
            new_video_model.set_stroke(opacity=0)
            
            new_action_model = ModelIndicator(width=ACTION_MODEL_WIDTH, color=ACTION_COLOR)
            new_action_model.move_to([VIDEO_MODEL_WIDTH / 2 + VIDEO_MODEL_WIDTH/2 + MODEL_GAP + ACTION_MODEL_WIDTH/2, ACTION_MODEL_Y, 0])
            new_action_model.set_stroke(opacity=0)
            
            self.add(new_video_model, new_action_model)
            
            # Elements that slide left
            sliding_elements_p3 = [loop_video_model, loop_action_model, loop_chunk_markers, loop_video_prediction, new_video_prediction]
            initial_positions_p3 = {id(mob): mob.get_center()[0] for mob in sliding_elements_p3}
            
            new_video_model_x = new_video_model.get_center()[0]
            new_action_model_x = new_action_model.get_center()[0]
            
            # Add updaters
            for mob in sliding_elements_p3:
                mob.add_updater(make_slide_p3(initial_positions_p3[id(mob)]))
            
            new_video_model.add_updater(make_slide_p3(new_video_model_x))
            new_action_model.add_updater(make_slide_p3(new_action_model_x))
            
            loop_video_model.add_updater(make_model_fade_out_p3(model_fade_start))
            loop_action_model.add_updater(make_model_fade_out_p3(model_fade_start))
            new_video_model.add_updater(make_model_fade_in_p3(model_fade_start))
            new_action_model.add_updater(make_model_fade_in_p3(model_fade_start))
            
            loop_vision_history.add_updater(history_grow_p3)
            fast_action_bar.add_updater(action_bar_shrink_p3)
            loop_video_prediction.add_updater(video_pred_fade_out_p3)
            new_video_prediction.add_updater(new_video_pred_fade_in_p3)
            
            # Animate
            self.play(
                chunk_time.animate(rate_func=linear).set_value(1.0),
                run_time=fast_loop_time
            )
            
            # Cleanup
            for mob in sliding_elements_p3:
                mob.clear_updaters()
            loop_vision_history.clear_updaters()
            fast_action_bar.clear_updaters()
            new_video_model.clear_updaters()
            new_action_model.clear_updaters()
            loop_video_model.clear_updaters()
            loop_action_model.clear_updaters()
            
            # Swap models
            self.remove(loop_video_model, loop_action_model)
            new_video_model.set_stroke(opacity=1)
            new_action_model.set_stroke(opacity=1)
            new_video_model.move_to([VIDEO_MODEL_WIDTH / 2, VIDEO_MODEL_Y, 0])
            new_action_model.move_to([VIDEO_MODEL_WIDTH / 2 + VIDEO_MODEL_WIDTH/2 + MODEL_GAP + ACTION_MODEL_WIDTH/2, ACTION_MODEL_Y, 0])
            
            loop_video_model = new_video_model
            loop_action_model = new_action_model
            
            # Update history position
            new_history_width = initial_history_width_p3 + CHUNK_WIDTH
            loop_vision_history.stretch_to_fit_width(new_history_width)
            loop_vision_history.move_to([-new_history_width / 2, VISION_HISTORY_Y, 0])
            
            # Reset action bar for next chunk
            fast_action_bar.stretch_to_fit_width(CHUNK_WIDTH)
            fast_action_bar.move_to([CHUNK_WIDTH / 2, ACTION_Y, 0])
            
            # Swap video predictions - old one is faded out, new one continues
            self.remove(loop_video_prediction)
            new_video_prediction.clear_updaters()
            new_video_prediction.set_fill(opacity=0.25)
            new_video_prediction.set_stroke(opacity=1)
            # Don't reset position - it should continue from where it slid to
            loop_video_prediction = new_video_prediction
            
            # Reset chunk markers (shift back by one chunk)
            loop_chunk_markers.shift([CHUNK_WIDTH, 0, 0])
        
        self.wait(1)


# =============================================================================
# RENDER COMMANDS
# =============================================================================
# Preview: manim -pql inference_rollout.py InferenceRollout
# High quality: manim -pqh inference_rollout.py InferenceRollout
