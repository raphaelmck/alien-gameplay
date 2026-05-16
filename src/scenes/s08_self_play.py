from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class SelfPlayScene(Scene):
    """Scene 8 – Self-play as data generation."""

    BG       = "#000000"
    C_NET    = "#A78BFA"   # purple — network
    C_PLAY   = "#5B9BD5"   # blue   — self-play games
    C_SEARCH = "#F0A500"   # orange — tree search
    C_DATA   = "#50C878"   # green  — training examples
    C_POLICY = "#F0A500"
    C_VALUE  = "#5B9BD5"
    C_LOSS   = "#FF6B6B"

    def construct(self):
        self.camera.background_color = self.BG
        self._phase_intro()
        self._phase_loop()
        self._phase_training_targets()
        self._phase_library_comparison()
        self._phase_closing()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _loop_node(self, label, color, pos, width=2.1):
        box = RoundedRectangle(
            width=width, height=0.68, corner_radius=0.14,
            fill_color=color, fill_opacity=0.13,
            stroke_color=color, stroke_width=2.0,
        )
        box.move_to(pos)
        lbl = Text(label, font_size=19, color=color)
        lbl.move_to(pos)
        return VGroup(box, lbl)

    def _glow_pulse(self, center, color, base_r=0.48):
        ring = Circle(
            radius=base_r, fill_opacity=0,
            stroke_color=color, stroke_width=4.0,
        )
        ring.move_to(center)
        return ring

    # ── phases ────────────────────────────────────────────────────────────────

    def _phase_intro(self):
        q = Tex(
            r"Where does the training data come from?",
            font_size=38, color=WHITE,
        )
        q.move_to(ORIGIN)
        self.play(FadeIn(q, shift=UP * 0.1), run_time=0.85)
        self.wait(1.0)

        ans = Tex(r"Self-play.", font_size=56, color=self.C_NET)
        ans.move_to(DOWN * 0.95)
        self.play(
            q.animate.shift(UP * 0.9).set_opacity(0.28),
            GrowFromCenter(ans),
            run_time=0.85,
        )
        self.wait(1.1)
        self.play(FadeOut(VGroup(q, ans)), run_time=0.6)
        self.wait(0.1)

    def _phase_loop(self):
        # Five nodes on a circle, top-to-bottom clockwise flow
        cx, cy, r = 0.0, 0.1, 2.35
        n = 5
        # start at top (π/2), go clockwise → subtract angle each step
        raw_angles = [np.pi / 2 - i * 2 * np.pi / n for i in range(n)]

        node_specs = [
            ("current network",    self.C_NET,    2.15),
            ("self-play games",    self.C_PLAY,   2.05),
            ("tree search",        self.C_SEARCH, 1.70),
            ("training examples",  self.C_DATA,   2.15),
            ("updated network",    self.C_NET,    2.15),
        ]
        positions = [
            np.array([cx + r * np.cos(a), cy + r * np.sin(a), 0.0])
            for a in raw_angles
        ]
        nodes = [
            self._loop_node(lbl, col, pos, w)
            for (lbl, col, w), pos in zip(node_specs, positions)
        ]

        # Arrows between consecutive nodes (straight, buffered past box edges)
        arrows = []
        for i in range(n):
            src, dst = positions[i], positions[(i + 1) % n]
            col = node_specs[i][1]
            arr = Arrow(
                src, dst,
                color=GRAY_D, stroke_width=2.5,
                max_tip_length_to_length_ratio=0.13,
                buff=0.40,
            )
            arrows.append(arr)

        # Build the loop node-by-node
        self.play(GrowFromCenter(nodes[0]), run_time=0.45)
        for i in range(n - 1):
            self.play(
                GrowArrow(arrows[i]),
                GrowFromCenter(nodes[i + 1]),
                run_time=0.50,
            )
        self.play(GrowArrow(arrows[n - 1]), run_time=0.45)
        self.wait(0.5)

        # Animate the loop 3 times; network node brightens each pass
        arc_colors = [s[1] for s in node_specs]
        for iteration in range(3):
            fill_boost = 0.14 * iteration
            for i in range(n):
                next_i = (i + 1) % n
                self.play(
                    arrows[i].animate.set_color(arc_colors[i]).set_stroke(width=3.5),
                    nodes[next_i][0].animate.set_fill(
                        arc_colors[next_i],
                        opacity=0.22 + fill_boost,
                    ),
                    run_time=0.28,
                )

            # Network glow pulse at top node
            pulse = self._glow_pulse(positions[0], self.C_NET, base_r=0.50)
            self.add(pulse)
            self.play(
                pulse.animate.scale(2.4).set_stroke(opacity=0.0),
                nodes[0][0].animate.set_fill(self.C_NET, opacity=0.25 + 0.15 * (iteration + 1)),
                run_time=0.55,
                rate_func=ease_out_quad,
            )
            self.remove(pulse)

            # Dim arrows back
            for arr in arrows:
                arr.set_color(GRAY_D).set_stroke(width=2.5)
            self.wait(0.15)

        curriculum_lbl = Tex(
            r"The system generates its own curriculum.",
            font_size=26, color=GRAY_C,
        )
        curriculum_lbl.to_edge(DOWN, buff=0.52)
        self.play(FadeIn(curriculum_lbl, shift=UP * 0.1), run_time=0.65)
        self.wait(1.6)
        self.play(
            FadeOut(VGroup(*nodes, *arrows, curriculum_lbl)),
            run_time=1.0,
        )
        self.wait(0.2)

    def _phase_training_targets(self):
        header = MathTex(
            r"\text{For each position } s_t \text{ :}",
            font_size=34, color=GRAY_B,
        )
        header.move_to(UP * 2.85)

        # ── target row ────────────────────────────────────────────────────────
        pol_key = MathTex(r"\text{target policy:}", font_size=26, color=GRAY_C)
        pol_val = MathTex(r"\pi_t", font_size=52, color=self.C_POLICY)
        pol_row = VGroup(pol_key, pol_val).arrange(RIGHT, buff=0.35)

        out_key = MathTex(r"\text{game outcome:}", font_size=26, color=GRAY_C)
        out_val = MathTex(r"z \;\in\; \{-1,\;+1\}", font_size=42, color=self.C_VALUE)
        out_row = VGroup(out_key, out_val).arrange(RIGHT, buff=0.35)

        targets = VGroup(pol_row, out_row).arrange(DOWN, buff=0.5, aligned_edge=LEFT)
        targets.move_to(UP * 1.35)

        # ── divider ───────────────────────────────────────────────────────────
        span_x = max(targets.get_right()[0], 3.8)
        divider = Line(
            np.array([-span_x, 0.0, 0.0]),
            np.array([ span_x, 0.0, 0.0]),
            color=GRAY_E, stroke_width=1.0,
        ).shift(DOWN * 0.22)

        # ── train equations ───────────────────────────────────────────────────
        train_lbl = Text("train:", font_size=24, color=GRAY_C)

        eq_pol = MathTex(
            r"\pi_\theta(\cdot \mid s_t)", r"\;\approx\;", r"\pi_t",
            font_size=38,
        )
        eq_pol[0].set_color(self.C_NET)
        eq_pol[2].set_color(self.C_POLICY)

        eq_val = MathTex(
            r"V_\theta(s_t)", r"\;\approx\;", r"z",
            font_size=38,
        )
        eq_val[0].set_color(self.C_NET)
        eq_val[2].set_color(self.C_VALUE)

        train_eqs = VGroup(eq_pol, eq_val).arrange(DOWN, buff=0.38, aligned_edge=LEFT)
        train_block = VGroup(train_lbl, train_eqs).arrange(RIGHT, buff=0.4)
        train_block.move_to(DOWN * 1.45)

        self.play(Write(header), run_time=0.65)
        self.play(
            LaggedStart(
                FadeIn(pol_row, shift=RIGHT * 0.12),
                FadeIn(out_row, shift=RIGHT * 0.12),
                lag_ratio=0.42,
            ),
            run_time=0.9,
        )
        self.wait(0.35)
        self.play(Create(divider), run_time=0.5)
        self.play(
            FadeIn(train_lbl, shift=RIGHT * 0.1),
            LaggedStart(Write(eq_pol), Write(eq_val), lag_ratio=0.5),
            run_time=1.4,
        )
        self.wait(1.8)

        # Emphasise: πt came from search, not human records
        search_note = Tex(
            r"$\pi_t$ is produced by tree search — not copied from human games",
            font_size=22, color=self.C_SEARCH,
        )
        search_note.to_edge(DOWN, buff=0.52)
        self.play(
            eq_pol[2].animate.set_color(self.C_SEARCH),
            FadeIn(search_note, shift=UP * 0.1),
            run_time=0.7,
        )
        self.wait(1.8)
        self.play(
            FadeOut(VGroup(
                header, targets, divider, train_block, search_note,
            )),
            run_time=0.9,
        )
        self.wait(0.2)

    def _phase_library_comparison(self):
        v_line = DashedLine(
            UP * 3.5, DOWN * 3.5,
            color=GRAY_E, stroke_width=1.2, dash_length=0.2,
        )

        left_title = Text("Human games", font_size=26, color=GRAY_B)
        left_sub   = Text("finite cultural history", font_size=19, color=GRAY_D)
        left_title.move_to(LEFT * 3.3 + UP * 2.75)
        left_sub.next_to(left_title, DOWN, buff=0.14)

        right_title = Text("Self-play games", font_size=26, color=self.C_NET)
        right_sub   = Text("generated experience", font_size=19, color=GRAY_D)
        right_title.move_to(RIGHT * 3.3 + UP * 2.75)
        right_sub.next_to(right_title, DOWN, buff=0.14)

        self.play(
            Create(v_line),
            FadeIn(left_title, shift=RIGHT * 0.1),
            FadeIn(right_title, shift=LEFT * 0.1),
            run_time=0.8,
        )
        self.play(
            FadeIn(left_sub, shift=UP * 0.05),
            FadeIn(right_sub, shift=UP * 0.05),
            run_time=0.5,
        )
        self.wait(0.3)

        # ── left: fixed stack of "book" slabs ────────────────────────────────
        def _slab(x, y, w, h, col, op):
            r = Rectangle(width=w, height=h)
            r.set_fill(col, opacity=op).set_stroke(color=col, width=0.8, opacity=0.6)
            r.move_to(np.array([x, y, 0.0]))
            return r

        human_slabs = VGroup(
            _slab(-4.25, 0.6,  0.32, 1.8, GRAY_C, 0.50),
            _slab(-3.88, 0.5,  0.32, 1.6, GRAY_C, 0.42),
            _slab(-3.51, 0.65, 0.32, 1.9, GRAY_D, 0.48),
            _slab(-3.16, 0.55, 0.28, 1.5, GRAY_C, 0.38),
            _slab(-2.82, 0.60, 0.30, 1.7, GRAY_D, 0.44),
        )
        h_brace = Brace(human_slabs, DOWN, color=GRAY_C, buff=0.10)
        h_count = Text("~500K games", font_size=18, color=GRAY_C)
        h_count.next_to(h_brace, DOWN, buff=0.08)

        self.play(
            LaggedStart(*[GrowFromCenter(s) for s in human_slabs], lag_ratio=0.10),
            run_time=0.85,
        )
        self.play(GrowFromCenter(h_brace), FadeIn(h_count, shift=UP * 0.05), run_time=0.55)
        self.wait(0.6)

        # ── right: self-play stack that keeps growing ─────────────────────────
        batch_labels = ["500K", "5M", "50M", "500M+"]
        batch_cols = [self.C_NET] * 4

        sp_batches = []
        sp_brace   = None
        sp_count_lbl = None

        base_x = 3.3
        for batch_i in range(4):
            grp = VGroup()
            y_center = -0.4 + batch_i * 0.62
            col = batch_cols[batch_i]
            op  = 0.22 + batch_i * 0.10
            for k in range(5):
                grp.add(_slab(
                    base_x + (k - 2) * 0.40,
                    y_center + k * 0.04,
                    0.34, 0.55 + batch_i * 0.08,
                    col, min(op + k * 0.03, 0.85),
                ))
            sp_batches.append(grp)

            new_brace = Brace(
                VGroup(*sp_batches),
                DOWN, color=self.C_NET, buff=0.10,
            )
            new_count = Text(batch_labels[batch_i] + " games", font_size=18, color=self.C_NET)
            new_count.next_to(new_brace, DOWN, buff=0.08)

            if batch_i == 0:
                self.play(
                    LaggedStart(*[GrowFromCenter(s) for s in grp], lag_ratio=0.08),
                    GrowFromCenter(new_brace),
                    FadeIn(new_count, shift=UP * 0.05),
                    run_time=0.75,
                )
                sp_brace     = new_brace
                sp_count_lbl = new_count
            else:
                self.play(
                    LaggedStart(*[GrowFromCenter(s) for s in grp], lag_ratio=0.06),
                    Transform(sp_brace, new_brace),
                    Transform(sp_count_lbl, new_count),
                    run_time=0.55,
                )
            self.wait(0.15)

        self.wait(1.0)

        not_history = Tex(
            r"Not learning from history. \ Building its own.",
            font_size=28, color=WHITE,
        )
        not_history.to_edge(DOWN, buff=0.52)
        self.play(FadeIn(not_history, shift=UP * 0.1), run_time=0.75)
        self.wait(2.2)

        self.play(
            FadeOut(VGroup(
                v_line,
                left_title, left_sub, right_title, right_sub,
                human_slabs, h_brace, h_count,
                *sp_batches, sp_brace, sp_count_lbl,
                not_history,
            )),
            run_time=1.0,
        )
        self.wait(0.2)

    def _phase_closing(self):
        l1 = Tex(
            r"The machine is not learning only from human games.",
            font_size=30, color=GRAY_B,
        )
        l2 = Tex(
            r"It is generating its own curriculum.",
            font_size=36, color=WHITE,
        )
        VGroup(l1, l2).arrange(DOWN, buff=0.55).move_to(ORIGIN)

        self.play(FadeIn(l1, shift=UP * 0.12), run_time=0.9)
        self.wait(0.55)
        self.play(FadeIn(l2, shift=UP * 0.12), run_time=0.9)
        self.wait(3.2)
        self.play(FadeOut(VGroup(l1, l2)), run_time=0.9)
