"""
Data Circles Figure - Visualization of training data hours

Shows circles with areas proportional to hours of training data.
Uses camera panning/zooming to reveal each circle at the same apparent size.
"""

from manim import *
import math
from matplotlib import font_manager
import sys
from pathlib import Path

# Add parent directory to path for colors import
sys.path.insert(0, str(Path(__file__).parent.parent))
from colors import (
    RHODA_ORANGE, RHODA_BLUE, RHODA_BLUE_LIGHT,
    BG_OFFWHITE, TEXT_DARK, MARKER_GRAY, ACTION_COLOR,
    get_gradient_color, GRADIENT_SIMPLE
)

def get_preferred_font():
    """Return 'Open Sans' if available, otherwise 'Arial'."""
    available_fonts = {f.name for f in font_manager.fontManager.ttflist}
    if "Open Sans" in available_fonts:
        print("Using Open Sans")
        return "Open Sans"
    print("Using Arial")
    return "Arial"

# Configure 2:1 aspect ratio
config.pixel_width = 3840
config.pixel_height = 1920
config.frame_width = 16
config.frame_height = 8


class DataCirclesFigure(MovingCameraScene):
    def construct(self):
        # Set background
        self.camera.background_color = BG_OFFWHITE
        
        # Data: (name, hours)
        data = [
            ("OXE", 4000),
            (r"\pi_0", 10000),
            ("GEN-0", 270000),
            ("Rhoda", 20),
        ]

        # Calculate radii proportional to sqrt(hours) for area scaling
        # Scale factor to make circles reasonably sized on screen (2x larger)
        scale_factor = 0.012
        
        circles = []
        labels = []
        radii = []
        
        for i, (name, hours) in enumerate(data):
            radius = math.sqrt(hours) * scale_factor
            radii.append(radius)
            circle = Circle(radius=radius)
            # Gradient fill within circle: orange → blue → white (diagonal)
            circle.set_fill(color=[RHODA_ORANGE, RHODA_BLUE, "#FFFFFF"], opacity=0.85)
            circle.set_sheen_direction(UR)  # Diagonal gradient direction
            # Use same color as baseline; Rhoda (last) gets thinner stroke
            stroke_width = 0.5 if i == len(data) - 1 else 1
            circle.set_stroke(color=MARKER_GRAY, width=stroke_width, opacity=1)
            circles.append(circle)
            
            # Create label with name and hours
            if hours >= 1000:
                hours_str = f"{hours // 1000}K HRS"
            else:
                hours_str = f"~{hours} HRS"
            
            # Use sans-serif font for all text
            sans_font = get_preferred_font()
            if name == r"\pi_0":
                # Use Text with Unicode pi for consistent sans-serif styling
                name_label = Text("π₀", font=sans_font, font_size=36, weight=SEMIBOLD, color=TEXT_DARK)
            else:
                name_label = Text(name, font=sans_font, font_size=28, weight=SEMIBOLD, color=TEXT_DARK)
            
            hours_label = Text(hours_str, font=sans_font, font_size=20, color=ACTION_COLOR)
            
            label_group = VGroup(name_label, hours_label).arrange(DOWN, buff=0.1)
            labels.append(label_group)

        # Position circles along a horizontal line
        # All circles should sit on the same baseline (bottom edges aligned)
        baseline_y = 0  # Arbitrary - camera positioning controls where baseline appears in frame
        
        # Position circles with tighter spacing - GEN-0 looms over neighbors
        # Custom gaps: keep OXE-pi_0 reasonable, tighten pi_0-GEN-0 and GEN-0-Rhoda
        cumulative_x = 0
        x_positions = []
        
        # Gap multipliers for each transition (smaller = tighter, negative = overlap)
        gap_multipliers = [0.8, 0.1, -0.50]  # OXE→pi_0, pi_0→GEN-0, GEN-0→Rhoda (significant overlap!)
        
        for i, radius in enumerate(radii):
            if i == 0:
                x_positions.append(cumulative_x)
            else:
                # Add spacing: previous radius + gap + current radius
                gap = max(radii[i-1], radii[i]) * gap_multipliers[i-1]
                cumulative_x += radii[i-1] + gap + radius
                x_positions.append(cumulative_x)
        
        for circle, x_pos in zip(circles, x_positions):
            # Position circle so its bottom edge is at the baseline
            circle.move_to([x_pos, baseline_y + circle.radius, 0])
        
        # Create a very long horizontal baseline (to accommodate all zoom levels)
        # Shift line down to account for both circle stroke and baseline stroke
        baseline_stroke_width = 1
        circle_stroke_width = 1
        # Total offset = half of circle stroke + half of baseline stroke
        stroke_to_world = lambda px: px / config.pixel_height * config.frame_height
        baseline_line_offset = stroke_to_world(circle_stroke_width / 2 + baseline_stroke_width / 2)
        baseline = Line(
            start=[-50, baseline_y - baseline_line_offset, 0],
            end=[50, baseline_y - baseline_line_offset, 0],
            color=MARKER_GRAY,
            stroke_width=baseline_stroke_width
        )
        
        # Base line weight for OXE (first circle)
        base_line_weight = 0.5
        base_radius = radii[0]
        
        # Create labels positioned above circles with thin solid line
        def create_label_and_line(circle, label, camera_height, circle_radius):
            """Position label above circle with connecting line based on current camera view."""
            # Scale label to be readable at current zoom
            label_scale = camera_height / 8  # Normalize to default camera height
            
            # Position label above the circle (50% closer)
            label_offset = camera_height * 0.20
            label.scale(label_scale)
            label.move_to([circle.get_center()[0], circle.get_top()[1] + label_offset, 0])
            
            # Line weight scales with circle radius (0.5 for base, proportionally larger for bigger circles)
            # Minimum weight of 0.1 to ensure visibility for tiny circles like Rhoda (doubled)
            line_weight = max(0.1, base_line_weight * (circle_radius / base_radius)) 
            # Double the weight for very small circles (Rhoda fix)
            if circle_radius < base_radius * 0.01:
                line_weight *= 2
            
            # Consistent gap on both ends (near text and near circle)
            gap = camera_height * 0.02
            
            # Create thin solid line from below label to just above circle
            connector_line = Line(
                start=[circle.get_center()[0], label.get_bottom()[1] - gap, 0],
                end=[circle.get_center()[0], circle.get_top()[1] + gap, 0],
                color=MARKER_GRAY,
                stroke_width=line_weight
            )
            return label, connector_line

        # Add baseline (always visible)
        self.add(baseline)
        
        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================
        
        # Initial camera setup: zoom in on OXE
        # Camera frame height should show OXE circle filling a good portion
        initial_frame_height = radii[0] * 4.5  # OXE appears large (25% more zoomed in)
        
        # Position camera so baseline is near BOTTOM of frame (with room for labels below)
        # Camera Y = baseline + offset puts baseline in lower portion with label space below
        camera_y_offset = 0.35  # Fraction of frame height above baseline for camera center
        
        self.camera.frame.set_height(initial_frame_height)
        self.camera.frame.move_to([x_positions[0], baseline_y + initial_frame_height * camera_y_offset, 0])
        
        # Show OXE circle
        label_0, line_0 = create_label_and_line(circles[0], labels[0], initial_frame_height, radii[0])
        self.play(
            DrawBorderThenFill(circles[0]),
            FadeIn(label_0),
            Create(line_0),
            run_time=1.5
        )
        self.wait(1)
        
        # ============================================================
        # Transition to π₀
        # ============================================================
        # Zoom out so π₀ appears at the same size OXE was initially
        # The ratio of frame heights should match the ratio of radii
        frame_height_1 = initial_frame_height * (radii[1] / radii[0])
        
        # Calculate camera center - keep baseline near bottom of frame
        camera_x_1 = x_positions[1]
        camera_y_1 = baseline_y + frame_height_1 * camera_y_offset
        
        label_1, line_1 = create_label_and_line(circles[1], labels[1], frame_height_1, radii[1])
        
        self.play(
            self.camera.frame.animate.set_height(frame_height_1).move_to([camera_x_1, camera_y_1, 0]),
            run_time=2
        )
        self.play(
            DrawBorderThenFill(circles[1]),
            FadeIn(label_1),
            Create(line_1),
            run_time=1.5
        )
        self.wait(1)
        
        # ============================================================
        # Transition to GEN-0
        # ============================================================
        # Zoom out dramatically for the huge GEN-0 circle
        frame_height_2 = initial_frame_height * (radii[2] / radii[0])
        
        camera_x_2 = x_positions[2]
        camera_y_2 = baseline_y + frame_height_2 * camera_y_offset
        
        label_2, line_2 = create_label_and_line(circles[2], labels[2], frame_height_2, radii[2])
        
        self.play(
            self.camera.frame.animate.set_height(frame_height_2).move_to([camera_x_2, camera_y_2, 0]),
            run_time=2.5
        )
        self.play(
            DrawBorderThenFill(circles[2]),
            FadeIn(label_2),
            Create(line_2),
            run_time=1.5
        )
        self.wait(1)
        
        # ============================================================
        # Transition to Rhoda - ZOOM WAY IN
        # ============================================================
        # Rhoda is tiny! Zoom in so Rhoda is visible, but GEN-0 becomes a massive arc
        # Frame height should make Rhoda appear at reasonable size (half as zoomed)
        frame_height_3 = radii[3] * 16  # Less tight zoom to show more context
        
        # Position camera centered on Rhoda's actual position
        # Use the circle's actual center (which accounts for negative gap positioning)
        rhoda_actual_center = circles[3].get_center()
        # Shift camera slightly left to catch GEN-0's arc on the left side of frame
        camera_x_3 = rhoda_actual_center[0] - frame_height_3 * 0.3
        camera_y_3 = baseline_y + frame_height_3 * camera_y_offset
        
        label_3, line_3 = create_label_and_line(circles[3], labels[3], frame_height_3, radii[3])
        
        self.play(
            self.camera.frame.animate.set_height(frame_height_3).move_to([camera_x_3, camera_y_3, 0]),
            run_time=2.5
        )
        self.play(
            DrawBorderThenFill(circles[3]),
            FadeIn(label_3),
            Create(line_3),
            run_time=1.5
        )
        self.wait(4)
        
        # ============================================================
        # FADE OUT - for looping
        # ============================================================
        # Fade out all while zooming back to initial scale and Y position (keep X position)
        # Fade takes 2 seconds, camera motion takes 4 seconds, both start together
        current_camera_x = self.camera.frame.get_center()[0]
        initial_camera_y = baseline_y + initial_frame_height * camera_y_offset
        
        self.play(
            *[FadeOut(c, run_time=2) for c in circles],
            FadeOut(label_0, run_time=2), FadeOut(label_1, run_time=2), 
            FadeOut(label_2, run_time=2), FadeOut(label_3, run_time=2),
            FadeOut(line_0, run_time=2), FadeOut(line_1, run_time=2), 
            FadeOut(line_2, run_time=2), FadeOut(line_3, run_time=2),
            self.camera.frame.animate(run_time=4).set_height(initial_frame_height).move_to([current_camera_x, initial_camera_y, 0]),
        )
        
        # Wait with just baseline visible (ready to loop)
        self.wait(2)


