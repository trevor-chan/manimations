"""
Overview Diagram - Static flowchart showing two-stage model architecture

Shows the flow: video context → video model → predicted video → action model → generated actions
With an "action rollout" feedback loop from actions back to video context.
"""

from manim import *
import sys
from pathlib import Path
from matplotlib import font_manager

# Add parent directory to path for colors import
sys.path.insert(0, str(Path(__file__).parent.parent))
from colors import (
    RHODA_ORANGE, RHODA_BLUE, BG_WHITE, TEXT_DARK, MARKER_GRAY,
    FILL_LIGHT_GRAY,
    VIDEO_CONTEXT_STROKE as VC_STROKE, VIDEO_CONTEXT_FILL as VC_FILL,
    VIDEO_PREDICTION_STROKE as VP_STROKE, VIDEO_PREDICTION_FILL as VP_FILL,
    ACTION_PREDICTION_STROKE as AP_STROKE, ACTION_PREDICTION_FILL as AP_FILL,
)

# =============================================================================
# FONT SELECTION
# =============================================================================

def get_preferred_font():
    """Return 'Open Sans' if available, otherwise 'Arial'."""
    available_fonts = {f.name for f in font_manager.fontManager.ttflist}
    if "Open Sans" in available_fonts:
        return "Open Sans"
    return "Arial"

LABEL_FONT = get_preferred_font()

# =============================================================================
# CONFIGURATION
# =============================================================================

# Aspect ratio (4:1 - wide diagram, tighter crop)
config.pixel_width = 3600
config.pixel_height = 1200
config.frame_width = 14
config.frame_height = 3.5

# =============================================================================
# COLORS (from unified colors.py)
# =============================================================================

# Main blocks - white fill with colored strokes from colors.py
VIDEO_CONTEXT_FILL = "#FFFFFF"       # White fill for outer box
VIDEO_CONTEXT_STROKE = VC_STROKE     # Blue stroke

PREDICTED_VIDEO_FILL = "#FFFFFF"     # White fill for outer box
PREDICTED_VIDEO_STROKE = VP_STROKE   # Purple stroke

GENERATED_ACTIONS_FILL = "#FFFFFF"   # White fill for outer box
GENERATED_ACTIONS_STROKE = AP_STROKE # Yellow stroke

# Model boxes and connectors
MODEL_BOX_FILL = "#ECECEC"           # Light gray
MODEL_BOX_STROKE = "#B3B3B3"         # Medium gray
CONNECTOR_COLOR = "#B3B3B3"          # Gray for arrows and loop

# =============================================================================
# CONSTANTS
# =============================================================================

# Box dimensions
VIDEO_CONTEXT_WIDTH = 3.75  # 50% wider than original
PREDICTED_VIDEO_WIDTH = 1.8  # Narrower
GENERATED_ACTIONS_WIDTH = 1.8  # Narrower
DATA_BOX_HEIGHT = 2.5
DATA_BOX_CORNER_RADIUS = 0.18
DATA_BOX_STROKE_WIDTH = 5  # Thicker borders

MODEL_BOX_WIDTH = 1.0
MODEL_BOX_HEIGHT = 1.0
MODEL_BOX_CORNER_RADIUS = 0.25
MODEL_BOX_STROKE_WIDTH = 4

LOOP_BOX_WIDTH = 2.0
LOOP_BOX_HEIGHT = 0.5
LOOP_BOX_CORNER_RADIUS = 0.25

# Spacing
HORIZONTAL_GAP = 0.45  # Gap between elements (reduced by 25%)

# Vertical positions - all elements on same Y for horizontal arrows
MAIN_Y = 0.4   # Y position for all main elements (data boxes and models)
LOOP_Y = -1.8  # Y position for action rollout label

# Arrow/connector properties - unified thickness
CONNECTOR_STROKE_WIDTH = 16  # Even thicker arrows and lines
ARROW_TIP_LENGTH = 0.25

# Text properties
LABEL_FONT_SIZE = 96
LABEL_SCALE = 0.18  # Slightly smaller to fit in boxes

# Data chunk (small square) properties
CHUNK_SIZE = 0.55  # Size of small squares
CHUNK_CORNER_RADIUS = 0.1
CHUNK_STROKE_WIDTH = 3
CHUNK_SPACING = 0.12  # Gap between chunks


# =============================================================================
# CUSTOM MOBJECTS
# =============================================================================

class DataChunk(VGroup):
    """
    A small rounded square representing a data chunk.
    Supports animation: fading, translation, and color changes.
    """
    
    def __init__(self, color, size=CHUNK_SIZE, fill_opacity=0.3, **kwargs):
        super().__init__(**kwargs)
        
        self.chunk_color = color
        self.base_fill_opacity = fill_opacity
        
        # Create rounded rectangle
        self.rect = RoundedRectangle(
            width=size,
            height=size,
            corner_radius=CHUNK_CORNER_RADIUS,
            fill_color=color,
            fill_opacity=fill_opacity,
            stroke_color=color,
            stroke_width=CHUNK_STROKE_WIDTH
        )
        self.add(self.rect)
    
    def set_chunk_opacity(self, opacity):
        """Set both fill and stroke opacity proportionally."""
        self.rect.set_fill(opacity=opacity * self.base_fill_opacity)
        self.rect.set_stroke(opacity=opacity)
        return self
    
    def set_chunk_color(self, color):
        """Change the chunk's color."""
        self.chunk_color = color
        self.rect.set_fill(color=color)
        self.rect.set_stroke(color=color)
        return self


