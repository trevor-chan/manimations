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
    FILL_LIGHT_GRAY
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

# Aspect ratio (3:1 - wide diagram)
config.pixel_width = 2400
config.pixel_height = 800
config.frame_width = 18
config.frame_height = 6

# =============================================================================
# COLORS (matching the inspiration)
# =============================================================================

# Main blocks
VIDEO_CONTEXT_FILL = "#FFCCAA"       # Peach/orange fill
VIDEO_CONTEXT_STROKE = "#FF9955"     # Orange stroke

PREDICTED_VIDEO_FILL = "#FFF6D5"     # Light yellow fill
PREDICTED_VIDEO_STROKE = "#FFE680"   # Yellow stroke

GENERATED_ACTIONS_FILL = "#D5E5FF"   # Light blue fill
GENERATED_ACTIONS_STROKE = "#80B3FF" # Blue stroke

# Model boxes and connectors
MODEL_BOX_FILL = "#ECECEC"           # Light gray
MODEL_BOX_STROKE = "#B3B3B3"         # Medium gray
CONNECTOR_COLOR = "#B3B3B3"          # Gray for arrows and loop

# =============================================================================
# CONSTANTS
# =============================================================================

# Box dimensions
DATA_BOX_WIDTH = 2.5
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
        
        # Video context (orange)
        video_context = RoundedRectangle(
            width=DATA_BOX_WIDTH,
            height=DATA_BOX_HEIGHT,
            corner_radius=DATA_BOX_CORNER_RADIUS,
            fill_color=VIDEO_CONTEXT_FILL,
            fill_opacity=1,
            stroke_color=VIDEO_CONTEXT_STROKE,
            stroke_width=DATA_BOX_STROKE_WIDTH
        )
        
        video_context_label = Text(
            "video context",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD
        ).scale(LABEL_SCALE)
        
        video_context_group = VGroup(video_context, video_context_label)
        # Position label at top of box
        video_context_label.move_to([video_context.get_center()[0], video_context.get_top()[1] - 0.3, 0])
        
        # Predicted video (yellow)
        predicted_video = RoundedRectangle(
            width=DATA_BOX_WIDTH,
            height=DATA_BOX_HEIGHT,
            corner_radius=DATA_BOX_CORNER_RADIUS,
            fill_color=PREDICTED_VIDEO_FILL,
            fill_opacity=1,
            stroke_color=PREDICTED_VIDEO_STROKE,
            stroke_width=DATA_BOX_STROKE_WIDTH
        )
        
        predicted_video_label = Text(
            "predicted video",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD
        ).scale(LABEL_SCALE)
        
        predicted_video_group = VGroup(predicted_video, predicted_video_label)
        # Position label at top of box
        predicted_video_label.move_to([predicted_video.get_center()[0], predicted_video.get_top()[1] - 0.3, 0])
        
        # Generated actions (blue)
        generated_actions = RoundedRectangle(
            width=DATA_BOX_WIDTH,
            height=DATA_BOX_HEIGHT,
            corner_radius=DATA_BOX_CORNER_RADIUS,
            fill_color=GENERATED_ACTIONS_FILL,
            fill_opacity=1,
            stroke_color=GENERATED_ACTIONS_STROKE,
            stroke_width=DATA_BOX_STROKE_WIDTH
        )
        
        generated_actions_label = Text(
            "generated actions",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD
        ).scale(LABEL_SCALE)
        
        generated_actions_group = VGroup(generated_actions, generated_actions_label)
        # Position label at top of box
        generated_actions_label.move_to([generated_actions.get_center()[0], generated_actions.get_top()[1] - 0.3, 0])
        
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
            "video", "model",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD,
            line_spacing=0.8,
            alignment="center"
        ).scale(LABEL_SCALE * 0.8)
        
        video_model_group = VGroup(video_model, video_model_label)
        video_model_label.move_to(video_model.get_center())
        
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
            "action", "model",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD,
            line_spacing=0.8,
            alignment="center"
        ).scale(LABEL_SCALE * 0.8)
        
        action_model_group = VGroup(action_model, action_model_label)
        action_model_label.move_to(action_model.get_center())
        
        # =====================================================================
        # POSITION ALL ELEMENTS
        # =====================================================================
        
        # Calculate positions from left to right
        # Layout: video_context -- video_model -- predicted_video -- action_model -- generated_actions
        
        total_width = (
            3 * DATA_BOX_WIDTH +      # 3 data boxes
            2 * MODEL_BOX_WIDTH +     # 2 model boxes
            4 * HORIZONTAL_GAP        # gaps between elements
        )
        
        start_x = -total_width / 2 + DATA_BOX_WIDTH / 2
        
        # Position video context
        video_context_group.move_to([start_x, MAIN_Y, 0])
        
        # Position video model (same Y as data boxes for horizontal arrows)
        # Nudge slightly left to better center between data boxes
        model_nudge = 0.1
        video_model_x = start_x + DATA_BOX_WIDTH / 2 + HORIZONTAL_GAP + MODEL_BOX_WIDTH / 2 - model_nudge
        video_model_group.move_to([video_model_x, MAIN_Y, 0])
        
        # Position predicted video
        predicted_video_x = video_model_x + MODEL_BOX_WIDTH / 2 + HORIZONTAL_GAP + DATA_BOX_WIDTH / 2
        predicted_video_group.move_to([predicted_video_x, MAIN_Y, 0])
        
        # Position action model (nudge left to match video model)
        action_model_x = predicted_video_x + DATA_BOX_WIDTH / 2 + HORIZONTAL_GAP + MODEL_BOX_WIDTH / 2 - model_nudge
        action_model_group.move_to([action_model_x, MAIN_Y, 0])
        
        # Position generated actions
        generated_actions_x = action_model_x + MODEL_BOX_WIDTH / 2 + HORIZONTAL_GAP + DATA_BOX_WIDTH / 2
        generated_actions_group.move_to([generated_actions_x, MAIN_Y, 0])
        
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
        connector1_line.set_z_index(-1)  # Behind shapes
        connector1_head = make_arrowhead(predicted_video.get_left()[0] - arrowhead_offset, arrow_y)
        connector1 = VGroup(connector1_line, connector1_head)
        
        # Create one continuous line from predicted_video through action_model to generated_actions
        # This goes behind the action_model
        connector2_line = Line(
            start=[predicted_video.get_right()[0], arrow_y, 0],
            end=[generated_actions.get_left()[0] - arrowhead_offset, arrow_y, 0],
            **line_config
        )
        connector2_line.set_z_index(-1)  # Behind shapes
        connector2_head = make_arrowhead(generated_actions.get_left()[0] - arrowhead_offset, arrow_y)
        connector2 = VGroup(connector2_line, connector2_head)
        
        # =====================================================================
        # CREATE FEEDBACK LOOP (action rollout)
        # =====================================================================
        
        # Loop path: from RIGHT of generated_actions, down, left, up to LEFT of video_context
        # The loop connects to the boxes but curves outward with a gap
        
        loop_gap = -.12  # Horizontal gap for the vertical portion of the loop
        box_right_x = generated_actions.get_right()[0]  # Start from box edge
        box_left_x = video_context.get_left()[0]        # End at box edge
        loop_right_x = box_right_x + loop_gap  # Offset for vertical portion
        loop_left_x = box_left_x - loop_gap    # Offset for vertical portion
        loop_bottom_y = MAIN_Y - DATA_BOX_HEIGHT / 2 - 0.5  # Below boxes
        corner_radius = 0.35  # Larger corners for smoother path
        
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
        
        # 5. Horizontal line at bottom going left
        loop_bottom_h = Line(
            start=[loop_right_x + corner_radius, loop_bottom_y, 0],
            end=[loop_left_x - corner_radius, loop_bottom_y, 0],
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        loop_parts.add(loop_bottom_h)
        
        # 6. Bottom-left corner arc (curving up)
        corner3 = Arc(
            radius=corner_radius,
            start_angle=-PI/2,  # Start pointing down
            angle=-PI/2,        # Curve clockwise (left then up)
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        corner3.move_arc_center_to([loop_left_x - corner_radius, loop_bottom_y + corner_radius, 0])
        loop_parts.add(corner3)
        
        # 7. Vertical line going up on the left side
        loop_left_v = Line(
            start=[loop_left_x - 2*corner_radius, loop_bottom_y + corner_radius, 0],
            end=[loop_left_x - 2*corner_radius, MAIN_Y - corner_radius, 0],
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        loop_parts.add(loop_left_v)
        
        # 8. Top-left corner arc (curving right, ending with arrow)
        corner4 = Arc(
            radius=corner_radius,
            start_angle=PI,     # Start pointing left
            angle=-PI/2,        # Curve clockwise (up then right)
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        corner4.move_arc_center_to([loop_left_x - corner_radius, MAIN_Y - corner_radius, 0])
        loop_parts.add(corner4)
        
        # 9. Final horizontal line + arrowhead into video_context
        loop_end_line = Line(
            start=[loop_left_x - corner_radius, MAIN_Y, 0],
            end=[box_left_x - arrowhead_offset, MAIN_Y, 0],  # End at box edge (minus arrowhead)
            stroke_width=CONNECTOR_STROKE_WIDTH,
            color=CONNECTOR_COLOR
        )
        loop_parts.add(loop_end_line)
        
        loop_end_head = make_arrowhead(box_left_x - arrowhead_offset, MAIN_Y)  # Arrowhead at box edge
        loop_parts.add(loop_end_head)
        
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
        action_rollout_box.move_to([-0.1, loop_bottom_y, 0])  # Slightly left of center on bottom of loop
        
        action_rollout_label = Text(
            "action rollout",
            font=LABEL_FONT,
            font_size=LABEL_FONT_SIZE,
            color=TEXT_DARK,
            weight=SEMIBOLD
        ).scale(LABEL_SCALE * 0.8)
        action_rollout_label.move_to(action_rollout_box.get_center())
        
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
            # Model boxes (on top)
            video_model_group,
            action_model_group,
        )
        
        # Wait a moment for rendering
        self.wait(1)


# =============================================================================
# RENDER COMMANDS
# =============================================================================
# Preview: manim -pql overview.py OverviewDiagram
# High quality: manim -pqh overview.py OverviewDiagram
# PNG export: manim -s overview.py OverviewDiagram
