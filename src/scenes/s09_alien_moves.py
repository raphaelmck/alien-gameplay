from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class AlienMovesScene(ThreeDScene):
    """Scene 9 – Why alien moves happen (climax)."""

    BG            = "#000000"
    BOARD_COLOR   = "#C8A96E"
    GRID_COLOR    = "#1A1A1A"
    BLACK_STONE   = "#1A1A1A"
    WHITE_STONE   = "#F5F5F5"
    SUPPORT_COLOR = "#1E1510"  # warm dark wood — same hue across all cube faces

    C_HUMAN = "#F0A500"
    C_MACH  = "#A78BFA"
    C_INFL  = "#5B9BD5"
    C_DIM   = "#505050"

    BOARD_SIZE = 6.0
    MOVE_37    = (14, 9)

    def construct(self):
        self.SPACING = self.BOARD_SIZE / 18
        self.camera.background_color = self.BG

        self.set_camera_orientation(phi=65 * DEGREES, theta=-128 * DEGREES)
        self._build_board_instant()

        self.begin_ambient_camera_rotation(rate=0.06)
        self.wait(3.0)

        self._phase_questions()
        self._phase_stats()
        self._phase_influence()

        self.wait(2.0)

    # ── board helpers ─────────────────────────────────────────────────────────

    def _pt(self, i, j, z=0.0):
        x = i * self.SPACING - self.BOARD_SIZE / 2
        y = j * self.SPACING - self.BOARD_SIZE / 2
        return np.array([x, y, z])

    def _stone_r(self):
        return self.SPACING * 0.46

    def _stone(self, color):
        r = self._stone_r()
        s = Sphere(radius=r, resolution=(18, 18))
        s.set_color(color)
        s.set_opacity(1)
        return s

    def _build_board_instant(self):
        # Board support — cascade same warm-dark fill to every cube face
        support = Cube(stroke_width=0)
        support.set_fill(self.SUPPORT_COLOR, opacity=1)
        support.set_stroke(width=0)
        w = self.BOARD_SIZE - 2.5
        support.scale(np.array([w, w, 0.28]))
        support.shift(np.array([0.0, 0.0, -0.38]))

        board = Square(side_length=self.BOARD_SIZE + 0.4)
        board.set_fill(self.BOARD_COLOR, opacity=1)
        board.set_stroke(width=0)

        z_line = 0.015
        grid_lines = VGroup()
        for i in range(19):
            grid_lines.add(Line(
                self._pt(i,  0, z_line), self._pt(i, 18, z_line),
                color=self.GRID_COLOR, stroke_width=1.5,
            ))
            grid_lines.add(Line(
                self._pt(0,  i, z_line), self._pt(18, i, z_line),
                color=self.GRID_COLOR, stroke_width=1.5,
            ))

        stars = VGroup(*[
            Dot(self._pt(i, j, 0.02), radius=0.055, color=self.GRID_COLOR)
            for i in [3, 9, 15] for j in [3, 9, 15]
        ])

        prior_moves = [
            (15,15),(3,3),(2,15),(16,3),(14,3),(14,2),(13,2),
            (15,2),(2,5),(5,2),(12,3),(16,5),(8,16),(3,9),
            (15,4),(16,4),(2,3),(2,2),(1,2),(2,4),(1,3),
            (1,4),(3,4),(1,5),(3,2),(4,3),(3,1),(2,6),
            (9,3),(2,12),(4,15),(16,13),(16,14),(15,13),(13,15),(15,10),
        ]
        r = self._stone_r()
        sz = r  # sphere center sits one radius above the board surface

        stones = VGroup()
        for idx, (cx, cy) in enumerate(prior_moves):
            color = self.BLACK_STONE if idx % 2 == 0 else self.WHITE_STONE
            s = self._stone(color)
            s.move_to(self._pt(cx, cy, sz))
            stones.add(s)

        # Move 37 — purple
        m37 = self._stone(self.C_MACH)
        m37.move_to(self._pt(*self.MOVE_37, sz))
        stones.add(m37)

        self.add(support, board, grid_lines, stars, stones)

    # ── phases ────────────────────────────────────────────────────────────────

    def _phase_questions(self):
        def _col(label, question, color):
            lbl = Tex(label,    font_size=22, color=self.C_DIM)
            q   = Tex(question, font_size=32, color=color)
            col = VGroup(lbl, q)
            col.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
            return col

        human = _col(r"Human question:", r"Does this look natural?",          self.C_HUMAN)
        mach  = _col(r"Machine question:", r"Does this improve $V_\theta(s)$?", self.C_MACH)

        divider = Line(UP * 0.62, DOWN * 0.62, color=self.C_DIM, stroke_width=0.8)

        panel = VGroup(human, divider, mach)
        panel.arrange(RIGHT, buff=0.55, aligned_edge=UP)
        panel.to_edge(UP, buff=0.5)

        self.add_fixed_in_frame_mobjects(panel)
        self.play(
            LaggedStart(Write(human), FadeIn(divider), Write(mach), lag_ratio=0.3),
            run_time=2.0,
        )
        self.wait(3.5)
        self.play(FadeOut(panel), run_time=0.9)
        self.wait(0.4)

    def _phase_stats(self):
        def _stat(math_lbl, value, v_color):
            lbl = MathTex(math_lbl, font_size=18, color=self.C_DIM)
            val = Tex(value,        font_size=18, color=v_color)
            grp = VGroup(lbl, val)
            grp.arrange(RIGHT, buff=0.28)
            return grp

        s1 = _stat(r"\pi_\theta(a \mid s) :", r"low human-like probability", self.C_HUMAN)
        s2 = _stat(r"V_\theta(T(s,a)) :",     r"high long-term value",        self.C_MACH)
        s3 = _stat(r"\text{MCTS visits} :",   r"unexpectedly high",           self.C_INFL)

        row = VGroup(s1, s2, s3)
        row.arrange(RIGHT, buff=0.7)
        row.to_edge(DOWN, buff=0.5)

        self.add_fixed_in_frame_mobjects(row)
        self.play(
            LaggedStart(Write(s1), Write(s2), Write(s3), lag_ratio=0.4),
            run_time=2.2,
        )
        self.wait(3.5)
        self._stats_row = row

    def _phase_influence(self):
        cx, cy = self.MOVE_37
        origin = self._pt(cx, cy, self._stone_r() * 2)

        targets = [
            (3,  3),
            (15, 3),
            (3,  15),
            (15, 15),
            (9,  16),
            (16, 10),
            (2,  9),
        ]

        lines = VGroup(*[
            Line(origin, self._pt(tx, ty, self._stone_r()), color=self.C_INFL, stroke_width=1.2)
            .set_stroke(opacity=0.5)
            for tx, ty in targets
        ])

        self.play(
            FadeOut(self._stats_row),
            LaggedStart(*[Create(l) for l in lines], lag_ratio=0.1),
            run_time=2.2,
        )
        self.wait(2.8)
        self.play(FadeOut(lines), run_time=1.2)
        self.wait(0.4)
