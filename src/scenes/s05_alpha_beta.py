from manim import *
from manim.utils.rate_functions import ease_out_quad, rush_from
import numpy as np


class AlphaBetaScene(Scene):
    """Scene 5 – Alpha-beta pruning: mathematically useful ignorance."""

    BG      = "#000000"
    C_MAX   = "#F0A500"   # orange  — maximiser / you
    C_MIN   = "#5B9BD5"   # blue    — minimiser / opponent
    C_WIN   = "#50C878"   # green   — positive leaf values
    C_PRUNE = "#FF6B6B"   # red     — pruned nodes/edges
    C_ALPHA = "#A78BFA"   # purple  — alpha bound annotation
    C_GHOST = "#2A2A2A"   # very dark — pruned subtree ghost

    NODE_R = 0.38

    # Tree layout
    #   root (MAX)
    #   ├── A  (MIN)  → min(8, 5) = 5  → root α = 5
    #   │   ├── A1  +8
    #   │   └── A2  +5
    #   └── B  (MIN)  → B1=3 seen → B ≤ 3 < 5 → prune B2
    #       ├── B1  +3
    #       └── B2  (pruned)
    POS = {
        "root": np.array([ 0.0,  2.65, 0.0]),
        "A":    np.array([-2.9,  0.55, 0.0]),
        "B":    np.array([ 2.9,  0.55, 0.0]),
        "A1":   np.array([-4.3, -1.45, 0.0]),
        "A2":   np.array([-1.6, -1.45, 0.0]),
        "B1":   np.array([ 1.6, -1.45, 0.0]),
        "B2":   np.array([ 4.3, -1.45, 0.0]),
    }

    def construct(self):
        self.camera.background_color = self.BG
        self._phase_intro()
        self._phase_build_tree()
        self._phase_left_branch()
        self._phase_alpha_lock()
        self._phase_right_start()
        self._phase_prune()
        self._phase_irrelevant()
        self._phase_same_answer()
        self._phase_equations()
        self._phase_closing()

    # ── geometry helpers ──────────────────────────────────────────────────────

    def _node(self, key, color, label=None, lfs=18):
        pos = self.POS[key]
        c = Circle(radius=self.NODE_R)
        c.set_fill(color, opacity=0.14).set_stroke(color=color, width=2.2)
        c.move_to(pos)
        g = VGroup(c)
        if label:
            t = MathTex(label, font_size=lfs, color=color).move_to(pos)
            g.add(t)
        return g

    def _leaf(self, key, val_tex, color):
        pos = self.POS[key]
        c = Circle(radius=self.NODE_R)
        c.set_fill(color, opacity=0.18).set_stroke(color=color, width=2.2)
        c.move_to(pos)
        lbl = MathTex(val_tex, font_size=30, color=color).move_to(pos)
        return VGroup(c, lbl)

    def _edge(self, k1, k2, color=GRAY_D, width=1.8):
        p1, p2 = self.POS[k1], self.POS[k2]
        d = (p2 - p1) / np.linalg.norm(p2 - p1)
        return Line(
            p1 + d * self.NODE_R, p2 - d * self.NODE_R,
            color=color, stroke_width=width,
        )

    def _val_below(self, key, val_tex, color, fs=26):
        lbl = MathTex(val_tex, font_size=fs, color=color)
        lbl.move_to(self.POS[key] + DOWN * (self.NODE_R + 0.08 + lbl.height / 2))
        return lbl

    def _travel(self, src_lbl, dest_key, run_time=0.55):
        copy = src_lbl.copy()
        self.play(copy.animate.move_to(self.POS[dest_key]),
                  run_time=run_time, rate_func=smooth)
        self.remove(copy)

    # ── phases ────────────────────────────────────────────────────────────────

    def _phase_intro(self):
        l1 = Text("Minimax always gives the right answer.",
                  font_size=38, color=WHITE)
        l2 = Text("But it searches more than it needs to.",
                  font_size=38, color=GRAY_C)
        VGroup(l1, l2).arrange(DOWN, buff=0.5).move_to(ORIGIN)

        self.play(FadeIn(l1, shift=UP * 0.12), run_time=0.85)
        self.wait(0.5)
        self.play(FadeIn(l2, shift=UP * 0.12), run_time=0.85)
        self.wait(1.6)
        self.play(FadeOut(VGroup(l1, l2)), run_time=0.7)
        self.wait(0.15)

    def _phase_build_tree(self):
        root_node = self._node("root", self.C_MAX, r"\max", lfs=18)
        node_a    = self._node("A",    self.C_MIN, r"\min", lfs=18)
        node_b    = self._node("B",    self.C_MIN, r"\min", lfs=18)

        edge_ra = self._edge("root", "A")
        edge_rb = self._edge("root", "B")
        edge_a1 = self._edge("A", "A1")
        edge_a2 = self._edge("A", "A2")
        edge_b1 = self._edge("B", "B1")
        edge_b2 = self._edge("B", "B2")

        leaf_a1 = self._leaf("A1", r"+8", self.C_WIN)
        leaf_a2 = self._leaf("A2", r"+5", self.C_WIN)
        leaf_b1 = self._leaf("B1", r"+3", self.C_WIN)
        leaf_b2 = self._leaf("B2", r"+?", GRAY_C)

        # Reveal tree top-down
        self.play(GrowFromCenter(root_node), run_time=0.6)
        self.play(
            LaggedStart(
                AnimationGroup(Create(edge_ra), GrowFromCenter(node_a)),
                AnimationGroup(Create(edge_rb), GrowFromCenter(node_b)),
                lag_ratio=0.3,
            ),
            run_time=0.9,
        )
        self.play(
            LaggedStart(
                AnimationGroup(Create(edge_a1), GrowFromCenter(leaf_a1)),
                AnimationGroup(Create(edge_a2), GrowFromCenter(leaf_a2)),
                AnimationGroup(Create(edge_b1), GrowFromCenter(leaf_b1)),
                AnimationGroup(Create(edge_b2), GrowFromCenter(leaf_b2)),
                lag_ratio=0.18,
            ),
            run_time=1.3,
        )
        self.wait(0.4)

        self._root_node = root_node
        self._node_a    = node_a
        self._node_b    = node_b
        self._edge_ra   = edge_ra
        self._edge_rb   = edge_rb
        self._edge_a1   = edge_a1
        self._edge_a2   = edge_a2
        self._edge_b1   = edge_b1
        self._edge_b2   = edge_b2
        self._leaf_a1   = leaf_a1
        self._leaf_a2   = leaf_a2
        self._leaf_b1   = leaf_b1
        self._leaf_b2   = leaf_b2

    def _phase_left_branch(self):
        """Explore the A subtree fully: min(+8, +5) = +5."""
        # Spotlight the A branch
        self.play(
            self._edge_ra.animate.set_color(self.C_MAX).set_stroke(width=3.0),
            run_time=0.4,
        )

        # Highlight A1
        self.play(
            Indicate(self._leaf_a1, color=self.C_WIN, scale_factor=1.22),
            run_time=0.65,
        )
        self.wait(0.2)

        # Highlight A2
        self.play(
            Indicate(self._leaf_a2, color=self.C_WIN, scale_factor=1.22),
            run_time=0.65,
        )
        self.wait(0.25)

        # Opponent picks min: A2 is smaller, A1 is dimmed
        self.play(
            self._leaf_a1.animate.set_opacity(0.28),
            self._edge_a1.animate.set_color(GRAY_E).set_stroke(width=1.0),
            self._edge_a2.animate.set_color(self.C_MIN).set_stroke(width=3.0),
            run_time=0.5,
        )

        # Backup +5 to node A
        val_a = self._val_below("A", r"+5", self.C_MIN)
        self._travel(self._leaf_a2[1], "A")
        self.add(val_a)
        self.wait(0.35)

        self._val_a = val_a

    def _phase_alpha_lock(self):
        """
        Root is MAX and just saw its first option is +5.
        Establish α = 5 — root's guaranteed floor.
        """
        # Backup +5 to root
        val_root_floor = self._val_below("root", r"\geq +5", self.C_MAX, fs=24)
        self._travel(self._val_a, "root")
        self.add(val_root_floor)
        self.wait(0.25)

        # Alpha badge: a small pill next to the root node
        alpha_pill = RoundedRectangle(
            width=1.55, height=0.48, corner_radius=0.10,
            fill_color=self.C_ALPHA, fill_opacity=0.18,
            stroke_color=self.C_ALPHA, stroke_width=1.8,
        )
        alpha_lbl = MathTex(r"\alpha = 5", font_size=22, color=self.C_ALPHA)
        alpha_pill.move_to(self.POS["root"] + LEFT * 1.62 + UP * 0.02)
        alpha_lbl.move_to(alpha_pill.get_center())
        alpha_grp = VGroup(alpha_pill, alpha_lbl)

        self.play(GrowFromCenter(alpha_grp), run_time=0.65)

        # Annotation: root can guarantee at least 5
        guarantee = Text("root can guarantee ≥ 5", font_size=20, color=self.C_ALPHA)
        guarantee.next_to(alpha_pill, DOWN, buff=0.22)
        self.play(FadeIn(guarantee, shift=UP * 0.08), run_time=0.5)
        self.wait(1.2)
        self.play(FadeOut(guarantee), run_time=0.4)

        self._alpha_grp       = alpha_grp
        self._val_root_floor  = val_root_floor

    def _phase_right_start(self):
        """Begin exploring B: edge lights up, opponent evaluates B1 = +3."""
        self.play(
            self._edge_rb.animate.set_color(self.C_MAX).set_stroke(width=3.0),
            run_time=0.4,
        )
        self.play(
            self._edge_b1.animate.set_color(self.C_MIN).set_stroke(width=2.5),
            run_time=0.35,
        )
        self.play(
            Indicate(self._leaf_b1, color=self.C_WIN, scale_factor=1.22),
            run_time=0.65,
        )
        self.wait(0.3)

        # Key deduction: opponent already has +3, so B ≤ 3
        # That means B ≤ 3 < α = 5 → root won't pick B regardless of B2
        val_b_ceil = self._val_below("B", r"\leq +3", self.C_PRUNE, fs=24)
        self._travel(self._leaf_b1[1], "B")
        self.add(val_b_ceil)
        self.wait(0.35)

        self._val_b_ceil = val_b_ceil

    def _phase_prune(self):
        """The prune: B2 is irrelevant. Show the cut dramatically."""
        # Comparison box appears near the root: α vs ceiling
        compare_box = RoundedRectangle(
            width=3.4, height=1.15, corner_radius=0.14,
            fill_color="#111111", fill_opacity=1.0,
            stroke_color=GRAY_D, stroke_width=1.4,
        )
        compare_box.to_edge(DOWN, buff=0.48)

        row1 = VGroup(
            Text("current best",        font_size=20, color=self.C_MAX),
            MathTex("= 5",              font_size=24, color=self.C_MAX),
        ).arrange(RIGHT, buff=0.25)
        row2 = VGroup(
            Text("this branch  ≤",      font_size=20, color=self.C_PRUNE),
            MathTex("3",                font_size=24, color=self.C_PRUNE),
        ).arrange(RIGHT, buff=0.25)
        rows = VGroup(row1, row2).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        rows.move_to(compare_box.get_center())

        self.play(FadeIn(compare_box), FadeIn(rows), run_time=0.6)
        self.wait(1.0)

        # "therefore: prune" materialises
        therefore = MathTex(
            r"\therefore \;\text{prune}",
            font_size=28, color=self.C_PRUNE,
        )
        therefore.next_to(compare_box, RIGHT, buff=0.45)
        self.play(Write(therefore), run_time=0.7)
        self.wait(0.7)

        # Animate the cut: B2 and edge_b2 turn red, then a slash X appears
        self.play(
            self._edge_b2.animate.set_color(self.C_PRUNE).set_stroke(width=3.5),
            self._leaf_b2.animate.set_color(self.C_PRUNE).set_stroke(color=self.C_PRUNE),
            run_time=0.45,
        )

        # Draw a bold X over B2
        cx, cy = self.POS["B2"][0], self.POS["B2"][1]
        r = self.NODE_R * 1.05
        slash1 = Line(
            np.array([cx - r, cy + r, 0.0]),
            np.array([cx + r, cy - r, 0.0]),
            color=self.C_PRUNE, stroke_width=4.5,
        )
        slash2 = Line(
            np.array([cx - r, cy - r, 0.0]),
            np.array([cx + r, cy + r, 0.0]),
            color=self.C_PRUNE, stroke_width=4.5,
        )
        self.play(Create(slash1), Create(slash2), run_time=0.5)

        # Pulse ring to emphasise the cut
        pulse = Circle(radius=self.NODE_R * 1.2, fill_opacity=0,
                       stroke_color=self.C_PRUNE, stroke_width=2.5)
        pulse.move_to(self.POS["B2"])
        self.add(pulse)
        self.play(pulse.animate.scale(3.8).set_opacity(0),
                  run_time=0.7, rate_func=ease_out_quad)
        self.remove(pulse)
        self.wait(0.5)

        self.play(FadeOut(VGroup(compare_box, rows, therefore)), run_time=0.5)

        self._slash1 = slash1
        self._slash2 = slash2

    def _phase_irrelevant(self):
        """
        Label the pruned node with the three-line mantra and
        dim the entire B subtree to ghost level.
        """
        # Dim B branch to ghost — visually "it doesn't matter"
        ghost = VGroup(
            self._node_b, self._edge_rb,
            self._edge_b1, self._edge_b2,
            self._leaf_b1, self._leaf_b2,
            self._val_b_ceil,
            self._slash1, self._slash2,
        )
        self.play(ghost.animate.set_opacity(0.18), run_time=0.8)

        # Three-line mantra appears to the right of the ghost B branch
        l1 = Text("not wrong",       font_size=26, color=GRAY_B)
        l2 = Text("not impossible",  font_size=26, color=GRAY_B)
        l3 = Text("just irrelevant", font_size=26, color=self.C_PRUNE, weight="BOLD")
        mantra = VGroup(l1, l2, l3).arrange(DOWN, buff=0.32)
        mantra.move_to(RIGHT * 3.3 + DOWN * 0.3)

        # Small connecting dashed line from pruned node to mantra
        dashed_connector = DashedLine(
            self.POS["B2"] + RIGHT * (self.NODE_R + 0.12),
            mantra.get_left() + LEFT * 0.15,
            color=GRAY_E, stroke_width=1.0, dash_length=0.12,
        )

        self.play(
            LaggedStart(
                FadeIn(l1, shift=LEFT * 0.1),
                FadeIn(l2, shift=LEFT * 0.1),
                FadeIn(l3, shift=LEFT * 0.1),
                lag_ratio=0.35,
            ),
            Create(dashed_connector),
            run_time=1.2,
        )
        self.wait(1.6)
        self.play(FadeOut(VGroup(mantra, dashed_connector)), run_time=0.55)

        self._ghost = ghost

    def _phase_same_answer(self):
        """
        Root picks max(5, ≤3) = 5.
        Emphasise: same answer, less work.
        """
        # Restore left branch brightness, keep B ghosted
        self.play(
            self._edge_ra.animate.set_stroke(opacity=1.0).set_color(self.C_MAX),
            self._edge_ra.animate.set_stroke(width=4.5),
            run_time=0.4,
        )

        val_root_final = MathTex(r"+5", font_size=36, color=self.C_MAX)
        val_root_final.next_to(self._root_node, RIGHT, buff=0.28)

        self._travel(self._val_a, "root")
        self.play(GrowFromCenter(val_root_final), run_time=0.5)

        # Highlight the winning path: root → A → A2
        opt_path = VGroup(
            self._edge_ra.copy().set_stroke(color=WHITE, width=5.0),
            self._edge_a2.copy().set_stroke(color=WHITE, width=5.0),
        )
        self.play(Create(opt_path[0]), Create(opt_path[1]), run_time=0.7)
        pulse2 = Circle(radius=self.NODE_R * 1.4, fill_opacity=0,
                        stroke_color=WHITE, stroke_width=2.5)
        pulse2.move_to(self.POS["A2"])
        self.add(pulse2)
        self.play(pulse2.animate.scale(2.6).set_opacity(0),
                  run_time=0.6, rate_func=ease_out_quad)
        self.remove(pulse2)
        self.wait(0.3)

        # Banner: "same answer — less work"
        banner = Text("Same answer.  Less work.", font_size=30, color=WHITE)
        banner.to_edge(DOWN, buff=0.55)
        self.play(FadeIn(banner, shift=UP * 0.1), run_time=0.6)
        self.wait(1.8)

        # Fade everything out
        all_mobs = VGroup(
            self._root_node, self._node_a,
            self._edge_ra, self._edge_rb,
            self._edge_a1, self._edge_a2,
            self._leaf_a1, self._leaf_a2,
            self._val_a, self._val_root_floor, self._alpha_grp,
            val_root_final, opt_path,
            self._ghost,
            banner,
        )
        self.play(FadeOut(all_mobs), run_time=1.1)
        self.wait(0.2)

    def _phase_equations(self):
        """
        Formal statement of alpha-beta: prune when ceiling ≤ α.
        """
        # α = best value MAX can guarantee along path from root
        eq_alpha = MathTex(
            r"\alpha", r"\;=\;",
            r"\text{best value } \textit{you} \text{ can already guarantee}",
            font_size=30,
        )
        eq_alpha[0].set_color(self.C_ALPHA)
        eq_alpha.move_to(UP * 1.6)

        # prune condition
        eq_prune = MathTex(
            r"\text{if } \hat{V}(B)",
            r"\;\leq\;",
            r"\alpha",
            r"\quad\Rightarrow\quad",
            r"\text{skip } B",
            font_size=36,
        )
        eq_prune[0].set_color(self.C_PRUNE)
        eq_prune[2].set_color(self.C_ALPHA)
        eq_prune[4].set_color(self.C_PRUNE)
        eq_prune.move_to(UP * 0.15)

        # Why it is safe
        safe_note = Tex(
            r"$B$ cannot improve on what you already have.",
            font_size=26, color=GRAY_C,
        )
        safe_note.next_to(eq_prune, DOWN, buff=0.5)

        self.play(Write(eq_alpha), run_time=1.1)
        self.wait(0.5)
        self.play(Write(eq_prune), run_time=1.4)
        self.wait(0.5)
        self.play(FadeIn(safe_note, shift=UP * 0.1), run_time=0.6)
        self.wait(2.2)
        self.play(FadeOut(VGroup(eq_alpha, eq_prune, safe_note)), run_time=0.8)
        self.wait(0.2)

    def _phase_closing(self):
        """
        Two-line scientific phrasing from the script.
        """
        l1 = Text(
            "Alpha-beta does not change the minimax answer.",
            font_size=30, color=GRAY_B,
        )
        l2 = Text(
            "It changes how much of the tree you need to inspect to find it.",
            font_size=30, color=WHITE,
        )
        VGroup(l1, l2).arrange(DOWN, buff=0.52).move_to(ORIGIN)

        self.play(FadeIn(l1, shift=UP * 0.12), run_time=1.0)
        self.wait(0.65)
        self.play(FadeIn(l2, shift=UP * 0.12), run_time=1.0)
        self.wait(3.0)
        self.play(FadeOut(VGroup(l1, l2)), run_time=1.0)
