from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class AlphaGoScene(Scene):
    """Scene 7 – AlphaGo: policy, value, and search as synthesis."""

    BG        = "#000000"
    C_POLICY  = "#A78BFA"   # purple  – policy network
    C_VALUE   = "#50C878"   # green   – value network
    C_SEARCH  = "#5B9BD5"   # blue    – MCTS
    C_MOVE    = "#F0A500"   # orange  – final selected move
    BOARD_COL = "#C8A96E"
    GRID_COL  = "#2A2A2A"
    C_BLACK   = "#1A1A1A"
    C_WHITE   = "#F5F5F5"

    N       = 5
    SIDE    = 2.4
    STONE_R = 0.195

    STONE_DATA = [
        (1, 3, "#1A1A1A"), (2, 3, "#F5F5F5"),
        (2, 2, "#1A1A1A"), (3, 2, "#F5F5F5"),
        (1, 1, "#F5F5F5"), (3, 3, "#1A1A1A"),
        (0, 2, "#1A1A1A"), (4, 1, "#F5F5F5"),
    ]
    OCCUPIED = {(1, 3), (2, 3), (2, 2), (3, 2), (1, 1), (3, 3), (0, 2), (4, 1)}

    def construct(self):
        self.camera.background_color = self.BG
        self.BC = np.array([-4.0, 0.0, 0.0])
        self.SP = self.SIDE / (self.N - 1)
        m = {}
        self._phase_title(m)
        self._phase_board_and_components(m)
        self._phase_policy_detail(m)
        self._phase_value_detail(m)
        self._phase_mcts_tree(m)
        self._phase_synthesis(m)
        self._phase_formula(m)
        self._phase_final_move(m)

    # ─── helpers ──────────────────────────────────────────────────────────────

    def gp(self, i, j):
        x = self.BC[0] - self.SIDE / 2 + i * self.SP
        y = self.BC[1] - self.SIDE / 2 + j * self.SP
        return np.array([x, y, 0.0])

    def _make_stone(self, col, r=None):
        r = r or self.STONE_R
        c = Circle(radius=r)
        c.set_fill(col, opacity=1)
        c.set_stroke(color="#C0C0C0" if col == self.C_WHITE else "#3A3A3A", width=1.2)
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

    def _tree_node(self, pos, color, radius=0.30, fill_opacity=0.15):
        c = Circle(radius=radius)
        c.set_fill(color, opacity=fill_opacity)
        c.set_stroke(color=color, width=2.0)
        c.move_to(pos)
        return c

    def _tree_edge(self, p1, p2, color=GRAY_D, width=1.5, clip=0.32):
        d = p2 - p1
        d_norm = d / np.linalg.norm(d)
        return Line(p1 + d_norm * clip, p2 - d_norm * clip,
                    color=color, stroke_width=width)

    # ─── phases ───────────────────────────────────────────────────────────────

    def _phase_title(self, m):
        line = Text("AlphaGo combined three ingredients.",
                    font_size=40, color=WHITE)
        self.play(FadeIn(line, shift=UP * 0.18), run_time=1.1)
        self.wait(1.6)
        self.play(FadeOut(line), run_time=0.65)

    def _phase_board_and_components(self, m):
        bg, lines = self._make_board_group()
        stones    = self._make_stones_group()
        s_lbl     = MathTex("s", font_size=28, color=GRAY_B)
        s_lbl.next_to(bg, UP, buff=0.14)

        self.play(GrowFromCenter(bg), run_time=0.55)
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.02), run_time=0.55)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in stones], lag_ratio=0.08), run_time=0.85)
        self.play(FadeIn(s_lbl), run_time=0.3)
        self.wait(0.35)

        # Three component boxes on right
        BOX_CX  = 2.2
        BOX_W   = 4.2
        BOX_H   = 1.45
        BOX_YS  = [1.8, 0.0, -1.8]
        configs = [
            (r"\pi_\theta(a \mid s)", "policy network",  self.C_POLICY),
            (r"V_\theta(s)",          "value network",   self.C_VALUE),
            ("MCTS",                  "tree search",     self.C_SEARCH),
        ]

        board_rx = self.BC[0] + self.SIDE / 2 + 0.175  # right edge of board bg

        comp_boxes   = VGroup()
        comp_arrows  = VGroup()
        comp_labels  = VGroup()

        for (formula_str, sub_str, color), by in zip(configs, BOX_YS):
            bx_center = np.array([BOX_CX, by, 0.0])

            box = RoundedRectangle(
                width=BOX_W, height=BOX_H, corner_radius=0.18,
                fill_color=color, fill_opacity=0.08,
                stroke_color=color, stroke_width=1.8,
            )
            box.move_to(bx_center)

            if formula_str == "MCTS":
                f_tex = Text("MCTS", font_size=30, color=color, weight="BOLD")
            else:
                f_tex = MathTex(formula_str, font_size=34, color=color)
            f_tex.move_to(bx_center + LEFT * 0.65)

            sub = Text(sub_str, font_size=16, color=GRAY_C)
            sub.move_to(bx_center + RIGHT * 0.9)

            div = Line(
                bx_center + LEFT * 0.08 + UP  * (BOX_H / 2 - 0.12),
                bx_center + LEFT * 0.08 + DOWN * (BOX_H / 2 - 0.12),
                color=color, stroke_width=0.8, stroke_opacity=0.35,
            )

            comp_boxes.add(VGroup(box, div))
            comp_labels.add(VGroup(f_tex, sub))

            # Arrow fans from board centre-y to each box y
            arr = Arrow(
                np.array([board_rx + 0.08, 0.0, 0.0]),
                np.array([BOX_CX - BOX_W / 2 - 0.05, by, 0.0]),
                color=color, stroke_width=2.0,
                max_tip_length_to_length_ratio=0.13,
                buff=0.0,
            )
            comp_arrows.add(arr)

        self.play(
            LaggedStart(
                *[AnimationGroup(
                    Create(cb), GrowArrow(ca),
                    Write(cl[0]), FadeIn(cl[1], shift=LEFT * 0.05),
                  )
                  for cb, ca, cl in zip(comp_boxes, comp_arrows, comp_labels)],
                lag_ratio=0.32,
            ),
            run_time=2.5,
        )
        self.wait(0.7)

        m["bg"]          = bg
        m["lines"]       = lines
        m["stones"]      = stones
        m["s_lbl"]       = s_lbl
        m["comp_boxes"]  = comp_boxes
        m["comp_arrows"] = comp_arrows
        m["comp_labels"] = comp_labels

    def _phase_policy_detail(self, m):
        policy_box = m["comp_boxes"][0][0]

        # Highlight box
        self.play(
            policy_box.animate.set_fill(opacity=0.22).set_stroke(width=2.8),
            run_time=0.35,
        )

        # Heatmap on the board – semi-transparent cells on empty intersections
        heat_probs = {
            (0, 0): 0.03, (1, 0): 0.05, (2, 0): 0.07, (3, 0): 0.04, (4, 0): 0.03,
            (0, 1): 0.06, (2, 1): 0.11, (4, 2): 0.07, (4, 3): 0.04,
            (0, 3): 0.05, (3, 1): 0.07, (0, 4): 0.03,
            (1, 4): 0.46, (2, 4): 0.21, (3, 4): 0.13, (4, 4): 0.07,
        }
        heat_cells = VGroup()
        for (ci, cj), prob in heat_probs.items():
            if (ci, cj) in self.OCCUPIED:
                continue
            cell = Square(side_length=self.SP * 0.80)
            cell.set_fill(self.C_POLICY, opacity=min(prob * 1.6, 0.88))
            cell.set_stroke(width=0)
            cell.move_to(self.gp(ci, cj))
            cell.set_z_index(2)
            heat_cells.add(cell)

        self.play(
            LaggedStart(*[GrowFromCenter(c) for c in heat_cells], lag_ratio=0.025),
            run_time=0.75,
        )

        # Top candidate move ring + label
        top_pos  = self.gp(1, 4)
        top_ring = Circle(radius=self.STONE_R * 1.25,
                          stroke_color=self.C_POLICY, stroke_width=2.5, fill_opacity=0)
        top_ring.move_to(top_pos)
        top_ring.set_z_index(3)

        prob_lbl = MathTex(r"p = 0.46", font_size=17, color=self.C_POLICY)
        prob_lbl.next_to(top_pos, UR, buff=0.07)
        prob_lbl.set_z_index(3)

        self.play(Create(top_ring), FadeIn(prob_lbl), run_time=0.5)

        # Pulse
        pulse = top_ring.copy()
        self.add(pulse)
        self.play(pulse.animate.scale(2.8).set_opacity(0),
                  run_time=0.65, rate_func=ease_out_quad)
        self.remove(pulse)
        self.wait(0.75)

        self.play(
            FadeOut(heat_cells), FadeOut(top_ring), FadeOut(prob_lbl),
            policy_box.animate.set_fill(opacity=0.08).set_stroke(width=1.8),
            run_time=0.55,
        )
        self.wait(0.2)

    def _phase_value_detail(self, m):
        value_box = m["comp_boxes"][1][0]

        self.play(
            value_box.animate.set_fill(opacity=0.22).set_stroke(width=2.8),
            run_time=0.35,
        )

        # Win-probability bar inside / next to the value box
        # Position it just below the value box label
        bar_center = np.array([2.2, -0.55, 0.0])
        WIN_PROB   = 0.73

        bar_bg = RoundedRectangle(width=2.8, height=0.40, corner_radius=0.08)
        bar_bg.set_fill(GRAY_E, opacity=0.30).set_stroke(color=GRAY_D, width=1.0)
        bar_bg.move_to(bar_center)

        bar_full = Rectangle(width=2.8 * WIN_PROB, height=0.40)
        bar_full.set_fill(self.C_VALUE, opacity=0.85).set_stroke(width=0)
        bar_full.align_to(bar_bg, LEFT)
        bar_full.set_y(bar_center[1])

        b_lbl = Text("Black", font_size=13, color=GRAY_C)
        b_lbl.next_to(bar_bg, LEFT, buff=0.12)
        w_lbl = Text("White", font_size=13, color=GRAY_C)
        w_lbl.next_to(bar_bg, RIGHT, buff=0.12)

        pct = MathTex(r"73\%", font_size=20, color=self.C_VALUE)
        pct.next_to(bar_bg, UP, buff=0.10)

        self.play(FadeIn(bar_bg), FadeIn(b_lbl), FadeIn(w_lbl), run_time=0.4)
        self.play(GrowFromEdge(bar_full, LEFT), run_time=0.90, rate_func=ease_out_quad)
        self.play(FadeIn(pct, shift=DOWN * 0.05), run_time=0.38)
        self.wait(0.8)

        self.play(
            FadeOut(VGroup(bar_bg, bar_full, b_lbl, w_lbl, pct)),
            value_box.animate.set_fill(opacity=0.08).set_stroke(width=1.8),
            run_time=0.55,
        )
        self.wait(0.15)

    def _phase_mcts_tree(self, m):
        fade_all = VGroup(
            m["bg"], m["lines"], m["stones"], m["s_lbl"],
            m["comp_boxes"], m["comp_arrows"], m["comp_labels"],
        )
        self.play(FadeOut(fade_all), run_time=0.85)

        title = Text("Monte Carlo Tree Search", font_size=30, color=self.C_SEARCH)
        title.to_edge(UP, buff=0.50)
        self.play(FadeIn(title, shift=DOWN * 0.10), run_time=0.55)

        ROOT_P = np.array([0.0,  2.1,  0.0])
        L1_POS = [
            np.array([-4.5,  0.5,  0.0]),
            np.array([-1.5,  0.5,  0.0]),
            np.array([ 1.5,  0.5,  0.0]),
            np.array([ 4.5,  0.5,  0.0]),
        ]
        L2_POS = [
            np.array([-5.4, -1.3,  0.0]),
            np.array([-3.6, -1.3,  0.0]),
            np.array([-2.4, -1.3,  0.0]),
            np.array([-0.6, -1.3,  0.0]),
        ]
        L1_POLICY = [0.46, 0.24, 0.17, 0.13]
        L1_VISITS = [31,   14,    6,    3]
        L2_VALUES = [+0.68, +0.31, -0.11, +0.57]

        # Root
        root_node = self._tree_node(ROOT_P, self.C_SEARCH, radius=0.36, fill_opacity=0.20)
        root_lbl  = MathTex("s", font_size=22, color=GRAY_B).move_to(ROOT_P)
        self.play(GrowFromCenter(root_node), Write(root_lbl), run_time=0.55)

        # L1 nodes – size encodes policy probability
        l1_nodes  = []
        l1_edges  = []
        l1_plbls  = []
        l1_vlbls  = []

        for i, (pos, policy, visits) in enumerate(zip(L1_POS, L1_POLICY, L1_VISITS)):
            r      = 0.18 + policy * 0.52
            ew     = 0.9  + policy * 3.8
            node   = self._tree_node(pos, self.C_POLICY, radius=r,
                                     fill_opacity=0.10 + policy * 0.25)
            edge   = self._tree_edge(ROOT_P, pos, color=self.C_SEARCH,
                                     width=ew, clip=max(r, 0.36))

            mid    = (ROOT_P + pos) / 2
            side   = LEFT * 0.38 if i < 2 else RIGHT * 0.38
            p_lbl  = MathTex(f"p={policy:.2f}", font_size=13, color=self.C_POLICY)
            p_lbl.move_to(mid + side + UP * 0.10)

            l1_nodes.append(node)
            l1_edges.append(edge)
            l1_plbls.append(p_lbl)

            if i < 2:
                v_lbl = Text(f"N={visits}", font_size=12, color=WHITE)
                v_lbl.move_to(pos + DOWN * 0.02)
                l1_vlbls.append(v_lbl)

        self.play(
            LaggedStart(
                *[AnimationGroup(Create(e), GrowFromCenter(n), FadeIn(pl))
                  for e, n, pl in zip(l1_edges, l1_nodes, l1_plbls)],
                lag_ratio=0.22,
            ),
            run_time=1.9,
        )
        self.wait(0.25)
        self.play(
            LaggedStart(*[FadeIn(v) for v in l1_vlbls], lag_ratio=0.25),
            run_time=0.55,
        )
        self.wait(0.3)

        # L2 – expand top two branches
        l2_nodes = []
        l2_edges = []
        l2_vlbls = []
        l2_parents = [0, 0, 1, 1]

        for idx, (parent_i, pos, val) in enumerate(zip(l2_parents, L2_POS, L2_VALUES)):
            node  = self._tree_node(pos, self.C_VALUE, radius=0.22, fill_opacity=0.14)
            edge  = self._tree_edge(L1_POS[parent_i], pos,
                                    color=self.C_SEARCH, width=1.2, clip=0.22)
            col   = self.C_VALUE if val > 0 else "#FF6B6B"
            v_lbl = MathTex(f"{val:+.2f}", font_size=17, color=col)
            v_lbl.next_to(pos + DOWN * 0.22, DOWN, buff=0.07)

            l2_nodes.append(node)
            l2_edges.append(edge)
            l2_vlbls.append(v_lbl)

        self.play(
            LaggedStart(
                *[AnimationGroup(Create(e), GrowFromCenter(n))
                  for e, n in zip(l2_edges, l2_nodes)],
                lag_ratio=0.18,
            ),
            run_time=1.1,
        )

        eval_ann = MathTex(r"V_\theta(\text{leaf})", font_size=22, color=self.C_VALUE)
        eval_ann.to_edge(DOWN, buff=0.55)
        self.play(FadeIn(eval_ann, shift=UP * 0.07), run_time=0.45)
        self.play(
            LaggedStart(*[FadeIn(v) for v in l2_vlbls], lag_ratio=0.14),
            run_time=0.65,
        )
        self.wait(0.4)

        # Highlight best path (root → L1[0] → L2[0])
        best_e1 = l1_edges[0].copy().set_stroke(color=self.C_MOVE, width=5.0)
        best_e2 = l2_edges[0].copy().set_stroke(color=self.C_MOVE, width=5.0)
        self.play(Create(best_e1), Create(best_e2), run_time=0.60)

        star = Star(n=5, outer_radius=0.24, color=self.C_MOVE, fill_opacity=0.92)
        star.set_stroke(width=0).move_to(L2_POS[0])
        self.play(GrowFromCenter(star), run_time=0.45)

        balance_ann = Text(
            "balance: exploit what looks good  ·  explore what is unknown",
            font_size=17, color=GRAY_C,
        )
        balance_ann.to_edge(DOWN, buff=0.28)
        self.play(FadeOut(eval_ann), FadeIn(balance_ann, shift=UP * 0.05), run_time=0.55)
        self.wait(1.6)

        m["mcts_all"] = VGroup(
            title, root_node, root_lbl,
            *l1_nodes, *l1_edges, *l1_plbls, *l1_vlbls,
            *l2_nodes, *l2_edges, *l2_vlbls,
            best_e1, best_e2, star, balance_ann,
        )

    def _phase_synthesis(self, m):
        self.play(FadeOut(m["mcts_all"]), run_time=0.85)

        items = [
            (r"\pi_\theta(a \mid s)", "policy", self.C_POLICY, +1.45),
            (r"V_\theta(s)",          "value",  self.C_VALUE,   0.0),
            ("MCTS",                  "search", self.C_SEARCH, -1.45),
        ]

        input_grps = VGroup()
        for formula_str, sub_str, color, y in items:
            if formula_str == "MCTS":
                f = Text("MCTS", font_size=30, color=color, weight="BOLD")
            else:
                f = MathTex(formula_str, font_size=34, color=color)
            f.move_to(LEFT * 3.4 + UP * y)
            sub = Text(sub_str, font_size=16, color=GRAY_C)
            sub.next_to(f, DOWN, buff=0.07)
            input_grps.add(VGroup(f, sub))

        # Central combine node
        hub = Circle(radius=0.44)
        hub.set_fill(self.C_MOVE, opacity=0.14)
        hub.set_stroke(color=self.C_MOVE, width=2.5)
        hub.move_to(RIGHT * 0.6)

        hub_lbl = Text("+", font_size=28, color=self.C_MOVE, weight="BOLD")
        hub_lbl.move_to(hub.get_center())

        conv_arrows = VGroup()
        for _, _, color, y in items:
            src = np.array([-1.95, y, 0.0])
            # arrow end: point on hub perimeter in direction of src→hub
            hub_c  = np.array([0.6, 0.0, 0.0])
            d      = hub_c - src
            d_norm = d / np.linalg.norm(d)
            dst    = hub_c - d_norm * 0.44
            arr    = Arrow(src, dst, color=color, stroke_width=2.2,
                           max_tip_length_to_length_ratio=0.14, buff=0.0)
            conv_arrows.add(arr)

        # Output arrow + label
        out_arr = Arrow(
            hub.get_right() + RIGHT * 0.06,
            RIGHT * 3.55,
            color=self.C_MOVE, stroke_width=3.0,
            max_tip_length_to_length_ratio=0.14,
        )
        a_star  = MathTex(r"a^*", font_size=54, color=self.C_MOVE)
        a_star.move_to(RIGHT * 4.25)
        best_lbl = Text("best move", font_size=17, color=GRAY_C)
        best_lbl.next_to(a_star, DOWN, buff=0.10)

        self.play(
            LaggedStart(*[FadeIn(g, shift=RIGHT * 0.14) for g in input_grps], lag_ratio=0.22),
            run_time=1.15,
        )
        self.play(
            LaggedStart(*[GrowArrow(a) for a in conv_arrows], lag_ratio=0.14),
            GrowFromCenter(hub),
            Write(hub_lbl),
            run_time=1.0,
        )
        self.play(
            GrowArrow(out_arr),
            Write(a_star),
            FadeIn(best_lbl, shift=UP * 0.06),
            run_time=0.80,
        )

        pulse = Circle(radius=0.38, stroke_color=self.C_MOVE, stroke_width=2.5, fill_opacity=0)
        pulse.move_to(a_star.get_center())
        self.add(pulse)
        self.play(pulse.animate.scale(3.8).set_opacity(0),
                  run_time=0.75, rate_func=ease_out_quad)
        self.remove(pulse)
        self.wait(1.5)

        m["synth_all"] = VGroup(
            input_grps, conv_arrows, hub, hub_lbl, out_arr, a_star, best_lbl,
        )

    def _phase_formula(self, m):
        self.play(FadeOut(m["synth_all"]), run_time=0.70)

        ucb = MathTex(
            r"Q(s,a)"
            r"\;+\;"
            r"c \cdot \frac{P(s,a)\,\sqrt{N(s)}}{1 + N(s,a)}",
            font_size=46,
        )
        ucb.move_to(UP * 0.55)

        under_q = MathTex(r"\underbrace{\hspace{2.0cm}}_{\text{value so far}}",
                          font_size=36, color=self.C_VALUE)
        under_q.align_to(ucb, LEFT).shift(DOWN * 0.35)

        under_exp = MathTex(
            r"\underbrace{\hspace{4.2cm}}_{\text{exploration bonus}}",
            font_size=36, color=self.C_POLICY,
        )
        under_exp.align_to(ucb, RIGHT).shift(DOWN * 0.35)

        caption = Text(
            "balance moves that already look good  ·  with moves not yet explored",
            font_size=20, color=GRAY_C,
        )
        caption.next_to(ucb, DOWN, buff=0.80)

        self.play(Write(ucb), run_time=1.7)
        self.play(
            FadeIn(under_q,   shift=UP * 0.06),
            FadeIn(under_exp, shift=UP * 0.06),
            run_time=0.65,
        )
        self.play(FadeIn(caption, shift=UP * 0.08), run_time=0.6)
        self.wait(2.1)
        self.play(FadeOut(VGroup(ucb, under_q, under_exp, caption)), run_time=0.75)

    def _phase_final_move(self, m):
        bg, lines = self._make_board_group()
        stones    = self._make_stones_group()

        self.play(FadeIn(VGroup(bg, lines, stones)), run_time=0.65)

        # Ghost candidates flicker briefly (policy-suggested)
        ghost_pos = [(0, 0), (3, 4), (4, 3), (0, 4)]
        ghosts = VGroup()
        for gi, gj in ghost_pos:
            g = Circle(radius=self.STONE_R * 0.75, fill_opacity=0)
            g.set_stroke(color=self.C_POLICY, width=1.4, opacity=0.40)
            g.move_to(self.gp(gi, gj))
            ghosts.add(g)

        self.play(LaggedStart(*[FadeIn(g) for g in ghosts], lag_ratio=0.15), run_time=0.45)
        self.play(FadeOut(ghosts), run_time=0.30)

        # AlphaGo move: (1, 4) — top-left area, unexpected
        move_pos = self.gp(1, 4)
        chosen   = self._make_stone(self.C_BLACK)
        chosen.move_to(move_pos)

        ring = Circle(radius=self.STONE_R * 1.45,
                      stroke_color=self.C_MOVE, stroke_width=2.5, fill_opacity=0)
        ring.move_to(move_pos)

        move_num = Text("37", font_size=13, color=self.C_MOVE, weight="BOLD")
        move_num.next_to(move_pos, UR, buff=0.06)

        self.play(GrowFromCenter(chosen), run_time=0.60)
        self.play(Create(ring), FadeIn(move_num), run_time=0.48)

        pulse = ring.copy()
        self.add(pulse)
        self.play(pulse.animate.scale(3.2).set_opacity(0),
                  run_time=0.75, rate_func=ease_out_quad)
        self.remove(pulse)

        # Three metric rows to the right of the board
        metrics_data = [
            (r"\pi_\theta(a \mid s)",   "low",    GRAY_C,        self.C_POLICY),
            (r"V_\theta(T(s,\,a))",     r"+0.81", self.C_VALUE,  self.C_VALUE),
            (r"N_{\mathrm{visits}}",    "high",   self.C_SEARCH, self.C_SEARCH),
        ]

        rows = VGroup()
        for formula_str, val_str, val_col, label_col in metrics_data:
            lbl = MathTex(formula_str, font_size=22, color=label_col)
            if val_str in ("low", "high"):
                val = Text(val_str, font_size=22, color=val_col)
            else:
                val = MathTex(val_str, font_size=22, color=val_col)
            row = VGroup(lbl, val).arrange(RIGHT, buff=0.45)
            rows.add(row)

        rows.arrange(DOWN, buff=0.38)
        rows.move_to(RIGHT * 3.2)

        self.play(
            LaggedStart(*[FadeIn(r, shift=LEFT * 0.10) for r in rows], lag_ratio=0.22),
            run_time=1.0,
        )
        self.wait(1.2)

        # Closing line
        close = Text("Not alien. Optimized.", font_size=36, color=WHITE, weight="BOLD")
        close.to_edge(DOWN, buff=0.52)
        self.play(FadeIn(close, shift=UP * 0.12), run_time=0.85)
        self.wait(3.2)