class VideoContextCache(VGroup):
    """
    Manages a cache of video context chunks with cycling animation.
    
    Layout: 5 positions from left to right:
    - Index 0: leftmost chunk (visible)
    - Index 1: ellipsis position (invisible)
    - Index 2-4: three chunks on the right (visible)
    
    When cycling:
    - Chunks shift left by one position
    - Chunk at index 2 fades out as it moves to index 1
    - Chunk at index 1 fades in as it moves to index 0
    - Chunk at index 0 fades out and exits
    - A new chunk appears at index 4
    """
    
    def __init__(self, center_x, y, color=VIDEO_CONTEXT_STROKE, **kwargs):
        super().__init__(**kwargs)
        
        self.color = color
        self.y = y
        self.center_x = center_x
        
        # Calculate 5 slot positions
        # Slots: [leftmost, ellipsis, right_0, right_1, right_2]
        spacing = CHUNK_SIZE + CHUNK_SPACING
        
        # Right group starts slightly right of center
        right_group_start_x = center_x + 0.05
        
        # Calculate positions for all 5 slots
        self.slot_positions = [
            center_x - VIDEO_CONTEXT_WIDTH/2 + CHUNK_SIZE/2 + 0.25,  # Index 0: leftmost
            None,  # Index 1: ellipsis (calculated below)
            right_group_start_x,                    # Index 2: first of right group
            right_group_start_x + spacing,          # Index 3: second of right group
            right_group_start_x + 2 * spacing,      # Index 4: third of right group (rightmost)
        ]
        # Ellipsis position: midpoint between leftmost right edge and right group left edge
        self.slot_positions[1] = (self.slot_positions[0] + CHUNK_SIZE/2 + self.slot_positions[2] - CHUNK_SIZE/2) / 2
        
        # Create 5 chunks, one for each slot
        self.chunks = []
        for i in range(5):
            chunk = DataChunk(color)
            chunk.move_to([self.slot_positions[i], y, 0])
            
            # Slot 1 (ellipsis position) starts invisible
            if i == 1:
                chunk.set_chunk_opacity(0)
            
            self.chunks.append(chunk)
            self.add(chunk)
        
        # Create the ellipsis text (positioned at slot 1)
        self.ellipsis = Text("...", font=LABEL_FONT, font_size=72, color=TEXT_DARK).scale(0.5)
        self.ellipsis.move_to([self.slot_positions[1], y, 0])
        self.add(self.ellipsis)
    
    def get_fadeout_animation(self, run_time=0.3):
        """
        Returns animation to fade out the leftmost chunk.
        Call this BEFORE get_shift_animations.
        """
        old_chunk_0 = self.chunks[0]
        return old_chunk_0.animate.set_chunk_opacity(0)
    
    def get_shift_animations(self, run_time=0.5):
        """
        Returns animations for shifting chunks left after leftmost has faded out.
        
        During a shift:
        - Chunk at slot 1 moves to slot 0, fades IN (fast)
        - Chunk at slot 2 moves to slot 1, fades OUT (fast)
        - Chunks at slots 3, 4 shift left (stay visible)
        """
        animations = []
        
        # Chunk at slot 1: move to slot 0, fade IN
        chunk_1 = self.chunks[1]
        target_pos_0 = [self.slot_positions[0], self.y, 0]
        animations.append(chunk_1.animate.move_to(target_pos_0).set_chunk_opacity(1))
        
        # Chunk at slot 2: move to slot 1, fade OUT
        chunk_2 = self.chunks[2]
        target_pos_1 = [self.slot_positions[1], self.y, 0]
        animations.append(chunk_2.animate.move_to(target_pos_1).set_chunk_opacity(0))
        
        # Chunk at slot 3: move to slot 2 (stays visible)
        chunk_3 = self.chunks[3]
        target_pos_2 = [self.slot_positions[2], self.y, 0]
        animations.append(chunk_3.animate.move_to(target_pos_2))
        
        # Chunk at slot 4: move to slot 3 (stays visible)
        chunk_4 = self.chunks[4]
        target_pos_3 = [self.slot_positions[3], self.y, 0]
        animations.append(chunk_4.animate.move_to(target_pos_3))
        
        return animations
    
    def finalize_cycle(self, scene, add_new_chunk=False):
        """
        Called after cycle animation completes.
        Removes old chunk at slot 0 and updates internal chunk list.
        
        Args:
            scene: The manim scene
            add_new_chunk: If True, creates a new chunk at slot 4 (rightmost)
        """
        # Remove the old chunk that faded out
        old_chunk = self.chunks[0]
        scene.remove(old_chunk)
        self.remove(old_chunk)
        
        # Shift chunk references
        self.chunks = self.chunks[1:]  # Remove index 0
        
        if add_new_chunk:
            # Create new chunk at slot 4 (rightmost)
            new_chunk = DataChunk(self.color)
            new_chunk.move_to([self.slot_positions[4], self.y, 0])
            self.chunks.append(new_chunk)
            self.add(new_chunk)
            scene.add(new_chunk)
            
            # Reset positions of all chunks to their proper slots
            for i, chunk in enumerate(self.chunks):
                chunk.move_to([self.slot_positions[i], self.y, 0])
                # Slot 1 should be invisible
                if i == 1:
                    chunk.set_chunk_opacity(0)
                else:
                    chunk.set_chunk_opacity(1)
    
    def get_visible_chunks(self):
        """Returns the chunks that are currently visible (all except the ellipsis slot).
        
        After finalize_cycle, the list may have fewer than 5 chunks.
        Slot 1 (ellipsis) is always invisible.
        """
        visible = []
        for i, chunk in enumerate(self.chunks):
            # Slot 1 is always invisible (ellipsis position)
            if i != 1:
                visible.append(chunk)
        return visible


