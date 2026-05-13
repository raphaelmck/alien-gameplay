from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class MinimaxScene(Scene):
    """Scene 2 – Minimax: intelligence as recursion."""

    BG     = "#000000"
    C_MAX  = "#F0A500"   # warm orange  — you / maximiser
    C_MIN  = "#5B9BD5"   # cool blue    — opponent / minimiser
    C_WIN  = "#50C878"   # green        — positive outcome
    C_LOSE = "#FF6B6B"   # red          — negative / refutation
    C_GOLD = "#F5C518"   # gold         — dream leaf highlight

    NODE_R = 0.38

    # Tree layout
    #   root (MAX)
    #   ├── A  (MIN opponent)
    #   │   ├── A1  +10  "dream"
    #   │   └── A2  -9   "refutation"
    #   └── B  (MIN opponent)
    #       ├── B1  +3
    #       └── B2  +2
    POS = {
        "root": np.array([ 0.0,  2.75, 0.0]),
        "A":    np.array([-2.8,  0.65, 0.0]),
        "B":    np.array([ 2.8,  0.65, 0.0]),
        "A1":   np.array([-4.2, -1.40, 0.0]),
        "A2":   np.array([-1.4, -1.40, 0.0]),
        "B1":   np.array([ 1.4, -1.40, 0.0]),
        "B2":   np.array([ 4.2, -1.40, 0.0]),
    }

    def construct(self):
        self.camera.background_color = self.BG
        self._phase_score_meter()
        self._phase_root()
        self._phase_candidates()
        self._phase_dream_and_refutation()
        self._phase_move_b()
        self._phase_backup_max()
        self._phase_equations()
        self._phase_quote()

    # ─── geometry helpers ────────────────────────────────────────────────────

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
        lbl = MathTex(val_tex, font_size=28, color=color).move_to(pos)
        return VGroup(c, lbl)

    def _edge(self, k1, k2, color=GRAY_D, width=1.8):
        p1, p2 = self.POS[k1], self.POS[k2]
        d = (p2 - p1) / np.linalg.norm(p2 - p1)
        return Line(p1 + d * self.NODE_R, p2 - d * self.NODE_R,
                    color=color, stroke_width=width)

    def _val_below(self, key, val_tex, color, fs=26):
        """Value label placed just below node circle at key."""
        lbl = MathTex(val_tex, font_size=fs, color=color)
        lbl.move_to(self.POS[key] + DOWN * (self.NODE_R + 0.07 + lbl.height / 2))
        return lbl

    def _travel(self, src_lbl, dest_key, run_time=0.60):
        """Animate a copy of src_lbl travelling to the centre of dest_key's node."""
        copy = src_lbl.copy()
        self.play(copy.animate.move_to(self.POS[dest_key]),
                  run_time=run_time, rate_func=smooth)
        self.remove(copy)

    # ─── phases ──────────────────────────────────────────────────────────────

    def _phase_score_meter(self):
        """Compact zero-sum score display: your gain = -opponent's gain."""
        title = Text("zero-sum", font_size=52, color=WHITE, weight="BOLD")
        title.to_edge(UP, buff=0.55)

        you_lbl = Text("YOUR SCORE",      font_size=20, color=self.C_MAX)
        opp_lbl = Text("OPPONENT SCORE",  font_size=20, color=self.C_MIN)

        score_t = ValueTracker(0.0)

        you_num = DecimalNumber(0, num_decimal_places=0,
                                include_sign=True, color=self.C_WIN, font_size=62)
        opp_num = DecimalNumber(0, num_decimal_places=0,
                                include_sign=True, color=self.C_LOSE, font_size=62)

        col_you = VGroup(you_lbl, you_num).arrange(DOWN, buff=0.25)
        col_opp = VGroup(opp_lbl, opp_num).arrange(DOWN, buff=0.25)
        cols = VGroup(col_you, col_opp).arrange(RIGHT, buff=3.0).move_to(DOWN * 0.15)

        eq_zero = MathTex(
            r"\text{your gain} + \text{opponent gain} = 0",
            font_size=26, color=GRAY_C,
        )
        eq_zero.next_to(cols, DOWN, buff=0.55)

        self.play(FadeIn(title, shift=UP * 0.15), FadeIn(cols), run_time=0.9)

        you_num.add_updater(lambda m: m.set_value( score_t.get_value()))
        opp_num.add_updater(lambda m: m.set_value(-score_t.get_value()))

        self.play(score_t.animate.set_value(7), run_time=1.8, rate_func=smooth)
        self.wait(0.25)
        self.play(score_t.animate.set_value(3), run_time=1.1, rate_func=smooth)
        self.wait(0.25)
        self.play(FadeIn(eq_zero, shift=UP * 0.08), run_time=0.65)
        self.wait(1.5)

        you_num.clear_updaters()
        opp_num.clear_updaters()
        self.play(FadeOut(VGroup(title, cols, eq_zero)), run_time=0.75)
        self.wait(0.15)

    def _phase_root(self):
        """Root MAX node labelled 'position s / your move'."""
        root_node = self._node("root", self.C_MAX, r"\max", lfs=18)

        pos_lbl = Text("position  s", font_size=16, color=GRAY_C)
        pos_lbl.next_to(self.POS["root"] + UP * self.NODE_R, UP, buff=0.12)
        your_move = Text("your move", font_size=15, color=self.C_MAX)
        your_move.next_to(pos_lbl, UP, buff=0.06)

        self.play(GrowFromCenter(root_node), run_time=0.65)
        self.play(
            FadeIn(pos_lbl, shift=DOWN * 0.08),
            FadeIn(your_move, shift=DOWN * 0.08),
            run_time=0.5,
        )
        self.wait(0.3)

        self._root_node = root_node
        self._pos_lbl   = pos_lbl
        self._your_move = your_move

    def _phase_candidates(self):
        """Two candidate moves branching from root, each reaching an opponent MIN node."""
        node_a = self._node("A", self.C_MIN, r"\min", lfs=18)
        node_b = self._node("B", self.C_MIN, r"\min", lfs=18)

        edge_ra = self._edge("root", "A")
        edge_rb = self._edge("root", "B")

        # Edge labels at the midpoint of each branch
        mid_a = (self.POS["root"] + self.POS["A"]) / 2
        mid_b = (self.POS["root"] + self.POS["B"]) / 2
        lbl_a = Text("Move A", font_size=15, color=self.C_MAX)
        lbl_b = Text("Move B", font_size=15, color=self.C_MAX)
        lbl_a.move_to(mid_a + LEFT * 0.52 + UP * 0.12)
        lbl_b.move_to(mid_b + RIGHT * 0.52 + UP * 0.12)

        opp_a = Text("opponent", font_size=13, color=self.C_MIN)
        opp_b = Text("opponent", font_size=13, color=self.C_MIN)
        opp_a.next_to(self.POS["A"] + UP * self.NODE_R, UP, buff=0.10)
        opp_b.next_to(self.POS["B"] + UP * self.NODE_R, UP, buff=0.10)

        self.play(
            LaggedStart(
                AnimationGroup(
                    Create(edge_ra), GrowFromCenter(node_a),
                    FadeIn(lbl_a), FadeIn(opp_a, shift=DOWN * 0.06),
                ),
                AnimationGroup(
                    Create(edge_rb), GrowFromCenter(node_b),
                    FadeIn(lbl_b), FadeIn(opp_b, shift=DOWN * 0.06),
                ),
                lag_ratio=0.35,
            ),
            run_time=1.4,
        )
        self.wait(0.35)

        self._node_a  = node_a
        self._node_b  = node_b
        self._edge_ra = edge_ra
        self._edge_rb = edge_rb
        self._lbl_a   = lbl_a
        self._lbl_b   = lbl_b
        self._opp_a   = opp_a
        self._opp_b   = opp_b

    def _phase_dream_and_refutation(self):
        """
        Under Move A:
          A1 = +10  labelled "dream" — glows gold, feels tempting.
          A2 = -9   labelled "opponent refutation" — arrives and kills the dream.
        Then min(+10, -9) = -9 backs up to node A.
        """
        edge_a1 = self._edge("A", "A1")
        edge_a2 = self._edge("A", "A2")
        self.play(Create(edge_a1), Create(edge_a2), run_time=0.55)

        # ── A1 = +10 : the dream ─────────────────────────────────────
        leaf_a1  = self._leaf("A1", r"+10", self.C_GOLD)
        glow     = Circle(radius=self.NODE_R * 2.4)
        glow.set_fill(self.C_GOLD, opacity=0.16).set_stroke(width=0)
        glow.move_to(self.POS["A1"])
        dream_lbl = Text("dream", font_size=14, color=self.C_GOLD)
        dream_lbl.next_to(self.POS["A1"] + DOWN * self.NODE_R, DOWN, buff=0.13)

        self.play(GrowFromCenter(leaf_a1), run_time=0.7)
        self.play(FadeIn(glow), FadeIn(dream_lbl, shift=UP * 0.08), run_time=0.5)
        self.play(glow.animate.scale(1.9).set_opacity(0), run_time=0.85, rate_func=ease_out_quad)
        self.remove(glow)
        self.wait(0.3)

        # ── A2 = -9 : the refutation ──────────────────────────────────
        leaf_a2    = self._leaf("A2", r"-9", self.C_LOSE)
        refute_lbl = Text("opponent refutation", font_size=12, color=self.C_LOSE)
        refute_lbl.next_to(self.POS["A2"] + DOWN * self.NODE_R, DOWN, buff=0.13)

        self.play(GrowFromCenter(leaf_a2), run_time=0.65)
        self.play(
            Write(refute_lbl),
            # Dream dims as the nightmare arrives
            leaf_a1.animate.set_opacity(0.25),
            dream_lbl.animate.set_opacity(0.25),
            Indicate(leaf_a2, color=self.C_LOSE, scale_factor=1.28),
            run_time=1.0,
        )
        self.wait(0.4)

        # ── Backup: opponent picks min(+10, -9) = -9 ─────────────────
        self.play(
            edge_a1.animate.set_color(GRAY_E).set_stroke(width=1.2),
            edge_a2.animate.set_color(self.C_LOSE).set_stroke(width=3.2),
            run_time=0.45,
        )
        val_a = self._val_below("A", r"-9", self.C_LOSE)
        self._travel(leaf_a2[1], "A")
        self.add(val_a)
        self.wait(0.35)

        self._leaf_a1    = leaf_a1
        self._leaf_a2    = leaf_a2
        self._dream_lbl  = dream_lbl
        self._refute_lbl = refute_lbl
        self._edge_a1    = edge_a1
        self._edge_a2    = edge_a2
        self._val_a      = val_a

    def _phase_move_b(self):
        """
        Under Move B:
          B1 = +3, B2 = +2 — modest but solid.
        min(+3, +2) = +2 backs up to node B.
        """
        edge_b1 = self._edge("B", "B1")
        edge_b2 = self._edge("B", "B2")
        self.play(Create(edge_b1), Create(edge_b2), run_time=0.55)

        leaf_b1 = self._leaf("B1", r"+3", self.C_WIN)
        leaf_b2 = self._leaf("B2", r"+2", self.C_WIN)
        self.play(
            LaggedStart(GrowFromCenter(leaf_b1), GrowFromCenter(leaf_b2), lag_ratio=0.3),
            run_time=1.0,
        )
        self.wait(0.3)

        # ── Backup: opponent picks min(+3, +2) = +2 ──────────────────
        self.play(
            Indicate(leaf_b1, color=self.C_WIN, scale_factor=1.18),
            Indicate(leaf_b2, color=self.C_WIN, scale_factor=1.18),
            run_time=0.65,
        )
        self.play(
            edge_b1.animate.set_color(GRAY_E).set_stroke(width=1.2),
            edge_b2.animate.set_color(self.C_WIN).set_stroke(width=3.2),
            run_time=0.42,
        )
        val_b = self._val_below("B", r"+2", self.C_WIN)
        self._travel(leaf_b2[1], "B")
        self.add(val_b)
        self.wait(0.35)

        self._leaf_b1 = leaf_b1
        self._leaf_b2 = leaf_b2
        self._edge_b1 = edge_b1
        self._edge_b2 = edge_b2
        self._val_b   = val_b

    def _phase_backup_max(self):
        """
        Root picks max(-9, +2) = +2.
        Move A had the dream but the nightmare decided.
        Move B is chosen; optimal path highlighted.
        """
        self.play(
            Indicate(self._val_a, color=self.C_LOSE, scale_factor=1.25),
            Indicate(self._val_b, color=self.C_WIN,  scale_factor=1.25),
            run_time=0.85,
        )
        # Dim the losing branch, light up the winner
        self.play(
            self._edge_ra.animate.set_color(GRAY_E).set_stroke(width=1.2),
            self._edge_rb.animate.set_color(self.C_MAX).set_stroke(width=3.5),
            run_time=0.5,
        )
        val_root = self._val_below("root", r"+2", self.C_MAX, fs=28)
        self._travel(self._val_b, "root")
        self.add(val_root)
        self.wait(0.4)

        # Highlight the full winning path: root → B → B2
        opt = VGroup(
            self._edge_rb.copy().set_stroke(color=WHITE, width=5.5),
            self._edge_b2.copy().set_stroke(color=WHITE, width=5.5),
        )
        self.play(Create(opt[0]), Create(opt[1]), run_time=0.65)
        pulse = Circle(radius=self.NODE_R * 1.5,
                       stroke_color=WHITE, stroke_width=2.5, fill_opacity=0)
        pulse.move_to(self.POS["B2"])
        self.add(pulse)
        self.play(pulse.animate.scale(2.7).set_opacity(0),
                  run_time=0.7, rate_func=ease_out_quad)
        self.remove(pulse)
        self.wait(0.8)

        self._val_root = val_root
        self._opt      = opt

    def _phase_equations(self):
        """
        Fade the tree out, then show the equations that formalise
        what the viewer just saw.  Example first, notation second.
        """
        tree_all = VGroup(
            self._root_node, self._pos_lbl, self._your_move,
            self._node_a,    self._node_b,
            self._leaf_a1,   self._leaf_a2,
            self._leaf_b1,   self._leaf_b2,
            self._dream_lbl, self._refute_lbl,
            self._lbl_a,     self._lbl_b,
            self._opp_a,     self._opp_b,
            self._edge_ra,   self._edge_rb,
            self._edge_a1,   self._edge_a2,
            self._edge_b1,   self._edge_b2,
            self._val_a,     self._val_b,     self._val_root,
            self._opt,
        )
        self.play(FadeOut(tree_all), run_time=0.9)

        eq_my = MathTex(
            r"V(s) = ", r"\max_{a}", r"\, V\!\bigl(T(s,a)\bigr)",
            font_size=40,
        )
        eq_my[1].set_color(self.C_MAX)

        eq_op = MathTex(
            r"V(s) = ", r"\min_{a}", r"\, V\!\bigl(T(s,a)\bigr)",
            font_size=40,
        )
        eq_op[1].set_color(self.C_MIN)

        tag_my = Text("your turn",        font_size=21, color=self.C_MAX)
        tag_op = Text("opponent's turn",  font_size=21, color=self.C_MIN)

        row_my = VGroup(eq_my, tag_my).arrange(RIGHT, buff=0.52)
        row_op = VGroup(eq_op, tag_op).arrange(RIGHT, buff=0.52)
        block  = VGroup(row_my, row_op).arrange(DOWN, buff=0.58).move_to(ORIGIN)

        self.play(
            LaggedStart(
                AnimationGroup(Write(eq_my), FadeIn(tag_my, shift=LEFT * 0.12)),
                AnimationGroup(Write(eq_op), FadeIn(tag_op, shift=LEFT * 0.12)),
                lag_ratio=0.5,
            ),
            run_time=3.0,
        )
        self.wait(2.0)
        self.play(FadeOut(block), run_time=0.8)
        self.wait(0.2)

    def _phase_quote(self):
        l1 = Text(
            "A good move is not the move with the best dream.",
            font_size=28, color=GRAY_B,
        )
        l2 = Text(
            "It is the move with the best nightmare.",
            font_size=28, color=WHITE,
        )
        VGroup(l1, l2).arrange(DOWN, buff=0.5).move_to(ORIGIN)

        self.play(FadeIn(l1, shift=UP * 0.14), run_time=1.0)
        self.wait(0.7)
        self.play(FadeIn(l2, shift=UP * 0.14), run_time=1.0)
        self.wait(3.2)
        self.play(FadeOut(VGroup(l1, l2)), run_time=1.1)
