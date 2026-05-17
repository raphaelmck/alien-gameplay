from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class SelfPlayScene(Scene):
    """Scene 8 – Self-play as data generation.

    Layout: board (left) | network (right) | data strip (bottom).
    The scene runs like a factory: game → search targets → z labels → network update.
    """

    BG        = "#000000"
    BOARD_COL = "#131210"
    GRID_COL  = "#4A4438"
    BLACK_COL = "#1A1A1A"
    WHITE_COL = "#F0F0F0"
    C_NET     = "#A78BFA"   # purple  — network / θ
    C_SEARCH  = "#F0A500"   # orange  — search / policy
    C_VALUE   = "#50C878"   # green   — outcome / z
    C_DATA    = "#5B9BD5"   # blue    — neutral data

    N       = 5
    SIDE    = 2.05
    STONE_R = 0.135
    BC      = np.array([-3.3,  0.40, 0.0])   # board centre
    NC      = np.array([ 3.3,  0.40, 0.0])   # network centre
    CARD_Y  = -2.80                           # y of the data strip
    # Three card x-positions (spacing 2.4; gap stays ≥ 0.35 even after green transform)
    CARD_XS = [-3.9, -1.5, 0.9]

    def construct(self):
        self.camera.background_color = self.BG
        self.SP      = self.SIDE / (self.N - 1)
        self._stones = VGroup()

        self._build_layout()
        self._phase_self_play()
        self._phase_search_targets()
        self._phase_result_labels()
        self._phase_network_update()
        self._phase_accelerated_loop()
        self._phase_comparison()

    # ── coordinate helpers ────────────────────────────────────────────────────

    def gp(self, i, j):
        return np.array([
            self.BC[0] - self.SIDE / 2 + i * self.SP,
            self.BC[1] - self.SIDE / 2 + j * self.SP,
            0.0,
        ])

    def _stone(self, i, j, col):
        c = Circle(radius=self.STONE_R)
        c.set_fill(col, opacity=1)
        c.set_stroke(
            color="#C0C0C0" if col == self.WHITE_COL else "#383838",
            width=0.8,
        )
        c.move_to(self.gp(i, j))
        return c

    def _net_dot(self, pos, opacity=0.78):
        d = Dot(pos, radius=0.11, color=self.C_NET)
        d.set_fill(self.C_NET, opacity=opacity)
        d.set_stroke(color=self.C_NET, width=1.0)
        return d

    def _data_card(self, tex_str, col=None, w=1.75, h=0.52):
        col = col or self.C_DATA
        box = RoundedRectangle(
            width=w, height=h, corner_radius=0.10,
            fill_color=col, fill_opacity=0.13,
            stroke_color=col, stroke_width=1.6,
        )
        lbl = MathTex(tex_str, font_size=17, color=col)
        lbl.move_to(box.get_center())
        return VGroup(box, lbl)

    # ── static layout ─────────────────────────────────────────────────────────

    def _build_layout(self):
        board_sq = Square(side_length=self.SIDE + 0.26)
        board_sq.set_fill(self.BOARD_COL, opacity=1).set_stroke(width=0)
        board_sq.move_to(self.BC)

        s2   = self.SIDE / 2
        grid = VGroup()
        for k in range(self.N):
            t = -s2 + k * self.SP
            grid.add(Line(
                [self.BC[0] + t, self.BC[1] - s2, 0],
                [self.BC[0] + t, self.BC[1] + s2, 0],
                color=self.GRID_COL, stroke_width=1.2,
            ))
            grid.add(Line(
                [self.BC[0] - s2, self.BC[1] + t, 0],
                [self.BC[0] + s2, self.BC[1] + t, 0],
                color=self.GRID_COL, stroke_width=1.2,
            ))

        # Neural network  (3 → 3 → 1 layout)
        lx = [self.NC[0] - 0.78, self.NC[0], self.NC[0] + 0.78]
        ly = [[0.52, 0.0, -0.52], [0.28, -0.28], [0.0]]

        net_layers = []
        all_dots   = VGroup()
        for x, ys in zip(lx, ly):
            layer = [self._net_dot(np.array([x, self.NC[1] + y, 0.0])) for y in ys]
            net_layers.append(layer)
            all_dots.add(*layer)

        edges = VGroup()
        for a, b in zip(net_layers[:-1], net_layers[1:]):
            for na in a:
                for nb in b:
                    edges.add(Line(
                        na.get_center(), nb.get_center(),
                        color=self.C_NET, stroke_width=0.75, stroke_opacity=0.35,
                    ))

        glow_box = RoundedRectangle(
            width=2.1, height=2.3, corner_radius=0.22,
            fill_color=self.C_NET, fill_opacity=0.06,
            stroke_color=self.C_NET, stroke_width=1.8, stroke_opacity=0.65,
        )
        glow_box.move_to(self.NC)

        theta_lbl = MathTex(r"\theta_0", font_size=38, color=self.C_NET)
        theta_lbl.next_to(glow_box, UP, buff=0.20)

        self.play(GrowFromCenter(board_sq), GrowFromCenter(glow_box), run_time=0.55)
        self.play(
            LaggedStart(*[Create(l) for l in grid], lag_ratio=0.02),
            Create(edges),
            LaggedStart(*[GrowFromCenter(d) for d in all_dots], lag_ratio=0.07),
            Write(theta_lbl),
            run_time=0.9,
        )

        self._board_sq   = board_sq
        self._grid       = grid
        self._glow_box   = glow_box
        self._net_edges  = edges
        self._net_dots   = all_dots
        self._net_layers = net_layers
        self._theta_lbl  = theta_lbl

    # ── phase 1: network plays both sides ─────────────────────────────────────

    def _phase_self_play(self):
        banner = Tex(
            r"network $\theta$ plays \textbf{both sides}",
            font_size=28, color=self.C_NET,
        )
        banner.to_edge(UP, buff=0.38)
        self.play(FadeIn(banner, shift=DOWN * 0.08), run_time=0.42)
        self.wait(0.18)

        move_seq = [
            (2, 2, self.BLACK_COL), (2, 3, self.WHITE_COL),
            (1, 2, self.BLACK_COL), (3, 2, self.WHITE_COL),
            (2, 1, self.BLACK_COL), (3, 3, self.WHITE_COL),
            (1, 3, self.BLACK_COL), (3, 1, self.WHITE_COL),
            (0, 2, self.BLACK_COL), (4, 2, self.WHITE_COL),
        ]
        for i, j, col in move_seq:
            s     = self._stone(i, j, col)
            pulse = Circle(
                radius=self.STONE_R * 1.55, fill_opacity=0,
                stroke_color=self.C_NET, stroke_width=1.8,
            )
            pulse.move_to(self.gp(i, j))
            self.add(pulse)
            self.play(
                GrowFromCenter(s),
                pulse.animate.scale(3.4).set_opacity(0),
                run_time=0.20, rate_func=ease_out_quad,
            )
            self.remove(pulse)
            self._stones.add(s)

        self.wait(0.30)
        self.play(FadeOut(banner), run_time=0.28)

    # ── phase 2: search produces policy targets ────────────────────────────────

    def _phase_search_targets(self):
        banner = Tex(
            r"search $\;\to\;$ target policy $\pi_t$",
            font_size=28, color=self.C_SEARCH,
        )
        banner.to_edge(UP, buff=0.38)
        self.play(FadeIn(banner, shift=DOWN * 0.08), run_time=0.38)

        empty = [
            (0, 0), (1, 0), (0, 1), (4, 0), (4, 1),
            (0, 3), (0, 4), (4, 3), (4, 4), (1, 4), (3, 4),
        ]
        self._saved_cards = []

        for pos_i, cx in enumerate(self.CARD_XS):
            rng    = np.random.default_rng(pos_i * 11 + 5)
            chosen = rng.choice(len(empty), size=5, replace=False)

            heat = VGroup()
            for rank, cell_idx in enumerate(chosen):
                ci, cj = empty[cell_idx]
                alpha  = 0.85 - rank * 0.13
                r      = self.STONE_R * (0.38 + 0.42 * alpha)
                dot    = Circle(radius=r)
                dot.set_fill(self.C_SEARCH, opacity=alpha)
                dot.set_stroke(width=0)
                dot.move_to(self.gp(ci, cj))
                heat.add(dot)

            visit = Tex(r"visits: 12", font_size=16, color=self.C_SEARCH)
            visit.next_to(heat[0], UP, buff=0.06)

            self.play(
                LaggedStart(*[GrowFromCenter(d) for d in heat], lag_ratio=0.06),
                run_time=0.32,
            )
            self.play(FadeIn(visit), run_time=0.16)

            for count in [r"visits: 41", r"visits: 108"]:
                new_v = Tex(count, font_size=16, color=self.C_SEARCH)
                new_v.move_to(visit.get_center())
                self.play(Transform(visit, new_v), run_time=0.16)

            card = self._data_card(
                rf"s_{{{pos_i+1}}},\;\pi_{{{pos_i+1}}}",
                col=self.C_DATA,
            )
            card.move_to(self._board_sq.get_center())
            self.play(
                FadeOut(heat), FadeOut(visit), GrowFromCenter(card),
                run_time=0.26,
            )
            self.play(
                card.animate.move_to(np.array([cx, self.CARD_Y, 0.0])),
                run_time=0.38, rate_func=ease_out_quad,
            )
            self._saved_cards.append(card)

        self.play(FadeOut(banner), run_time=0.26)

    # ── phase 3: game ends; z flows backward into each card ───────────────────

    def _phase_result_labels(self):
        end_banner = Tex("Game over", font_size=28, color=GRAY_C)
        end_banner.to_edge(UP, buff=0.38)
        self.play(FadeIn(end_banner, shift=DOWN * 0.08), run_time=0.32)

        # Opaque backdrop so the result is readable over the stones
        result_bg = Rectangle(
            width=3.2, height=0.88,
            fill_color="#0B1A10", fill_opacity=0.96,
            stroke_width=0,
        )
        result_bg.move_to(self._board_sq.get_center())
        result_box = RoundedRectangle(
            width=3.2, height=0.88, corner_radius=0.14,
            fill_opacity=0,
            stroke_color=self.C_VALUE, stroke_width=2.6,
        )
        result_box.move_to(result_bg.get_center())
        result_tex = MathTex(
            r"\text{Black wins} \quad z = +1",
            font_size=30, color=self.C_VALUE,
        )
        result_tex.move_to(result_bg.get_center())

        self.play(
            FadeIn(result_bg),
            GrowFromCenter(result_box),
            run_time=0.5,
        )
        self.play(Write(result_tex), run_time=0.5)
        self.wait(0.42)

        for idx, card in enumerate(self._saved_cards):
            z_dot = Dot(result_bg.get_center(), radius=0.11, color=self.C_VALUE)
            z_dot.set_fill(self.C_VALUE, opacity=0.9)
            self.add(z_dot)
            self.play(
                z_dot.animate.move_to(card.get_center()).scale(0.45).set_opacity(0),
                run_time=0.30, rate_func=smooth,
            )
            self.remove(z_dot)

            new_card = self._data_card(
                rf"s_{{{idx+1}}},\;\pi_{{{idx+1}}},\;+1",
                col=self.C_VALUE, w=2.05,
            )
            new_card.move_to(card.get_center())
            self.play(Transform(card, new_card), run_time=0.35)

        self.wait(0.38)
        self.play(
            FadeOut(VGroup(result_bg, result_box, result_tex, end_banner)),
            run_time=0.35,
        )

    # ── phase 4: cards stream into network; θ₀ → θ₁ ─────────────────────────

    def _phase_network_update(self):
        banner = Tex(
            r"$\pi_\theta \to \pi_t \qquad V_\theta \to z$",
            font_size=28, color=GRAY_C,
        )
        banner.to_edge(UP, buff=0.38)
        self.play(FadeIn(banner, shift=DOWN * 0.08), run_time=0.35)

        for card in self._saved_cards:
            ghost = card.copy()
            self.add(ghost)
            self.play(
                FadeOut(card),
                ghost.animate.move_to(self.NC).scale(0.25),
                self._glow_box.animate.set_fill(opacity=0.22),
                run_time=0.36, rate_func=smooth,
            )
            self.play(
                FadeOut(ghost),
                self._glow_box.animate.set_fill(opacity=0.08),
                run_time=0.18,
            )

        self.play(
            *[d.animate.set_fill(self.C_NET, opacity=1.0) for d in self._net_dots],
            self._net_edges.animate.set_stroke(opacity=0.82),
            self._glow_box.animate.set_fill(opacity=0.26).set_stroke(width=2.8),
            run_time=0.38,
        )
        self.play(
            *[d.animate.set_fill(self.C_NET, opacity=0.80) for d in self._net_dots],
            self._net_edges.animate.set_stroke(opacity=0.42),
            self._glow_box.animate.set_fill(opacity=0.11),
            run_time=0.32,
        )

        new_lbl = MathTex(r"\theta_1", font_size=38, color=self.C_NET)
        new_lbl.move_to(self._theta_lbl.get_center())
        self.play(Transform(self._theta_lbl, new_lbl), run_time=0.42)
        self.wait(0.28)
        self.play(FadeOut(banner), run_time=0.25)

    # ── phase 5: accelerated loop — θ₁ → θ₆ (5 cycles) ──────────────────────

    def _phase_accelerated_loop(self):
        # Five distinct move sequences; each cycle runs faster than the last
        loop_moves = [
            # θ₁ → θ₂
            [(2, 2, self.BLACK_COL), (1, 3, self.WHITE_COL),
             (3, 1, self.BLACK_COL), (2, 4, self.WHITE_COL),
             (0, 2, self.BLACK_COL), (4, 2, self.WHITE_COL)],
            # θ₂ → θ₃
            [(2, 2, self.BLACK_COL), (3, 3, self.WHITE_COL),
             (1, 1, self.BLACK_COL), (4, 0, self.WHITE_COL),
             (2, 4, self.BLACK_COL)],
            # θ₃ → θ₄
            [(1, 2, self.BLACK_COL), (3, 2, self.WHITE_COL),
             (2, 1, self.BLACK_COL), (2, 3, self.WHITE_COL),
             (0, 4, self.BLACK_COL)],
            # θ₄ → θ₅  (very fast)
            [(2, 2, self.BLACK_COL), (2, 3, self.WHITE_COL),
             (3, 3, self.BLACK_COL), (1, 1, self.WHITE_COL)],
            # θ₅ → θ₆  (ultra-fast)
            [(2, 2, self.BLACK_COL), (1, 1, self.WHITE_COL),
             (3, 3, self.BLACK_COL)],
        ]
        # Move run-times: 0.12, 0.10, 0.08, 0.06, 0.05 s
        move_rts = [0.12, 0.10, 0.08, 0.06, 0.05]

        for cycle, (moves, move_rt) in enumerate(zip(loop_moves, move_rts)):
            theta_next = cycle + 2

            # Board clears
            self.play(FadeOut(self._stones), run_time=0.20)
            self._stones = VGroup()

            # Play moves with shrinking pulse rings
            pulse_scale = max(2.0, 2.8 - cycle * 0.2)
            for i, j, col in moves:
                s     = self._stone(i, j, col)
                pulse = Circle(
                    radius=self.STONE_R * 1.3, fill_opacity=0,
                    stroke_color=self.C_NET, stroke_width=1.5,
                )
                pulse.move_to(self.gp(i, j))
                self.add(pulse)
                self.play(
                    GrowFromCenter(s),
                    pulse.animate.scale(pulse_scale).set_opacity(0),
                    run_time=move_rt, rate_func=ease_out_quad,
                )
                self.remove(pulse)
                self._stones.add(s)

            # Flash data cards — same positions across all cycles
            flash_cards = VGroup()
            for k, cx in enumerate(self.CARD_XS):
                c = self._data_card(
                    rf"(s_{{{k+1}}},\;\pi_{{{k+1}}},\;+1)",
                    col=self.C_VALUE, w=1.98,
                )
                c.move_to(np.array([cx, self.CARD_Y, 0.0]))
                flash_cards.add(c)

            appear_rt = max(0.18, 0.38 - cycle * 0.04)
            self.play(
                LaggedStart(*[GrowFromCenter(c) for c in flash_cards], lag_ratio=0.10),
                run_time=appear_rt,
            )

            # Stream all cards into network
            fill_op  = min(0.38, 0.20 + 0.04 * (cycle + 1))
            stroke_w = min(3.4, 2.6 + 0.2 * (cycle + 1))
            stream_rt = max(0.26, 0.40 - cycle * 0.03)
            self.play(
                flash_cards.animate.move_to(self.NC).scale(0.20),
                self._glow_box.animate.set_fill(opacity=fill_op).set_stroke(width=stroke_w),
                *[d.animate.set_fill(self.C_NET, opacity=1.0) for d in self._net_dots],
                run_time=stream_rt, rate_func=ease_out_quad,
            )
            node_op = min(0.98, 0.80 + 0.04 * (cycle + 1))
            settle_fill = min(0.32, 0.11 + 0.04 * (cycle + 1))
            self.play(
                FadeOut(flash_cards),
                *[d.animate.set_fill(self.C_NET, opacity=node_op) for d in self._net_dots],
                self._glow_box.animate.set_fill(opacity=settle_fill),
                run_time=0.24,
            )

            new_lbl = MathTex(rf"\theta_{theta_next}", font_size=38, color=self.C_NET)
            new_lbl.move_to(self._theta_lbl.get_center())
            self.play(Transform(self._theta_lbl, new_lbl), run_time=0.32)
            self.wait(0.10)

    # ── phase 6: data-scale comparison + closing ──────────────────────────────

    def _phase_comparison(self):
        # Fade out the game board and stones; keep network glowing on the right
        scene_elements = VGroup(
            self._board_sq, self._grid, self._stones,
        )
        self.play(FadeOut(scene_elements), run_time=0.55)

        # Brief final network pulse before the comparison
        outer_ring = Circle(
            radius=1.4, fill_opacity=0,
            stroke_color=self.C_NET, stroke_width=6.0,
        )
        outer_ring.move_to(self.NC)
        self.add(outer_ring)
        self.play(
            outer_ring.animate.scale(2.4).set_opacity(0),
            self._glow_box.animate.set_fill(opacity=0.38).set_stroke(
                width=3.2, opacity=1.0
            ),
            run_time=0.70, rate_func=ease_out_quad,
        )
        self.remove(outer_ring)
        self.wait(0.20)

        # ── Two-column comparison ─────────────────────────────────────────────
        # Left column: human games (bounded)
        # Right column: self-play (unbounded, grows off-screen)
        # Both centred in the left half of the screen
        base_y = -1.60
        bar_w  = 1.25
        h_h    = 1.10   # fixed human bar height
        cx_h   = -2.20
        cx_sp  = 0.40

        # Human bar
        human_bar = Rectangle(width=bar_w, height=h_h)
        human_bar.set_fill(GRAY_C, opacity=0.65).set_stroke(color=GRAY_C, width=1.4)
        human_bar.move_to(np.array([cx_h, base_y + h_h / 2, 0.0]))

        human_title = Tex(r"Human games", font_size=24, color=GRAY_B)
        human_title.next_to(human_bar, DOWN, buff=0.16)
        human_count = Tex(r"$\sim$360K", font_size=24, color=GRAY_B)
        human_count.next_to(human_bar, UP, buff=0.12)
        human_sub = Tex(r"centuries of records", font_size=17, color=GRAY_D)
        human_sub.next_to(human_title, DOWN, buff=0.08)

        # Self-play bar (starts same height, then shoots off-screen)
        sp_bar = Rectangle(width=bar_w, height=h_h)
        sp_bar.set_fill(self.C_NET, opacity=0.65).set_stroke(color=self.C_NET, width=1.4)
        sp_bar.move_to(np.array([cx_sp, base_y + h_h / 2, 0.0]))

        sp_title = Tex(r"Self-play games", font_size=24, color=self.C_NET)
        sp_title.next_to(sp_bar, DOWN, buff=0.16)
        sp_title.set_x(cx_sp)

        v_div = DashedLine(
            np.array([(cx_h + cx_sp) / 2, base_y - 0.35, 0.0]),
            np.array([(cx_h + cx_sp) / 2, base_y + h_h + 0.6, 0.0]),
            color=GRAY_E, stroke_width=1.0, dash_length=0.14,
        )

        self.play(
            Create(v_div),
            GrowFromEdge(human_bar, DOWN),
            GrowFromEdge(sp_bar, DOWN),
            run_time=0.65,
        )
        self.play(
            FadeIn(human_title), FadeIn(sp_title),
            FadeIn(human_count, shift=UP * 0.06),
            run_time=0.42,
        )
        self.play(FadeIn(human_sub), run_time=0.30)
        self.wait(0.40)

        # Self-play bar erupts upward — frame is 8 units tall so 11 goes well off-screen
        sp_bar_big = Rectangle(width=bar_w, height=11.0)
        sp_bar_big.set_fill(self.C_NET, opacity=0.65).set_stroke(color=self.C_NET, width=1.4)
        sp_bar_big.align_to(sp_bar, DOWN)
        sp_bar_big.set_x(cx_sp)

        self.play(
            Transform(sp_bar, sp_bar_big),
            run_time=0.90, rate_func=ease_out_quad,
        )

        # ∞ symbol at top of the erupting bar (within frame)
        inf_sym = MathTex(r"\infty", font_size=62, color=self.C_NET)
        inf_sym.move_to(np.array([cx_sp, 2.55, 0.0]))
        sp_count = Tex(r"billions per run", font_size=20, color=self.C_NET)
        sp_count.next_to(inf_sym, DOWN, buff=0.14)

        self.play(FadeIn(inf_sym, scale=0.55), run_time=0.45)
        self.play(FadeIn(sp_count, shift=UP * 0.05), run_time=0.30)
        self.wait(0.50)

        # ── Closing line (appears below while comparison is still visible) ────
        closing = Tex(
            r"The machine builds its own curriculum.",
            font_size=32, color=WHITE,
        )
        closing.to_edge(DOWN, buff=0.55)
        self.play(FadeIn(closing, shift=UP * 0.12), run_time=0.9)
        self.wait(3.4)

        self.play(
            FadeOut(VGroup(
                v_div, human_bar, human_title, human_count, human_sub,
                sp_bar, sp_title, sp_count, inf_sym,
                self._glow_box, self._net_edges, self._net_dots, self._theta_lbl,
                closing,
            )),
            run_time=0.9,
        )
