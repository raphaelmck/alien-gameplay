from manim import *
import numpy as np


class EvaluationScene(Scene):
    """Scene 4 – Evaluation: scoring the frontier, backing up values."""

    BG     = "#000000"
    C_NODE = "#A78BFA"
    C_EDGE = "#3A3A3A"
    C_LIM  = "#FF6B6B"
    C_EST  = "#F0A500"
    C_TRUE = "#5B9BD5"
    C_BOX  = "#A78BFA"
    C_POS  = "#50C878"
    C_NEG  = "#FF6B6B"

    NODE_R = 0.22

    ROOT_POS = np.array([ 0.0,  2.6, 0.0])
    D1_POS   = [np.array([-2.5,  1.1, 0.0]),
                np.array([ 2.5,  1.1, 0.0])]
    D2_POS   = [np.array([-3.8, -0.4, 0.0]),
                np.array([-1.3, -0.4, 0.0]),
                np.array([ 1.3, -0.4, 0.0]),
                np.array([ 3.8, -0.4, 0.0])]

    LIMIT_Y = -1.1

    # D1 nodes are MIN; root is MAX
    # min(+0.4, -0.2) = -0.2   min(+0.7, +0.3) = +0.3   max(-0.2, +0.3) = +0.3
    D2_SCORES  = [+0.4, -0.2, +0.7, +0.3]
    D1_SCORES  = [-0.2, +0.3]
    ROOT_SCORE = +0.3

    def construct(self):
        self.camera.background_color = self.BG
        self._phase_horizon()
        self._phase_frontier()
        self._phase_evaluator()
        self._phase_backup()
        self._phase_morph()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _node(self, pos, color=None, r=None, opacity=1.0):
        color = color or self.C_NODE
        r     = r     or self.NODE_R
        d = Dot(pos, radius=r, color=color)
        d.set_fill(color, opacity=opacity)
        d.set_stroke(width=0)
        return d

    def _edge(self, p1, p2, opacity=1.0, width=1.4):
        l = Line(p1, p2, color=self.C_EDGE, stroke_width=width)
        l.set_stroke(opacity=opacity)
        return l

    def _score_label(self, val, font_size=26):
        col = self.C_POS if val >= 0 else self.C_NEG
        return MathTex(f"{val:+.1f}", font_size=font_size, color=col)

    # ── phases ────────────────────────────────────────────────────────────────

    def _phase_horizon(self):
        root = self._node(self.ROOT_POS)
        d1   = [self._node(p) for p in self.D1_POS]
        d2   = [self._node(p) for p in self.D2_POS]

        e01 = [self._edge(self.ROOT_POS, p) for p in self.D1_POS]
        e12 = [
            self._edge(self.D1_POS[0], self.D2_POS[0]),
            self._edge(self.D1_POS[0], self.D2_POS[1]),
            self._edge(self.D1_POS[1], self.D2_POS[2]),
            self._edge(self.D1_POS[1], self.D2_POS[3]),
        ]

        self.play(GrowFromCenter(root), run_time=0.4)
        self.play(
            LaggedStart(*[Create(e) for e in e01], lag_ratio=0.15),
            LaggedStart(*[GrowFromCenter(n) for n in d1], lag_ratio=0.15),
            run_time=0.65,
        )
        self.play(
            LaggedStart(*[Create(e) for e in e12], lag_ratio=0.08),
            LaggedStart(*[GrowFromCenter(n) for n in d2], lag_ratio=0.08),
            run_time=0.85,
        )
        self.wait(0.2)

        limit = DashedLine(
            np.array([-5.6, self.LIMIT_Y, 0.0]),
            np.array([ 5.6, self.LIMIT_Y, 0.0]),
            color=self.C_LIM, stroke_width=2.5, dash_length=0.18,
        )
        self.play(Create(limit), run_time=0.8)

        t1 = Text("Search stops here.", font_size=26, color=self.C_LIM)
        t2 = Text("The game does not.", font_size=26, color=GRAY_C)
        txt = VGroup(t1, t2).arrange(DOWN, buff=0.24)
        txt.move_to(np.array([0.0, self.LIMIT_Y - 1.0, 0.0]))

        self.play(FadeIn(t1, shift=UP * 0.1), run_time=0.55)
        self.play(FadeIn(t2, shift=UP * 0.1), run_time=0.55)
        self.wait(1.8)

        fog = Rectangle(
            width=config.frame_width + 1.0, height=9.0,
            fill_color=BLACK, fill_opacity=0.0, stroke_width=0,
        )
        fog.move_to(np.array([0.0, self.LIMIT_Y - 0.08 - 4.5, 0.0]))
        self.add(fog)
        self.play(
            fog.animate.set_fill(opacity=0.92),
            FadeOut(txt),
            run_time=0.8,
        )
        self.wait(0.1)

        self._root  = root
        self._d1    = d1
        self._d2    = d2
        self._e01   = e01
        self._e12   = e12
        self._limit = limit
        self._fog   = fog

    def _phase_frontier(self):
        # Ghost branches peering into fog
        rng = np.random.default_rng(17)
        fog_branches = VGroup()
        for pos in self.D2_POS:
            px, py = pos[0], pos[1]
            branch_roots = []
            for _ in range(5):
                ang = rng.uniform(-0.55, 0.55)
                ln  = rng.uniform(0.40, 0.80)
                x2  = px + np.sin(ang) * ln
                y2  = py - np.cos(ang) * ln * 0.85
                fog_branches.add(
                    Line(pos, np.array([x2, y2, 0.0]),
                         color=GRAY_E, stroke_width=0.7, stroke_opacity=0.0)
                )
                branch_roots.append((x2, y2, ang))
            for (x2, y2, ang) in branch_roots:
                for _ in range(2):
                    ang2 = ang + rng.uniform(-0.40, 0.40)
                    ln2  = rng.uniform(0.25, 0.55)
                    x3   = x2 + np.sin(ang2) * ln2
                    y3   = y2 - np.cos(ang2) * ln2 * 0.85
                    fog_branches.add(
                        Line(np.array([x2, y2, 0.0]), np.array([x3, y3, 0.0]),
                             color=GRAY_E, stroke_width=0.45, stroke_opacity=0.0)
                    )
        self.add(fog_branches)

        not_ending = Tex(r"not endings --- game continues", font_size=28, color=GRAY_C)
        not_ending.move_to(np.array([0.0, self.LIMIT_Y - 0.62, 0.0]))

        # Build leaf triangle groups: top vertex aligned with edge endpoint (dot center),
        # single disc only at the top tip.
        leaf_groups = []
        transforms  = []
        for dot in self._d2:
            tri = Triangle(color=self.C_NODE, fill_opacity=0.12, stroke_width=1.5)
            tri.scale(0.32)
            # shift so the top vertex lands exactly at the edge endpoint
            tri.shift(dot.get_center() - tri.get_top())
            tip_dot = Dot(dot.get_center(), radius=0.07, color=self.C_NODE)
            tip_dot.set_fill(self.C_NODE, opacity=0.9)
            grp = VGroup(tri, tip_dot)
            leaf_groups.append(grp)
            transforms.append(ReplacementTransform(dot, grp))

        # Branches reveal, text fades in, and circles smoothly morph to triangles together
        self.play(
            *[b.animate.set_stroke(opacity=0.14) for b in fog_branches],
            FadeIn(not_ending, shift=UP * 0.08),
            *transforms,
            run_time=0.9,
            rate_func=smooth,
        )
        self.wait(1.5)
        self.play(FadeOut(not_ending), run_time=0.4)
        self.play(FadeOut(self._limit), run_time=0.5)

        self._d2          = leaf_groups
        self._fog_branches = fog_branches

    def _phase_evaluator(self):
        eval_box = RoundedRectangle(
            width=2.0, height=1.1, corner_radius=0.20,
            fill_color=self.C_BOX, fill_opacity=0.14,
            stroke_color=self.C_BOX, stroke_width=2.5,
        )
        eval_box.move_to(np.array([0.0, -2.1, 0.0]))
        eval_lbl = MathTex(r"\hat{V}_\theta", font_size=38, color=self.C_BOX)
        eval_lbl.move_to(eval_box.get_center())

        score_txt = Text("Score the frontier.", font_size=24, color=GRAY_B)
        score_txt.to_edge(DOWN, buff=0.48)

        # Box appears first, label writes in after
        self.play(GrowFromCenter(eval_box), run_time=0.5)
        self.wait(0.1)
        self.play(Write(eval_lbl), run_time=0.5)
        self.play(FadeIn(score_txt, shift=UP * 0.1), run_time=0.5)
        self.wait(0.25)

        score_lbls = []
        for dot, val in zip(self._d2, self.D2_SCORES):
            stex = self._score_label(val, font_size=24)
            stex.next_to(dot, DOWN, buff=0.16)
            self.play(eval_box.animate.set_fill(opacity=0.42), run_time=0.22)
            self.play(
                GrowFromCenter(stex),
                eval_box.animate.set_fill(opacity=0.14),
                run_time=0.38,
            )
            score_lbls.append(stex)

        self.wait(1.0)
        self.play(FadeOut(score_txt), run_time=0.4)
        # Lock fill state explicitly so subsequent animations don't trigger a blink
        eval_box.set_fill(self.C_BOX, opacity=0.14)

        self._eval_box   = eval_box
        self._eval_lbl   = eval_lbl
        self._score_lbls = score_lbls

    def _phase_backup(self):
        min_tags = [
            Text("MIN", font_size=13, color=GRAY_D).next_to(d, RIGHT, buff=0.12)
            for d in self._d1
        ]
        max_tag = Text("MAX", font_size=13, color=GRAY_D).next_to(
            self._root, RIGHT, buff=0.12
        )

        self.play(
            *[FadeIn(t, shift=LEFT * 0.06) for t in min_tags],
            FadeIn(max_tag, shift=LEFT * 0.06),
            run_time=0.55,
        )
        self.wait(0.25)

        # D2 → D1: ghost copies flow upward, result grows as they arrive
        d1_score_lbls = []
        for i, (d1_dot, d1_val) in enumerate(zip(self._d1, self.D1_SCORES)):
            gl = self._score_lbls[i * 2].copy()
            gr = self._score_lbls[i * 2 + 1].copy()
            self.add(gl, gr)

            stex = self._score_label(d1_val, font_size=24)
            stex.next_to(d1_dot, DOWN, buff=0.16)

            self.play(
                gl.animate.move_to(d1_dot.get_center()).set_opacity(0),
                gr.animate.move_to(d1_dot.get_center()).set_opacity(0),
                GrowFromCenter(stex),
                run_time=1.0,
                rate_func=smooth,
            )
            self.remove(gl, gr)
            d1_score_lbls.append(stex)

        self.wait(0.2)

        # D1 → root backup
        root_stex = self._score_label(self.ROOT_SCORE, font_size=30)
        root_stex.next_to(max_tag, RIGHT, buff=0.18)

        gl2 = d1_score_lbls[0].copy()
        gr2 = d1_score_lbls[1].copy()
        self.add(gl2, gr2)
        self.play(
            gl2.animate.move_to(self._root.get_center()).set_opacity(0),
            gr2.animate.move_to(self._root.get_center()).set_opacity(0),
            GrowFromCenter(root_stex),
            run_time=1.1,
            rate_func=smooth,
        )
        self.remove(gl2, gr2)
        self.wait(0.35)

        approx = MathTex(
            r"\hat{V}_\theta(s) \;\approx\; V(s)", font_size=40, color=GRAY_B
        )
        approx.to_edge(DOWN, buff=0.52)
        self.play(Write(approx), run_time=0.85)
        self.wait(2.0)

        compress = Tex(
            r"A huge future, compressed into one number.",
            font_size=22, color=GRAY_C,
        )
        compress.move_to(DOWN * 3.4)
        self.play(
            FadeOut(approx, shift=UP * 0.06),
            FadeIn(compress, shift=UP * 0.06),
            run_time=0.6,
        )
        self.wait(1.8)

        # limit is already gone (faded in _phase_frontier); eval_box/lbl stay for morph
        all_tree = VGroup(
            self._root, *self._d1, *self._d2,
            *self._e01, *self._e12,
            self._fog, self._fog_branches,
            *self._score_lbls, *d1_score_lbls, root_stex,
            *min_tags, max_tag, compress,
        )
        self.play(FadeOut(all_tree), run_time=1.0)
        self.wait(0.2)

    def _phase_morph(self):
        eval_box = self._eval_box
        eval_lbl = self._eval_lbl

        big_box = RoundedRectangle(
            width=3.8, height=2.8, corner_radius=0.28,
            fill_color=self.C_BOX, fill_opacity=0.14,
            stroke_color=self.C_BOX, stroke_width=2.5,
        )
        big_box.move_to(ORIGIN)
        big_lbl = MathTex(r"\hat{V}_\theta", font_size=40, color=self.C_BOX)
        big_lbl.next_to(big_box, UP, buff=0.22)

        self.play(
            ReplacementTransform(eval_box, big_box),
            ReplacementTransform(eval_lbl, big_lbl),
            run_time=0.85,
        )
        self.wait(0.2)

        # ── interior layout helper ────────────────────────────────────────────
        def _make_interior(title_str, title_color, items):
            checks = VGroup(*[
                MathTex(r"\checkmark", font_size=20, color=self.C_TRUE)
                for _ in items
            ])
            feats = VGroup(*[
                Tex(t, font_size=20, color=GRAY_B)
                for t in items
            ])
            checks.arrange(DOWN, buff=0.28)
            feats.arrange(DOWN, buff=0.28, aligned_edge=LEFT)
            content = VGroup(checks, feats).arrange(RIGHT, buff=0.14)
            content.move_to(big_box.get_center() + DOWN * 0.12)
            title = Tex(rf"\textbf{{{title_str}}}", font_size=22, color=title_color)
            title.move_to(big_box.get_center() + UP * 1.05)
            return VGroup(title, content), content[0], content[1]

        # ── Chess hand-coded ──────────────────────────────────────────────────
        chess_items = ["material count", "king safety", "pawn structure", "mobility"]
        chess_grp, chess_checks, chess_feats = _make_interior(
            "hand-coded (Chess)", self.C_TRUE, chess_items
        )
        chess_title = chess_grp[0]

        self.play(
            FadeIn(chess_title, shift=DOWN * 0.08),
            LaggedStart(
                *[FadeIn(VGroup(chess_checks[i], chess_feats[i]), shift=RIGHT * 0.08)
                  for i in range(len(chess_items))],
                lag_ratio=0.18,
            ),
            run_time=1.1,
        )
        self.wait(1.4)

        # ── Go hand-coded ─────────────────────────────────────────────────────
        go_items = ["territory counting", "life and death", "influence", "ko fights"]
        go_grp, go_checks, go_feats = _make_interior(
            "hand-coded (Go)", self.C_TRUE, go_items
        )
        go_title = go_grp[0]

        self.play(FadeOut(chess_grp, shift=LEFT * 0.12), run_time=0.45)
        self.play(
            FadeIn(go_title, shift=DOWN * 0.08),
            LaggedStart(
                *[FadeIn(VGroup(go_checks[i], go_feats[i]), shift=RIGHT * 0.08)
                  for i in range(len(go_items))],
                lag_ratio=0.18,
            ),
            run_time=1.1,
        )
        self.wait(1.4)

        # ── Neural-network interior ───────────────────────────────────────────
        # Center the graph slightly below the box center
        nc     = big_box.get_center() + DOWN * 0.15
        inp_ys = [+0.52,  0.0, -0.52]
        hid_ys = [+0.26, -0.26]

        def _nd(x, y, col):
            d = Dot(np.array([x, y, 0.0]), radius=0.13, color=col)
            d.set_fill(col, opacity=0.85)
            return d

        inp_dots = VGroup(*[_nd(nc[0] - 0.88, nc[1] + y, self.C_EST) for y in inp_ys])
        hid_dots = VGroup(*[_nd(nc[0],          nc[1] + y, self.C_EST) for y in hid_ys])
        out_dot  = _nd(nc[0] + 0.88, nc[1], self.C_EST)

        nn_edges = VGroup()
        for iy in inp_ys:
            for hy in hid_ys:
                nn_edges.add(Line(
                    np.array([nc[0] - 0.88, nc[1] + iy, 0.0]),
                    np.array([nc[0],          nc[1] + hy, 0.0]),
                    color=self.C_EST, stroke_width=0.9, stroke_opacity=0.38,
                ))
        for hy in hid_ys:
            nn_edges.add(Line(
                np.array([nc[0],        nc[1] + hy, 0.0]),
                np.array([nc[0] + 0.88, nc[1],       0.0]),
                color=self.C_EST, stroke_width=0.9, stroke_opacity=0.38,
            ))

        nn_title = Tex(r"\textbf{neural network}", font_size=22, color=self.C_EST)
        nn_title.move_to(big_box.get_center() + UP * 1.05)

        nn_interior = VGroup(nn_title, nn_edges, inp_dots, hid_dots, out_dot)

        self.play(FadeOut(go_grp, shift=LEFT * 0.12), run_time=0.45)
        self.play(
            FadeIn(nn_title, shift=DOWN * 0.08),
            Create(nn_edges),
            LaggedStart(
                *[GrowFromCenter(d) for d in [*inp_dots, *hid_dots, out_dot]],
                lag_ratio=0.1,
            ),
            run_time=1.0,
        )
        self.wait(1.2)

        caption = Tex(r"The machinery changed. The role did not.",
                      font_size=22, color=GRAY_C)
        caption.to_edge(DOWN, buff=0.55)
        self.play(FadeIn(caption, shift=UP * 0.1), run_time=0.65)
        self.wait(2.5)

        self.play(
            FadeOut(VGroup(big_box, big_lbl, nn_interior, caption)),
            run_time=1.0,
        )
        self.wait(0.4)
