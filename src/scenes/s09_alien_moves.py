from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class AlienMovesScene(Scene):
    """Scene 9 – Why alien moves happen: the climax."""

    BG        = "#000000"
    BOARD_COL = "#C8A96E"
    GRID_COL  = "#2A2A2A"
    C_BLACK_S = "#1A1A1A"
    C_WHITE_S = "#F5F5F5"
    C_POLICY  = "#A78BFA"
    C_VALUE   = "#50C878"
    C_SEARCH  = "#5B9BD5"
    C_MOVE    = "#F0A500"
    C_HUMAN   = "#E8C97A"
    C_MACHINE = "#5B9BD5"

    N       = 5
    SIDE    = 2.4
    STONE_R = 0.195

    STONE_DATA = [
        (1, 3, "#1A1A1A"), (2, 3, "#F5F5F5"),
        (2, 2, "#1A1A1A"), (3, 2, "#F5F5F5"),
        (1, 1, "#F5F5F5"), (3, 3, "#1A1A1A"),
        (0, 2, "#1A1A1A"), (4, 1, "#F5F5F5"),
    ]
    OCCUPIED  = {(1, 3), (2, 3), (2, 2), (3, 2), (1, 1), (3, 3), (0, 2), (4, 1)}
    MOVE37_IJ = (1, 4)

    def construct(self):
        self.camera.background_color = self.BG
        self.BC = np.array([-3.2, 0.0, 0.0])
        self.SP = self.SIDE / (self.N - 1)
        m = {}
        self._phase_opener(m)
        self._phase_two_questions(m)
        self._phase_metrics(m)
        self._phase_influence(m)
        self._phase_closing(m)

    # ─── helpers ──────────────────────────────────────────────────────────────

    def gp(self, i, j):
        x = self.BC[0] - self.SIDE / 2 + i * self.SP
        y = self.BC[1] - self.SIDE / 2 + j * self.SP
        return np.array([x, y, 0.0])

    def _make_stone(self, col, r=None):
        r = r or self.STONE_R
        c = Circle(radius=r)
        c.set_fill(col, opacity=1)
        c.set_stroke(color="#C0C0C0" if col == self.C_WHITE_S else "#3A3A3A", width=1.2)
        return c

    def _make_board_group(self):
        bg = Square(side_length=self.SIDE + 0.35)
        bg.set_fill(self.BOARD_COL, opacity=1).set_stroke(width=0)
        bg.move_to(self.BC)
        lines = VGroup()
        for k in range(self.N):
            t = -self.SIDE / 2 + k * self.SP
            lines.add(Line(
                [self.BC[0] + t, self.BC[1] - self.SIDE / 2, 0],
                [self.BC[0] + t, self.BC[1] + self.SIDE / 2, 0],
                color=self.GRID_COL, stroke_width=1.5,
            ))
            lines.add(Line(
                [self.BC[0] - self.SIDE / 2, self.BC[1] + t, 0],
                [self.BC[0] + self.SIDE / 2, self.BC[1] + t, 0],
                color=self.GRID_COL, stroke_width=1.5,
            ))
        return bg, lines

    def _make_stones_group(self):
        stones = VGroup()
        for i, j, col in self.STONE_DATA:
            s = self._make_stone(col)
            s.move_to(self.gp(i, j))
            stones.add(s)
        return stones

    # ─── phases ───────────────────────────────────────────────────────────────

    def _phase_opener(self, m):
        opener = Tex(r"Now Move 37 is no longer mysterious.", font_size=38, color=WHITE)
        self.play(FadeIn(opener, shift=UP * 0.12), run_time=1.0)
        self.wait(1.6)
        self.play(FadeOut(opener), run_time=0.65)

        bg, lines = self._make_board_group()
        stones    = self._make_stones_group()

        self.play(GrowFromCenter(bg), run_time=0.50)
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.02), run_time=0.45)
        self.play(
            LaggedStart(*[GrowFromCenter(s) for s in stones], lag_ratio=0.07),
            run_time=0.70,
        )

        move_pos = self.gp(*self.MOVE37_IJ)

        # "?" ghost dissolves into the stone — recalling the mystery of the opening
        q_ghost = Text("?", font_size=30, color=GRAY_C)
        q_ghost.move_to(move_pos)
        self.play(FadeIn(q_ghost, scale=0.8), run_time=0.35)
        self.wait(0.25)

        move37 = self._make_stone(self.C_BLACK_S)
        move37.move_to(move_pos)
        move37.set_z_index(2)
        self.play(FadeOut(q_ghost), GrowFromCenter(move37), run_time=0.45)

        ring = Circle(radius=self.STONE_R * 1.6,
                      stroke_color=self.C_MOVE, stroke_width=2.0, fill_opacity=0)
        ring.move_to(move_pos)
        move_num = Text("37", font_size=12, color=self.C_MOVE, weight="BOLD")
        move_num.next_to(move_pos, UR, buff=0.06)

        self.play(Create(ring), FadeIn(move_num), run_time=0.40)
        pulse = ring.copy()
        self.add(pulse)
        self.play(pulse.animate.scale(4.0).set_opacity(0),
                  run_time=0.75, rate_func=ease_out_quad)
        self.remove(pulse)
        self.wait(0.5)

        m.update(dict(
            bg=bg, lines=lines, stones=stones,
            move37=move37, ring=ring, move_num=move_num, move_pos=move_pos,
        ))

    def _phase_two_questions(self, m):
        # Board stays left; two contrasting questions animate in on the right.
        cx = 2.5

        h_tag   = Text("Human asks:", font_size=18, color=self.C_HUMAN, weight="BOLD")
        h_q     = Tex(r"Does this look natural?", font_size=25, color=self.C_HUMAN)
        h_block = VGroup(h_tag, h_q).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        h_block.move_to(np.array([cx, 0.85, 0.0]))

        sep = DashedLine(
            np.array([cx - 2.8, 0.0, 0.0]),
            np.array([cx + 2.8, 0.0, 0.0]),
            color=GRAY_E, stroke_width=0.8, dash_length=0.15,
        )

        m_tag   = Text("Machine asks:", font_size=18, color=self.C_MACHINE, weight="BOLD")
        m_q     = MathTex(r"\text{Does this improve } V_\theta(s)?",
                          font_size=25, color=self.C_MACHINE)
        m_block = VGroup(m_tag, m_q).arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        m_block.move_to(np.array([cx, -0.78, 0.0]))

        self.play(FadeIn(h_tag, shift=LEFT * 0.08), run_time=0.38)
        self.play(Write(h_q), run_time=0.60)
        self.wait(0.30)
        self.play(Create(sep), run_time=0.40)
        self.play(FadeIn(m_tag, shift=LEFT * 0.08), run_time=0.38)
        self.play(Write(m_q), run_time=0.60)
        self.wait(0.85)

        # The cold precision of the machine's question wins out
        self.play(h_block.animate.set_opacity(0.22), run_time=0.55)
        self.wait(0.90)
        self.play(FadeOut(VGroup(h_block, sep, m_block)), run_time=0.60)
        self.wait(0.10)

    def _phase_metrics(self, m):
        move_pos = m["move_pos"]

        # Keep Move 37 highlighted as the reference point
        highlight = Circle(
            radius=self.STONE_R * 1.75,
            stroke_color=self.C_MOVE, stroke_width=1.8, fill_opacity=0,
        )
        highlight.move_to(move_pos)
        self.play(Create(highlight), run_time=0.35)

        cx       = 2.6
        BAR_W    = 2.0
        BAR_H    = 0.22

        metrics = [
            (r"\pi_\theta(a \mid s)",  r"0.03",   0.03, self.C_POLICY),
            (r"V_\theta(T(s,\,a))",    r"+0.81",  0.81, self.C_VALUE),
            (r"N_{\mathrm{visits}}",   r"\gg 1",  0.92, self.C_SEARCH),
        ]

        row_groups = []
        for idx, (lbl_str, val_str, ratio, color) in enumerate(metrics):
            y = 0.88 - idx * 0.82

            lbl = MathTex(lbl_str, font_size=21, color=color)
            lbl.align_to([cx - 2.7, 0, 0], LEFT).set_y(y)

            bar_bg = RoundedRectangle(width=BAR_W, height=BAR_H, corner_radius=0.05)
            bar_bg.set_fill(GRAY_E, opacity=0.20).set_stroke(color=GRAY_D, width=0.7)
            bar_bg.move_to(np.array([cx + 0.30, y, 0.0]))

            bar_fill = Rectangle(width=BAR_W * ratio, height=BAR_H)
            bar_fill.set_fill(color, opacity=0.82).set_stroke(width=0)
            bar_fill.align_to(bar_bg, LEFT).set_y(y)

            val = MathTex(val_str, font_size=19, color=color)
            val.next_to(bar_bg, RIGHT, buff=0.14).set_y(y)

            row_groups.append(VGroup(lbl, bar_bg, bar_fill, val))

        self.play(
            LaggedStart(
                *[AnimationGroup(
                    FadeIn(rg[0], shift=RIGHT * 0.06),
                    FadeIn(rg[1]),
                    GrowFromEdge(rg[2], LEFT),
                    FadeIn(rg[3]),
                  )
                  for rg in row_groups],
                lag_ratio=0.45,
            ),
            run_time=2.4,
        )
        self.wait(0.55)

        # Cross out the policy bar — human intuition would discard this move
        slash1 = Line(
            row_groups[0][1].get_corner(UL),
            row_groups[0][1].get_corner(DR),
            color=GRAY_C, stroke_width=1.2, stroke_opacity=0.70,
        )
        slash2 = Line(
            row_groups[0][1].get_corner(UR),
            row_groups[0][1].get_corner(DL),
            color=GRAY_C, stroke_width=1.2, stroke_opacity=0.70,
        )
        self.play(
            Create(slash1), Create(slash2),
            row_groups[0].animate.set_opacity(0.30),
            run_time=0.55,
        )
        self.wait(0.45)

        # Frame value + visits: this is what the machine trusted
        surr = SurroundingRectangle(
            VGroup(row_groups[1], row_groups[2]),
            color=self.C_VALUE, buff=0.15,
            corner_radius=0.09, stroke_width=1.5,
        )
        self.play(Create(surr), run_time=0.55)
        self.wait(1.10)

        self.play(
            FadeOut(VGroup(*row_groups, slash1, slash2, surr, highlight)),
            run_time=0.70,
        )
        self.wait(0.10)

    def _phase_influence(self, m):
        move_pos    = m["move_pos"]
        board_bot_y = m["bg"].get_bottom()[1]

        # ── Act 1: human attention — warm glow concentrated on the local fight ──
        # The cluster of stones in the centre of the board is where human eyes go.
        fight_center = (self.gp(2, 2) + self.gp(3, 3)) / 2

        h_glow_inner = Circle(radius=0.35,
                               fill_color=self.C_HUMAN, fill_opacity=0.30,
                               stroke_width=0)
        h_glow_inner.move_to(fight_center)

        h_glow_outer = Circle(radius=0.62,
                               fill_color=self.C_HUMAN, fill_opacity=0.12,
                               stroke_color=self.C_HUMAN, stroke_width=1.4,
                               stroke_opacity=0.50)
        h_glow_outer.move_to(fight_center)

        h_lbl = Text("human attention", font_size=16, color=self.C_HUMAN)
        h_lbl.move_to(np.array([self.BC[0], board_bot_y - 0.30, 0.0]))

        self.play(
            GrowFromCenter(h_glow_inner),
            GrowFromCenter(h_glow_outer),
            FadeIn(h_lbl, shift=UP * 0.08),
            run_time=0.70,
        )
        self.wait(0.80)

        # ── Act 2: machine influence — cold lines radiate from Move 37 ──────────
        self.play(FadeOut(VGroup(h_glow_inner, h_glow_outer, h_lbl)), run_time=0.45)

        targets = [
            (0, 0), (4, 0), (4, 4), (0, 3),
            (3, 0), (4, 2), (0, 1), (3, 1),
        ]
        influence_lines = VGroup()
        for ti, tj in targets:
            tp = self.gp(ti, tj)
            influence_lines.add(Line(
                move_pos, tp,
                stroke_color=self.C_VALUE,
                stroke_width=1.25,
                stroke_opacity=0.52,
            ))

        center_dot = Dot(move_pos, radius=0.065, color=self.C_VALUE)
        center_dot.set_z_index(5)

        m_lbl = Text("machine influence", font_size=16, color=self.C_VALUE)
        m_lbl.move_to(np.array([self.BC[0], board_bot_y - 0.30, 0.0]))

        self.play(GrowFromCenter(center_dot), run_time=0.28)
        self.play(
            LaggedStart(*[Create(l) for l in influence_lines], lag_ratio=0.08),
            FadeIn(m_lbl, shift=UP * 0.08),
            run_time=1.30,
        )

        # Two expanding rings — the move's value propagates through time
        for base_r, scale_f in [(self.STONE_R * 1.1, 4.8), (self.STONE_R * 1.1, 7.5)]:
            pulse = Circle(radius=base_r, fill_opacity=0,
                           stroke_color=self.C_VALUE, stroke_width=1.5)
            pulse.move_to(move_pos)
            self.add(pulse)
            self.play(pulse.animate.scale(scale_f).set_opacity(0),
                      run_time=0.85, rate_func=ease_out_quad)
            self.remove(pulse)

        # Endpoint dots flicker on — each one is an intersection the machine "saw"
        end_dots = VGroup(*[
            Dot(self.gp(ti, tj), radius=0.048, color=self.C_VALUE, fill_opacity=0.75)
            for ti, tj in targets
        ])
        self.play(
            LaggedStart(*[GrowFromCenter(d) for d in end_dots], lag_ratio=0.06),
            run_time=0.65,
        )
        self.wait(0.65)
        self.play(
            FadeOut(VGroup(influence_lines, center_dot, end_dots, m_lbl)),
            run_time=0.55,
        )
        self.wait(0.20)

    def _phase_closing(self, m):
        board_grp = VGroup(
            m["bg"], m["lines"], m["stones"],
            m["move37"], m["ring"], m["move_num"],
        )
        self.play(FadeOut(board_grp), run_time=0.90)
        self.wait(0.20)

        l1 = Text(
            "The move is not alien because it is random.",
            font_size=30, color=GRAY_B,
        )
        l2 = Text(
            "It is alien because it is optimized",
            font_size=38, color=WHITE, weight="BOLD",
        )
        l3 = Text(
            "for a geometry of the game we do not naturally see.",
            font_size=30, color=GRAY_B,
        )
        VGroup(l1, l2, l3).arrange(DOWN, buff=0.46).move_to(ORIGIN)

        self.play(FadeIn(l1, shift=UP * 0.10), run_time=0.90)
        self.wait(0.50)
        self.play(FadeIn(l2, shift=UP * 0.10), run_time=1.00)
        self.wait(0.45)
        self.play(FadeIn(l3, shift=UP * 0.10), run_time=0.90)

        # Gentle glow under the middle line to hold the eye
        glow = SurroundingRectangle(
            l2, color=WHITE, buff=0.14,
            corner_radius=0.12, stroke_width=0,
            fill_color=WHITE, fill_opacity=0.0,
        )
        self.add(glow)
        self.play(glow.animate.set_fill(opacity=0.06), run_time=0.80)
        self.wait(3.80)
