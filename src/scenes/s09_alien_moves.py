from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class AlienMovesScene(ThreeDScene):
    """Scene 9 – Why alien moves happen (climax)."""

    BG          = "#000000"
    BOARD_COLOR = "#C8A96E"
    GRID_COLOR  = "#1A1A1A"
    BLACK_STONE = "#1A1A1A"
    WHITE_STONE = "#F5F5F5"
    STONE_Z     = 0.025

    C_HUMAN = "#F0A500"   # amber  — human side
    C_MACH  = "#A78BFA"   # purple — machine side
    C_INFL  = "#5B9BD5"   # blue   — influence lines
    C_DIM   = "#505050"   # muted  — secondary labels

    BOARD_SIZE = 6.0
    MOVE_37    = (14, 9)

    def construct(self):
        self.SPACING = self.BOARD_SIZE / 18
        self.camera.background_color = self.BG

        self.set_camera_orientation(phi=65 * DEGREES, theta=-128 * DEGREES)
        self._build_board_instant()

        self.begin_ambient_camera_rotation(rate=0.06)
        self.wait(3.0)

        # ── overlays play while board keeps spinning ───────────────────────────
        self._phase_questions()
        self._phase_stats()
        self._phase_influence()

        self.wait(2.0)

    # ── board helpers ─────────────────────────────────────────────────────────

    def _pt(self, i, j, z=0.0):
        x = i * self.SPACING - self.BOARD_SIZE / 2
        y = j * self.SPACING - self.BOARD_SIZE / 2
        return np.array([x, y, z])

    def _stone(self, color):
        r = self.SPACING * 0.46
        sc = "#C0C0C0" if color == self.WHITE_STONE else "#2A2A2A"
        s = Circle(radius=r)
        s.set_fill(color, opacity=1)
        s.set_stroke(color=sc, width=0.8)
        return s

    def _build_board_instant(self):
        support = Cube(stroke_width=0)
        support.set_fill(BLACK, opacity=1)
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
                self._pt(i, 0, z_line), self._pt(i, 18, z_line),
                color=self.GRID_COLOR, stroke_width=1.5,
            ))
            grid_lines.add(Line(
                self._pt(0, i, z_line), self._pt(18, i, z_line),
                color=self.GRID_COLOR, stroke_width=1.5,
            ))

        stars = VGroup(*[
            Dot(self._pt(i, j, 0.02), radius=0.055, color=self.GRID_COLOR)
            for i in [3, 9, 15] for j in [3, 9, 15]
        ])

        all_moves = [
            (15,15),(3,3),(2,15),(16,3),(14,3),(14,2),(13,2),
            (15,2),(2,5),(5,2),(12,3),(16,5),(8,16),(3,9),
            (15,4),(16,4),(2,3),(2,2),(1,2),(2,4),(1,3),
            (1,4),(3,4),(1,5),(3,2),(4,3),(3,1),(2,6),
            (9,3),(2,12),(4,15),(16,13),(16,14),(15,13),(13,15),(15,10),
            self.MOVE_37,  # move 37 — black
        ]

        stones = VGroup()
        for idx, (cx, cy) in enumerate(all_moves):
            color = self.BLACK_STONE if idx % 2 == 0 else self.WHITE_STONE
            s = self._stone(color)
            s.move_to(self._pt(cx, cy, self.STONE_Z))
            stones.add(s)

        self.add(support, board, grid_lines, stars, stones)

    # ── phases ────────────────────────────────────────────────────────────────

    def _phase_questions(self):
        def _col(label_txt, q_txt, color):
            lbl = Text(label_txt, font_size=14, color=self.C_DIM)
            q   = Text(q_txt,     font_size=19, color=color)
            col = VGroup(lbl, q)
            col.arrange(DOWN, aligned_edge=LEFT, buff=0.16)
            return col

        human_col = _col("Human question:", "Does this look natural?", self.C_HUMAN)
        mach_col  = _col("Machine question:", "Does this improve Vθ(s)?", self.C_MACH)

        divider = Line(UP * 0.55, DOWN * 0.55, color=self.C_DIM, stroke_width=0.8)

        panel = VGroup(human_col, divider, mach_col)
        panel.arrange(RIGHT, buff=0.48, aligned_edge=UP)
        panel.to_corner(UL, buff=0.45)

        self.add_fixed_in_frame_mobjects(panel)
        self.play(FadeIn(panel), run_time=1.2, rate_func=smooth)
        self.wait(3.5)
        self.play(FadeOut(panel), run_time=0.9)
        self.wait(0.4)

    def _phase_stats(self):
        def _row(label, value, v_color):
            lbl = Text(label, font_size=13, color=self.C_DIM)
            val = Text(value, font_size=13, color=v_color)
            row = VGroup(lbl, val)
            row.arrange(RIGHT, buff=0.3)
            return row

        rows = VGroup(
            _row("πθ(a | s) :", "low human-like probability", self.C_HUMAN),
            _row("Vθ(T(s,a)):", "high long-term value",       self.C_MACH),
            _row("MCTS visits:", "unexpectedly high",         self.C_INFL),
        )
        rows.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        rows.to_corner(DL, buff=0.45)

        self.add_fixed_in_frame_mobjects(rows)
        self.play(
            LaggedStart(*[FadeIn(r) for r in rows], lag_ratio=0.5),
            run_time=2.0,
        )
        self.wait(3.5)
        self._stats_rows = rows

    def _phase_influence(self):
        cx, cy = self.MOVE_37
        origin = self._pt(cx, cy, 0.045)

        targets = [
            (3,  3),   # bottom-left corner cluster
            (15, 3),   # bottom-right corner cluster
            (3,  15),  # top-left corner
            (15, 15),  # top-right corner — Q16
            (9,  16),  # top-center
            (16, 10),  # R11 — right-side contest
            (2,  9),   # D10 — left-side stone
        ]

        lines = VGroup(*[
            Line(
                origin, self._pt(tx, ty, 0.045),
                color=self.C_INFL, stroke_width=1.2,
            ).set_stroke(opacity=0.5)
            for tx, ty in targets
        ])

        self.play(
            FadeOut(self._stats_rows),
            LaggedStart(*[Create(l) for l in lines], lag_ratio=0.1),
            run_time=2.2,
        )
        self.wait(2.8)
        self.play(FadeOut(lines), run_time=1.2)
        self.wait(0.4)