class DataCirclesFigureStatic(Scene):
    """Static version showing all circles at once (original version)."""
    
    def construct(self):
        # Set background
        self.camera.background_color = BG_OFFWHITE
        
        # Data: (name, hours)
        data = [
            ("OXE", 4000),
            (r"\pi_0", 10000),
            ("GEN-0", 270000),
            ("Rhoda", 100),
        ]

        scale_factor = 0.012
        
        circles = []
        labels = []
        radii = []
        
        for i, (name, hours) in enumerate(data):
            radius = math.sqrt(hours) * scale_factor
            radii.append(radius)
            circle = Circle(radius=radius)
            # Gradient fill within circle: orange → blue → white (diagonal)
            circle.set_fill(color=[RHODA_ORANGE, RHODA_BLUE, "#FFFFFF"], opacity=0.85)
            circle.set_sheen_direction(UR)  # Diagonal gradient direction
            circle.set_stroke(color=TEXT_DARK, width=2, opacity=1)  # Consistent dark border
            circles.append(circle)
            
            if hours >= 1000:
                hours_str = f"{hours // 1000}K HRS"
            else:
                hours_str = f"~{hours} HRS"
            
            # Use sans-serif font for all text
            sans_font = get_preferred_font()
            if name == r"\pi_0":
                name_label = Text("π₀", font=sans_font, font_size=36, color=TEXT_DARK)
            else:
                name_label = Text(name, font=sans_font, font_size=28, color=TEXT_DARK)
            
            hours_label = Text(hours_str, font=sans_font, font_size=20, color=ACTION_COLOR)
            
            label_group = VGroup(name_label, hours_label).arrange(DOWN, buff=0.1)
            labels.append(label_group)

        baseline_y = -3.0
        
        # Position with tighter spacing
        gap_multipliers = [0.4, 0.15, 0.08]
        cumulative_x = -5
        x_positions = []
        for i, radius in enumerate(radii):
            if i == 0:
                x_positions.append(cumulative_x)
            else:
                gap = max(radii[i-1], radii[i]) * gap_multipliers[i-1]
                cumulative_x += radii[i-1] + gap + radius
                x_positions.append(cumulative_x)
        
        for circle, x_pos in zip(circles, x_positions):
            circle.move_to([x_pos, baseline_y + circle.radius, 0])
        
        # Shift line down by half stroke width so circles sit flush on top
        baseline_stroke_width = 1
        circle_stroke_width = 1
        stroke_to_world = lambda px: px / config.pixel_height * config.frame_height
        baseline_line_offset = stroke_to_world(circle_stroke_width / 2 + baseline_stroke_width / 2)
        baseline = Line(
            start=[-10, baseline_y - baseline_line_offset, 0],
            end=[15, baseline_y - baseline_line_offset, 0],
            color=MARKER_GRAY,
            stroke_width=baseline_stroke_width
        )
        
        label_y = 3.5
        dashed_lines = []
        
        for circle, label in zip(circles, labels):
            label.move_to([circle.get_center()[0], label_y, 0])
            
            dashed_line = DashedLine(
                start=[circle.get_center()[0], label_y - 0.6, 0],
                end=[circle.get_center()[0], circle.get_top()[1] + 0.1, 0],
                color=MARKER_GRAY,
                stroke_width=1,
                dash_length=0.1
            )
            dashed_lines.append(dashed_line)

        self.add(baseline)
        
        for circle, label, dashed_line in zip(circles, labels, dashed_lines):
            self.add(circle, label, dashed_line)
        
        self.wait(2)


# Render commands:
# Animated version with camera panning:
# manim -pql data_circles_figure.py DataCirclesFigure
#
# Static version (all circles visible):
# manim -pql data_circles_figure.py DataCirclesFigureStatic