from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class GamesAsMathObjects(Scene):
    """Scene 1 – Games as mathematical objects."""

    BG        = "#000000"
    BOARD_COL = "#C8A96E"
    GRID_COL  = "#2A2A2A"
    BLACK_COL = "#1A1A1A"
    WHITE_COL = "#F5F5F5"
    C_STATE   = "#5B9BD5"
    C_ACTION  = "#F0A500"
    C_TRANS   = "#A78BFA"
    C_REWARD  = "#50C878"
    C_LOSS    = "#FF6B6B"

    N       = 5
    SIDE    = 2.6
    STONE_R = 0.21

    def construct(self):
        self.camera.background_color = self.BG
        self.BC = LEFT * 2.8
        self.SP = self.SIDE / (self.N - 1)

        m = {}
        self._phase_board(m)
        self._phase_state(m)
        self._phase_action(m)
        self._phase_transition(m)
        self._phase_reward(m)
        self._phase_framework(m)
        self._phase_goal()

    # ─── geometry helpers ─────────────────────────────────────────────

    def gp(self, i, j):
        x = self.BC[0] - self.SIDE / 2 + i * self.SP
        y = self.BC[1] - self.SIDE / 2 + j * self.SP
        return np.array([x, y, 0.0])

    def _make_stone(self, col):
        c = Circle(radius=self.STONE_R)
        c.set_fill(col, opacity=1)
        c.set_stroke(color="#C0C0C0" if col == self.WHITE_COL else "#3A3A3A", width=1.2)
        return c

    # ─── phases ───────────────────────────────────────────────────────

    def _phase_board(self, m):
        bg = Square(side_length=self.SIDE + 0.35)
        bg.set_fill(self.BOARD_COL, opacity=1).set_stroke(width=0)
        bg.move_to(self.BC)

        s2, sp, n, bc = self.SIDE / 2, self.SP, self.N, self.BC
        lines = VGroup()
        for k in range(n):
            t = -s2 + k * sp
            lines.add(Line(
                [bc[0] + t, bc[1] - s2, 0], [bc[0] + t, bc[1] + s2, 0],
                color=self.GRID_COL, stroke_width=1.5,
            ))
            lines.add(Line(
                [bc[0] - s2, bc[1] + t, 0], [bc[0] + s2, bc[1] + t, 0],
                color=self.GRID_COL, stroke_width=1.5,
            ))

        stone_data = [
            (1, 3, self.BLACK_COL), (2, 3, self.WHITE_COL),
            (2, 2, self.BLACK_COL), (3, 2, self.WHITE_COL),
            (1, 1, self.WHITE_COL), (3, 3, self.BLACK_COL),
        ]
        stones = VGroup()
        for i, j, col in stone_data:
            s = self._make_stone(col)
            s.move_to(self.gp(i, j))
            stones.add(s)

        self.play(GrowFromCenter(bg), run_time=0.9)
        self.play(
            LaggedStart(*[Create(l) for l in lines], lag_ratio=0.03),
            run_time=1.0,
        )
        self.play(
            LaggedStart(*[GrowFromCenter(s) for s in stones], lag_ratio=0.14),
            run_time=1.4,
        )
        self.wait(0.3)

        m["bg"], m["lines"], m["stones"] = bg, lines, stones

    def _phase_state(self, m):
        brace = Brace(m["bg"], UP, color=self.C_STATE, buff=0.15)
        lbl   = MathTex("s", color=self.C_STATE, font_size=60)
        lbl.next_to(brace, UP, buff=0.15)
        sub   = Text("position  =  state", font_size=24, color=GRAY_C)
        sub.next_to(m["bg"], DOWN, buff=0.45)

        self.play(GrowFromCenter(brace), Write(lbl), run_time=0.9)
        self.play(FadeIn(sub, shift=UP * 0.15), run_time=0.6)
        self.wait(0.8)

        m["brace"], m["s_label"], m["sub"] = brace, lbl, sub

    def _phase_action(self, m):
        dest = self.gp(2, 4)
        new_stone = self._make_stone(self.WHITE_COL)
        new_stone.move_to(dest + UP * 2.4)
        self.add(new_stone)

        arrow = Arrow(
            dest + UP * 2.0 + RIGHT * 0.45,
            dest + UP * 0.28 + RIGHT * 0.45,
            color=self.C_ACTION, stroke_width=3.5,
            max_tip_length_to_length_ratio=0.18,
        )
        a_lbl = MathTex("a", color=self.C_ACTION, font_size=52)
        a_lbl.next_to(arrow, RIGHT, buff=0.15)

        new_sub = Text("move  =  action", font_size=24, color=GRAY_C)
        new_sub.move_to(m["sub"].get_center())

        self.play(FadeOut(m["sub"]), GrowArrow(arrow), Write(a_lbl), run_time=0.8)
        self.play(new_stone.animate.move_to(dest), run_time=0.75, rate_func=ease_out_quad)
        m["stones"].add(new_stone)
        self.play(FadeIn(new_sub, shift=UP * 0.15), run_time=0.5)
        self.wait(0.7)

        m["arrow"] = arrow
        m["a_label"] = a_lbl
        m["sub"] = new_sub

    def _phase_transition(self, m):
        brace2 = Brace(VGroup(m["bg"], m["stones"]), UP, color=self.C_TRANS, buff=0.15)
        t_lbl  = MathTex(r"T(s,\,a)", color=self.C_TRANS, font_size=48)
        t_lbl.next_to(brace2, UP, buff=0.15)

        new_sub = Text("new position  =  T(s, a)", font_size=24, color=GRAY_C)
        new_sub.move_to(m["sub"].get_center())

        self.play(
            Transform(m["brace"],  brace2),
            Transform(m["s_label"], t_lbl),
            FadeOut(m["sub"]),
            FadeOut(m["arrow"]),
            FadeOut(m["a_label"]),
            run_time=1.1,
        )
        self.play(FadeIn(new_sub, shift=UP * 0.15), run_time=0.5)
        self.wait(0.8)
        m["sub"] = new_sub

    def _phase_reward(self, m):
        r_eq  = MathTex(r"r \;\in\; \{-1,\;0,\;+1\}", color=WHITE, font_size=42)
        r_lbl = Text("reward", font_size=24, color=GRAY_C)
        r_grp = VGroup(r_eq, r_lbl).arrange(DOWN, buff=0.18)
        r_grp.to_edge(RIGHT, buff=1.6).align_to(m["bg"], DOWN)

        self.play(FadeIn(r_grp, shift=LEFT * 0.3), run_time=0.9)
        self.play(r_eq.animate.set_color(self.C_REWARD), run_time=0.38)
        self.play(r_eq.animate.set_color(self.C_LOSS),   run_time=0.38)
        self.play(r_eq.animate.set_color(WHITE),         run_time=0.3)
        self.wait(0.6)
        m["r_grp"] = r_grp

    def _phase_framework(self, m):
        fade_all = VGroup(
            m["bg"], m["lines"], m["stones"],
            m["brace"], m["s_label"],
            m["sub"], m["r_grp"],
        )
        self.play(FadeOut(fade_all), run_time=1.3)

        rows_data = [
            ("State:",      "s",                        self.C_STATE),
            ("Action:",     "a",                        self.C_ACTION),
            ("Transition:", r"s' = T(s,\,a)",           self.C_TRANS),
            ("Reward:",     r"r \in \{-1,\;0,\;+1\}",  WHITE),
        ]

        label_col = VGroup(*[
            Text(txt, font_size=36, color=col)
            for txt, _, col in rows_data
        ])
        expr_col = VGroup(*[
            MathTex(expr, font_size=46, color=col)
            for _, expr, col in rows_data
        ])

        label_col.arrange(DOWN, buff=0.6, aligned_edge=RIGHT)
        expr_col.arrange(DOWN,  buff=0.6, aligned_edge=LEFT)

        table = VGroup(label_col, expr_col).arrange(RIGHT, buff=0.55)
        table.move_to(ORIGIN + UP * 0.4)

        row_pairs = [(label_col[i], expr_col[i]) for i in range(len(rows_data))]

        self.play(
            LaggedStart(
                *[AnimationGroup(FadeIn(lbl, shift=RIGHT * 0.2), Write(expr))
                  for lbl, expr in row_pairs],
                lag_ratio=0.32,
            ),
            run_time=3.0,
        )
        self.wait(0.5)

        self._table   = table
        self._lbl_col = label_col
        self._exp_col = expr_col

    def _phase_goal(self):
        divider = Line(
            self._table.get_left(), self._table.get_right(),
            color=GRAY_D, stroke_width=1,
        )
        divider.next_to(self._table, DOWN, buff=0.35)

        goal_lbl  = Text("Goal:", font_size=36, color=self.C_ACTION)
        goal_expr = MathTex(r"\text{choose a good } a", font_size=46, color=self.C_ACTION)

        goal_lbl.align_to(self._lbl_col,  RIGHT)
        goal_expr.align_to(self._exp_col, LEFT)

        ref_y = divider.get_center()[1] - 0.55
        goal_lbl.set_y(ref_y)
        goal_expr.set_y(ref_y)

        goal_row = VGroup(goal_lbl, goal_expr)

        self.play(Create(divider), run_time=0.5)
        self.play(
            FadeIn(goal_lbl, shift=RIGHT * 0.2),
            Write(goal_expr),
            run_time=1.0,
        )
        self.wait(0.3)

        box  = SurroundingRectangle(
            goal_row, color=self.C_ACTION, buff=0.22,
            corner_radius=0.12, stroke_width=2.5,
        )
        glow = box.copy().set_stroke(color=self.C_ACTION, width=10, opacity=0.2)

        self.play(Create(box), run_time=0.8)
        self.play(FadeIn(glow), run_time=0.4)
        self.wait(2.5)
