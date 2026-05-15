from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class BitterLessonScene(Scene):
    """Scene 6 – The Bitter Lesson."""

    BG      = "#000000"
    C_HUMAN = "#F0A500"   # amber  – human-knowledge path
    C_SCALE = "#A78BFA"   # purple – search / learning / compute
    C_AXIS  = "#555555"

    # Curve definitions (t ∈ [0, 1], output ∈ [0, 1])
    @staticmethod
    def _f_human(t):
        """Fast early rise, hard plateau near 0.58."""
        return 0.58 * (1.0 - np.exp(-8.0 * t))

    @staticmethod
    def _f_scale(t):
        """Slow start, accelerating growth that overtakes ~t=0.71."""
        return 0.92 * (t ** 1.3)

    def construct(self):
        self.camera.background_color = self.BG

        # Chart geometry – origin bottom-left, normalised axes
        self._orig = LEFT * 3.8 + DOWN * 2.2
        self._aw   = 5.8   # width  (t = 0 → 1)
        self._ah   = 3.6   # height (y = 0 → 1)

        self._phase_intro()
        self._phase_chart()
        self._phase_bitter_lesson()
        self._phase_games_tie()
        self._phase_closing()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _pt(self, t, y):
        """Normalised (t, y) → scene coordinates."""
        return np.array([
            self._orig[0] + t * self._aw,
            self._orig[1] + y * self._ah,
            0.0,
        ])

    def _make_curve(self, f, color, n=300):
        pts = [self._pt(i / (n - 1), f(i / (n - 1))) for i in range(n)]
        c = VMobject(color=color, stroke_width=3.2)
        c.set_points_smoothly(pts)
        return c

    # ── phases ────────────────────────────────────────────────────────────────

    def _phase_intro(self):
        row1 = VGroup(
            Text("Path 1:", font_size=26, color=GRAY_C),
            Text("human concepts  ·  clever rules", font_size=28, color=self.C_HUMAN),
        ).arrange(RIGHT, buff=0.28)

        row2 = VGroup(
            Text("Path 2:", font_size=26, color=GRAY_C),
            Text("search  ·  learning  ·  compute", font_size=28, color=self.C_SCALE),
        ).arrange(RIGHT, buff=0.28)

        grp = VGroup(row1, row2).arrange(DOWN, buff=0.60).move_to(ORIGIN)

        self.play(FadeIn(row1, shift=RIGHT * 0.2), run_time=0.75)
        self.wait(0.3)
        self.play(FadeIn(row2, shift=RIGHT * 0.2), run_time=0.75)
        self.wait(1.2)
        self.play(FadeOut(grp), run_time=0.55)
        self.wait(0.1)

    def _phase_chart(self):
        orig, aw, ah = self._orig, self._aw, self._ah

        # Axes
        x_axis = Arrow(
            orig, orig + RIGHT * (aw + 0.35),
            color=self.C_AXIS, stroke_width=2.0, buff=0,
            max_tip_length_to_length_ratio=0.04,
        )
        y_axis = Arrow(
            orig, orig + UP * (ah + 0.35),
            color=self.C_AXIS, stroke_width=2.0, buff=0,
            max_tip_length_to_length_ratio=0.06,
        )
        x_lbl = Text("Computation / Time", font_size=18, color=GRAY_D)
        x_lbl.next_to(x_axis.get_right(), DOWN, buff=0.22)
        y_lbl = Text("Performance", font_size=18, color=GRAY_D)
        y_lbl.next_to(y_axis.get_top(), UP, buff=0.14)

        self.play(Create(x_axis), Create(y_axis), run_time=0.7)
        self.play(FadeIn(x_lbl), FadeIn(y_lbl), run_time=0.45)

        # Legend (right side of frame)
        def _leg_item(col, label):
            bar = Line(ORIGIN, RIGHT * 0.5, color=col, stroke_width=3.0)
            txt = Text(label, font_size=19, color=col)
            return VGroup(bar, txt).arrange(RIGHT, buff=0.18)

        legend = VGroup(
            _leg_item(self.C_HUMAN, "human knowledge"),
            _leg_item(self.C_SCALE, "search + learning + compute"),
        ).arrange(DOWN, buff=0.32, aligned_edge=LEFT)
        legend.to_edge(RIGHT, buff=0.55).shift(UP * 0.8)
        self.play(FadeIn(legend), run_time=0.45)

        # Human curve
        h_curve = self._make_curve(self._f_human, self.C_HUMAN)
        self.play(Create(h_curve), run_time=1.6, rate_func=smooth)

        # Plateau marker
        plat_y = self._f_human(1.0)          # ≈ 0.579
        plat_x0 = 0.40
        plat_line = DashedLine(
            self._pt(plat_x0, plat_y),
            self._pt(1.0,     plat_y),
            color=self.C_HUMAN, stroke_width=1.2,
            dash_length=0.14, stroke_opacity=0.45,
        )
        plat_lbl = Text("plateau", font_size=18, color=self.C_HUMAN)
        plat_lbl.move_to(self._pt(0.70, plat_y) + UP * 0.24)

        self.play(Create(plat_line), FadeIn(plat_lbl, shift=DOWN * 0.08), run_time=0.65)
        self.wait(0.4)

        # Scale curve
        s_curve = self._make_curve(self._f_scale, self.C_SCALE)
        self.play(Create(s_curve), run_time=2.1, rate_func=smooth)

        # Crossover pulse (curves meet near t≈0.71)
        cross_t  = 0.71
        cross_pt = self._pt(cross_t, self._f_human(cross_t))
        ring = Circle(radius=0.18, fill_opacity=0,
                      stroke_color=WHITE, stroke_width=2.4)
        ring.move_to(cross_pt)
        self.add(ring)
        self.play(ring.animate.scale(4.5).set_opacity(0), run_time=0.8, rate_func=ease_out_quad)
        self.remove(ring)

        # Dim the human curve to show it's been surpassed
        self.play(h_curve.animate.set_stroke(opacity=0.40), run_time=0.65)

        # "breakthrough" annotation
        brk_t  = 0.88
        brk_pt = self._pt(brk_t, self._f_scale(brk_t))
        brk_dot = Dot(brk_pt, radius=0.08, color=self.C_SCALE)
        brk_lbl = Text("breakthrough", font_size=18, color=self.C_SCALE)
        brk_lbl.next_to(brk_pt, UP, buff=0.18).shift(RIGHT * 0.15)

        self.play(GrowFromCenter(brk_dot), FadeIn(brk_lbl, shift=DOWN * 0.08), run_time=0.6)
        self.wait(1.8)

        self._chart_grp = VGroup(
            x_axis, y_axis, x_lbl, y_lbl, legend,
            h_curve, s_curve,
            plat_line, plat_lbl,
            brk_dot, brk_lbl,
        )

    def _phase_bitter_lesson(self):
        # Shrink chart to left panel
        self.play(
            self._chart_grp.animate.scale(0.52).to_edge(LEFT, buff=0.25).shift(DOWN * 0.15),
            run_time=1.0,
        )

        # Title + attribution
        title  = Text("The Bitter Lesson", font_size=44, color=WHITE)
        credit = Text("— Richard Sutton, 2019", font_size=19, color=GRAY_D)
        title.move_to(RIGHT * 2.2 + UP * 2.1)
        credit.next_to(title, DOWN, buff=0.22)

        self.play(Write(title), run_time=0.95)
        self.play(FadeIn(credit, shift=UP * 0.08), run_time=0.5)
        self.wait(0.4)

        # Thesis box
        thesis = Tex(
            r"Methods that scale with computation\\[6pt]eventually dominate.",
            font_size=28, color=WHITE,
        )
        box = RoundedRectangle(
            width=4.5, height=1.65, corner_radius=0.22,
            fill_color="#0C0C1A", fill_opacity=1.0,
            stroke_color=self.C_SCALE, stroke_width=2.5,
        )
        box.move_to(RIGHT * 2.2 + UP * 0.5)
        thesis.move_to(box.get_center())
        glow = box.copy().set_stroke(color=self.C_SCALE, width=12, opacity=0.18)

        self.play(GrowFromCenter(box), run_time=0.65)
        self.play(FadeIn(glow), Write(thesis), run_time=1.0)
        self.wait(0.6)

        # Bitter qualifier
        bitter = Tex(
            r"Human insight is elegant.\\[4pt]It just doesn't scale.",
            font_size=24, color=GRAY_C,
        )
        bitter.next_to(box, DOWN, buff=0.48)
        self.play(FadeIn(bitter, shift=UP * 0.1), run_time=0.8)
        self.wait(2.2)

        self.play(
            FadeOut(VGroup(
                self._chart_grp, title, credit, box, thesis, glow, bitter,
            )),
            run_time=1.0,
        )
        self.wait(0.2)

    def _phase_games_tie(self):
        header = Tex(
            r"Chess and Go are almost perfect examples.",
            font_size=32, color=GRAY_B,
        )
        header.move_to(UP * 2.8)
        self.play(FadeIn(header, shift=DOWN * 0.1), run_time=0.7)
        self.wait(0.3)

        chess_rows = [
            Text("Chess",                          font_size=28, color=GRAY_B),
            Text("Deep Blue  (1997)",               font_size=21, color=self.C_HUMAN),
            Text("hand-crafted evaluation",         font_size=19, color=GRAY_C),
            Text("human concepts → early peak",     font_size=19, color=GRAY_C),
            Text("→  plateau",                      font_size=22, color=self.C_HUMAN),
        ]
        go_rows = [
            Text("Go",                              font_size=28, color=GRAY_B),
            Text("AlphaGo / AlphaZero  (2016–17)", font_size=21, color=self.C_SCALE),
            Text("search + learning + self-play",   font_size=19, color=GRAY_C),
            Text("scale reveals new patterns",      font_size=19, color=GRAY_C),
            Text("→  superhuman",                   font_size=22, color=self.C_SCALE),
        ]

        chess_col = VGroup(*chess_rows).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        go_col    = VGroup(*go_rows).arrange(  DOWN, buff=0.28, aligned_edge=LEFT)
        chess_col.move_to(LEFT * 2.85 + DOWN * 0.3)
        go_col.move_to(   RIGHT * 2.0  + DOWN * 0.3)

        div = Line(UP * 1.9, DOWN * 2.1, color=GRAY_E, stroke_width=1.0)

        self.play(
            LaggedStart(*[FadeIn(r, shift=UP * 0.08) for r in chess_col], lag_ratio=0.15),
            run_time=1.0,
        )
        self.play(Create(div), run_time=0.35)
        self.play(
            LaggedStart(*[FadeIn(r, shift=UP * 0.08) for r in go_col], lag_ratio=0.15),
            run_time=1.0,
        )
        self.wait(2.5)
        self.play(FadeOut(VGroup(header, chess_col, go_col, div)), run_time=0.8)
        self.wait(0.15)

    def _phase_closing(self):
        l1 = Tex(
            r"The winning systems did not become superhuman\\by imitating human thought.",
            font_size=30, color=GRAY_C,
        )
        l2 = Tex(
            r"They became superhuman by\\searching, learning, and scaling.",
            font_size=34, color=WHITE,
        )
        VGroup(l1, l2).arrange(DOWN, buff=0.68).move_to(ORIGIN)

        self.play(FadeIn(l1, shift=UP * 0.1), run_time=1.0)
        self.wait(0.7)
        self.play(FadeIn(l2, shift=UP * 0.1), run_time=1.0)
        self.wait(3.2)
        self.play(FadeOut(VGroup(l1, l2)), run_time=1.0)
