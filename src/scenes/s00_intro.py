from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


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

        self.set_camera_orientation(phi=65 * DEGREES, theta=45 * DEGREES)
        self.create_and_add_board_elements()

        self.begin_ambient_camera_rotation(rate=0.06)
        self.play_first_36_moves()
        self.stop_ambient_camera_rotation()

        self.transition_to_top_down()

        heatmap = self.create_heatmap()
        self.play(FadeIn(heatmap), run_time=1.5, rate_func=smooth)

        self.play_move_37()
        self.play(FadeOut(heatmap), run_time=1)

        self.wait(2.0)

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

        self.play(
            GrowFromCenter(board),
            FadeIn(support),
            run_time=2.0,
            rate_func=smooth,
        )
        # Grid lines grow from the centre of the board outward
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
        # Interleave H and V lines sorted from the centre outward so the
        # grid appears to crystallise from the middle of the board.
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
            for i in [3, 9, 15]
            for j in [3, 9, 15]
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
        z = 0.022
        # (cx, cy, max_radius, peak_opacity, hex_color)
        # Zones the model expected to be likely after move 36 —
        # deliberately NOT near P10 to set up the surprise.
        zones = [
            (15, 3,  1.0, 0.45, "#FF4500"),  # bottom-right corner cluster
            (14, 2,  0.7, 0.30, "#FF6B35"),
            (3,  4,  0.9, 0.35, "#FF6B00"),  # bottom-left cluster
            (2,  5,  0.6, 0.25, "#FF8C00"),
            (3,  15, 0.7, 0.22, "#FFA500"),  # top-left
            (15, 15, 0.6, 0.18, "#FFB347"),  # top-right
            (16, 9,  0.5, 0.12, "#4A90D9"),  # right-side extension
        ]
        for cx, cy, max_r, peak_op, color in zones:
            cp = self.board_to_point(cx, cy, z_offset=z)
            radii = np.linspace(0.05, max_r, 12)
            # Gaussian falloff so blobs look soft
            opacities = peak_op * np.exp(-3.5 * (radii / max_r) ** 2)
            for r, op in zip(radii, opacities):
                blob = Circle(radius=r, stroke_width=0, fill_color=color, fill_opacity=op)
                blob.move_to(cp)
                heatmap.add(blob)
        return heatmap

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

        # Place all stones at their final positions first, then grow them
        # in sequence with a single play() call so the ambient camera
        # rotation runs completely uninterrupted.
        stone_anims = []
        for i, (cx, cy) in enumerate(moves):
            color = self.BLACK_STONE if (i % 2 == 0) else self.WHITE_STONE
            stone = self.create_stone(color)
            stone.move_to(self.board_to_point(cx, cy, self.STONE_Z))
            self.add(stone)
            stone_anims.append(GrowFromCenter(stone))

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
        self.play(
            move37.animate.move_to(dest),
            run_time=1.6,
            rate_func=ease_out_quad,
        )

        halo = Circle(radius=self.SPACING * 0.48, color=WHITE, stroke_width=3)
        halo.move_to(self.board_to_point(cx, cy, z_offset=0.03))
        self.add(halo)
        self.play(
            halo.animate.scale(4).set_opacity(0),
            run_time=1.8,
            rate_func=ease_out_quad,
        )
