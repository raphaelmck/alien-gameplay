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
        self._phase_closing()

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
        # Board
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

        # Appear together
        self.play(GrowFromCenter(board_sq), GrowFromCenter(glow_box), run_time=0.55)
        self.play(
            LaggedStart(*[Create(l) for l in grid], lag_ratio=0.02),
            Create(edges),
            LaggedStart(*[GrowFromCenter(d) for d in all_dots], lag_ratio=0.07),
            Write(theta_lbl),
            run_time=0.9,
        )

        self._board_sq    = board_sq
        self._grid        = grid
        self._glow_box    = glow_box
        self._net_edges   = edges
        self._net_dots    = all_dots
        self._net_layers  = net_layers
        self._theta_lbl   = theta_lbl

    # ── phase 1: network plays both sides ─────────────────────────────────────

    def _phase_self_play(self):
        banner = Tex(
            r"network $\theta$ plays \textbf{both sides}",
            font_size=22, color=self.C_NET,
        )
        banner.to_edge(UP, buff=0.38)
        self.play(FadeIn(banner, shift=DOWN * 0.08), run_time=0.42)
        self.wait(0.18)

        # Sequence of 10 moves — alternating black / white
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
            font_size=22, color=self.C_SEARCH,
        )
        banner.to_edge(UP, buff=0.38)
        self.play(FadeIn(banner, shift=DOWN * 0.08), run_time=0.38)

        # Cells that are empty after the move sequence
        empty = [
            (0, 0), (1, 0), (0, 1), (4, 0), (4, 1),
            (0, 3), (0, 4), (4, 3), (4, 4), (1, 4), (3, 4),
        ]

        # Three card positions in the data strip
        card_xs  = [-4.2, -2.2, -0.2]
        self._saved_cards = []

        for pos_i, cx in enumerate(card_xs):
            rng    = np.random.default_rng(pos_i * 11 + 5)
            chosen = rng.choice(len(empty), size=5, replace=False)

            # Heatmap: circles on empty intersections, varying size/opacity
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

            # Visit counter rising on the top-ranked candidate (heat[0])
            visit = MathTex("12", font_size=18, color=self.C_SEARCH)
            visit.next_to(heat[0], UP, buff=0.05)

            self.play(
                LaggedStart(*[GrowFromCenter(d) for d in heat], lag_ratio=0.06),
                run_time=0.32,
            )
            self.play(FadeIn(visit), run_time=0.16)

            for count in ["41", "108"]:
                new_v = MathTex(count, font_size=18, color=self.C_SEARCH)
                new_v.move_to(visit.get_center())
                self.play(Transform(visit, new_v), run_time=0.16)

            # Spawn a data card from the board, slide it to the strip
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
        end_banner = Tex("Game over", font_size=22, color=GRAY_C)
        end_banner.to_edge(UP, buff=0.38)
        self.play(FadeIn(end_banner, shift=DOWN * 0.08), run_time=0.32)

        result_box = RoundedRectangle(
            width=3.1, height=0.78, corner_radius=0.14,
            fill_color=self.C_VALUE, fill_opacity=0.14,
            stroke_color=self.C_VALUE, stroke_width=2.2,
        )
        result_box.move_to(self._board_sq.get_center())
        result_tex = MathTex(
            r"\text{Black wins} \quad z = +1",
            font_size=28, color=self.C_VALUE,
        )
        result_tex.move_to(result_box.get_center())

        self.play(GrowFromCenter(result_box), Write(result_tex), run_time=0.65)
        self.wait(0.42)

        # z signal travels from the result box into each saved card
        for idx, card in enumerate(self._saved_cards):
            z_dot = Dot(
                result_box.get_center(), radius=0.11,
                color=self.C_VALUE,
            )
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
        self.play(FadeOut(VGroup(result_box, result_tex, end_banner)), run_time=0.35)

    # ── phase 4: cards stream into network; θ₀ → θ₁ ─────────────────────────

    def _phase_network_update(self):
        banner = Tex(
            r"$\pi_\theta \to \pi_t \qquad V_\theta \to z$",
            font_size=22, color=GRAY_C,
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

        # Weight pulse
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

    # ── phase 5: accelerated loop — θ₁→θ₂→θ₃ ────────────────────────────────

    def _phase_accelerated_loop(self):
        loop_moves = [
            # cycle 0: θ₁ → θ₂
            [(2, 2, self.BLACK_COL), (1, 3, self.WHITE_COL),
             (3, 1, self.BLACK_COL), (2, 4, self.WHITE_COL),
             (0, 2, self.BLACK_COL), (4, 2, self.WHITE_COL)],
            # cycle 1: θ₂ → θ₃
            [(2, 2, self.BLACK_COL), (3, 3, self.WHITE_COL),
             (1, 1, self.BLACK_COL), (4, 0, self.WHITE_COL),
             (2, 4, self.BLACK_COL)],
        ]

        for cycle, moves in enumerate(loop_moves):
            theta_next = cycle + 2

            # Board clears
            self.play(FadeOut(self._stones), run_time=0.20)
            self._stones = VGroup()

            # Rapid moves — each cycle is quicker
            move_rt = 0.12 - cycle * 0.02
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
                    pulse.animate.scale(2.8).set_opacity(0),
                    run_time=move_rt, rate_func=ease_out_quad,
                )
                self.remove(pulse)
                self._stones.add(s)

            # Flash data cards in the strip
            flash_cards = VGroup()
            for k in range(3):
                c = self._data_card(
                    rf"(s_{{{k+1}}},\;\pi_{{{k+1}}},\;+1)",
                    col=self.C_VALUE, w=2.12,
                )
                c.move_to(np.array([-3.9 + k * 1.95, self.CARD_Y, 0.0]))
                flash_cards.add(c)

            self.play(
                LaggedStart(*[GrowFromCenter(c) for c in flash_cards], lag_ratio=0.10),
                run_time=0.38,
            )

            # Stream all cards into network
            fill_op  = 0.20 + 0.10 * (cycle + 1)
            stroke_w = 2.6 + 0.5 * (cycle + 1)
            self.play(
                flash_cards.animate.move_to(self.NC).scale(0.20),
                self._glow_box.animate.set_fill(opacity=fill_op).set_stroke(width=stroke_w),
                *[d.animate.set_fill(self.C_NET, opacity=1.0) for d in self._net_dots],
                run_time=0.40, rate_func=ease_out_quad,
            )
            self.play(
                FadeOut(flash_cards),
                *[d.animate.set_fill(self.C_NET, opacity=0.80 + 0.07 * (cycle + 1))
                  for d in self._net_dots],
                self._glow_box.animate.set_fill(opacity=0.12 + 0.06 * (cycle + 1)),
                run_time=0.26,
            )

            new_lbl = MathTex(rf"\theta_{theta_next}", font_size=38, color=self.C_NET)
            new_lbl.move_to(self._theta_lbl.get_center())
            self.play(Transform(self._theta_lbl, new_lbl), run_time=0.35)
            self.wait(0.12)

    # ── phase 6: closing ──────────────────────────────────────────────────────

    def _phase_closing(self):
        # Final network glow
        outer_ring = Circle(
            radius=1.4, fill_opacity=0,
            stroke_color=self.C_NET, stroke_width=6.0,
        )
        outer_ring.move_to(self.NC)
        self.add(outer_ring)
        self.play(
            outer_ring.animate.scale(2.5).set_opacity(0),
            self._glow_box.animate.set_fill(opacity=0.36).set_stroke(
                width=3.2, opacity=1.0
            ),
            run_time=0.85, rate_func=ease_out_quad,
        )
        self.remove(outer_ring)
        self.wait(0.28)

        closing = Tex(
            r"The machine builds its own curriculum.",
            font_size=34, color=WHITE,
        )
        closing.to_edge(DOWN, buff=0.55)
        self.play(FadeIn(closing, shift=UP * 0.12), run_time=0.9)
        self.wait(3.6)
        self.play(FadeOut(closing), run_time=0.8)
