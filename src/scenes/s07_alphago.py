from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class AlphaGoScene(Scene):
    """Scene 7 – AlphaGo: policy, value, and search as synthesis."""

    BG        = "#000000"
    C_POLICY  = "#A78BFA"
    C_VALUE   = "#50C878"
    C_SEARCH  = "#5B9BD5"
    C_MOVE    = "#F0A500"
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
    OCCUPIED = {(1,3),(2,3),(2,2),(3,2),(1,1),(3,3),(0,2),(4,1)}

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
        self._phase_formula(m)

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
        logo = SVGMobject("src/scenes/alphago.svg")
        logo.set(width=6)
        for part in logo.family_members_with_points():
            part.set_fill(opacity=1)

        self.play(DrawBorderThenFill(logo), run_time=3)
        self.wait(0.5)

        # Move straight up, stay centred horizontally, don't shrink much
        logo.generate_target()
        logo.target.set(width=3.2)
        logo.target.to_edge(UP, buff=0.28)
        logo.target.set_x(0)   # keep centred
        self.play(MoveToTarget(logo), run_time=0.80)
        self.wait(0.25)

        m["logo"] = logo

    def _phase_board_and_components(self, m):
        bg, lines = self._make_board_group()
        stones    = self._make_stones_group()
        s_lbl     = MathTex("s", font_size=28, color=GRAY_B)
        s_lbl.next_to(bg, UP, buff=0.20)

        self.play(GrowFromCenter(bg), run_time=0.55)
        self.play(LaggedStart(*[Create(l) for l in lines], lag_ratio=0.02), run_time=0.55)
        self.play(LaggedStart(*[GrowFromCenter(s) for s in stones], lag_ratio=0.08), run_time=0.85)
        self.play(FadeIn(s_lbl), run_time=0.3)
        self.wait(0.35)

        # Three component boxes ─────────────────────────────────────────────
        BOX_CX = 2.2
        BOX_W  = 3.6
        BOX_H  = 1.22
        BOX_YS = [1.40, 0.0, -1.40]   # closer together → more space above

        configs = [
            (r"\pi_\theta(a \mid s)", "policy network",  self.C_POLICY),
            (r"V_\theta(s)",          "value network",   self.C_VALUE),
            ("MCTS",                  "tree search",     self.C_SEARCH),
        ]

        board_rx = self.BC[0] + self.SIDE / 2 + 0.175

        comp_boxes   = VGroup()
        comp_arrows  = VGroup()
        comp_labels  = VGroup()

        for (formula_str, sub_str, color), by in zip(configs, BOX_YS):
            bx = np.array([BOX_CX, by, 0.0])

            box = RoundedRectangle(
                width=BOX_W, height=BOX_H, corner_radius=0.16,
                fill_color=color, fill_opacity=0.08,
                stroke_color=color, stroke_width=1.8,
            )
            box.move_to(bx)

            if formula_str == "MCTS":
                f_tex = Tex(r"\textbf{MCTS}", font_size=30, color=color)
            else:
                f_tex = MathTex(formula_str, font_size=31, color=color)
            # push formula to the left quarter of the box
            f_tex.move_to(bx + LEFT * 0.88)

            # subtitle sits in the right half, clear of the centre divider
            sub = Tex(sub_str, font_size=14, color=GRAY_C)
            sub.move_to(bx + RIGHT * 0.72)

            # divider at box centre
            div = Line(
                bx + np.array([0.0,  BOX_H / 2 - 0.10, 0]),
                bx + np.array([0.0, -(BOX_H / 2 - 0.10), 0]),
                color=color, stroke_width=0.8, stroke_opacity=0.35,
            )

            comp_boxes.add(VGroup(box, div))
            comp_labels.add(VGroup(f_tex, sub))

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
        s_lbl      = m["s_lbl"]

        self.play(
            policy_box.animate.set_fill(opacity=0.22).set_stroke(width=2.8),
            run_time=0.35,
        )

        # Probability map – rings only (ghost / outline pieces), size+opacity by prob
        heat_probs = {
            (0,0):0.04, (1,0):0.06, (2,0):0.08, (3,0):0.05, (4,0):0.04,
            (0,1):0.07, (2,1):0.12, (3,1):0.09,
            (1,2):0.10,             (4,2):0.09,
            (0,3):0.06,             (4,3):0.07,
            (0,4):0.05, (1,4):0.55, (2,4):0.22, (3,4):0.14, (4,4):0.09,
        }

        pulse_rings = VGroup()
        for (ci, cj), prob in heat_probs.items():
            r       = self.STONE_R * (0.80 + prob * 0.55)
            opacity = min(0.45 + prob * 0.85, 1.0)
            ring    = Circle(radius=r, fill_opacity=0)
            ring.set_stroke(color=self.C_POLICY, width=2.2, opacity=opacity)
            ring.move_to(self.gp(ci, cj))
            ring.set_z_index(2)
            pulse_rings.add(ring)

        # Rings appear (pulse in), then s label rises
        self.play(
            LaggedStart(*[GrowFromCenter(r) for r in pulse_rings], lag_ratio=0.020),
            s_lbl.animate.shift(UP * 0.34),
            run_time=0.80,
        )
        self.wait(0.40)

        # Rings pulse outward and fade — leaving a clean board
        self.play(
            *[r.animate.scale(2.2).set_opacity(0) for r in pulse_rings],
            run_time=0.65,
            rate_func=ease_out_quad,
        )
        self.remove(*pulse_rings)

        # Top candidate
        top_pos  = self.gp(1, 4)
        top_ring = Circle(radius=self.STONE_R * 1.38,
                          stroke_color=self.C_POLICY, stroke_width=2.5, fill_opacity=0)
        top_ring.move_to(top_pos).set_z_index(3)
        prob_lbl = MathTex(r"p = 0.55", font_size=16, color=self.C_POLICY)
        prob_lbl.next_to(top_pos, UR, buff=0.06).set_z_index(3)

        self.play(Create(top_ring), FadeIn(prob_lbl), run_time=0.45)
        pulse = top_ring.copy()
        self.add(pulse)
        self.play(pulse.animate.scale(2.8).set_opacity(0),
                  run_time=0.60, rate_func=ease_out_quad)
        self.remove(pulse)
        self.wait(0.65)

        self.play(
            FadeOut(top_ring), FadeOut(prob_lbl),
            policy_box.animate.set_fill(opacity=0.08).set_stroke(width=1.8),
            s_lbl.animate.shift(DOWN * 0.34),
            run_time=0.50,
        )
        self.wait(0.20)

    def _phase_value_detail(self, m):
        value_box = m["comp_boxes"][1][0]

        self.play(
            value_box.animate.set_fill(opacity=0.22).set_stroke(width=2.8),
            run_time=0.35,
        )

        # Bar directly below the board, pushed a bit lower
        BAR_W     = 2.6
        WIN_PROB  = 0.73
        board_bot = self.BC[1] - (self.SIDE + 0.35) / 2
        bar_cy    = board_bot - 0.62        # lower than before
        bar_bg_cx = self.BC[0]

        bar_bg = RoundedRectangle(width=BAR_W, height=0.38, corner_radius=0.08)
        bar_bg.set_fill(GRAY_E, opacity=0.28).set_stroke(color=GRAY_D, width=1.0)
        bar_bg.move_to(np.array([bar_bg_cx, bar_cy, 0.0]))

        b_lbl = Tex("Black", font_size=13, color=GRAY_C)
        b_lbl.next_to(bar_bg, LEFT, buff=0.24)    # pushed further away
        w_lbl = Tex("White", font_size=13, color=GRAY_C)
        w_lbl.next_to(bar_bg, RIGHT, buff=0.24)   # pushed further away
        pct = MathTex(r"73\%", font_size=18, color=self.C_VALUE)
        pct.next_to(bar_bg, UP, buff=0.09)

        # ValueTracker — strict left-to-right fill, no diagonal artefacts
        progress = ValueTracker(0.0)

        def make_fill():
            w    = max(BAR_W * WIN_PROB * progress.get_value(), 0.001)
            fill = Rectangle(width=w, height=0.38)
            fill.set_fill(self.C_VALUE, opacity=0.85).set_stroke(width=0)
            fill.align_to(bar_bg, LEFT)
            fill.set_y(bar_cy)
            return fill

        bar_fill = always_redraw(make_fill)

        self.play(FadeIn(bar_bg), FadeIn(b_lbl), FadeIn(w_lbl), run_time=0.40)
        self.add(bar_fill)
        self.play(progress.animate.set_value(1.0), run_time=0.90, rate_func=ease_out_quad)
        self.play(FadeIn(pct, shift=DOWN * 0.04), run_time=0.35)
        self.wait(0.80)

        bar_fill.clear_updaters()
        self.play(
            FadeOut(VGroup(bar_bg, bar_fill, b_lbl, w_lbl, pct)),
            value_box.animate.set_fill(opacity=0.08).set_stroke(width=1.8),
            run_time=0.55,
        )
        self.wait(0.15)

    def _phase_mcts_tree(self, m):
        # Fade board + the first two boxes/arrows; leave the MCTS box on screen
        fade_partial = VGroup(
            m["bg"], m["lines"], m["stones"], m["s_lbl"],
            m["comp_boxes"][0], m["comp_boxes"][1],
            m["comp_arrows"][0], m["comp_arrows"][1],  # NOT the MCTS arrow
            m["comp_labels"][0], m["comp_labels"][1],
        )
        self.play(FadeOut(fade_partial), run_time=0.75)

        mcts_box = m["comp_boxes"][2][0]
        mcts_div = m["comp_boxes"][2][1]
        mcts_f   = m["comp_labels"][2][0]   # "MCTS" label
        mcts_sub = m["comp_labels"][2][1]   # "tree search"
        mcts_arr = m["comp_arrows"][2]

        # Fade the MCTS arrow and subtitle, then undraw the box border
        self.play(FadeOut(mcts_arr), FadeOut(mcts_sub), run_time=0.30)
        self.play(Uncreate(mcts_box), Uncreate(mcts_div), run_time=0.60)

        # Fly MCTS label to top-centre, hide logo at the same time
        title_target = mcts_f.copy()
        title_target.to_edge(UP, buff=0.42)
        title_target.set_x(0)   # horizontally centred

        self.play(
            Transform(mcts_f, title_target),
            FadeOut(m["logo"]),
            run_time=0.55,
        )
        title = mcts_f

        # ── Tree geometry ─────────────────────────────────────────────────────
        ROOT_P = np.array([ 0.0,  2.10, 0.0])
        L1_POS = [
            np.array([-3.6,  0.50, 0.0]),
            np.array([ 0.0,  0.50, 0.0]),
            np.array([ 3.3,  0.50, 0.0]),
        ]
        L2_POS = [
            np.array([-4.7, -0.95, 0.0]),
            np.array([-2.5, -0.95, 0.0]),
        ]
        L1_POLICY = [0.55, 0.28, 0.17]

        # Root node
        root_nd = self._tree_node(ROOT_P, self.C_SEARCH, radius=0.33, fill_opacity=0.22)
        root_lb = MathTex("s", font_size=20, color=GRAY_B).move_to(ROOT_P)
        self.play(GrowFromCenter(root_nd), Write(root_lb), run_time=0.42)

        # L1: edge thickness + node size encode policy probability
        l1_nodes = []
        l1_edges = []
        l1_plbls = []

        for i, (pos, policy) in enumerate(zip(L1_POS, L1_POLICY)):
            r    = 0.20 + policy * 0.36
            ew   = 0.9  + policy * 4.2
            node = self._tree_node(pos, self.C_POLICY, radius=r,
                                   fill_opacity=0.12 + policy * 0.22)
            edge = self._tree_edge(ROOT_P, pos, color=self.C_SEARCH,
                                   width=ew, clip=max(r, 0.33))
            mid  = (ROOT_P + pos) / 2
            side = LEFT * 0.30 if i == 0 else RIGHT * 0.28
            plbl = MathTex(f"p={policy:.2f}", font_size=12, color=self.C_POLICY)
            plbl.move_to(mid + side + UP * 0.07)
            l1_nodes.append(node)
            l1_edges.append(edge)
            l1_plbls.append(plbl)

        self.play(
            LaggedStart(
                *[AnimationGroup(Create(e), GrowFromCenter(n), FadeIn(pl))
                  for e, n, pl in zip(l1_edges, l1_nodes, l1_plbls)],
                lag_ratio=0.22,
            ),
            run_time=1.2,
        )
        self.wait(0.18)

        # ── Monte Carlo simulations ───────────────────────────────────────────
        n_visits = [0, 0, 0]
        q_vals   = [0.0, 0.0, 0.0]
        n_labels = [None, None, None]
        l2_nodes_created = []
        l2_edges_created = []

        def rollout_path(start, seed):
            rng  = np.random.default_rng(seed)
            segs = VGroup()
            pos  = start.copy()
            for _ in range(5):
                dx  = rng.uniform(-0.55, 0.55)
                dy  = -rng.uniform(0.26, 0.44)
                end = pos + np.array([dx, dy, 0.0])
                end[1] = max(end[1], -3.4)
                seg = DashedLine(pos, end, color=GRAY_C, stroke_width=1.2,
                                 dash_length=0.09, stroke_opacity=0.55)
                segs.add(seg)
                pos = end
            return segs, pos

        def run_sim(l1_idx, result, l2_expand=None, seed=0):
            flash = l1_edges[l1_idx].copy()
            flash.set_stroke(color=self.C_MOVE, width=6.0, opacity=1.0)
            self.play(Create(flash), run_time=0.15)

            l2_nd = l2_ed = None
            if l2_expand is not None:
                pos   = L2_POS[l2_expand]
                l2_nd = self._tree_node(pos, self.C_VALUE, radius=0.18, fill_opacity=0.15)
                l2_ed = self._tree_edge(L1_POS[l1_idx], pos,
                                        color=self.C_SEARCH, width=1.0, clip=0.18)
                self.play(Create(l2_ed), GrowFromCenter(l2_nd), run_time=0.20)
                rollout_start = pos
            else:
                rollout_start = L1_POS[l1_idx]

            segs, end_pos = rollout_path(rollout_start, seed)
            self.play(
                LaggedStart(*[Create(s) for s in segs], lag_ratio=0.07),
                run_time=0.30,
            )

            col     = self.C_VALUE if result > 0 else "#FF6B6B"
            res_tex = MathTex(f"{result:+.1f}", font_size=19, color=col)
            res_tex.move_to(end_pos + DOWN * 0.04)
            self.play(GrowFromCenter(res_tex), run_time=0.16)
            self.wait(0.10)

            backup = res_tex.copy()
            self.play(
                backup.animate.move_to(L1_POS[l1_idx]).set_opacity(0),
                FadeOut(segs),
                run_time=0.30,
                rate_func=ease_out_quad,
            )
            self.remove(backup)
            self.play(FadeOut(flash), FadeOut(res_tex), run_time=0.10)

            n_visits[l1_idx] += 1
            q_vals[l1_idx] = (
                q_vals[l1_idx] * (n_visits[l1_idx] - 1) + result
            ) / n_visits[l1_idx]

            if n_labels[l1_idx] is not None:
                self.remove(n_labels[l1_idx])
            nlbl = Tex(f"N={n_visits[l1_idx]}", font_size=11, color=WHITE)
            nlbl.move_to(L1_POS[l1_idx])
            self.add(nlbl)
            n_labels[l1_idx] = nlbl

            return l2_nd, l2_ed

        nd, ed = run_sim(0, +1.0, seed=1)
        nd, ed = run_sim(1, -0.4, seed=2)
        nd, ed = run_sim(0, +0.8, l2_expand=0, seed=3)
        l2_nodes_created.append(nd); l2_edges_created.append(ed)
        nd, ed = run_sim(0, +0.3, l2_expand=1, seed=4)
        l2_nodes_created.append(nd); l2_edges_created.append(ed)
        nd, ed = run_sim(1, +0.2, seed=5)

        self.wait(0.25)

        best_edge = l1_edges[0].copy().set_stroke(color=self.C_MOVE, width=5.5)
        best_star = Star(n=5, outer_radius=0.22, color=self.C_MOVE, fill_opacity=0.92)
        best_star.set_stroke(width=0).move_to(L1_POS[0])
        self.play(Create(best_edge), GrowFromCenter(best_star), run_time=0.50)
        self.wait(1.0)

        m["mcts_tree_all"] = VGroup(
            root_nd, root_lb,
            *l1_nodes, *l1_edges, *l1_plbls,
            *[lb for lb in n_labels if lb is not None],
            *[n for n in l2_nodes_created if n is not None],
            *[e for e in l2_edges_created if e is not None],
            best_edge, best_star,
        )
        m["mcts_title"] = title

    def _phase_formula(self, m):
        self.play(
            FadeOut(m["mcts_tree_all"]),
            FadeOut(m["mcts_title"]),
            run_time=0.72,
        )

        # Inline underbraces: each term's label is anchored naturally under it,
        # separated by the standalone + so they never overlap.
        # Extra \; before c · pushes the exploration term away from the +.
        ucb = MathTex(
            r"\underbrace{Q(s,a)}_{\scriptstyle\text{value so far}}",
            r"+",
            r"\;\; c \cdot"
            r"\underbrace{\dfrac{P(s,a)\,\sqrt{N(s)}}{1 + N(s,a)}}"
            r"_{\scriptstyle\text{exploration bonus}}",
            font_size=40,
        )
        ucb[0].set_color(self.C_VALUE)
        ucb[2].set_color(self.C_POLICY)
        ucb.move_to(ORIGIN + UP * 0.3)

        caption = Tex(
            r"balance moves that look good $\cdot$ with moves not yet explored",
            font_size=20, color=GRAY_C,
        )
        caption.next_to(ucb, DOWN, buff=0.75)

        self.play(Write(ucb[0]), run_time=0.80)
        self.play(Write(ucb[1]), run_time=0.25)
        # exploration term: slower, smooth fade-in rather than stroke-by-stroke
        self.play(FadeIn(ucb[2], shift=RIGHT * 0.12), run_time=1.40)
        self.play(FadeIn(caption, shift=UP * 0.08), run_time=0.55)
        self.wait(2.5)
