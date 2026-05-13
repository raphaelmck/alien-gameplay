from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


def _ease_out_back(t):
    """Slight overshoot so stones feel like they're being stamped onto the board."""
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


class Move37ColdOpen(ThreeDScene):
    def construct(self):
        self.BOARD_SIZE = 6.0
        self.SPACING = self.BOARD_SIZE / 18
        self.MOVE_37_COORD = (14, 9)

        self.BOARD_COLOR = "#C8A96E"
        self.GRID_COLOR = "#1A1A1A"
        self.BLACK_STONE = "#1A1A1A"
        self.WHITE_STONE = "#F5F5F5"
        self.STONE_Z = 0.025

        self.camera.background_color = "#000000"

        # Start at -128° so the ~38° of ambient rotation during the 36-move
        # sequence (11 s × 0.06 rad/s) lands near -90°, keeping the top-down
        # camera transition short and natural.
        self.set_camera_orientation(phi=65 * DEGREES, theta=-128 * DEGREES)
        self.create_and_add_board_elements()

        self.begin_ambient_camera_rotation(rate=0.06)
        self.play_first_36_moves()
        self.stop_ambient_camera_rotation()

        self.transition_to_top_down()
        self.play_move_37()

        # Heatmap reveals after move 37 lands — "here's where everyone was looking."
        heatmap = self.create_heatmap()
        legend = self.create_legend()
        self.add_fixed_in_frame_mobjects(legend)
        self.play(FadeIn(heatmap), FadeIn(legend), run_time=2.2, rate_func=smooth)
        self.wait(2.5)
        self.play(FadeOut(heatmap), FadeOut(legend), run_time=1.2)
        self.wait(1.0)

    # ==========================================
    # HELPERS
    # ==========================================

    def board_to_point(self, i, j, z_offset=0.0):
        x = i * self.SPACING - self.BOARD_SIZE / 2
        y = j * self.SPACING - self.BOARD_SIZE / 2
        return np.array([x, y, z_offset])

    def create_and_add_board_elements(self):
        support = self.create_support()
        board = self.create_board()
        grid_lines = self.create_grid_lines()
        star_points = self.create_star_points()

        self.play(GrowFromCenter(board), FadeIn(support), run_time=2.0, rate_func=smooth)
        # Grid crystallises from the centre outward.
        self.play(
            LaggedStart(*[GrowFromCenter(l) for l in grid_lines], lag_ratio=0.03),
            run_time=2.5,
        )
        self.play(
            LaggedStart(*[GrowFromCenter(sp) for sp in star_points], lag_ratio=0.06),
            run_time=0.8,
        )
        self.board_surface = board
        self.board_support = support

    def create_board(self):
        board = Square(side_length=self.BOARD_SIZE + 0.4)
        board.set_fill(self.BOARD_COLOR, opacity=1)
        board.set_stroke(width=0)
        return board

    def create_support(self):
        support = Cube(stroke_width=0)
        support.set_fill(BLACK, opacity=1)
        support.set_stroke(width=0)
        w = self.BOARD_SIZE - 2.5
        support.scale(np.array([w, w, 0.28]))
        support.shift(np.array([0.0, 0.0, -0.38]))
        return support

    def create_grid_lines(self):
        z = 0.015
        indices = sorted(range(19), key=lambda k: abs(k - 9))
        lines = []
        for i in indices:
            lines.append(Line(
                self.board_to_point(i, 0, z), self.board_to_point(i, 18, z),
                color=self.GRID_COLOR, stroke_width=1.5,
            ))
            lines.append(Line(
                self.board_to_point(0, i, z), self.board_to_point(18, i, z),
                color=self.GRID_COLOR, stroke_width=1.5,
            ))
        return lines

    def create_star_points(self):
        z = 0.02
        return [
            Dot(self.board_to_point(i, j, z), radius=0.055, color=self.GRID_COLOR)
            for i in [3, 9, 15] for j in [3, 9, 15]
        ]

    def create_stone(self, color):
        r = self.SPACING * 0.46
        stone = Circle(radius=r)
        stroke_col = "#C0C0C0" if color == self.WHITE_STONE else "#2A2A2A"
        stone.set_fill(color, opacity=1)
        stone.set_stroke(color=stroke_col, width=0.8)
        return stone

    def create_heatmap(self):
        heatmap = VGroup()
        # z=0.002: above the board surface, below the grid (0.015) and stones (0.025)
        # so it reads as a background glow layer, not floating over pieces.
        z = 0.002
        # (cx, cy, max_radius, peak_opacity, hex_color)
        # Concentrated on the corner fights active after move 36;
        # intentionally absent near P10 (move 37) to emphasise the surprise.
        zones = [
            # Bottom-right corner cluster  (P4 / Q3 / R4 fights)
            (15,  3, 1.40, 0.58, "#FF2200"),
            (13,  2, 1.00, 0.42, "#FF4400"),
            # Bottom-left corner cluster   (C4 / C6 / B4 / B5 fights)
            ( 2,  4, 1.30, 0.54, "#FF2200"),
            ( 3,  3, 0.90, 0.36, "#FF5522"),
            # Right side near Q11 / R14    (White just extended here)
            (15, 10, 1.10, 0.42, "#FF6600"),
            (16, 13, 0.75, 0.30, "#FF8800"),
            # Top-left area                (C16 Black influence)
            ( 3, 15, 0.85, 0.32, "#FFAA00"),
            ( 4, 14, 0.60, 0.22, "#FFBB22"),
            # Top-right area               (Q16 / R15 influence)
            (15, 15, 0.80, 0.25, "#FFAA00"),
            (16, 14, 0.55, 0.18, "#FFBB44"),
        ]
        n_rings = 28
        for cx, cy, max_r, peak_op, color in zones:
            cp = self.board_to_point(cx, cy, z_offset=z)
            radii = np.linspace(0.03, max_r, n_rings)
            # Gaussian decay: full brightness at centre, zero at the edge.
            opacities = peak_op * np.exp(-4.5 * (radii / max_r) ** 2)
            for r, op in zip(radii, opacities):
                blob = Circle(radius=r, stroke_width=0, fill_color=color, fill_opacity=op)
                blob.move_to(cp)
                heatmap.add(blob)
        return heatmap

    def create_legend(self):
        """Small fixed-frame legend: gradient bar + labels."""
        stops = ["#3A7BD5", "#7FB3D3", "#FFD700", "#FF6B35", "#FF2200"]
        n_segs, seg_w, seg_h = 45, 0.050, 0.14
        bar = VGroup()
        for i in range(n_segs):
            t = i / (n_segs - 1)
            f = t * (len(stops) - 1)
            lo = ManimColor(stops[int(f)])
            hi = ManimColor(stops[min(int(f) + 1, len(stops) - 1)])
            col = interpolate_color(lo, hi, f - int(f))
            seg = Rectangle(width=seg_w, height=seg_h,
                            fill_color=col, fill_opacity=0.90, stroke_width=0)
            seg.shift(RIGHT * i * seg_w)
            bar.add(seg)
        bar.center()

        title = Text(
            "Expected move probability  (before move 37)",
            font_size=12, color=ManimColor("#AAAAAA"),
        )
        title.next_to(bar, UP, buff=0.11)
        low_lbl  = Text("low",  font_size=10, color=ManimColor("#777777"))
        high_lbl = Text("high", font_size=10, color=ManimColor("#777777"))
        low_lbl.next_to(bar,  LEFT,  buff=0.09)
        high_lbl.next_to(bar, RIGHT, buff=0.09)

        legend = VGroup(title, bar, low_lbl, high_lbl)
        legend.to_corner(DR, buff=0.35)
        return legend

    # ==========================================
    # ANIMATION SEQUENCES
    # ==========================================

    def play_first_36_moves(self):
        moves = [
            # Moves 1–7:   Q16 D4 C16 R4 P4 P3 O3
            (15, 15), (3, 3),   (2, 15),  (16, 3),  (14, 3),  (14, 2),  (13, 2),
            # Moves 8–14:  Q3 C6 F3 N4 R6 J17 D10
            (15, 2),  (2, 5),   (5, 2),   (12, 3),  (16, 5),  (8, 16),  (3, 9),
            # Moves 15–21: Q5 R5 C4 C3 B3 C5 B4
            (15, 4),  (16, 4),  (2, 3),   (2, 2),   (1, 2),   (2, 4),   (1, 3),
            # Moves 22–28: B5 D5 B6 D3 E4 D2 C7
            (1, 4),   (3, 4),   (1, 5),   (3, 2),   (4, 3),   (3, 1),   (2, 6),
            # Moves 29–36: K4 C13 E16 R14 R15 Q14 O16 Q11
            (9, 3),   (2, 12),  (4, 15),  (16, 13), (16, 14), (15, 13), (13, 15), (15, 10),
        ]

        # All stones placed at their final positions first; one single play()
        # call keeps the ambient camera rotation completely uninterrupted.
        # _ease_out_back gives a confident "stamp" feel — each stone grows to
        # ~107 % then snaps back, like it's being pressed onto the board.
        stone_anims = []
        for i, (cx, cy) in enumerate(moves):
            color = self.BLACK_STONE if (i % 2 == 0) else self.WHITE_STONE
            stone = self.create_stone(color)
            stone.move_to(self.board_to_point(cx, cy, self.STONE_Z))
            self.add(stone)
            stone_anims.append(GrowFromCenter(stone, rate_func=_ease_out_back))

        self.play(
            LaggedStart(*stone_anims, lag_ratio=0.07),
            run_time=11.0,
            rate_func=linear,
        )

    def transition_to_top_down(self):
        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=4.5, rate_func=smooth)

    def play_move_37(self):
        cx, cy = self.MOVE_37_COORD
        dest = self.board_to_point(cx, cy, self.STONE_Z)
        move37 = self.create_stone(self.BLACK_STONE)
        move37.move_to(np.array([dest[0], dest[1], self.STONE_Z + 1.8]))
        self.add(move37)
        self.play(move37.animate.move_to(dest), run_time=1.6, rate_func=ease_out_quad)

        halo = Circle(radius=self.SPACING * 0.48, color=WHITE, stroke_width=3)
        halo.move_to(self.board_to_point(cx, cy, z_offset=0.03))
        self.add(halo)
        self.play(halo.animate.scale(4).set_opacity(0), run_time=1.8, rate_func=ease_out_quad)
