from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class EvaluationScene(Scene):
    """Scene 4 – Evaluation functions: approximating the value function."""

    BG      = "#000000"
    C_TRUE  = "#5B9BD5"   # blue  — true value V(s)
    C_EST   = "#F0A500"   # orange — estimated value V̂(s)
    C_BOX   = "#A78BFA"   # purple — evaluator box
    C_POS   = "#50C878"   # green — positive score
    C_HAND  = "#5B9BD5"   # blue  — hand-coded card
    C_NN    = "#F0A500"   # orange — neural-network card

    N       = 5
    SIDE    = 2.2
    STONE_R = 0.18

    def construct(self):
        self.camera.background_color = self.BG
        self.SP = self.SIDE / (self.N - 1)
        self._phase_bridge()
        self._phase_notation()
        self._phase_blackbox()
        self._phase_two_approaches()
        self._phase_collapse()

    # ─── board helpers ────────────────────────────────────────────────────────

    def _gp(self, bc, i, j):
        x = bc[0] - self.SIDE / 2 + i * self.SP
        y = bc[1] - self.SIDE / 2 + j * self.SP
        return np.array([x, y, 0.0])

    def _make_board(self, bc):
        bg = Square(side_length=self.SIDE + 0.3)
        bg.set_fill("#C8A96E", opacity=1).set_stroke(width=0)
        bg.move_to(bc)
        lines = VGroup()
        s2, sp = self.SIDE / 2, self.SP
        for k in range(self.N):
            t = -s2 + k * sp
            lines.add(Line([bc[0] + t, bc[1] - s2, 0], [bc[0] + t, bc[1] + s2, 0],
                           color="#2A2A2A", stroke_width=1.2))
            lines.add(Line([bc[0] - s2, bc[1] + t, 0], [bc[0] + s2, bc[1] + t, 0],
                           color="#2A2A2A", stroke_width=1.2))
        return bg, lines

    def _make_stone(self, col):
        c = Circle(radius=self.STONE_R)
        c.set_fill(col, opacity=1)
        c.set_stroke(color="#C0C0C0" if col == "#F5F5F5" else "#3A3A3A", width=1.0)
        return c

    # ─── phases ──────────────────────────────────────────────────────────────

    def _phase_bridge(self):
        l1 = Text("The search must stop.", font_size=40, color=WHITE)
        l2 = Text("But we still need to judge the position.", font_size=28, color=GRAY_C)
        g  = VGroup(l1, l2).arrange(DOWN, buff=0.52).move_to(ORIGIN)

        self.play(FadeIn(l1, shift=UP * 0.14), run_time=0.9)
        self.wait(0.4)
        self.play(FadeIn(l2, shift=UP * 0.12), run_time=0.8)
        self.wait(1.8)
        self.play(FadeOut(g), run_time=0.7)
        self.wait(0.15)

    def _phase_notation(self):
        true_lbl = Text("true value", font_size=22, color=GRAY_C)
        true_eq  = MathTex(r"V(s)", font_size=64, color=self.C_TRUE)
        true_grp = VGroup(true_lbl, true_eq).arrange(DOWN, buff=0.22)
        true_grp.move_to(LEFT * 3.0)

        arr = Arrow(LEFT * 1.2, RIGHT * 1.2, color=GRAY_D,
                    stroke_width=3, max_tip_length_to_length_ratio=0.2)
        arr.move_to(ORIGIN)
        arr_lbl = Text("impossible to compute exactly", font_size=16, color=GRAY_D)
        arr_lbl.next_to(arr, UP, buff=0.12)

        est_lbl = Text("estimated value", font_size=22, color=GRAY_C)
        est_eq  = MathTex(r"\hat{V}_\theta(s)", font_size=64, color=self.C_EST)
        est_grp = VGroup(est_lbl, est_eq).arrange(DOWN, buff=0.22)
        est_grp.move_to(RIGHT * 3.0)

        approx = MathTex(
            r"\hat{V}_\theta(s) \;\approx\; V(s)",
            font_size=42, color=GRAY_B,
        )
        approx.move_to(DOWN * 1.9)

        self.play(FadeIn(true_grp, shift=RIGHT * 0.15), run_time=0.9)
        self.wait(0.35)
        self.play(GrowArrow(arr), FadeIn(arr_lbl, shift=DOWN * 0.08), run_time=0.7)
        self.play(FadeIn(est_grp, shift=LEFT * 0.15), run_time=0.9)
        self.wait(0.4)
        self.play(Write(approx), run_time=0.9)
        self.wait(1.8)
        self.play(FadeOut(VGroup(true_grp, arr, arr_lbl, est_grp, approx)), run_time=0.8)
        self.wait(0.2)

    def _phase_blackbox(self):
        # board → V̂θ → single number, then slide up to make room
        bc = np.array([-3.6, 0.0, 0.0])

        bg, lines = self._make_board(bc)
        stone_data = [
            (1, 3, "#1A1A1A"), (2, 3, "#F5F5F5"),
            (2, 2, "#1A1A1A"), (3, 2, "#F5F5F5"),
            (1, 1, "#F5F5F5"), (3, 3, "#1A1A1A"),
        ]
        stones = VGroup()
        for i, j, col in stone_data:
            s = self._make_stone(col)
            s.move_to(self._gp(bc, i, j))
            stones.add(s)
        board_grp = VGroup(bg, lines, stones)

        s_lbl = MathTex(r"s", font_size=34, color=self.C_TRUE)
        s_lbl.next_to(board_grp, DOWN, buff=0.26)

        arr_in = Arrow(
            np.array([bc[0] + self.SIDE / 2 + 0.30, 0.0, 0.0]),
            np.array([bc[0] + self.SIDE / 2 + 1.25, 0.0, 0.0]),
            color=GRAY_C, stroke_width=3, max_tip_length_to_length_ratio=0.22,
        )

        box = RoundedRectangle(
            width=2.1, height=1.35, corner_radius=0.22,
            fill_color=self.C_BOX, fill_opacity=0.14,
            stroke_color=self.C_BOX, stroke_width=2.5,
        )
        box.next_to(arr_in, RIGHT, buff=0.0)
        box_lbl = MathTex(r"\hat{V}_\theta", font_size=36, color=self.C_BOX)
        box_lbl.move_to(box.get_center())

        arr_out = Arrow(
            box.get_right() + RIGHT * 0.05,
            box.get_right() + RIGHT * 1.2,
            color=GRAY_C, stroke_width=3, max_tip_length_to_length_ratio=0.22,
        )

        score = MathTex(r"+0.73", font_size=54, color=self.C_POS)
        score.next_to(arr_out, RIGHT, buff=0.16)
        score_sub = Text("position value", font_size=17, color=GRAY_C)
        score_sub.next_to(score, DOWN, buff=0.18)

        self.play(GrowFromCenter(bg), run_time=0.6)
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.04), run_time=0.6)
        self.play(
            LaggedStart(*[GrowFromCenter(s) for s in stones], lag_ratio=0.12),
            FadeIn(s_lbl, shift=UP * 0.08),
            run_time=1.0,
        )
        self.wait(0.25)
        self.play(GrowArrow(arr_in), run_time=0.5)
        self.play(GrowFromCenter(box), Write(box_lbl), run_time=0.65)
        self.play(GrowArrow(arr_out), run_time=0.45)
        self.play(GrowFromCenter(score), FadeIn(score_sub, shift=UP * 0.08), run_time=0.65)
        self.wait(1.4)

        pipeline = VGroup(board_grp, s_lbl, arr_in, box, box_lbl, arr_out, score, score_sub)
        self.play(pipeline.animate.scale(0.78).to_edge(UP, buff=0.48), run_time=1.1)
        self.wait(0.2)
        self._pipeline = pipeline

    def _phase_two_approaches(self):
        # Left card: hand-coded features    Right card: neural network

        # ── shared card factory ───────────────────────────────────────────────
        def _card(color, x_centre):
            box = RoundedRectangle(
                width=3.0, height=2.9, corner_radius=0.22,
                fill_color=color, fill_opacity=0.08,
                stroke_color=color, stroke_width=2.0,
            )
            box.move_to(np.array([x_centre, -1.05, 0.0]))
            return box

        # ── hand-coded card ───────────────────────────────────────────────────
        hand_box   = _card(self.C_HAND, -3.2)
        hand_title = Text("hand-coded", font_size=22, color=self.C_HAND, weight="BOLD")
        hand_title.next_to(hand_box, UP, buff=0.18)

        feat_texts = ["material count", "king safety", "pawn structure", "mobility"]
        features   = VGroup(*[Text(t, font_size=17, color=GRAY_B) for t in feat_texts])
        features.arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        features.move_to(hand_box.get_center() + RIGHT * 0.18)

        checks = VGroup(*[Text("✓", font_size=17, color=self.C_HAND) for _ in feat_texts])
        checks.arrange(DOWN, buff=0.24)
        checks.next_to(features, LEFT, buff=0.14)

        hand_grp = VGroup(hand_box, hand_title, features, checks)

        # ── neural-network card ───────────────────────────────────────────────
        nn_box   = _card(self.C_NN, 3.2)
        nn_title = Text("neural network", font_size=22, color=self.C_NN, weight="BOLD")
        nn_title.next_to(nn_box, UP, buff=0.18)

        nc       = nn_box.get_center()
        inp_ys   = [0.52, 0.0, -0.52]
        hid_ys   = [0.26, -0.26]

        def _nd(x, y, col):
            d = Dot(np.array([x, y, 0.0]), radius=0.13, color=col)
            d.set_fill(col, opacity=0.85)
            return d

        inp_dots = VGroup(*[_nd(nc[0] - 0.75, nc[1] + y, self.C_NN) for y in inp_ys])
        hid_dots = VGroup(*[_nd(nc[0],          nc[1] + y, self.C_NN) for y in hid_ys])
        out_dot  = _nd(nc[0] + 0.75, nc[1], self.C_NN)

        nn_edges = VGroup()
        for iy in inp_ys:
            for hy in hid_ys:
                nn_edges.add(Line(
                    np.array([nc[0] - 0.75, nc[1] + iy, 0.0]),
                    np.array([nc[0],          nc[1] + hy, 0.0]),
                    color=self.C_NN, stroke_width=0.9, stroke_opacity=0.4,
                ))
        for hy in hid_ys:
            nn_edges.add(Line(
                np.array([nc[0],         nc[1] + hy, 0.0]),
                np.array([nc[0] + 0.75,  nc[1],      0.0]),
                color=self.C_NN, stroke_width=0.9, stroke_opacity=0.4,
            ))

        nn_grp = VGroup(nn_box, nn_title, nn_edges, inp_dots, hid_dots, out_dot)

        # ── divider + bottom note ─────────────────────────────────────────────
        divider = Line(
            np.array([0.0, -0.3, 0.0]), np.array([0.0, -3.0, 0.0]),
            color=GRAY_E, stroke_width=1.0,
        )
        role = Text("same role: compress a huge future into one number",
                    font_size=20, color=GRAY_C)
        role.to_edge(DOWN, buff=0.48)

        # ── animate ───────────────────────────────────────────────────────────
        self.play(
            LaggedStart(
                AnimationGroup(FadeIn(hand_box, shift=RIGHT * 0.15), Write(hand_title)),
                AnimationGroup(FadeIn(nn_box,   shift=LEFT  * 0.15), Write(nn_title)),
                lag_ratio=0.3,
            ),
            Create(divider),
            run_time=1.1,
        )
        self.play(
            LaggedStart(
                *[FadeIn(VGroup(checks[i], features[i]), shift=RIGHT * 0.1)
                  for i in range(len(feat_texts))],
                lag_ratio=0.18,
            ),
            run_time=1.2,
        )
        self.play(
            Create(nn_edges),
            LaggedStart(
                *[GrowFromCenter(d) for d in [*inp_dots, *hid_dots, out_dot]],
                lag_ratio=0.1,
            ),
            run_time=1.1,
        )
        self.play(FadeIn(role, shift=UP * 0.1), run_time=0.7)
        self.wait(2.0)

        self._two_cards = VGroup(hand_grp, nn_grp, divider, role)

    def _phase_collapse(self):
        # The whole future tree collapses into one scalar — key visual
        self.play(FadeOut(self._two_cards), FadeOut(self._pipeline), run_time=0.9)
        self.wait(0.15)

        # Triangle representing the uncharted future tree
        tree_tri = Triangle(stroke_color=GRAY_D, stroke_width=1.5, fill_opacity=0)
        tree_tri.set_width(4.6).set_height(3.0).rotate(PI)
        tree_tri.move_to(LEFT * 2.4 + UP * 0.2)

        rng = np.random.default_rng(7)
        density_dots = VGroup()
        cx, cy = LEFT[0] * 2.4, 0.2
        for _ in range(40):
            rx = rng.uniform(-1.9, 1.9)
            ry = rng.uniform(-1.3, 1.3)
            if abs(rx) < (1.55 - abs(ry) * 0.65):
                d = Dot(np.array([cx + rx, cy + ry, 0.0]),
                        radius=0.042, color=GRAY_E)
                d.set_fill(GRAY_E, opacity=rng.uniform(0.2, 0.6))
                density_dots.add(d)

        root_lbl = MathTex(r"s", font_size=30, color=self.C_TRUE)
        root_lbl.next_to(tree_tri, UP, buff=0.16)
        tree_grp = VGroup(tree_tri, density_dots, root_lbl)

        arr = Arrow(
            np.array([-0.4, 0.2, 0.0]),
            np.array([ 1.8, 0.2, 0.0]),
            color=GRAY_C, stroke_width=3,
            max_tip_length_to_length_ratio=0.14,
        )

        result = MathTex(r"\hat{V}_\theta(s) = +0.73", font_size=46, color=self.C_EST)
        result.move_to(RIGHT * 3.6 + UP * 0.2)

        compress = Text("one number\nfor the whole future", font_size=20, color=GRAY_C,
                        line_spacing=1.35)
        compress.next_to(result, DOWN, buff=0.36)

        self.play(
            Create(tree_tri),
            LaggedStart(*[GrowFromCenter(d) for d in density_dots], lag_ratio=0.04),
            FadeIn(root_lbl, shift=DOWN * 0.08),
            run_time=1.2,
        )
        self.wait(0.3)
        self.play(GrowArrow(arr), run_time=0.6)

        # Tree collapses into the scalar
        self.play(
            tree_grp.animate.scale(0.04).move_to(arr.get_left()).set_opacity(0),
            GrowFromCenter(result),
            run_time=1.4, rate_func=ease_out_quad,
        )
        self.play(FadeIn(compress, shift=UP * 0.1), run_time=0.6)
        self.wait(2.5)

        self.play(FadeOut(VGroup(arr, result, compress)), run_time=1.1)
        self.wait(0.4)
