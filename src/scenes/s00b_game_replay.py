from manim import *
import numpy as np


def _ease_out_back(t):
    c1 = 1.70158
    c3 = c1 + 1
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2


class Move37GameReplay(ThreeDScene):
    """Picks up from the end of Move37ColdOpen and replays the rest of the game."""

    def construct(self):
        self.BOARD_SIZE = 6.0
        self.SPACING = self.BOARD_SIZE / 18
        self.BOARD_COLOR = "#C8A96E"
        self.GRID_COLOR = "#1A1A1A"
        self.BLACK_STONE = "#1A1A1A"
        self.WHITE_STONE = "#F5F5F5"
        self.STONE_Z = 0.025

        self.camera.background_color = "#000000"
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

        self._build_static_board()
        self._play_remaining_moves()

    # ------------------------------------------------------------------

    def board_to_point(self, i, j, z_offset=0.0):
        x = i * self.SPACING - self.BOARD_SIZE / 2
        y = j * self.SPACING - self.BOARD_SIZE / 2
        return np.array([x, y, z_offset])

    def create_stone(self, color):
        r = self.SPACING * 0.46
        stone = Circle(radius=r)
        stroke_col = "#C0C0C0" if color == self.WHITE_STONE else "#2A2A2A"
        stone.set_fill(color, opacity=1)
        stone.set_stroke(color=stroke_col, width=0.8)
        return stone

    # ------------------------------------------------------------------

    def _build_static_board(self):
        board = Square(side_length=self.BOARD_SIZE + 0.4)
        board.set_fill(self.BOARD_COLOR, opacity=1)
        board.set_stroke(width=0)

        support = Cube(stroke_width=0)
        support.set_fill(BLACK, opacity=1)
        support.set_stroke(width=0)
        w = self.BOARD_SIZE - 2.5
        support.scale(np.array([w, w, 0.28]))
        support.shift(np.array([0.0, 0.0, -0.38]))

        z = 0.015
        grid_lines = []
        for i in range(19):
            grid_lines.append(Line(
                self.board_to_point(i, 0, z), self.board_to_point(i, 18, z),
                color=self.GRID_COLOR, stroke_width=1.5,
            ))
            grid_lines.append(Line(
                self.board_to_point(0, i, z), self.board_to_point(18, i, z),
                color=self.GRID_COLOR, stroke_width=1.5,
            ))

        star_points = [
            Dot(self.board_to_point(i, j, 0.02), radius=0.055, color=self.GRID_COLOR)
            for i in [3, 9, 15] for j in [3, 9, 15]
        ]

        self.add(support, board, *grid_lines, *star_points)

        # Moves 1–37 placed statically (same sequence as Move37ColdOpen)
        moves_1_37 = [
            # 1–7
            (15, 15), ( 3,  3), ( 2, 15), (16,  3), (14,  3), (14,  2), (13,  2),
            # 8–14
            (15,  2), ( 2,  5), ( 5,  2), (12,  3), (16,  5), ( 8, 16), ( 3,  9),
            # 15–21
            (15,  4), (16,  4), ( 2,  3), ( 2,  2), ( 1,  2), ( 2,  4), ( 1,  3),
            # 22–28
            ( 1,  4), ( 3,  4), ( 1,  5), ( 3,  2), ( 4,  3), ( 3,  1), ( 2,  6),
            # 29–36
            ( 9,  3), ( 2, 12), ( 4, 15), (16, 13), (16, 14), (15, 13), (13, 15), (15, 10),
            # 37: move 37 (Black, AlphaGo's famous play)
            (14,  9),
        ]

        for idx, (cx, cy) in enumerate(moves_1_37):
            color = self.BLACK_STONE if (idx % 2 == 0) else self.WHITE_STONE
            stone = self.create_stone(color)
            stone.move_to(self.board_to_point(cx, cy, self.STONE_Z))
            self.add(stone)

    # ------------------------------------------------------------------

    def _play_remaining_moves(self):
        # Moves 38–211.
        # SGF → Manim: col letter a–s maps directly (a=0…s=18);
        # row letter flips (a=top=18 … s=bottom=0).  Move 38 is White.
        remaining = [
            # 38–44:  W B W B W B W
            (14, 10), (13,  9), (12, 11), ( 6,  3), ( 6,  2), ( 3,  5), ( 3,  6),
            # 45–51:  B W B W B W B
            ( 5,  4), ( 7,  3), ( 7,  4), ( 4,  4), ( 4,  5), ( 5,  5), ( 4,  6),
            # 52–58:  W B W B W B W
            ( 4,  7), ( 5,  6), ( 6,  5), ( 5,  7), ( 6,  4), ( 4,  8), ( 3,  8),
            # 59–65:  B W B W B W B
            ( 3,  7), ( 2,  7), ( 4, 11), ( 3, 10), (15,  9), (16, 10), (17, 13),
            # 66–72:  W B W B W B W
            (17, 12), (10, 15), ( 7,  5), (14,  6), (17, 14), (17, 15), (18, 13),
            # 73–79:  B W B W B W B
            ( 5, 10), ( 6,  8), ( 7,  6), ( 8,  5), ( 7,  7), (10,  4), (10,  3),
            # 80–86:  W B W B W B W
            ( 6, 16), ( 3, 13), ( 8, 15), ( 9, 16), ( 6, 14), ( 3, 12), ( 2, 13),
            # 87–93:  B W B W B W B
            ( 2, 11), ( 1, 11), ( 3, 11), ( 1, 10), ( 7, 15), ( 7, 14), ( 6, 15),
            # 94–100: W B W B W B W
            ( 5, 15), ( 7, 16), ( 5, 14), ( 4, 16), ( 6, 11), ( 5, 16), ( 6, 10),
            # 101–107: B W B W B W B
            ( 8, 10), ( 7,  8), ( 8,  8), ( 8,  7), ( 8,  6), ( 8,  9), ( 9,  7),
            # 108–114: W B W B W B W
            ( 9,  9), ( 8, 13), (10,  6), (10,  7), (11,  9), (11,  8), (11,  4),
            # 115–121: B W B W B W B
            (11, 10), (10,  9), ( 2, 10), ( 2,  9), (12,  9), (13,  1), (12,  1),
            # 122–128: W B W B W B W
            (11,  2), (11,  3), (12,  2), (13,  3), (11,  1), (11,  6), (10, 11),
            # 129–135: B W B W B W B
            ( 7, 12), (16, 16), (16, 15), (17, 16), (15, 16), (18, 15), ( 6, 12),
            # 136–142: W B W B W B W
            ( 2, 14), ( 1, 15), (16, 17), ( 7, 10), ( 9, 12), ( 7,  9), (14, 17),
            # 143–149: B W B W B W B
            (15, 17), (15, 18), (13, 17), ( 3, 14), ( 4, 14), ( 6,  9), ( 7, 11),
            # 150–156: W B W B W B W
            ( 4,  9), (13, 13), (12, 13), (12, 14), (17,  8), ( 5, 11), ( 4,  7),
            # 157–163: B W B W B W B
            (13, 11), (13, 12), (11, 12), (11, 11), (12, 12), (14, 12), (10, 12),
            # 164–170: W B W B W B W
            (13, 10), ( 9, 11), (13, 18), (10, 10), (12, 10), ( 9, 10), (13, 16),
            # 171–177: B W B W B W B
            (12, 17), (14, 15), (12, 16), (14, 16), (10,  1), (12,  0), ( 8,  4),
            # 178–184: W B W B W B W
            ( 8,  3), ( 9,  4), ( 9,  5), ( 8,  1), ( 7,  1), (16,  7), (17,  7),
            # 185–191: B W B W B W B
            (16,  6), (17,  6), (11,  5), (10,  5), ( 0,  4), ( 1,  6), (12,  4),
            # 192–198: W B W B W B W
            ( 1, 14), ( 0, 14), ( 0, 13), ( 0, 15), (12, 18), (11, 18), (14, 18),
            # 199–205: B W B W B W B
            ( 3, 15), ( 1, 12), (11, 17), (15,  5), (14,  5), ( 4,  1), ( 2,  1),
            # 206–211: W B W B W B
            ( 5,  3), ( 8,  2), ( 7,  2), (16,  9), (17,  9), (10,  0),
        ]

        stone_anims = []
        for idx, (cx, cy) in enumerate(remaining):
            # idx=0 → move 38 (White); parity flips each move
            color = self.WHITE_STONE if (idx % 2 == 0) else self.BLACK_STONE
            stone = self.create_stone(color)
            stone.move_to(self.board_to_point(cx, cy, self.STONE_Z))
            stone_anims.append(GrowFromCenter(stone, rate_func=_ease_out_back))

        self.play(
            LaggedStart(*stone_anims, lag_ratio=0.045),
            run_time=18.0,
            rate_func=linear,
        )
        self.wait(1.5)

        bg, text = self._create_result_card()
        self.add_fixed_in_frame_mobjects(bg)
        self.play(FadeIn(bg), run_time=0.6, rate_func=smooth)
        self.add_fixed_in_frame_mobjects(text)
        self.play(Write(text), run_time=1.2, rate_func=smooth)
        self.wait(3.0)

    def _create_result_card(self):
        line1 = Tex(r"\textbf{Black wins by resignation}", font_size=36, color=ManimColor("#E8E8E8"))
        line2 = Tex("211 moves", font_size=22, color=ManimColor("#BBBBBB"))
        text = VGroup(line1, line2).arrange(DOWN, aligned_edge=ORIGIN, buff=0.22)
        text.move_to(ORIGIN)

        pad_x, pad_y = 0.5, 0.32
        bg = Rectangle(
            width=text.width + pad_x * 2,
            height=text.height + pad_y * 2,
        )
        bg.set_fill(BLACK, opacity=0.72)
        bg.set_stroke(width=0)
        bg.move_to(text)

        return bg, text
