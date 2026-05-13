from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class MinimaxScene(Scene):
    """Scene 2 – Minimax: intelligence as recursion."""

    BG     = "#000000"
    C_MAX  = "#F0A500"   # orange  — maximiser
    C_MIN  = "#5B9BD5"   # blue    — minimiser
    C_WIN  = "#50C878"   # green   — positive value
    C_LOSE = "#FF6B6B"   # red     — negative value
    C_DRAW = "#909090"   # gray    — zero value

    NODE_R = 0.36

    POS = {
        "root": np.array([ 0.0,  2.7, 0.0]),
        "L":    np.array([-2.6,  0.7, 0.0]),
        "R":    np.array([ 2.6,  0.7, 0.0]),
        "LL":   np.array([-3.9, -1.3, 0.0]),
        "LR":   np.array([-1.3, -1.3, 0.0]),
        "RL":   np.array([ 1.3, -1.3, 0.0]),
        "RR":   np.array([ 3.9, -1.3, 0.0]),
    }

    LEAF_VALS = {"LL": +1, "LR": -1, "RL": 0, "RR": +1}

    def construct(self):
        self.camera.background_color = self.BG
        self._phase_zero_sum()
        self._phase_equations()
        self._phase_tree()
        self._phase_leaves()
        self._phase_propagate()
        self._phase_argmax()
        self._phase_quote()

    # ─── helpers ─────────────────────────────────────────────────────────────

    def _node(self, key, color, label=None, lfs=20):
        pos = self.POS[key]
        c = Circle(radius=self.NODE_R)
        c.set_fill(color, opacity=0.12).set_stroke(color=color, width=2.2)
        c.move_to(pos)
        g = VGroup(c)
        if label:
            t = MathTex(label, font_size=lfs, color=color).move_to(pos)
            g.add(t)
        return g

    def _edge(self, k1, k2, color=GRAY_D, width=1.8):
        p1, p2 = self.POS[k1], self.POS[k2]
        d = (p2 - p1) / np.linalg.norm(p2 - p1)
        return Line(p1 + d * self.NODE_R, p2 - d * self.NODE_R,
                    color=color, stroke_width=width)

    def _val_col(self, v):
        return self.C_WIN if v > 0 else (self.C_LOSE if v < 0 else self.C_DRAW)

    def _val_tex(self, v):
        return r"+1" if v > 0 else (r"-1" if v < 0 else r"0")

    # ─── phases ──────────────────────────────────────────────────────────────

    def _phase_zero_sum(self):
        t = Text("zero-sum", font_size=58, color=WHITE, weight="BOLD")
        s = Text("your gain  =  your opponent's loss", font_size=26, color=GRAY_C)
        g = VGroup(t, s).arrange(DOWN, buff=0.42).move_to(ORIGIN)
        self.play(FadeIn(t, shift=UP * 0.18), run_time=0.85)
        self.play(FadeIn(s, shift=UP * 0.12), run_time=0.75)
        self.wait(1.6)
        self.play(FadeOut(g), run_time=0.75)
        self.wait(0.15)

    def _phase_equations(self):
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

        tag_my = Text("my turn",         font_size=21, color=self.C_MAX)
        tag_op = Text("opponent's turn", font_size=21, color=self.C_MIN)

        row_my = VGroup(eq_my, tag_my).arrange(RIGHT, buff=0.52)
        row_op = VGroup(eq_op, tag_op).arrange(RIGHT, buff=0.52)
        block  = VGroup(row_my, row_op).arrange(DOWN, buff=0.58).move_to(ORIGIN)

        self.play(
            LaggedStart(
                AnimationGroup(Write(eq_my), FadeIn(tag_my, shift=LEFT * 0.12)),
                AnimationGroup(Write(eq_op), FadeIn(tag_op, shift=LEFT * 0.12)),
                lag_ratio=0.5,
            ),
            run_time=3.2,
        )
        self.wait(2.0)
        self.play(FadeOut(block), run_time=0.8)
        self.wait(0.2)

    def _phase_tree(self):
        n_root = self._node("root", self.C_MAX, r"\max")
        n_l    = self._node("L",    self.C_MIN, r"\min")
        n_r    = self._node("R",    self.C_MIN, r"\min")
        lf_ll  = self._node("LL",   GRAY_D)
        lf_lr  = self._node("LR",   GRAY_D)
        lf_rl  = self._node("RL",   GRAY_D)
        lf_rr  = self._node("RR",   GRAY_D)

        e_l  = self._edge("root", "L")
        e_r  = self._edge("root", "R")
        e_ll = self._edge("L", "LL")
        e_lr = self._edge("L", "LR")
        e_rl = self._edge("R", "RL")
        e_rr = self._edge("R", "RR")

        self.play(GrowFromCenter(n_root), run_time=0.55)
        self.play(
            LaggedStart(
                AnimationGroup(Create(e_l), GrowFromCenter(n_l)),
                AnimationGroup(Create(e_r), GrowFromCenter(n_r)),
                lag_ratio=0.28,
            ),
            run_time=0.95,
        )
        self.play(
            LaggedStart(*[
                AnimationGroup(Create(e), GrowFromCenter(lf))
                for e, lf in [
                    (e_ll, lf_ll), (e_lr, lf_lr),
                    (e_rl, lf_rl), (e_rr, lf_rr),
                ]
            ], lag_ratio=0.18),
            run_time=1.3,
        )
        self.wait(0.35)

        self._n_root = n_root
        self._n_l    = n_l
        self._n_r    = n_r
        self._lf     = {"LL": lf_ll, "LR": lf_lr, "RL": lf_rl, "RR": lf_rr}
        self._e_l    = e_l
        self._e_r    = e_r
        self._e_ll   = e_ll
        self._e_lr   = e_lr
        self._e_rl   = e_rl
        self._e_rr   = e_rr

    def _phase_leaves(self):
        self._vl = {}
        anims = []
        for k in ("LL", "LR", "RL", "RR"):
            v      = self.LEAF_VALS[k]
            col    = self._val_col(v)
            new_lf = self._node(k, col)
            lbl    = MathTex(self._val_tex(v), font_size=34, color=col)
            lbl.move_to(self.POS[k])
            self._vl[k] = lbl
            anims.append(AnimationGroup(Transform(self._lf[k], new_lf), Write(lbl)))

        self.play(LaggedStart(*anims, lag_ratio=0.22), run_time=2.0)
        self.wait(0.45)

    def _phase_propagate(self):
        # ── Left MIN: min(+1, -1) = -1 ──────────────────────────────
        self.play(
            Indicate(self._vl["LL"], color=self.C_WIN,  scale_factor=1.28),
            Indicate(self._vl["LR"], color=self.C_LOSE, scale_factor=1.28),
            run_time=0.8,
        )
        copy_lr = self._vl["LR"].copy()
        self.play(
            self._e_ll.animate.set_color(GRAY_E).set_stroke(width=1.2),
            self._e_lr.animate.set_color(self.C_LOSE).set_stroke(width=3.2),
            copy_lr.animate.move_to(self.POS["L"]),
            run_time=0.62,
        )
        self.remove(copy_lr)
        lv_l = MathTex(r"-1", font_size=26, color=self.C_LOSE)
        lv_l.next_to(self._n_l[0], DOWN, buff=0.07)
        self.play(Write(lv_l), run_time=0.42)
        self.wait(0.22)

        # ── Right MIN: min(0, +1) = 0 ────────────────────────────────
        self.play(
            Indicate(self._vl["RL"], color=self.C_DRAW, scale_factor=1.28),
            Indicate(self._vl["RR"], color=self.C_WIN,  scale_factor=1.28),
            run_time=0.8,
        )
        copy_rl = self._vl["RL"].copy()
        self.play(
            self._e_rl.animate.set_color(self.C_DRAW).set_stroke(width=3.2),
            self._e_rr.animate.set_color(GRAY_E).set_stroke(width=1.2),
            copy_rl.animate.move_to(self.POS["R"]),
            run_time=0.62,
        )
        self.remove(copy_rl)
        lv_r = MathTex(r"0", font_size=26, color=self.C_DRAW)
        lv_r.next_to(self._n_r[0], DOWN, buff=0.07)
        self.play(Write(lv_r), run_time=0.42)
        self.wait(0.22)

        # ── Root MAX: max(-1, 0) = 0  →  right branch wins ───────────
        self.play(
            Indicate(lv_l, color=self.C_LOSE, scale_factor=1.28),
            Indicate(lv_r, color=self.C_DRAW, scale_factor=1.28),
            run_time=0.8,
        )
        copy_r = lv_r.copy()
        self.play(
            self._e_l.animate.set_color(GRAY_E).set_stroke(width=1.2),
            self._e_r.animate.set_color(self.C_MAX).set_stroke(width=3.2),
            copy_r.animate.move_to(self.POS["root"]),
            run_time=0.62,
        )
        self.remove(copy_r)
        lv_root = MathTex(r"0", font_size=28, color=self.C_MAX)
        lv_root.next_to(self._n_root[0], DOWN, buff=0.07)
        self.play(Write(lv_root), run_time=0.44)
        self.wait(0.35)

        # ── Highlight optimal path ────────────────────────────────────
        opt = VGroup(
            self._e_r.copy().set_stroke(color=WHITE, width=5.0),
            self._e_rl.copy().set_stroke(color=WHITE, width=5.0),
        )
        self.play(Create(opt[0]), Create(opt[1]), run_time=0.65)
        pulse = Circle(
            radius=self.NODE_R * 1.5,
            stroke_color=WHITE, stroke_width=2.5, fill_opacity=0,
        )
        pulse.move_to(self.POS["RL"])
        self.add(pulse)
        self.play(
            pulse.animate.scale(2.8).set_opacity(0),
            run_time=0.7, rate_func=ease_out_quad,
        )
        self.remove(pulse)
        self.wait(0.7)

        self._lv_l    = lv_l
        self._lv_r    = lv_r
        self._lv_root = lv_root
        self._opt     = opt

    def _phase_argmax(self):
        tree_all = VGroup(
            self._n_root, self._n_l, self._n_r,
            *self._lf.values(), *self._vl.values(),
            self._e_l, self._e_r,
            self._e_ll, self._e_lr, self._e_rl, self._e_rr,
            self._lv_l, self._lv_r, self._lv_root,
            self._opt,
        )

        eq = MathTex(
            r"a^*", r"\;=\;",
            r"\underset{a}{\mathrm{arg\,max}}",
            r"\; V\!\bigl(T(s,a)\bigr)",
            font_size=42,
        )
        eq[2].set_color(self.C_MAX)
        eq.move_to(RIGHT * 2.55)

        tree_all.generate_target()
        tree_all.target.scale(0.76).move_to(LEFT * 2.8)

        self.play(MoveToTarget(tree_all), run_time=1.15)
        self.play(Write(eq), run_time=1.4)
        self.wait(1.8)

        self._tree_all  = tree_all
        self._eq_argmax = eq

    def _phase_quote(self):
        self.play(FadeOut(self._tree_all), FadeOut(self._eq_argmax), run_time=1.05)

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
