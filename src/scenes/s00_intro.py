from manim import *
from manim.utils.rate_functions import ease_in_out_sine, ease_out_quad
import numpy as np


class Move37ColdOpen(ThreeDScene):
    def construct(self):
        self.BOARD_SIZE = 6.0
        self.SPACING = self.BOARD_SIZE / 18
        self.MOVE_37_COORD = (14, 9)

        # Grayscale palette
        self.BOARD_COLOR = "#F0F0EC"
        self.SUPPORT_COLOR = "#C0C0C0"
        self.GRID_COLOR = "#1A1A1A"
        self.BLACK_STONE = "#222222"
        self.WHITE_STONE = "#EFEFEF"

        self.set_camera_orientation(phi=65 * DEGREES, theta=45 * DEGREES)
        self.create_and_add_board_elements()

        self.begin_ambient_camera_rotation(rate=0.12)
        self.play_first_36_moves()
        self.stop_ambient_camera_rotation()

        self.transition_to_top_down()

        heatmap = self.create_heatmap()
        self.play(FadeIn(heatmap), run_time=3, rate_func=smooth)
        self.wait(1)

        self.play_move_37()
        self.play(FadeOut(heatmap), run_time=1)

        self.show_labels_and_zoom()

    # ==========================================
    # HELPERS
    # ==========================================

    def board_to_point(self, i, j, z_offset=0.0):
        x = i * self.SPACING - self.BOARD_SIZE / 2
        y = j * self.SPACING - self.BOARD_SIZE / 2
        return np.array([x, y, z_offset])

    def create_and_add_board_elements(self):
        self.board = self.create_board()
        self.support = self.create_support()
        self.grid = self.create_grid()
        self.star_points = self.create_star_points()

        self.add(self.support, self.board, self.grid, self.star_points)
        self.play(
            FadeIn(self.board),
            FadeIn(self.support),
            Create(self.grid),
            FadeIn(self.star_points),
            run_time=2,
        )

    def create_board(self):
        board = Cube(stroke_width=0)
        board.set_fill(self.BOARD_COLOR, opacity=1)
        board.set_stroke(width=0)
        board.scale(np.array([self.BOARD_SIZE + 0.4, self.BOARD_SIZE + 0.4, 0.3]))
        board.shift(DOWN * 0.15)
        return board

    def create_support(self):
        support = Cube(stroke_width=0)
        # Explicit fill + a thin matching stroke so the cube reads as a solid block
        support.set_fill(self.SUPPORT_COLOR, opacity=1)
        support.set_stroke(color=self.SUPPORT_COLOR, width=1.5, opacity=1)
        support.scale(np.array([self.BOARD_SIZE - 0.5, self.BOARD_SIZE - 0.5, 0.8]))
        support.shift(DOWN * 0.7)
        return support

    def create_grid(self):
        grid = VGroup()
        z_level = 0.01
        for i in range(19):
            start_v = self.board_to_point(i, 0, z_offset=z_level)
            end_v = self.board_to_point(i, 18, z_offset=z_level)
            grid.add(Line(start_v, end_v, color=self.GRID_COLOR, stroke_width=1.5))
            start_h = self.board_to_point(0, i, z_offset=z_level)
            end_h = self.board_to_point(18, i, z_offset=z_level)
            grid.add(Line(start_h, end_h, color=self.GRID_COLOR, stroke_width=1.5))
        return grid

    def create_star_points(self):
        stars = VGroup()
        z_level = 0.015
        for i in [3, 9, 15]:
            for j in [3, 9, 15]:
                pos = self.board_to_point(i, j, z_offset=z_level)
                stars.add(Dot(pos, radius=0.055, color=self.GRID_COLOR))
        return stars

    def create_stone(self, color):
        stone_radius = self.SPACING * 0.46
        stone = Sphere(radius=stone_radius, resolution=(14, 14))
        stone.set_fill(color, opacity=1)
        stone.set_stroke(width=0)
        stone.scale(np.array([1, 1, 0.38]))
        # Shift up so the bottom face sits exactly on the board surface
        stone.shift(OUT * (stone_radius * 0.38 + 0.025))
        return stone

    def create_heatmap(self):
        heatmap = VGroup()
        # Grayscale clusters showing human-predicted areas
        centers = [
            (15, 3, 1.5, "#909090"),
            (3, 15, 0.8, "#A8A8A8"),
            (15, 15, 0.5, "#B8B8B8"),
        ]
        z_level = 0.02
        for cx, cy, radius, color in centers:
            center_pos = self.board_to_point(cx, cy, z_offset=z_level)
            for r in np.linspace(0.2, radius, 6):
                ring = Circle(radius=r, stroke_width=0, fill_color=color, fill_opacity=0.07)
                ring.move_to(center_pos)
                heatmap.add(ring)
        return heatmap

    def create_text_labels(self):
        labels = VGroup()
        words = ["too early?", "too far?", "mistake?", "brilliant?"]
        positions = [(8, 14), (3, 8), (11, 4), (16, 12)]
        z_level = 0.1
        for word, (cx, cy) in zip(words, positions):
            pos = self.board_to_point(cx, cy, z_offset=z_level)
            lbl = Text(word, font_size=22, color=WHITE).move_to(pos)
            labels.add(lbl)
        return labels

    # ==========================================
    # ANIMATION SEQUENCES
    # ==========================================

    def play_first_36_moves(self):
        moves = [
            (15, 3),  (3, 15),  (15, 15), (3, 3),   (14, 2),  (16, 4),  (2, 14),
            (15, 2),  (16, 2),  (14, 3),  (16, 3),  (14, 4),  (15, 4),  (13, 2),
            (16, 1),  (17, 2),  (15, 5),  (16, 5),  (17, 4),  (12, 3),  (2, 15),
            (4, 15),  (3, 16),  (3, 14),  (4, 14),  (2, 13),  (9, 3),   (15, 9),
            (3, 9),   (9, 15),  (10, 3),  (16, 14), (14, 15), (15, 13), (2, 16), (4, 16),
        ]

        for i, (cx, cy) in enumerate(moves):
            color = self.BLACK_STONE if (i % 2 == 0) else self.WHITE_STONE
            stone = self.create_stone(color)

            target_pos = self.board_to_point(cx, cy)
            final_z = stone.get_center()[2]
            drop_z = final_z + 0.9

            # Place stone above the board then animate it dropping — no opacity tricks
            stone.move_to(np.array([target_pos[0], target_pos[1], drop_z]))
            self.add(stone)

            rt = max(0.12, 0.36 - i * 0.006)
            self.play(
                stone.animate.move_to(np.array([target_pos[0], target_pos[1], final_z])),
                run_time=rt,
                rate_func=ease_out_quad,
            )

    def transition_to_top_down(self):
        self.move_camera(phi=0, theta=-90 * DEGREES, run_time=5, rate_func=smooth)

    def play_move_37(self):
        cx, cy = self.MOVE_37_COORD
        move37 = self.create_stone(self.BLACK_STONE)
        target_pos = self.board_to_point(cx, cy)
        final_z = move37.get_center()[2]

        move37.move_to(np.array([target_pos[0], target_pos[1], final_z + 1.8]))
        self.add(move37)
        self.play(
            move37.animate.move_to(np.array([target_pos[0], target_pos[1], final_z])),
            run_time=1.8,
            rate_func=ease_out_quad,
        )

        halo = Circle(radius=self.SPACING * 0.48, color=WHITE, stroke_width=4)
        halo.move_to(self.board_to_point(cx, cy, z_offset=0.03))
        self.add(halo)
        self.play(
            halo.animate.scale(5).set_opacity(0),
            run_time=2,
            rate_func=ease_out_quad,
        )

    def show_labels_and_zoom(self):
        labels = self.create_text_labels()
        self.play(FadeIn(labels, shift=UP * 0.2), run_time=1.5)
        self.play(
            LaggedStart(
                *[Indicate(lbl, color=WHITE, scale_factor=1.15) for lbl in labels],
                lag_ratio=0.2,
            ),
            run_time=2.5,
        )
        move_37_pos = self.board_to_point(*self.MOVE_37_COORD, z_offset=0)
        self.move_camera(
            focal_point=move_37_pos,
            zoom=2.5,
            run_time=5,
            rate_func=smooth,
        )
        self.wait(1)
