from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class BitterLessonScene(Scene):
    BG      = "#000000"
    C_HUMAN = "#F0A500"
    C_SCALE = "#A78BFA"
    C_PLAT  = "#FF5555"
    C_AXIS  = "#444444"

    @staticmethod
    def _f_human(t):
        return 0.60 * (1.0 - np.exp(-8.5 * t))

    @staticmethod
    def _f_scale(t):
        if t < 0.12:
            return 0.0
        return 0.96 * ((t - 0.12) / 0.88) ** 1.25

    def construct(self):
        self.camera.background_color = self.BG
        self._phase_two_boxes()
        self._phase_graph()

    # ── text-only card (human knowledge) ─────────────────────────────────────

    def _make_inner_card(self, text, color):
        bg = RoundedRectangle(
            width=4.4, height=0.56, corner_radius=0.08,
            fill_color="#0D0900" if color == self.C_HUMAN else "#090614",
            fill_opacity=1.0,
            stroke_color=color, stroke_width=1.3,
        )
        lbl = Tex(text, font_size=15, color=color)
        lbl.move_to(bg)
        return VGroup(bg, lbl)

    # ── visual card (ML methods) ──────────────────────────────────────────────

    def _make_ml_card(self, visual, text):
        bg = RoundedRectangle(
            width=4.4, height=0.84, corner_radius=0.08,
            fill_color="#090614", fill_opacity=1.0,
            stroke_color=self.C_SCALE, stroke_width=1.3,
        )
        lbl = Tex(text, font_size=15, color=self.C_SCALE)
        content = VGroup(visual, lbl).arrange(RIGHT, buff=0.26)
        content.move_to(bg)
        return VGroup(bg, content)

    # ── mini diagrams for ML methods ──────────────────────────────────────────

    def _vis_prob_bar(self, value=0.73):
        """Horizontal probability gauge."""
        w, h = 0.84, 0.28
        bg = Rectangle(width=w, height=h,
                       fill_color="#0a0618", fill_opacity=1.0,
                       stroke_color=self.C_SCALE, stroke_width=0.8)
        fill = Rectangle(width=w * value, height=h,
                         fill_color=self.C_SCALE, fill_opacity=0.82, stroke_width=0)
        fill.align_to(bg, LEFT)
        return VGroup(bg, fill)

    def _vis_policy_hist(self):
        """Bar chart showing a policy distribution over five moves."""
        vals    = [0.31, 0.18, 0.24, 0.12, 0.15]
        max_h   = 0.42
        bars    = VGroup()
        for v in vals:
            bar = Rectangle(
                width=0.12,
                height=max_h * v / max(vals),
                fill_color=self.C_SCALE,
                fill_opacity=min(0.50 + v * 1.4, 1.0),
                stroke_width=0,
            )
            bars.add(bar)
        bars.arrange(RIGHT, buff=0.05, aligned_edge=DOWN)
        base = Line(bars.get_left(), bars.get_right(),
                    stroke_color=GRAY_D, stroke_width=0.6)
        base.next_to(bars, DOWN, buff=0.02)
        return VGroup(bars, base)

    def _vis_mini_tree(self):
        """Two-level branching search tree."""
        root = ORIGIN
        l1   = [LEFT * 0.30 + UP * 0.22, UP * 0.22, RIGHT * 0.30 + UP * 0.22]
        g    = VGroup(Dot(root, radius=0.055, color=self.C_SCALE))
        for p in l1:
            g.add(
                Line(root, p, stroke_color=self.C_SCALE,
                     stroke_width=0.9, stroke_opacity=0.70),
                Dot(p, radius=0.045, color=self.C_SCALE, fill_opacity=0.85),
            )
        for parent in [l1[0], l1[2]]:
            for dx in [-0.15, 0.15]:
                p2 = parent + RIGHT * dx + UP * 0.18
                g.add(
                    Line(parent, p2, stroke_color=self.C_SCALE,
                         stroke_width=0.6, stroke_opacity=0.50),
                    Dot(p2, radius=0.030, color=self.C_SCALE, fill_opacity=0.65),
                )
        return g

    # ── phase 1: two side-by-side boxes ──────────────────────────────────────

    def _phase_two_boxes(self):
        left_box = RoundedRectangle(
            width=5.4, height=4.7, corner_radius=0.22,
            fill_color="#0D0900", fill_opacity=1.0,
            stroke_color=self.C_HUMAN, stroke_width=2.2,
        )
        right_box = RoundedRectangle(
            width=5.4, height=4.7, corner_radius=0.22,
            fill_color="#090614", fill_opacity=1.0,
            stroke_color=self.C_SCALE, stroke_width=2.2,
        )
        left_box.move_to(LEFT * 3.0 + DOWN * 0.35)
        right_box.move_to(RIGHT * 3.0 + DOWN * 0.35)

        # Draw both rectangles first
        self.play(Create(left_box), Create(right_box), run_time=0.75)

        # Titles outside / above
        left_title  = Tex(r"\textbf{Human Knowledge}", font_size=26, color=self.C_HUMAN)
        right_title = Tex(r"\textbf{ML Methods}",      font_size=26, color=self.C_SCALE)
        left_title.next_to(left_box,  UP, buff=0.24)
        right_title.next_to(right_box, UP, buff=0.24)
        self.play(Write(left_title), Write(right_title), run_time=0.6)

        # ── Human knowledge inner cards ──────────────────────────────────────
        human_cards = VGroup(
            self._make_inner_card(r"pawn $= 1$\,pt \quad rook $= 5$\,pt",       self.C_HUMAN),
            self._make_inner_card(r"king safety $+0.3$ per defended square",     self.C_HUMAN),
            self._make_inner_card(r"open file bonus \quad doubled pawn penalty", self.C_HUMAN),
            self._make_inner_card(r"Go: corner before centre",                   self.C_HUMAN),
            self._make_inner_card(r"fork patterns \quad pin and skewer",         self.C_HUMAN),
        )
        human_cards.arrange(DOWN, buff=0.14)
        dots_left    = Tex(r"$\vdots$", font_size=28, color=self.C_HUMAN)
        left_content = VGroup(human_cards, dots_left)
        left_content.arrange(DOWN, buff=0.16)
        left_content.move_to(left_box)  # fix final positions while box is in place

        # Slide each card in one by one from off-screen left
        final_pos = [c.get_center().copy() for c in human_cards]
        for card, fp in zip(human_cards, final_pos):
            card.move_to(np.array([-8.5, fp[1], 0.0]))

        for card, fp in zip(human_cards, final_pos):
            self.play(card.animate.move_to(fp), run_time=0.45, rate_func=smooth)

        self.play(FadeIn(dots_left), run_time=0.3)

        # ── ML Methods: visual diagram cards ────────────────────────────────
        scale_cards = VGroup(
            self._make_ml_card(self._vis_prob_bar(0.73), r"win probability"),
            self._make_ml_card(self._vis_policy_hist(), r"move policy $\pi(a|s)$"),
            self._make_ml_card(self._vis_mini_tree(),   r"tree search depth $40$"),
        )
        scale_cards.arrange(DOWN, buff=0.30)
        dots_right    = Tex(r"$\vdots$", font_size=28, color=self.C_SCALE)
        right_content = VGroup(scale_cards, dots_right)
        right_content.arrange(DOWN, buff=0.22)
        right_content.move_to(right_box)

        self.play(
            LaggedStart(*[GrowFromCenter(c) for c in scale_cards], lag_ratio=0.25),
            run_time=1.0,
        )
        self.play(FadeIn(dots_right), run_time=0.3)
        self.wait(1.5)

        self.play(
            FadeOut(VGroup(
                left_box,  right_box,
                left_title, right_title,
                left_content, right_content,
            )),
            run_time=0.7,
        )
        self.wait(0.15)

    # ── phase 2: comparison graph ─────────────────────────────────────────────

    def _phase_graph(self):
        orig = LEFT * 5.5 + DOWN * 2.8
        aw, ah = 9.5, 4.8

        def pt(t, y):
            return np.array([orig[0] + t * aw, orig[1] + y * ah, 0.0])

        def make_curve(f, color, n=300):
            pts = [pt(i / (n - 1), f(i / (n - 1))) for i in range(n)]
            c = VMobject(color=color, stroke_width=3.5)
            c.set_points_smoothly(pts)
            return c

        # ── axes ──────────────────────────────────────────────────────────────
        x_ax = Arrow(orig, orig + RIGHT * (aw + 0.5),
                     color=self.C_AXIS, stroke_width=2.0, buff=0,
                     max_tip_length_to_length_ratio=0.025)
        y_ax = Arrow(orig, orig + UP * (ah + 0.5),
                     color=self.C_AXIS, stroke_width=2.0, buff=0,
                     max_tip_length_to_length_ratio=0.03)
        x_lbl = Tex(r"Computation / Time", font_size=20, color=GRAY_B)
        x_lbl.next_to(x_ax.get_right(), DOWN, buff=0.24)
        y_lbl = Tex(r"Performance", font_size=20, color=GRAY_B)
        y_lbl.next_to(y_ax.get_top(), UP, buff=0.16)

        self.play(Create(x_ax), Create(y_ax), run_time=0.6)
        self.play(Write(x_lbl), Write(y_lbl), run_time=0.5)

        # ── human curve → human label ─────────────────────────────────────────
        h_curve = make_curve(self._f_human, self.C_HUMAN)
        plat_y  = self._f_human(1.0)   # ≈ 0.60

        # Both labels share the same y (above the scale curve's peak ≈ 1.81)
        common_y = 2.10

        h_lbl = Tex(r"human knowledge", font_size=16, color=self.C_HUMAN)
        h_lbl.set_y(common_y)
        h_lbl.align_to(np.array([orig[0] + 0.06 * aw, 0.0, 0.0]), LEFT)

        self.play(Create(h_curve), run_time=1.6, rate_func=smooth)
        self.play(Write(h_lbl), run_time=0.4)

        # ── plateau (extended to the left) ────────────────────────────────────
        plat_line = DashedLine(
            pt(0.18, plat_y), pt(1.00, plat_y),
            color=self.C_PLAT, stroke_width=2.5,
            dash_length=0.16, stroke_opacity=0.92,
        )
        plat_lbl = Tex(r"plateau", font_size=17, color=self.C_PLAT)
        plat_lbl.move_to(pt(0.60, plat_y + 0.15))
        self.play(Create(plat_line), run_time=0.6)
        self.play(Write(plat_lbl), run_time=0.4)
        self.wait(0.4)

        # ── scale curve → scale label ─────────────────────────────────────────
        s_curve = make_curve(self._f_scale, self.C_SCALE)

        s_lbl = Tex(r"search $+$ learning $+$ compute", font_size=16, color=self.C_SCALE)
        s_lbl.set_y(common_y)
        s_lbl.align_to(np.array([orig[0] + 0.83 * aw, 0.0, 0.0]), LEFT)

        self.play(Create(s_curve), run_time=2.2, rate_func=smooth)
        self.play(Write(s_lbl), run_time=0.5)
        self.wait(0.3)

        # ── overtake pulse ─────────────────────────────────────────────────────
        cross_t     = 0.72
        cross_point = pt(cross_t, self._f_human(cross_t))

        ring = Circle(radius=0.22, fill_opacity=0, stroke_color=WHITE, stroke_width=3.0)
        ring.move_to(cross_point)
        self.add(ring)
        self.play(ring.animate.scale(5.5).set_opacity(0), run_time=0.85, rate_func=ease_out_quad)
        self.remove(ring)

        overtake_lbl = Tex(r"overtake", font_size=16, color=WHITE)
        overtake_lbl.move_to(cross_point + LEFT * 0.70 + UP * 0.42)
        self.play(Write(overtake_lbl), run_time=0.4)

        self.play(
            h_curve.animate.set_stroke(opacity=0.28),
            plat_line.animate.set_stroke(opacity=0.28),
            plat_lbl.animate.set_opacity(0.28),
            h_lbl.animate.set_opacity(0.28),
            run_time=0.7,
        )

        # ── breakthrough (left of the curve) ──────────────────────────────────
        brk_t     = 0.91
        brk_point = pt(brk_t, self._f_scale(brk_t))
        brk_dot   = Dot(brk_point, radius=0.10, color=self.C_SCALE)
        brk_lbl   = Tex(r"breakthrough", font_size=16, color=self.C_SCALE)
        brk_lbl.move_to(brk_point + LEFT * 1.30 + UP * 0.12)

        self.play(GrowFromCenter(brk_dot), Write(brk_lbl), run_time=0.6)
        self.wait(1.2)

        # ── title + attribution (graph stays) ─────────────────────────────────
        title  = Tex(r"\textbf{The Bitter Lesson}", font_size=44, color=WHITE)
        credit = Tex(r"---\,Richard Sutton, 2019",   font_size=22, color=GRAY_D)
        title_grp = VGroup(title, credit).arrange(DOWN, buff=0.22)
        title_grp.to_edge(UP, buff=0.35)

        self.play(Write(title),  run_time=0.9)
        self.play(Write(credit), run_time=0.5)
        self.wait(2.5)

        # ── fade everything ────────────────────────────────────────────────────
        self.play(
            FadeOut(VGroup(
                x_ax, y_ax, x_lbl, y_lbl,
                h_curve, s_curve,
                plat_line, plat_lbl,
                h_lbl, s_lbl,
                overtake_lbl,
                brk_dot, brk_lbl,
                title, credit,
            )),
            run_time=1.0,
        )
