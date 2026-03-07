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
TRACK_HEIGHT = 0.5            # Height of data blocks
MODEL_HEIGHT = 0.7            # Height of model indicator boxes

# Model positioning within a chunk (no margins - models span full chunk)
MODEL_GAP = 0      # Small gap between video and action model

# Calculate model widths (both fit within one chunk, no margins)
# Video model gets ~60%, action model gets ~40%
AVAILABLE_MODEL_WIDTH = CHUNK_WIDTH - MODEL_GAP
VIDEO_MODEL_WIDTH = AVAILABLE_MODEL_WIDTH * 0.6
ACTION_MODEL_WIDTH = AVAILABLE_MODEL_WIDTH * 0.4

# Vertical positions (y-coordinates)
VIDEO_PRED_Y = 1.8            # Video prediction track
MODEL_Y = 0.6                 # Model indicators track
VISION_HISTORY_Y = -1.2       # Vision history track
ACTION_Y = -0.2               # Action output track

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
            start=[0, -3, 0],
            end=[0, 3.5, 0],
            stroke_width=3,
            color=TIMEBAR_COLOR
        )
        timebar_marker = Triangle(
            fill_color=TIMEBAR_COLOR,
            fill_opacity=1,
            stroke_width=0
        ).scale(0.15).rotate(PI).move_to([0, 3.5, 0])
        timebar_group = VGroup(timebar, timebar_marker)
        
        # Chunk markers - vertical lines at each chunk boundary (including t=0)
        chunk_markers = VGroup()
        for i in range(-4, 6):
            marker = Line(
                start=[i * CHUNK_WIDTH, -2.5, 0],
                end=[i * CHUNK_WIDTH, 3, 0],
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
        # Shows ~2.5 chunks of history
        history_start = -2.5  # 2.5 chunks in the past
        history_end = 0       # Up to current time
        history_width = (history_end - history_start) * CHUNK_WIDTH
        
        vision_history = Rectangle(
            width=history_width,
            height=TRACK_HEIGHT,
            fill_color=VISION_COLOR,
            fill_opacity=0.7,
            stroke_color=VISION_COLOR,
            stroke_width=2
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
        video_model.move_to([video_model_x, MODEL_Y, 0])
        
        # Action Model indicator: immediately after video model with small gap
        action_model = ModelIndicator(
            width=ACTION_MODEL_WIDTH,
            color=ACTION_COLOR
        )
        # Position: left edge at video model right edge + gap
        action_model_x = video_model_x + VIDEO_MODEL_WIDTH/2 + MODEL_GAP + ACTION_MODEL_WIDTH/2
        action_model.move_to([action_model_x, MODEL_Y, 0])
        
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
        
        # Special updater for vision_history: grows to keep right edge at x=0
        initial_history_width = vision_history.get_width()
        initial_history_left = vision_history.get_left()[0]
        
        def history_grow_updater(mob):
            dt = time_tracker.get_value()
            # Right edge stays at x=0, left edge extends further left
            new_width = initial_history_width + dt * CHUNK_WIDTH
            # Stretch to new width
            mob.stretch_to_fit_width(new_width)
            # Position so right edge is at x=0
            mob.move_to([-new_width/2, VISION_HISTORY_Y, 0])
        
        vision_history.add_updater(history_grow_updater)
        
        # Animate time progression through video model
        self.play(
            time_tracker.animate.set_value(video_model_time),
            run_time=1.5
        )
        
        # Remove updaters
        for mob in sliding_elements:
            mob.clear_updaters()
        vision_history.clear_updaters()
        
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
        
        # Special updater for vision_history: grows to keep right edge at x=0
        initial_history_width_2 = vision_history.get_width()
        
        def history_grow_updater_2(mob):
            dt = time_tracker_2.get_value()
            new_width = initial_history_width_2 + dt * CHUNK_WIDTH
            mob.stretch_to_fit_width(new_width)
            mob.move_to([-new_width/2, VISION_HISTORY_Y, 0])
        
        vision_history.add_updater(history_grow_updater_2)
        
        # Animate time progression through action model
        self.play(
            time_tracker_2.animate.set_value(action_model_time),
            run_time=1.0
        )
        
        # Remove updaters
        for mob in sliding_elements_2:
            mob.clear_updaters()
        vision_history.clear_updaters()
        
        # =====================================================================
        # KEYFRAME 5 (Part 2): Action output appears from Action Model
        # =====================================================================
        
        # Action output: 1 chunk wide, positioned at the next chunk
        # The chunk starts where the action model's right edge was before sliding
        # After action_model_time slide, the next chunk boundary is at x = 0
        action_output_width = CHUNK_WIDTH
        action_output_x = action_output_width / 2  # Centered on next chunk (starting at timebar)
        
        # Create ghost from action model that expands to action output
        action_model_current_pos = action_model.get_center()
        
        action_ghost = Rectangle(
            width=ACTION_MODEL_WIDTH,
            height=TRACK_HEIGHT,
            fill_color=ACTION_COLOR,
            fill_opacity=0.25,
            stroke_color=ACTION_COLOR,
            stroke_width=2
        )
        action_ghost.move_to(action_model_current_pos)
        self.add(action_ghost)
        
        # Final action output
        action_output = Rectangle(
            width=action_output_width,
            height=TRACK_HEIGHT,
            fill_color=ACTION_COLOR,
            fill_opacity=0.25,
            stroke_color=ACTION_COLOR,
            stroke_width=2
        )
        action_output.move_to([action_output_x, ACTION_Y, 0])
        
        # Animate ghost expanding from action model to action output position
        self.play(
            action_ghost.animate.stretch(action_output_width / ACTION_MODEL_WIDTH, dim=0).move_to([action_output_x, ACTION_Y, 0]),
            run_time=0.8
        )
        
        # Instant swap
        self.remove(action_ghost)
        self.add(action_output)
        
        self.wait(0.5)
        
        # =====================================================================
        # CLEAN BREAK: Fade out all explanatory phase objects
        # =====================================================================
        
        # Collect all objects from explanatory phase
        explanatory_objects = [
            vision_history, video_model, action_model, 
            video_prediction, action_output, chunk_markers
        ]
        
        # Fade everything out
        self.play(
            *[FadeOut(obj) for obj in explanatory_objects],
            run_time=0.5
        )
        
        # Remove from scene to be sure
        for obj in explanatory_objects:
            self.remove(obj)
        
        # =====================================================================
        # CONTINUOUS LOOP PHASE: Fresh objects, independent logic
        # =====================================================================
        
        loop_time = SLOW_CHUNK_TIME * 2  # 2x slower
        video_model_frac = VIDEO_MODEL_WIDTH / CHUNK_WIDTH
        action_model_frac = ACTION_MODEL_WIDTH / CHUNK_WIDTH
        ghost_duration_frac = 1/8  # Ghost animations complete in 1/8 chunk
        
        # --- Create fresh objects for the loop phase ---
        
        # Chunk markers (static reference lines) - match explanatory phase stroke width
        loop_chunk_markers = VGroup()
        for i in range(-5, 8):
            marker = Line(
                start=[i * CHUNK_WIDTH, -2.5, 0],
                end=[i * CHUNK_WIDTH, 2.5, 0],
                stroke_color=MARKER_COLOR,
                stroke_width=2  # Match explanatory phase
            )
            loop_chunk_markers.add(marker)
        self.add(loop_chunk_markers)
        
        # Vision history: starts at 2.5 chunks before timebar
        loop_history_start = -2.5
        loop_history_width = abs(loop_history_start) * CHUNK_WIDTH
        loop_vision_history = Rectangle(
            width=loop_history_width,
            height=TRACK_HEIGHT,
            fill_color=VISION_COLOR,
            fill_opacity=1.0,
            stroke_color=VISION_COLOR,
            stroke_width=2
        )
        loop_vision_history.move_to([-loop_history_width/2, VISION_HISTORY_Y, 0])
        self.add(loop_vision_history)
        
        # Video model - starts at the model position for the current chunk
        loop_video_model = ModelIndicator(width=VIDEO_MODEL_WIDTH, color=VISION_COLOR)
        loop_video_model.move_to([VIDEO_MODEL_WIDTH / 2, MODEL_Y, 0])
        self.add(loop_video_model)
        
        # Action model
        loop_action_model = ModelIndicator(width=ACTION_MODEL_WIDTH, color=ACTION_COLOR)
        loop_action_model.move_to([VIDEO_MODEL_WIDTH / 2 + VIDEO_MODEL_WIDTH/2 + MODEL_GAP + ACTION_MODEL_WIDTH/2, MODEL_Y, 0])
        self.add(loop_action_model)
        
        # Video prediction: 3 chunks wide, starts at chunk boundary before timebar
        loop_video_pred_width = 3 * CHUNK_WIDTH
        loop_video_prediction = Rectangle(
            width=loop_video_pred_width,
            height=TRACK_HEIGHT,
            fill_color=VISION_COLOR,
            fill_opacity=0.25,
            stroke_color=VISION_COLOR,
            stroke_width=2
        )
        loop_video_prediction.move_to([-CHUNK_WIDTH + loop_video_pred_width/2, VIDEO_PRED_Y, 0])
        self.add(loop_video_prediction)
        
        # Action output: 1 chunk wide, positioned at the current chunk (just past timebar)
        loop_action_output = Rectangle(
            width=CHUNK_WIDTH,
            height=TRACK_HEIGHT,
            fill_color=ACTION_COLOR,
            fill_opacity=0.25,
            stroke_color=ACTION_COLOR,
            stroke_width=2
        )
        loop_action_output.move_to([CHUNK_WIDTH / 2, ACTION_Y, 0])  # Current chunk
        self.add(loop_action_output)
        
        # Fade in all loop objects together
        loop_objects = [
            loop_vision_history, loop_video_model, loop_action_model,
            loop_video_prediction, loop_action_output, loop_chunk_markers
        ]
        self.play(
            *[FadeIn(obj) for obj in loop_objects],
            run_time=0.5
        )
        
        for loop_iteration in range(4):  # Run loop 2 times
            
            # Single time tracker for entire chunk (0 to 1)
            chunk_time = ValueTracker(0)
            
            # Create new models for the NEXT chunk (will fade in at end of this chunk)
            new_video_model = ModelIndicator(width=VIDEO_MODEL_WIDTH, color=VISION_COLOR)
            new_video_model.move_to([VIDEO_MODEL_WIDTH / 2, MODEL_Y, 0])
            new_video_model.set_stroke(opacity=0)  # Start invisible
            
            new_action_model = ModelIndicator(width=ACTION_MODEL_WIDTH, color=ACTION_COLOR)
            new_action_model.move_to([VIDEO_MODEL_WIDTH / 2 + VIDEO_MODEL_WIDTH/2 + MODEL_GAP + ACTION_MODEL_WIDTH/2, MODEL_Y, 0])
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
                loop_video_prediction, loop_action_output
            ]
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
            
            # Vision history grows continuously
            initial_history_width_loop = loop_vision_history.get_width()
            def history_grow_continuous(mob):
                t = chunk_time.get_value()
                new_width = initial_history_width_loop + t * CHUNK_WIDTH
                mob.stretch_to_fit_width(new_width)
                mob.move_to([-new_width/2, VISION_HISTORY_Y, 0])
            loop_vision_history.add_updater(history_grow_continuous)
            
            # Old video prediction fades out
            old_video_pred_initial_opacity = loop_video_prediction.get_fill_opacity()
            def old_video_pred_fade(mob):
                t = chunk_time.get_value()
                fade_progress = min(t / 0.25, 1.0)
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
                current_y = VISION_HISTORY_Y + (MODEL_Y - VISION_HISTORY_Y) * ghost_progress
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
                current_y = MODEL_Y + (VIDEO_PRED_Y - MODEL_Y) * ghost_progress
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
                current_y = VIDEO_PRED_Y + (MODEL_Y - VIDEO_PRED_Y) * ghost_progress
                mob.move_to([current_x, current_y, 0])
                
                new_width = video_pred_width_loop + (ACTION_MODEL_WIDTH - video_pred_width_loop) * ghost_progress
                mob.stretch_to_fit_width(new_width)
                mob.set_opacity(0.25 * (1 - ghost_progress))
            
            pred_ghost_in.add_updater(pred_ghost_in_updater)
            
            # Action output ghost OUT of action model
            action_ghost_out = Rectangle(
                width=ACTION_MODEL_WIDTH * 0.8,
                height=TRACK_HEIGHT,
                fill_color=ACTION_COLOR,
                fill_opacity=0.0,
                stroke_color=ACTION_COLOR,
                stroke_width=2
            )
            action_ghost_out.set_stroke(opacity=0)
            self.add(action_ghost_out)
            
            action_out_start_t = 1 - ghost_duration_frac
            def action_ghost_out_updater(mob):
                t = chunk_time.get_value()
                if t < action_out_start_t:
                    return
                
                ghost_progress = min((t - action_out_start_t) / ghost_duration_frac, 1.0)
                
                action_model_current_x = action_model_initial_x - (t - video_model_frac) * CHUNK_WIDTH
                action_output_final_x = CHUNK_WIDTH / 2
                
                current_x = action_model_current_x + (action_output_final_x - action_model_current_x) * ghost_progress
                current_y = MODEL_Y + (ACTION_Y - MODEL_Y) * ghost_progress
                mob.move_to([current_x, current_y, 0])
                
                start_width = ACTION_MODEL_WIDTH * 0.8
                new_width = start_width + (CHUNK_WIDTH - start_width) * ghost_progress
                mob.stretch_to_fit_width(new_width)
                
                mob.set_fill(ACTION_COLOR, opacity=0.25 * ghost_progress)
                mob.set_stroke(ACTION_COLOR, opacity=ghost_progress)
            
            action_ghost_out.add_updater(action_ghost_out_updater)
            
            # Old action output fades out
            old_action_output_initial_opacity = loop_action_output.get_fill_opacity()
            old_action_initial_x = loop_action_output.get_center()[0]
            def old_action_fade_and_slide(mob):
                t = chunk_time.get_value()
                new_x = old_action_initial_x - (t - video_model_frac) * CHUNK_WIDTH
                mob.move_to([new_x, mob.get_center()[1], 0])
                fade_progress = min((t - video_model_frac) / action_model_frac, 1.0) if action_model_frac > 0 else 1.0
                mob.set_fill(opacity=old_action_output_initial_opacity * (1 - fade_progress))
                mob.set_stroke(opacity=1 - fade_progress)
            loop_action_output.add_updater(old_action_fade_and_slide)
            
            # Animate through action model phase
            self.play(
                chunk_time.animate(rate_func=linear).set_value(1.0),
                run_time=loop_time * action_model_frac
            )
            
            # Cleanup action model phase
            pred_ghost_in.clear_updaters()
            self.remove(pred_ghost_in)
            action_ghost_out.clear_updaters()
            self.remove(action_ghost_out)
            loop_action_output.clear_updaters()
            self.remove(loop_action_output)
            
            # Create new action output
            new_action_output = Rectangle(
                width=CHUNK_WIDTH,
                height=TRACK_HEIGHT,
                fill_color=ACTION_COLOR,
                fill_opacity=0.25,
                stroke_color=ACTION_COLOR,
                stroke_width=2
            )
            new_action_output.move_to([CHUNK_WIDTH / 2, ACTION_Y, 0])
            self.add(new_action_output)
            loop_action_output = new_action_output
            
            # Clear all updaters
            for mob in sliding_elements_loop:
                mob.clear_updaters()
            loop_vision_history.clear_updaters()
            loop_video_prediction.clear_updaters()
            
            # Swap to new models
            loop_video_model.clear_updaters()
            loop_action_model.clear_updaters()
            new_video_model.clear_updaters()
            new_action_model.clear_updaters()
            
            self.remove(loop_video_model, loop_action_model)
            new_video_model.set_stroke(opacity=1)
            new_action_model.set_stroke(opacity=1)
            
            # Reset new models to correct position for next iteration
            new_video_model.move_to([VIDEO_MODEL_WIDTH / 2, MODEL_Y, 0])
            new_action_model.move_to([VIDEO_MODEL_WIDTH / 2 + VIDEO_MODEL_WIDTH/2 + MODEL_GAP + ACTION_MODEL_WIDTH/2, MODEL_Y, 0])
            
            loop_video_model = new_video_model
            loop_action_model = new_action_model
        
        self.wait(1)


# =============================================================================
# RENDER COMMANDS
# =============================================================================
# Preview: manim -pql inference_rollout.py InferenceRollout
# High quality: manim -pqh inference_rollout.py InferenceRollout