# =============================================================================
# MAIN SCENE
# =============================================================================

class OverviewDiagram(Scene):
    def construct(self):
        # Set background
        self.camera.background_color = BG_WHITE
        
        # =====================================================================
        # CREATE DATA BOXES
        # =====================================================================
        
        # Video context (orange) - wider box
        video_context = RoundedRectangle(
            width=VIDEO_CONTEXT_WIDTH,
            height=DATA_BOX_HEIGHT,
            corner_radius=DATA_BOX_CORNER_RADIUS,
            fill_color=VIDEO_CONTEXT_FILL,
            fill_opacity=1,
            stroke_color=VIDEO_CONTEXT_STROKE,
            stroke_width=DATA_BOX_STROKE_WIDTH
        )
        
        video_context_label = Paragraph(
            "video", "context",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD,
            line_spacing=0.5,
            alignment="center"
        ).scale(LABEL_SCALE)
        
        video_context_group = VGroup(video_context, video_context_label)
        # Position label at top of box (lowered)
        video_context_label.move_to([video_context.get_center()[0], video_context.get_top()[1] - 0.45, 0])
        # Set z-index: intermediate priority for colored data boxes
        video_context.set_z_index(0)
        video_context_label.set_z_index(1)
        
        # Predicted video (yellow) - narrower box
        predicted_video = RoundedRectangle(
            width=PREDICTED_VIDEO_WIDTH,
            height=DATA_BOX_HEIGHT,
            corner_radius=DATA_BOX_CORNER_RADIUS,
            fill_color=PREDICTED_VIDEO_FILL,
            fill_opacity=1,
            stroke_color=PREDICTED_VIDEO_STROKE,
            stroke_width=DATA_BOX_STROKE_WIDTH
        )
        
        predicted_video_label = Paragraph(
            "predicted", "video",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD,
            line_spacing=0.5,
            alignment="center"
        ).scale(LABEL_SCALE)
        
        predicted_video_group = VGroup(predicted_video, predicted_video_label)
        # Position label at top of box (lowered)
        predicted_video_label.move_to([predicted_video.get_center()[0], predicted_video.get_top()[1] - 0.45, 0])
        # Set z-index: intermediate priority for colored data boxes
        predicted_video.set_z_index(0)
        predicted_video_label.set_z_index(1)
        
        # Generated actions (blue) - narrower box
        generated_actions = RoundedRectangle(
            width=GENERATED_ACTIONS_WIDTH,
            height=DATA_BOX_HEIGHT,
            corner_radius=DATA_BOX_CORNER_RADIUS,
            fill_color=GENERATED_ACTIONS_FILL,
            fill_opacity=1,
            stroke_color=GENERATED_ACTIONS_STROKE,
            stroke_width=DATA_BOX_STROKE_WIDTH
        )
        
        generated_actions_label = Paragraph(
            "generated", "actions",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD,
            line_spacing=0.5,
            alignment="center"
        ).scale(LABEL_SCALE)
        
        generated_actions_group = VGroup(generated_actions, generated_actions_label)
        # Position label at top of box (lowered)
        generated_actions_label.move_to([generated_actions.get_center()[0], generated_actions.get_top()[1] - 0.45, 0])
        # Set z-index: intermediate priority for colored data boxes
        generated_actions.set_z_index(0)
        generated_actions_label.set_z_index(1)
        
        # =====================================================================
        # CREATE MODEL BOXES
        # =====================================================================
        
        # Video model
        video_model = RoundedRectangle(
            width=MODEL_BOX_WIDTH,
            height=MODEL_BOX_HEIGHT,
            corner_radius=MODEL_BOX_CORNER_RADIUS,
            fill_color=MODEL_BOX_FILL,
            fill_opacity=1,
            stroke_color=MODEL_BOX_STROKE,
            stroke_width=MODEL_BOX_STROKE_WIDTH
        )
        
        video_model_label = Paragraph(
            "causal", "video", "model",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD,
            line_spacing=0.5,
            alignment="center"
        ).scale(LABEL_SCALE * 0.8)
        
        video_model_group = VGroup(video_model, video_model_label)
        video_model_label.move_to(video_model.get_center())
        # Set z-index: top priority for model boxes
        video_model.set_z_index(10)
        video_model_label.set_z_index(11)
        
        # Action model
        action_model = RoundedRectangle(
            width=MODEL_BOX_WIDTH,
            height=MODEL_BOX_HEIGHT,
            corner_radius=MODEL_BOX_CORNER_RADIUS,
            fill_color=MODEL_BOX_FILL,
            fill_opacity=1,
            stroke_color=MODEL_BOX_STROKE,
            stroke_width=MODEL_BOX_STROKE_WIDTH
        )
        
        action_model_label = Paragraph(
            "inverse", "dynamics", "model",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD,
            line_spacing=0.5,
            alignment="center"
        ).scale(LABEL_SCALE * 0.8)
        
        action_model_group = VGroup(action_model, action_model_label)
        action_model_label.move_to(action_model.get_center())
        # Set z-index: top priority for model boxes
        action_model.set_z_index(10)
        action_model_label.set_z_index(11)
        
        # =====================================================================
        # POSITION ALL ELEMENTS
        # =====================================================================
        
        # Calculate positions from left to right
        # Layout: video_context -- video_model -- predicted_video -- action_model -- generated_actions
        
        total_width = (
            VIDEO_CONTEXT_WIDTH +         # video context (wider)
            PREDICTED_VIDEO_WIDTH +       # predicted video (narrower)
            GENERATED_ACTIONS_WIDTH +     # generated actions (narrower)
            2 * MODEL_BOX_WIDTH +         # 2 model boxes
            4 * HORIZONTAL_GAP            # gaps between elements
        )
        
        start_x = -total_width / 2 + VIDEO_CONTEXT_WIDTH / 2
        
        # Position video context
        video_context_group.move_to([start_x, MAIN_Y, 0])
        
        # Position video model (same Y as data boxes for horizontal arrows)
        # Nudge slightly left to better center between data boxes
        model_nudge = 0.1
        video_model_x = start_x + VIDEO_CONTEXT_WIDTH / 2 + HORIZONTAL_GAP + MODEL_BOX_WIDTH / 2 - model_nudge
        video_model_group.move_to([video_model_x, MAIN_Y, 0])
        
        # Position predicted video
        predicted_video_x = video_model_x + MODEL_BOX_WIDTH / 2 + HORIZONTAL_GAP + PREDICTED_VIDEO_WIDTH / 2
        predicted_video_group.move_to([predicted_video_x, MAIN_Y, 0])
        
        # Position action model (nudge left to match video model)
        action_model_x = predicted_video_x + PREDICTED_VIDEO_WIDTH / 2 + HORIZONTAL_GAP + MODEL_BOX_WIDTH / 2 - model_nudge
        action_model_group.move_to([action_model_x, MAIN_Y, 0])
        
        # Position generated actions
        generated_actions_x = action_model_x + MODEL_BOX_WIDTH / 2 + HORIZONTAL_GAP + GENERATED_ACTIONS_WIDTH / 2
        generated_actions_group.move_to([generated_actions_x, MAIN_Y, 0])
        
        # =====================================================================
        # CREATE DATA CHUNKS (small squares inside data boxes)
        # =====================================================================
        
        # Vertical position for chunks: align with arrows (MAIN_Y)
        chunk_y = MAIN_Y
        
        # --- Video Context Chunks (using VideoContextCache for cycling animation) ---
        video_context_center = video_context.get_center()
        video_context_cache = VideoContextCache(
            center_x=video_context_center[0],
            y=chunk_y,
            color=VIDEO_CONTEXT_STROKE
        )
        video_context_cache.set_z_index(2)  # Above the box but below labels
        
        # --- Predicted Video Chunks (2 yellow squares) - start invisible ---
        predicted_video_center = predicted_video.get_center()
        
        pv_chunks = VGroup()
        # Center the 2 chunks
        total_pv_chunks_width = 2 * CHUNK_SIZE + CHUNK_SPACING
        pv_start_x = predicted_video_center[0] - total_pv_chunks_width / 2 + CHUNK_SIZE / 2
        for i in range(2):
            chunk = DataChunk(PREDICTED_VIDEO_STROKE)
            chunk_x = pv_start_x + i * (CHUNK_SIZE + CHUNK_SPACING)
            chunk.move_to([chunk_x, chunk_y, 0])
            chunk.set_chunk_opacity(0)  # Start invisible
            pv_chunks.add(chunk)
        
        pv_chunks.set_z_index(2)
        
        # Store final positions for predicted video chunks (for animation)
        pv_final_positions = [
            [pv_start_x, chunk_y, 0],
            [pv_start_x + CHUNK_SIZE + CHUNK_SPACING, chunk_y, 0]
        ]
        
        # --- Generated Actions Chunks (1 blue square) - start invisible ---
        generated_actions_center = generated_actions.get_center()
        
        ga_chunk = DataChunk(GENERATED_ACTIONS_STROKE)
        ga_chunk.move_to([generated_actions_center[0], chunk_y, 0])
        ga_chunk.set_chunk_opacity(0.5)  # Start invisible
        ga_chunk.set_z_index(2)
        
        # Store final position for generated actions chunk (for animation)
        ga_final_position = [generated_actions_center[0], chunk_y, 0]
        
        # # =====================================================================
        # # CREATE INDEX LABELS UNDERNEATH CHUNKS (fixed, math typeset)
        # # =====================================================================
        
        # label_y = chunk_y - CHUNK_SIZE / 2 - 0.25  # Position below chunks (moved down)
        # index_label_scale = 0.5  # Larger scale
        
        # # Helper to create index label with MathTex (bold)
        # def make_index_label(tex, x, color):
        #     # Use \mathbf for bold
        #     label = MathTex(r"\boldsymbol{" + tex + "}", color=color).scale(index_label_scale)
        #     label.move_to([x, label_y, 0])
        #     return label
        
        # # Video context labels: -N, (ellipsis), -2, -1, 0 (orange color)
        # vc_slot_positions = video_context_cache.slot_positions
        
        # vc_label_n = make_index_label("-N", vc_slot_positions[0], VIDEO_CONTEXT_STROKE)
        # vc_label_2 = make_index_label("-2", vc_slot_positions[2], VIDEO_CONTEXT_STROKE)
        # vc_label_1 = make_index_label("-1", vc_slot_positions[3], VIDEO_CONTEXT_STROKE)
        # vc_label_0 = make_index_label("0", vc_slot_positions[4], VIDEO_CONTEXT_STROKE)
        
        # vc_index_labels = VGroup(vc_label_n, vc_label_2, vc_label_1, vc_label_0)
        
        # # Predicted video labels: 0, +1 (blue color)
        # pv_label_0 = make_index_label("+1", pv_final_positions[0][0], PREDICTED_VIDEO_STROKE)
        # pv_label_1 = make_index_label("+2", pv_final_positions[1][0], PREDICTED_VIDEO_STROKE)
        
        # pv_index_labels = VGroup(pv_label_0, pv_label_1)
        
        # # Generated actions label: +1 (yellow color)
        # ga_label_1 = make_index_label("+1", ga_final_position[0], GENERATED_ACTIONS_STROKE)
        
        # ga_index_labels = VGroup(ga_label_1)
        
        # # Group all index labels
        # all_index_labels = VGroup(vc_index_labels, pv_index_labels, ga_index_labels)
        # all_index_labels.set_z_index(5)  # Above chunks
        
        # =====================================================================
        # CREATE CONNECTORS BETWEEN ELEMENTS (horizontal, thick)
        # Using continuous Lines that go behind shapes + separate Triangles for arrowheads
        # =====================================================================
        
        line_config = {
            "stroke_width": CONNECTOR_STROKE_WIDTH,
            "color": CONNECTOR_COLOR,
        }
        
        # All connectors at MAIN_Y to ensure they're horizontal
        arrow_y = MAIN_Y
        arrowhead_size = 0.18  # Size of triangle arrowheads (smaller)
        
        # Helper to create a right-pointing arrowhead triangle
        def make_arrowhead(x, y):
            tri = Triangle(
                fill_color=CONNECTOR_COLOR,
                fill_opacity=1,
                stroke_width=0
            )
            tri.scale(arrowhead_size)
            tri.rotate(-PI/2)  # Point right
            tri.move_to([x, y, 0])
            return tri
        
        # Arrowhead offset: position arrowhead tip just before the shape
        arrowhead_offset = arrowhead_size * 1.0  # Center of triangle offset from shape edge
        
        # Create one continuous line from video_context through video_model to predicted_video
        # This goes behind the video_model
        connector1_line = Line(
            start=[video_context.get_right()[0], arrow_y, 0],
            end=[predicted_video.get_left()[0] - arrowhead_offset, arrow_y, 0],
            **line_config
        )
        connector1_line.set_z_index(-10)  # Bottom priority - behind everything
        connector1_head = make_arrowhead(predicted_video.get_left()[0] - arrowhead_offset, arrow_y)
        connector1_head.set_z_index(-10)  # Bottom priority
        connector1 = VGroup(connector1_line, connector1_head)
        
        # Create one continuous line from predicted_video through action_model to generated_actions
        # This goes behind the action_model
        connector2_line = Line(
            start=[predicted_video.get_right()[0], arrow_y, 0],
            end=[generated_actions.get_left()[0] - arrowhead_offset, arrow_y, 0],
            **line_config
        )
        connector2_line.set_z_index(-10)  # Bottom priority - behind everything
        connector2_head = make_arrowhead(generated_actions.get_left()[0] - arrowhead_offset, arrow_y)
        connector2_head.set_z_index(-10)  # Bottom priority
        connector2 = VGroup(connector2_line, connector2_head)
        
        # =====================================================================
        # CREATE FEEDBACK LOOP (action rollout)
        # =====================================================================
        
        # Loop path: from RIGHT of generated_actions, down, left to rightmost chunk, up into video_context
        # Uses 3 right turns (not 4) to enter from bottom
        
        loop_gap = -.12  # Horizontal gap for the vertical portion of the loop
        box_right_x = generated_actions.get_right()[0]  # Start from box edge
        loop_right_x = box_right_x + loop_gap  # Offset for vertical portion
        loop_bottom_y = MAIN_Y - DATA_BOX_HEIGHT / 2 - 0.5  # Below boxes
        corner_radius = 0.35  # Larger corners for smoother path
        
        # Calculate rightmost chunk position (where loop enters video_context from below)
        spacing = CHUNK_SIZE + CHUNK_SPACING
        vc_center_x = video_context.get_center()[0]
        right_group_start_x = vc_center_x + 0.05
        rightmost_chunk_x = right_group_start_x + 2 * spacing
        video_context_bottom_y = MAIN_Y - DATA_BOX_HEIGHT / 2
        
        # Create the loop path - use unified stroke width
        loop_parts = VGroup()
        
        # 1. Horizontal line from right of generated_actions going right to start of curve
        loop_start_h = Line(
            start=[box_right_x, MAIN_Y, 0],  # Start from box edge
            end=[loop_right_x + corner_radius, MAIN_Y, 0],
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        loop_parts.add(loop_start_h)
        
        # 2. Top-right corner arc (curving down)
        corner1 = Arc(
            radius=corner_radius,
            start_angle=PI/2,   # Start pointing up
            angle=-PI/2,        # Curve clockwise (down)
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        corner1.move_arc_center_to([loop_right_x + corner_radius, MAIN_Y - corner_radius, 0])
        loop_parts.add(corner1)
        
        # 3. Vertical line going down on the right side
        loop_right_v = Line(
            start=[loop_right_x + 2*corner_radius, MAIN_Y - corner_radius, 0],
            end=[loop_right_x + 2*corner_radius, loop_bottom_y + corner_radius, 0],
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        loop_parts.add(loop_right_v)
        
        # 4. Bottom-right corner arc (curving left)
        corner2 = Arc(
            radius=corner_radius,
            start_angle=0,      # Start pointing right
            angle=-PI/2,        # Curve clockwise (down then left)
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        corner2.move_arc_center_to([loop_right_x + corner_radius, loop_bottom_y + corner_radius, 0])
        loop_parts.add(corner2)
        
        # 5. Horizontal line at bottom going left (to rightmost chunk position)
        loop_bottom_h = Line(
            start=[loop_right_x + corner_radius, loop_bottom_y, 0],
            end=[rightmost_chunk_x + corner_radius, loop_bottom_y, 0],
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        loop_parts.add(loop_bottom_h)
        
        # 6. Bottom corner arc at rightmost chunk (curving up)
        corner3 = Arc(
            radius=corner_radius,
            start_angle=-PI/2,  # Start pointing down (coming from right)
            angle=-PI/2,        # Curve clockwise (to point up)
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        corner3.move_arc_center_to([rightmost_chunk_x + corner_radius, loop_bottom_y + corner_radius, 0])
        loop_parts.add(corner3)
        
        # 7. Vertical line going up toward video_context (stops short of box)
        line_gap = 0.15  # Gap between line end and box edge
        loop_up_v = Line(
            start=[rightmost_chunk_x, loop_bottom_y + corner_radius, 0],
            end=[rightmost_chunk_x, video_context_bottom_y - line_gap, 0],
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        loop_parts.add(loop_up_v)
        
        # 8. Arrowhead pointing UP into video_context (positioned near box edge)
        loop_end_head = Triangle(
            fill_color=CONNECTOR_COLOR,
            fill_opacity=1,
            stroke_width=0
        )
        loop_end_head.scale(arrowhead_size)
        # Triangle points up by default, no rotation needed
        # Position arrowhead tip just below the box edge
        loop_end_head.move_to([rightmost_chunk_x + 0.01, video_context_bottom_y - arrowhead_offset * 0.9, 0])
        loop_parts.add(loop_end_head)
        
        # Set z-index for all loop parts: bottom priority
        loop_parts.set_z_index(-10)
        
        # Action rollout label box (positioned on the bottom horizontal line)
        action_rollout_box = RoundedRectangle(
            width=LOOP_BOX_WIDTH,
            height=LOOP_BOX_HEIGHT,
            corner_radius=LOOP_BOX_CORNER_RADIUS,
            fill_color=MODEL_BOX_FILL,
            fill_opacity=1,
            stroke_color=MODEL_BOX_STROKE,
            stroke_width=MODEL_BOX_STROKE_WIDTH
        )
        # Center on the bottom horizontal segment (between loop_right_x and rightmost_chunk_x)
        action_rollout_x = (loop_right_x + corner_radius + rightmost_chunk_x + corner_radius) / 2
        action_rollout_box.move_to([action_rollout_x, loop_bottom_y, 0])
        
        action_rollout_label = Text(
            "action rollout",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD
        ).scale(LABEL_SCALE * 0.8)
        action_rollout_label.move_to(action_rollout_box.get_center())
        # Set z-index: top priority for action rollout (same as model boxes)
        action_rollout_box.set_z_index(10)
        action_rollout_label.set_z_index(11)
        
        action_rollout_group = VGroup(action_rollout_box, action_rollout_label)
        
        # =====================================================================
        # ADD ALL ELEMENTS TO SCENE
        # =====================================================================
        
        # Add all elements (static diagram - no animation)
        # Add connectors first (behind), then shapes on top
        self.add(
            # Connectors (behind everything)
            connector1, connector2,
            # Feedback loop
            loop_parts,
            action_rollout_group,
            # Data boxes (on top)
            video_context_group,
            predicted_video_group,
            generated_actions_group,
            # Data chunks inside boxes
            video_context_cache,
            pv_chunks,
            ga_chunk,
            # # Index labels underneath chunks
            # all_index_labels,
            # Model boxes (on top)
            video_model_group,
            action_model_group,
        )
        
        # =====================================================================
        # ANIMATION CYCLE - Top and Bottom loops run in parallel
        # =====================================================================
        
        # Both loops take exactly the same time
        CYCLE_TIME = 2.5  # seconds per full cycle
        
        # Store model centers
        video_model_center = video_model.get_center()
        action_model_center = action_model.get_center()
        
        # Final destination for bottom loop path
        rightmost_x = video_context_cache.slot_positions[4]
        final_vc_position = np.array([rightmost_x, chunk_y, 0])
        
        # Colors for bottom loop interpolation
        start_color = ManimColor(GENERATED_ACTIONS_STROKE)
        end_color = ManimColor(VIDEO_CONTEXT_STROKE)
        
        # Phase timing within top loop (as fractions of CYCLE_TIME)
        PHASE1_FRAC = 0.30  # Context ghosts → video model + cache shuffle
        PHASE2_FRAC = 0.20  # Predicted video emerges
        PHASE3_FRAC = 0.30  # PV ghosts → action model
        PHASE4_FRAC = 0.20  # Generated action emerges
        
        # -----------------------------------------------------------------
        # Build the bottom loop path (reusable)
        # Path: ga_final_position → right → down → left → up into video_context
        # -----------------------------------------------------------------
        def build_bottom_loop_path():
            path = VMobject()
            path.set_points_as_corners([
                np.array([ga_final_position[0], MAIN_Y, 0]),
                np.array([box_right_x, MAIN_Y, 0]),
                np.array([loop_right_x + corner_radius, MAIN_Y, 0]),
            ])
            
            # Corner 1: Turn down
            c1 = Arc(radius=corner_radius, start_angle=PI/2, angle=-PI/2)
            c1.move_arc_center_to(np.array([loop_right_x + corner_radius, MAIN_Y - corner_radius, 0]))
            path.append_vectorized_mobject(c1)
            
            # Go down
            path.add_line_to(np.array([loop_right_x + 2*corner_radius, loop_bottom_y + corner_radius, 0]))
            
            # Corner 2: Turn left
            c2 = Arc(radius=corner_radius, start_angle=0, angle=-PI/2)
            c2.move_arc_center_to(np.array([loop_right_x + corner_radius, loop_bottom_y + corner_radius, 0]))
            path.append_vectorized_mobject(c2)
            
            # Go left to rightmost chunk position
            path.add_line_to(np.array([rightmost_chunk_x + corner_radius, loop_bottom_y, 0]))
            
            # Corner 3: Turn up
            c3 = Arc(radius=corner_radius, start_angle=-PI/2, angle=-PI/2)
            c3.move_arc_center_to(np.array([rightmost_chunk_x + corner_radius, loop_bottom_y + corner_radius, 0]))
            path.append_vectorized_mobject(c3)
            
            # Go up into video_context to final position
            path.add_line_to(final_vc_position)
            
            return path
        
        # -----------------------------------------------------------------
        # SINGLE CYCLE - Multiple self.play() with bottom loop via updater
        # -----------------------------------------------------------------
        
        # Calculate phase times
        p1_time = PHASE1_FRAC * CYCLE_TIME
        p2_time = PHASE2_FRAC * CYCLE_TIME
        p3_time = PHASE3_FRAC * CYCLE_TIME
        p4_time = PHASE4_FRAC * CYCLE_TIME
        
        # Context shuffle timing
        shuffle_delay = 0.25  # Delay before shuffle starts (as fraction of p1_time)
        fadeout_time = 0.15  # Leftmost chunk fadeout duration
        shift_time = 0.25    # Shift animation duration
        
        # =================================================================
        # PRE-CREATE ALL ANIMATED OBJECTS
        # =================================================================
        
        # --- Bottom loop chunk ---
        bottom_chunk = DataChunk(GENERATED_ACTIONS_STROKE)
        bottom_chunk.move_to(ga_final_position)
        bottom_chunk.set_chunk_opacity(1.0)
        self.add(bottom_chunk)
        
        bottom_path = build_bottom_loop_path()
        
        # --- Context ghosts (for Phase 1) ---
        visible_chunks = video_context_cache.get_visible_chunks()
        context_ghosts = VGroup()
        for chunk in visible_chunks:
            ghost = chunk.copy()
            ghost.set_chunk_opacity(1.0)
            context_ghosts.add(ghost)
        self.add(context_ghosts)
        
        # --- PV chunks: start at video model (scaled down, low opacity) ---
        for i, pv_chunk in enumerate(pv_chunks):
            pv_chunk.move_to(video_model_center)
            pv_chunk.scale(0.3)
            pv_chunk.set_chunk_opacity(0.5)
        
        # --- PV ghosts (for Phase 3): pre-create at final PV positions ---
        pv_ghosts = VGroup()
        for i, pv_chunk in enumerate(pv_chunks):
            ghost = DataChunk(PREDICTED_VIDEO_STROKE)
            ghost.move_to(pv_final_positions[i])
            ghost.set_chunk_opacity(0)  # Start invisible, will be shown in Phase 3
            pv_ghosts.add(ghost)
        self.add(pv_ghosts)
        
        # --- GA chunk: start at action model (scaled down, low opacity) ---
        ga_chunk.move_to(action_model_center)
        ga_chunk.scale(0.3)
        ga_chunk.set_chunk_opacity(0.5)
        
        # =================================================================
        # BUILD ANIMATION GROUPS
        # =================================================================
        
        # --- LOWER LOOP: MoveAlongPath with color interpolation ---
        # Use UpdateFromAlphaFunc to control color based on animation progress
        def update_color(mob, alpha):
            new_color = interpolate_color(start_color, end_color, alpha)
            mob.rect.set_stroke(color=new_color)
            mob.rect.set_fill(color=new_color)
            mob.set_chunk_opacity(0.8 + 0.2 * alpha)
        
        # Create a dummy mobject for the color animation (since MoveAlongPath controls position)
        color_dummy = Mobject()
        
        lower_loop = AnimationGroup(
            MoveAlongPath(bottom_chunk, bottom_path, rate_func=linear),
            UpdateFromAlphaFunc(color_dummy, lambda m, a: update_color(bottom_chunk, a), rate_func=linear),
            run_time=CYCLE_TIME
        )
        
        # --- UPPER LOOP SEQUENCE (Phases 1-4) ---
        
        # Phase 1: Context ghosts → Video Model
        phase1_ghost_anim = AnimationGroup(
            *[ghost.animate.move_to(video_model_center).scale(0.3).set_chunk_opacity(0.5)
              for ghost in context_ghosts],
            run_time=p1_time
        )
        
        # Phase 2: Predicted Video emerges from video model
        phase2_anim = AnimationGroup(
            *[pv_chunk.animate.move_to(pv_final_positions[i]).scale(1/0.3).set_chunk_opacity(1)
              for i, pv_chunk in enumerate(pv_chunks)],
            run_time=p2_time
        )
        
        # Phase 3: PV ghosts appear and move → Action Model
        # First show ghosts at full opacity, then move them to action model
        phase3_anim = Succession(
            # Instantly show ghosts and hide originals
            AnimationGroup(
                *[ghost.animate(run_time=0.01).set_chunk_opacity(1) for ghost in pv_ghosts],
                *[pv_chunk.animate(run_time=0.01).set_chunk_opacity(0) for pv_chunk in pv_chunks],
            ),
            # Move ghosts to action model
            AnimationGroup(
                *[ghost.animate.move_to(action_model_center).scale(0.3).set_chunk_opacity(0.5)
                  for ghost in pv_ghosts],
                run_time=p3_time - 0.01
            ),
        )
        
        # Phase 4: Generated Action emerges from action model
        phase4_anim = AnimationGroup(
            ga_chunk.animate.move_to(ga_final_position).scale(1/0.3).set_chunk_opacity(1),
            run_time=p4_time
        )
        
        # Combine phases 1-4 into a Succession
        upper_loop_sequence = Succession(
            phase1_ghost_anim,
            phase2_anim,
            phase3_anim,
            phase4_anim,
        )
        
        # --- CONTEXT SHUFFLE (delayed, two-stage) ---
        context_shuffle = Succession(
            Wait(shuffle_delay),  # Delay before starting
            video_context_cache.get_fadeout_animation(),  # Fadeout leftmost
            AnimationGroup(*video_context_cache.get_shift_animations(), run_time=shift_time),  # Shift
        )
        
        # --- UPPER LOOP: Sequence + Shuffle in parallel ---
        upper_loop = AnimationGroup(
            upper_loop_sequence,
            context_shuffle,
        )
        
        # =================================================================
        # RUN BOTH LOOPS IN PARALLEL
        # =================================================================
        
        self.play(
            upper_loop,
            lower_loop,
            run_time=CYCLE_TIME
        )
        
        # =================================================================
        # CLEANUP
        # =================================================================
        
        video_context_cache.finalize_cycle(self, add_new_chunk=False)
        self.remove(context_ghosts, pv_ghosts)
        
        # Add arrived bottom chunk to cache
        video_context_cache.chunks.append(bottom_chunk)
        video_context_cache.add(bottom_chunk)
        
        # Animation ends with ga_chunk at ga_final_position (same visual state as start)
        # Video context cache has cycled (one removed left, one added right)
        # This creates a seamless loop


# =============================================================================
# RENDER COMMANDS
# =============================================================================
# Preview: manim -pql overview.py OverviewDiagram
# High quality: manim -pqh overview.py OverviewDiagram
# PNG export: manim -s overview.py OverviewDiagram
