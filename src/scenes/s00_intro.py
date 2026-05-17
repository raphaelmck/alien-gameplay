from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


def _ease_out_back(t):
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

        self.set_camera_orientation(phi=65 * DEGREES, theta=-128 * DEGREES)
        self.create_and_add_board_elements()

        self.begin_ambient_camera_rotation(rate=0.06)
        self.play_first_36_moves()
        self.stop_ambient_camera_rotation()

        self.transition_to_top_down()

        # Attention field appears *before* move 37 so the viewer sees
        # where human attention was concentrated, then watches the stone
        # land in the quiet region outside those zones.
        attention = self.create_attention_field()
        caption = self.create_attention_caption()
        self.add_fixed_in_frame_mobjects(caption)
        self.play(FadeIn(attention), FadeIn(caption), run_time=2.2, rate_func=smooth)
        self.wait(1.5)

        self.play_move_37()

        annotation = self.create_move37_annotation()
        self.add_fixed_in_frame_mobjects(annotation)
        self.play(FadeIn(annotation), run_time=0.9, rate_func=smooth)
        self.wait(2.2)
        self.play(FadeOut(attention), FadeOut(caption), FadeOut(annotation), run_time=1.2)
        self.wait(0.8)

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

    # ------------------------------------------------------------------
    # Rasterised attention field
    # ------------------------------------------------------------------

    def _gaussian_field(self, W: int, H: int, zones: list) -> np.ndarray:
        """
        Build a smooth scalar field by summing Gaussians at board positions.

        zones: [(board_i, board_j, sigma_intersections, amplitude), ...]
        Returns float32 (H, W) array clipped to [0, 1].
        """
        board_extent = self.BOARD_SIZE + 0.4  # physical size including border

        field = np.zeros((H, W), dtype=np.float32)
        xs = np.arange(W, dtype=np.float32)
        ys = np.arange(H, dtype=np.float32)
        gx, gy = np.meshgrid(xs, ys)

        for ci, cj, sigma_int, amp in zones:
            # Board position in Manim world units
            bx = ci * self.SPACING - self.BOARD_SIZE / 2
            by = cj * self.SPACING - self.BOARD_SIZE / 2
            # Map to pixel space (row 0 = top of image = +y in world)
            px = (bx + board_extent / 2) / board_extent * W
            py = (board_extent / 2 - by) / board_extent * H
            # Convert sigma from board-intersection units to pixels
            sigma_px = sigma_int * self.SPACING / board_extent * W

            field += amp * np.exp(
                -((gx - px) ** 2 + (gy - py) ** 2) / (2.0 * sigma_px ** 2)
            )

        return np.clip(field, 0.0, 1.0)

    def _field_to_rgba(self, field: np.ndarray, max_alpha: float = 0.72) -> np.ndarray:
        """
        Map a [0,1] scalar field to an RGBA uint8 image.
        Color: warm amber-gold — no scientific rainbow palette.
        Alpha: field^0.60 so edges fade gracefully without a hard edge.
        """
        f = field.astype(np.float32)
        rgba = np.zeros((*f.shape, 4), dtype=np.uint8)
        rgba[..., 0] = np.clip(f * 255,      0, 255).astype(np.uint8)  # R full
        rgba[..., 1] = np.clip(f * 148,      0, 255).astype(np.uint8)  # G ~amber
        rgba[..., 2] = np.clip(f *  25,      0, 255).astype(np.uint8)  # B trace
        alpha = np.power(np.clip(f, 0, 1), 0.60) * max_alpha
        rgba[..., 3] = np.clip(alpha * 255,  0, 255).astype(np.uint8)
        return rgba

    def create_attention_field(self) -> ImageMobject:
        """
        Soft amber glow over the board regions that hold human attention
        after move 36. Move 37 at (14,9) intentionally falls outside the
        bright zones — the visual asks 'where would you have looked?'
        without claiming to be a probability distribution.

        Sigma values are in board-intersection units; the corner fights
        are broad and bright, isolated stones cast a gentler glow.
        """
        W, H = 512, 512
        zones = [
            # board_i  board_j  sigma  amplitude
            # ── Bottom-right corner cluster ──────────────────────────
            # P4 / Q3 / P3 / R4 / R6 — most moves landed here
            (15,  3,   3.8,  0.92),
            (13,  2,   3.0,  0.72),
            (15,  2,   2.2,  0.55),   # Q3 / P3 sub-cluster
            # ── Bottom-left corner cluster ───────────────────────────
            # C4 / C3 / B3 / B4 / B5 / C5 / C6 / D5 / D3 / E4 / D2 / C7
            ( 2,  4,   3.8,  0.88),
            ( 3,  3,   3.0,  0.68),
            ( 3,  2,   2.0,  0.50),   # D3 / D2 sub-cluster
            # ── Right-side tension ───────────────────────────────────
            # Q5 / R5 contest + Q11 / R14 / R15 / Q14 extensions
            (15,  4,   2.2,  0.42),   # Q5 area
            (15, 10,   2.2,  0.44),   # Q11 — last White move
            (16, 13,   2.4,  0.46),   # R14 / R15 cluster
            (15, 13,   1.8,  0.36),   # Q14
            # ── Upper-left ───────────────────────────────────────────
            ( 3, 15,   2.8,  0.50),   # C16 Black stone + influence
            ( 4, 15,   2.0,  0.34),   # E16
            ( 2, 12,   2.2,  0.34),   # C13 White extension
            # ── Upper-right ──────────────────────────────────────────
            (15, 15,   2.6,  0.44),   # Q16 Black stone
            (16, 14,   2.0,  0.34),   # R15
            # ── Isolated stones — softer halos ───────────────────────
            ( 9,  3,   2.8,  0.34),   # K4
            ( 8, 16,   2.2,  0.30),   # J17
            ( 3,  9,   2.2,  0.28),   # D10
            (13, 15,   2.0,  0.28),   # O16
        ]

        field = self._gaussian_field(W, H, zones)
        rgba  = self._field_to_rgba(field, max_alpha=0.68)

        img = ImageMobject(rgba)
        img.set_width(self.BOARD_SIZE + 0.4)
        img.move_to(ORIGIN)
        # Place between board surface (z=0) and grid lines (z=0.015)
        # so the grid and all stones render cleanly on top.
        img.shift(np.array([0.0, 0.0, 0.005]))
        return img

    def create_move37_annotation(self) -> VGroup:
        """Two-row card that appears after move 37 lands."""
        lbl_color = ManimColor("#505050")

        labels = VGroup(
            Text("Human prior",   font_size=20, color=lbl_color),
            Text("Machine value", font_size=20, color=lbl_color),
        )
        values = VGroup(
            Text("unlikely", font_size=20, color=ManimColor("#787878")),
            Text("high",     font_size=20, color=ManimColor("#D49A22")),
        )

        labels.arrange(DOWN, aligned_edge=LEFT,  buff=0.20)
        values.arrange(DOWN, aligned_edge=LEFT,  buff=0.20)
        values.next_to(labels, RIGHT, buff=0.50)

        group = VGroup(labels, values)
        group.to_edge(RIGHT, buff=0.42)
        group.set_y(0)
        return group

    def create_attention_caption(self) -> VGroup:
        amber = ManimColor("#D49A22")
        text_color = ManimColor("#585858")

        swatch = Square(side_length=0.22)
        swatch.set_fill(amber, opacity=1)
        swatch.set_stroke(width=0)

        line1 = Text("where the obvious", font_size=20, color=text_color)
        line2 = Text("fight seems to be", font_size=20, color=text_color)
        lines = VGroup(line1, line2).arrange(DOWN, aligned_edge=LEFT, buff=0.12)

        legend = VGroup(swatch, lines)
        legend.arrange(RIGHT, buff=0.20, aligned_edge=UP)

        legend.to_edge(LEFT, buff=0.50)
        legend.set_y(0)
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

        stone_anims = []
        for i, (cx, cy) in enumerate(moves):
            color = self.BLACK_STONE if (i % 2 == 0) else self.WHITE_STONE
            stone = self.create_stone(color)
            stone.move_to(self.board_to_point(cx, cy, self.STONE_Z))
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

        halo = Circle(radius=self.SPACING * 0.48, color=WHITE, stroke_width=2.5)
        halo.move_to(self.board_to_point(cx, cy, z_offset=0.03))
        self.add(halo)
        self.play(halo.animate.scale(5).set_opacity(0), run_time=2.2, rate_func=smooth)
