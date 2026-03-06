"""
Data Circles Figure - Visualization of training data hours

Shows circles with areas proportional to hours of training data.
Uses camera panning/zooming to reveal each circle at the same apparent size.
"""

from manim import *
import math

# Configure 2:1 aspect ratio
config.pixel_width = 1920
config.pixel_height = 960
config.frame_width = 16
config.frame_height = 8


class DataCirclesFigure(MovingCameraScene):
    def construct(self):
        # Data: (name, hours)
        data = [
            ("OXE", 4000),
            (r"\pi_0", 10000),
            ("GEN-0", 270000),
            ("Rhoda", 10),
        ]

        # Calculate radii proportional to sqrt(hours) for area scaling
        # Scale factor to make circles reasonably sized on screen (2x larger)
        scale_factor = 0.012
        
        circles = []
        labels = []
        radii = []
        
        for name, hours in data:
            radius = math.sqrt(hours) * scale_factor
            radii.append(radius)
            circle = Circle(radius=radius)
            circle.set_fill(WHITE, opacity=0.8)
            circle.set_stroke(WHITE, width=2)
            circles.append(circle)
            
            # Create label with name and hours
            if hours >= 1000:
                hours_str = f"{hours // 1000}K HRS"
            else:
                hours_str = f"~{hours} HRS"
            
            # Use MathTex for pi_0, Text for others
            if name == r"\pi_0":
                name_label = MathTex(name, font_size=36)
            else:
                name_label = Text(name, font_size=28)
            
            hours_label = Text(hours_str, font_size=20)
            
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
        gap_multipliers = [0.4, 0.1, -0.70]  # OXE→pi_0, pi_0→GEN-0, GEN-0→Rhoda (significant overlap!)
        
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
        baseline = Line(
            start=[-50, baseline_y, 0],
            end=[50, baseline_y, 0],
            color=WHITE,
            stroke_width=1
        )
        
        # Create labels and dashed lines for each circle
        # These will be created dynamically as we reveal each circle
        def create_label_and_line(circle, label, camera_height):
            """Position label and create dashed line based on current camera view."""
            # Scale label to be readable at current zoom
            label_scale = camera_height / 8  # Normalize to default camera height
            
            # Position label above the circle, within camera frame
            label_offset = camera_height * 0.35
            label.scale(label_scale)
            label.move_to([circle.get_center()[0], circle.get_top()[1] + label_offset, 0])
            
            # Create dashed line from label to circle
            dashed_line = DashedLine(
                start=[circle.get_center()[0], label.get_bottom()[1] - 0.05 * label_scale, 0],
                end=[circle.get_center()[0], circle.get_top()[1] + 0.05 * label_scale, 0],
                color=WHITE,
                stroke_width=1,
                dash_length=0.1 * label_scale
            )
            return label, dashed_line

        # Add baseline (always visible)
        self.add(baseline)
        
        # ============================================================
        # ANIMATION SEQUENCE
        # ============================================================
        
        # Initial camera setup: zoom in on OXE
        # Camera frame height should show OXE circle filling a good portion
        initial_frame_height = radii[0] * 6  # OXE appears large
        
        # Position camera so baseline is near BOTTOM of frame
        # Camera Y = baseline + 40% of frame height puts baseline near bottom
        camera_y_offset = 0.35  # Fraction of frame height above baseline for camera center
        
        self.camera.frame.set_height(initial_frame_height)
        self.camera.frame.move_to([x_positions[0], baseline_y + initial_frame_height * camera_y_offset, 0])
        
        # Show OXE circle
        label_0, dashed_0 = create_label_and_line(circles[0], labels[0], initial_frame_height)
        self.play(
            Create(circles[0]),
            FadeIn(label_0),
            Create(dashed_0),
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
        
        label_1, dashed_1 = create_label_and_line(circles[1], labels[1], frame_height_1)
        
        self.play(
            self.camera.frame.animate.set_height(frame_height_1).move_to([camera_x_1, camera_y_1, 0]),
            run_time=2
        )
        self.play(
            Create(circles[1]),
            FadeIn(label_1),
            Create(dashed_1),
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
        
        label_2, dashed_2 = create_label_and_line(circles[2], labels[2], frame_height_2)
        
        self.play(
            self.camera.frame.animate.set_height(frame_height_2).move_to([camera_x_2, camera_y_2, 0]),
            run_time=2.5
        )
        self.play(
            Create(circles[2]),
            FadeIn(label_2),
            Create(dashed_2),
            run_time=1.5
        )
        self.wait(1)
        
        # ============================================================
        # Transition to Rhoda - ZOOM WAY IN
        # ============================================================
        # Rhoda is tiny! Zoom in so Rhoda is visible, but GEN-0 becomes a massive arc
        # Frame height should make Rhoda appear at reasonable size
        frame_height_3 = radii[3] * 8  # Zoom in tight on Rhoda
        
        # Position camera centered on Rhoda's actual position
        # Use the circle's actual center (which accounts for negative gap positioning)
        rhoda_actual_center = circles[3].get_center()
        # Shift camera slightly left to catch GEN-0's arc on the left side of frame
        camera_x_3 = rhoda_actual_center[0] - frame_height_3 * 0.3
        camera_y_3 = baseline_y + frame_height_3 * camera_y_offset
        
        label_3, dashed_3 = create_label_and_line(circles[3], labels[3], frame_height_3)
        
        self.play(
            self.camera.frame.animate.set_height(frame_height_3).move_to([camera_x_3, camera_y_3, 0]),
            run_time=2.5
        )
        self.play(
            Create(circles[3]),
            FadeIn(label_3),
            Create(dashed_3),
            run_time=1.5
        )
        self.wait(2)


class DataCirclesFigureStatic(Scene):
    """Static version showing all circles at once (original version)."""
    
    def construct(self):
        # Data: (name, hours)
        data = [
            ("OXE", 4000),
            (r"\pi_0", 10000),
            ("GEN-0", 270000),
            ("Rhoda", 10),
        ]

        scale_factor = 0.012
        
        circles = []
        labels = []
        radii = []
        
        for name, hours in data:
            radius = math.sqrt(hours) * scale_factor
            radii.append(radius)
            circle = Circle(radius=radius)
            circle.set_fill(WHITE, opacity=0.8)
            circle.set_stroke(WHITE, width=2)
            circles.append(circle)
            
            if hours >= 1000:
                hours_str = f"{hours // 1000}K HRS"
            else:
                hours_str = f"~{hours} HRS"
            
            if name == r"\pi_0":
                name_label = MathTex(name, font_size=36)
            else:
                name_label = Text(name, font_size=28)
            
            hours_label = Text(hours_str, font_size=20)
            
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
        
        baseline = Line(
            start=[-10, baseline_y, 0],
            end=[15, baseline_y, 0],
            color=WHITE,
            stroke_width=1
        )
        
        label_y = 3.5
        dashed_lines = []
        
        for circle, label in zip(circles, labels):
            label.move_to([circle.get_center()[0], label_y, 0])
            
            dashed_line = DashedLine(
                start=[circle.get_center()[0], label_y - 0.6, 0],
                end=[circle.get_center()[0], circle.get_top()[1] + 0.1, 0],
                color=WHITE,
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