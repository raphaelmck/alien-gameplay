from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class TreeExplosionScene(Scene):
    """Scene 3 – The tree explosion: exponential complexity."""

    BG     = "#000000"
    C_NODE = "#A78BFA"   # purple — tree nodes
    C_EDGE = "#3A3A3A"   # dark gray — edges
    C_EXP  = "#F0A500"   # orange — exponent labels
    C_LIM  = "#FF6B6B"   # red — depth limit line

    B      = 3           # branching factor shown in tree
    NODE_R = 0.20

    Y_TOP  =  2.6
    Y_STEP =  1.45

    def construct(self):
        self.camera.background_color = self.BG
        self._phase_intro()
        self._phase_formula()
        self._phase_tree_growth()
        self._phase_fog()
        self._phase_numbers()
        self._phase_depth_limit()

    # ─── layout helpers ───────────────────────────────────────────────────────

    def _xs(self, depth):
        """X-coordinates for nodes at a given depth."""
        n = self.B ** depth
        if n == 1:
            return np.array([0.0])
        spreads = [0.0, 3.2, 6.0, 7.6, 7.8]
        s = spreads[min(depth, len(spreads) - 1)]
        return np.linspace(-s / 2, s / 2, n)

    def _y(self, depth):
        return self.Y_TOP - depth * self.Y_STEP

    # ─── phases ──────────────────────────────────────────────────────────────

    def _phase_intro(self):
        l1 = Text("Minimax is correct.", font_size=46, color=WHITE)
        l2 = Text("But real games are too large to search completely.",
                  font_size=28, color=GRAY_C)
        g = VGroup(l1, l2).arrange(DOWN, buff=0.52).move_to(ORIGIN)

        self.play(FadeIn(l1, shift=UP * 0.15), run_time=0.9)
        self.wait(0.45)
        self.play(FadeIn(l2, shift=UP * 0.12), run_time=0.8)
        self.wait(1.8)
        self.play(FadeOut(g), run_time=0.7)
        self.wait(0.2)

    def _phase_formula(self):
        header = Text("nodes in a depth-d tree with branching factor b",
                      font_size=20, color=GRAY_C)

        series = MathTex(
            r"1", r"\;+\;", r"b", r"\;+\;",
            r"b^2", r"\;+\;", r"b^3", r"\;+\;\cdots+\;",
            r"b^d",
            font_size=46,
        )
        series[-1].set_color(self.C_EXP)
        series.move_to(UP * 0.55)
        header.next_to(series, UP, buff=0.42)

        approx = MathTex(r"\approx\; b^d", font_size=52, color=self.C_EXP)
        approx.next_to(series, DOWN, buff=0.55)
        note = Text("exponential in search depth", font_size=22, color=GRAY_C)
        note.next_to(approx, DOWN, buff=0.3)

        self.play(FadeIn(header, shift=UP * 0.1), run_time=0.5)
        self.play(
            LaggedStart(*[Write(series[i]) for i in range(len(series))],
                        lag_ratio=0.22),
            run_time=2.5,
        )
        self.wait(0.55)
        self.play(
            GrowFromCenter(approx),
            FadeIn(note, shift=UP * 0.1),
            run_time=0.9,
        )
        self.wait(1.8)
        self.play(FadeOut(VGroup(header, series, approx, note)), run_time=0.8)
        self.wait(0.2)

    def _phase_tree_growth(self):
        MAX_D     = 3
        exp_strs  = [r"1", r"b", r"b^2", r"b^3"]
        nodes     = []   # nodes[d] = list of Dot
        edges     = []   # edges[d] = edges from level d → d+1
        dtags     = []   # right-side depth annotations

        for d in range(MAX_D + 1):
            n   = self.B ** d
            r   = self.NODE_R if d < 3 else self.NODE_R * 0.6
            opc = 1.0          if d < 3 else 0.80
            level = []
            for i in range(n):
                pos = np.array([self._xs(d)[i], self._y(d), 0.0])
                dot = Dot(pos, radius=r, color=self.C_NODE)
                dot.set_fill(self.C_NODE, opacity=opc)
                dot.set_stroke(width=0)
                level.append(dot)
            nodes.append(level)

            tag = MathTex(
                rf"d={d}:\quad {exp_strs[d]}",
                font_size=26, color=self.C_EXP,
            )
            tag.move_to(np.array([5.3, self._y(d), 0.0]))
            dtags.append(tag)

        for d in range(MAX_D):
            xs_p = self._xs(d)
            xs_c = self._xs(d + 1)
            yp   = self._y(d)
            yc   = self._y(d + 1)
            sw   = 1.4 if d < 2 else 0.7
            level_edges = []
            for pi, px in enumerate(xs_p):
                for ci in range(self.B):
                    cx = xs_c[pi * self.B + ci]
                    level_edges.append(Line(
                        np.array([px, yp, 0.0]),
                        np.array([cx, yc, 0.0]),
                        color=self.C_EDGE, stroke_width=sw,
                    ))
            edges.append(level_edges)

        # ── animate depth by depth ────────────────────────────────────────────

        # Root
        self.play(GrowFromCenter(nodes[0][0]), run_time=0.5)
        self.play(FadeIn(dtags[0], shift=LEFT * 0.1), run_time=0.4)
        self.wait(0.2)

        # Depth 1 — annotate branching factor
        self.play(
            LaggedStart(*[Create(e) for e in edges[0]], lag_ratio=0.15),
            LaggedStart(*[GrowFromCenter(n) for n in nodes[1]], lag_ratio=0.15),
            run_time=0.9,
        )
        mid_edge = edges[0][self.B // 2]
        b_lbl    = MathTex(r"b\;\text{branches}", font_size=22, color=self.C_NODE)
        b_lbl.next_to(mid_edge.get_midpoint(), RIGHT, buff=0.15)
        self.play(
            FadeIn(b_lbl, shift=UP * 0.08),
            FadeIn(dtags[1], shift=LEFT * 0.1),
            run_time=0.5,
        )
        self.wait(0.25)

        # Depth 2
        self.play(
            LaggedStart(*[Create(e) for e in edges[1]], lag_ratio=0.06),
            LaggedStart(*[GrowFromCenter(n) for n in nodes[2]], lag_ratio=0.06),
            run_time=1.1,
        )
        self.play(FadeIn(dtags[2], shift=LEFT * 0.1), run_time=0.4)
        self.wait(0.3)

        # Depth 3 — crowded, shows the explosion
        self.play(FadeOut(b_lbl), run_time=0.3)
        self.play(
            LaggedStart(*[Create(e) for e in edges[2]], lag_ratio=0.02),
            LaggedStart(*[GrowFromCenter(n) for n in nodes[3]], lag_ratio=0.02),
            run_time=1.5,
        )
        self.play(FadeIn(dtags[3], shift=LEFT * 0.1), run_time=0.4)
        self.wait(0.6)

        self._nodes = nodes
        self._edges = edges
        self._dtags = dtags

    def _phase_fog(self):
        # Ghost depth-4 level (81 nodes) fades in then fog swallows it all
        n4    = self.B ** 4   # 81
        y4    = self._y(4)
        xs4   = np.linspace(-7.5 / 2, 7.5 / 2, n4)
        xs3   = self._xs(3)

        ghost_dots  = []
        ghost_lines = []

        for x in xs4:
            g = Dot(np.array([x, y4, 0.0]), radius=0.08, color=self.C_NODE)
            g.set_fill(self.C_NODE, opacity=0.0)
            ghost_dots.append(g)

        for pi, px in enumerate(xs3):
            for ci in range(self.B):
                cx = xs4[pi * self.B + ci]
                gl = Line(
                    np.array([px, self._y(3), 0.0]),
                    np.array([cx, y4, 0.0]),
                    color=self.C_EDGE, stroke_width=0.4,
                )
                gl.set_stroke(opacity=0.0)
                ghost_lines.append(gl)

        for obj in ghost_dots + ghost_lines:
            self.add(obj)

        # Ghost level materialises
        self.play(
            *[g.animate.set_fill(opacity=0.55)   for g in ghost_dots],
            *[gl.animate.set_stroke(opacity=0.28) for gl in ghost_lines],
            run_time=0.9,
        )
        self.wait(0.2)

        # Fog covers depth 3 and everything below
        y_fog_top = self._y(2) - 0.65
        fog = Rectangle(
            width=config.frame_width + 1,
            height=abs(y4) + 6.0,
            fill_color=BLACK,
            fill_opacity=0.0,
            stroke_width=0,
        )
        fog.move_to(np.array([0.0, y_fog_top - fog.get_height() / 2, 0.0]))
        self.add(fog)

        self.play(
            fog.animate.set_fill(opacity=0.93),
            *[n.animate.set_fill(opacity=0.12)   for n in self._nodes[3]],
            *[e.animate.set_stroke(opacity=0.08)  for e in self._edges[2]],
            *[g.animate.set_fill(opacity=0.0)    for g in ghost_dots],
            *[gl.animate.set_stroke(opacity=0.0)  for gl in ghost_lines],
            run_time=1.8, rate_func=smooth,
        )

        self._fog         = fog
        self._ghost_dots  = ghost_dots
        self._ghost_lines = ghost_lines

    def _phase_numbers(self):
        # Show concrete node counts for Chess and Go — floating over the fog
        # Row data: (game label, b value, d value, result tex, result color)
        rows = [
            (r"\text{Chess}", r"b \approx 35",  r"d \approx 40",  r"\approx 10^{62}",  WHITE),
            (r"\text{Go}",    r"b \approx 250", r"d \approx 150", r"\approx 10^{359}", WHITE),
        ]

        col_game   = VGroup()
        col_b      = VGroup()
        col_d      = VGroup()
        col_result = VGroup()

        for game_tex, b_tex, d_tex, res_tex, res_col in rows:
            col_game.add(  MathTex(game_tex,  font_size=30, color=GRAY_B))
            col_b.add(     MathTex(b_tex,     font_size=30, color=self.C_EXP))
            col_d.add(     MathTex(d_tex,     font_size=30, color=self.C_EXP))
            col_result.add(MathTex(res_tex,   font_size=30, color=res_col))

        col_game.arrange(DOWN,   buff=0.42, aligned_edge=RIGHT)
        col_b.arrange(DOWN,      buff=0.42, aligned_edge=LEFT)
        col_d.arrange(DOWN,      buff=0.42, aligned_edge=LEFT)
        col_result.arrange(DOWN, buff=0.42, aligned_edge=LEFT)

        sep   = MathTex(r"\Rightarrow", font_size=30, color=GRAY_D)
        sep2  = sep.copy()
        seps  = VGroup(sep, sep2).arrange(DOWN, buff=0.42)

        table = VGroup(col_game, col_b, col_d, seps, col_result)
        table.arrange(RIGHT, buff=0.38, aligned_edge=UP)

        # Place in the fog — vertically centred in the dark region below the tree
        y_fog_centre = self._y(3) - 0.6
        table.move_to(np.array([0.0, y_fog_centre, 0.0]))

        ref = MathTex(
            r"\text{atoms in the observable universe} \approx 10^{80}",
            font_size=20, color=GRAY_D,
        )
        ref.next_to(table, DOWN, buff=0.42)

        # Animate rows one at a time
        for i in range(len(rows)):
            self.play(
                LaggedStart(
                    FadeIn(col_game[i],   shift=UP * 0.08),
                    FadeIn(col_b[i],      shift=UP * 0.08),
                    FadeIn(col_d[i],      shift=UP * 0.08),
                    FadeIn(seps[i],       shift=UP * 0.08),
                    FadeIn(col_result[i], shift=UP * 0.08),
                    lag_ratio=0.18,
                ),
                run_time=1.0,
            )
            self.wait(0.5)

        self.play(FadeIn(ref, shift=UP * 0.08), run_time=0.7)
        self.wait(2.0)

        self._numbers_grp = VGroup(table, ref)

    def _phase_depth_limit(self):
        # Centered dashed line cuts the tree between depth 2 and the fog
        y_limit  = self._y(2) - 0.52
        half_w   = 5.2   # symmetric around x = 0, stops just inside the depth tags

        line = DashedLine(
            np.array([-half_w, y_limit, 0.0]),
            np.array([ half_w, y_limit, 0.0]),
            color=self.C_LIM, stroke_width=2.5,
            dash_length=0.18,
        )

        stop = Text("Search stops here.", font_size=26, color=self.C_LIM)
        game = Text("But the game does not.", font_size=26, color=GRAY_C)
        VGroup(stop, game).arrange(DOWN, buff=0.24).next_to(line, UP, buff=0.32)

        self.play(Create(line), run_time=0.9)
        self.wait(0.15)
        self.play(FadeIn(stop, shift=UP * 0.1), run_time=0.65)
        self.play(FadeIn(game, shift=UP * 0.1), run_time=0.65)
        self.wait(2.5)

        # Fade everything out — hands off to the evaluation scene
        all_mobs = VGroup(
            *[n for level in self._nodes for n in level],
            *[e for level in self._edges  for e in level],
            *self._dtags,
            self._fog,
            self._numbers_grp,
            line, stop, game,
        )
        self.play(FadeOut(all_mobs), run_time=1.3)
        self.wait(0.4)
