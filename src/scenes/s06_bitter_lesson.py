from manim import *
from manim.utils.rate_functions import ease_out_quad
import numpy as np


class BitterLessonScene(Scene):
    BG = "#000000"
    C_HUMAN = "#F0A500"
    C_SCALE = "#A78BFA"
    C_PLATEAU = "#FF5555"
    C_AXIS = "#444444"

    def construct(self):
        self.camera.background_color = self.BG
        self._phase_knowledge_cards()
        self._phase_human_plateau()
        self._phase_scaling_begins()
        self._phase_overtake()
        self._phase_game_examples()
        self._phase_thesis()

    # ── helpers ───────────────────────────────────────────────────────────────

    def _make_card(self, lines, color=None):
        color = color or self.C_HUMAN
        bg = RoundedRectangle(
            width=2.4, height=0.72, corner_radius=0.1,
            fill_color="#100C00", fill_opacity=1.0,
            stroke_color=color, stroke_width=1.8,
        )
        label = VGroup(*[Text(l, font_size=13, color=color) for l in lines])
        label.arrange(DOWN, buff=0.05).move_to(bg)
        return VGroup(bg, label)

    def _make_go_board(self, n=4, spacing=0.22):
        total = spacing * (n - 1)
        bg = Square(
            side_length=total + spacing * 0.9,
            fill_color="#080812", fill_opacity=1.0,
            stroke_color=self.C_SCALE, stroke_width=1.2,
        )
        lines = VGroup()
        for i in range(n):
            x = -total / 2 + i * spacing
            y = total / 2 - i * spacing
            lines.add(
                Line(UP * total / 2 + RIGHT * x, DOWN * total / 2 + RIGHT * x,
                     stroke_color=self.C_SCALE, stroke_width=0.7, stroke_opacity=0.55),
                Line(LEFT * total / 2 + UP * y, RIGHT * total / 2 + UP * y,
                     stroke_color=self.C_SCALE, stroke_width=0.7, stroke_opacity=0.55),
            )
        return VGroup(bg, lines)

    def _make_chess_squares(self, n=4, sq=0.28):
        squares = VGroup()
        for r in range(n):
            for c in range(n):
                fill = "#2A1A08" if (r + c) % 2 == 0 else "#120A02"
                cell = Square(
                    side_length=sq,
                    fill_color=fill, fill_opacity=1.0,
                    stroke_color=self.C_HUMAN, stroke_width=0.5,
                )
                cell.move_to(RIGHT * c * sq + DOWN * r * sq)
                squares.add(cell)
        squares.move_to(ORIGIN)
        return squares

    def _make_compute_block(self, size=0.38):
        return Square(
            side_length=size,
            fill_color="#150A28", fill_opacity=1.0,
            stroke_color=self.C_SCALE, stroke_width=1.4,
        )

    # ── phases ────────────────────────────────────────────────────────────────

    def _phase_knowledge_cards(self):
        path_lbl = Text("Path 1: Human Knowledge", font_size=26, color=self.C_HUMAN)
        path_lbl.to_edge(UP, buff=0.45)
        self.play(FadeIn(path_lbl, shift=DOWN * 0.1), run_time=0.6)

        machine_box = RoundedRectangle(
            width=2.6, height=3.2, corner_radius=0.28,
            fill_color="#0D0900", fill_opacity=1.0,
            stroke_color=self.C_HUMAN, stroke_width=2.2,
        )
        machine_box.move_to(RIGHT * 3.2 + DOWN * 0.2)
        machine_lbl = Text("AI System", font_size=17, color=self.C_HUMAN)
        machine_lbl.next_to(machine_box, UP, buff=0.15)
        self.play(GrowFromCenter(machine_box), FadeIn(machine_lbl), run_time=0.55)

        card_defs = [
            ["pawn = 1 pt",  "rook = 5 pt"],
            ["king safety",  "open file +0.3"],
            ["fork patterns", "pin / skewer"],
            ["Go: corner first", "territory rules"],
        ]
        card_targets = [
            machine_box.get_center() + UP * 1.0,
            machine_box.get_center() + UP * 0.33,
            machine_box.get_center() + DOWN * 0.33,
            machine_box.get_center() + DOWN * 1.0,
        ]
        cards = [self._make_card(d) for d in card_defs]
        for i, (card, target) in enumerate(zip(cards, card_targets)):
            card.move_to(LEFT * 4.8 + UP * (1.2 - i * 0.85))
            self.play(
                card.animate.move_to(target).scale(0.78),
                run_time=0.45,
                rate_func=smooth,
            )
            self.wait(0.1)
        self.wait(0.3)

        # Performance meter
        meter_h = 2.8
        meter_bg = Rectangle(
            width=0.55, height=meter_h,
            fill_color="#111111", fill_opacity=1.0,
            stroke_color=GRAY_D, stroke_width=1.0,
        )
        meter_bg.move_to(LEFT * 0.8 + DOWN * 0.3)
        meter_lbl = Text("performance", font_size=14, color=GRAY_C)
        meter_lbl.next_to(meter_bg, DOWN, buff=0.14)

        fill_h = meter_h * 0.65
        meter_fill = Rectangle(
            width=0.51, height=0.05,
            fill_color=self.C_HUMAN, fill_opacity=0.9,
            stroke_width=0,
        )
        meter_fill.align_to(meter_bg, DOWN).shift(UP * 0.03)

        fill_target = Rectangle(
            width=0.51, height=fill_h,
            fill_color=self.C_HUMAN, fill_opacity=0.9,
            stroke_width=0,
        )
        fill_target.align_to(meter_bg, DOWN).shift(UP * 0.03)

        rising_lbl = Text("rising fast", font_size=15, color=self.C_HUMAN)
        rising_lbl.next_to(meter_bg, RIGHT, buff=0.3)

        self.play(FadeIn(meter_bg), FadeIn(meter_lbl), run_time=0.4)
        self.add(meter_fill)
        self.play(
            Transform(meter_fill, fill_target),
            FadeIn(rising_lbl, shift=LEFT * 0.1),
            run_time=1.3,
            rate_func=smooth,
        )
        self.wait(0.4)

        self._meter_bg = meter_bg
        self._meter_fill = meter_fill
        self._meter_h = meter_h
        self._human_path_grp = VGroup(
            path_lbl, machine_box, machine_lbl,
            *cards, meter_bg, meter_fill, meter_lbl, rising_lbl,
        )

    def _phase_human_plateau(self):
        meter_bg = self._meter_bg
        meter_fill = self._meter_fill
        meter_h = self._meter_h

        ceil_y = meter_bg.get_bottom()[1] + meter_h * 0.68 + 0.03
        ceil_x = meter_bg.get_center()[0]

        ceiling = DashedLine(
            np.array([ceil_x - 0.5, ceil_y, 0.0]),
            np.array([ceil_x + 1.6, ceil_y, 0.0]),
            color=self.C_PLATEAU, stroke_width=2.0,
            dash_length=0.14, stroke_opacity=0.8,
        )
        plat_lbl = Text("plateau", font_size=15, color=self.C_PLATEAU)
        plat_lbl.move_to(np.array([ceil_x + 1.2, ceil_y + 0.23, 0.0]))

        self.play(Create(ceiling), FadeIn(plat_lbl, shift=DOWN * 0.08), run_time=0.6)

        fill_strain = Rectangle(
            width=0.51, height=meter_h * 0.67,
            fill_color=self.C_HUMAN, fill_opacity=0.9,
            stroke_width=0,
        )
        fill_strain.align_to(meter_bg, DOWN).shift(UP * 0.03)

        self.play(Transform(meter_fill, fill_strain), run_time=0.7, rate_func=ease_out_quad)
        self.play(meter_fill.animate.shift(UP * 0.06), run_time=0.18, rate_func=there_and_back)
        self.wait(0.25)

        self.play(ceiling.animate.set_color(RED), run_time=0.2)
        self.play(ceiling.animate.set_color(self.C_PLATEAU), run_time=0.3)

        wall_text = Text("human concepts\nhit a ceiling", font_size=15, color=self.C_PLATEAU)
        wall_text.next_to(ceiling, RIGHT, buff=0.25).shift(DOWN * 0.1)
        self.play(FadeIn(wall_text, shift=LEFT * 0.1), run_time=0.5)
        self.wait(0.8)

        all_human = VGroup(self._human_path_grp, ceiling, plat_lbl, wall_text)
        self.play(all_human.animate.shift(LEFT * 3.8).set_opacity(0.12), run_time=1.0)
        self.wait(0.2)

    def _phase_scaling_begins(self):
        scale_lbl = Text("Path 2: Search + Learning + Compute", font_size=23, color=self.C_SCALE)
        scale_lbl.to_edge(UP, buff=0.45)
        self.play(FadeIn(scale_lbl, shift=DOWN * 0.1), run_time=0.6)

        center = RIGHT * 0.8 + DOWN * 0.5
        root = Dot(center, radius=0.14, color=self.C_SCALE, fill_opacity=0.25)
        root_lbl = Text("initial model", font_size=13, color=GRAY_D)
        root_lbl.next_to(root, DOWN, buff=0.14)
        self.play(GrowFromCenter(root), FadeIn(root_lbl), run_time=0.45)
        self.wait(0.25)

        l1_pos = [center + UP * 0.9 + d for d in [LEFT * 0.9, ORIGIN, RIGHT * 0.9]]
        l1_lines = VGroup(*[
            Line(center, p, stroke_color=self.C_SCALE, stroke_width=1.0, stroke_opacity=0.4)
            for p in l1_pos
        ])
        l1_dots = VGroup(*[
            Dot(p, radius=0.10, color=self.C_SCALE, fill_opacity=0.5)
            for p in l1_pos
        ])
        self.play(Create(l1_lines), run_time=0.4)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in l1_dots], lag_ratio=0.2), run_time=0.45)

        l2_pos = []
        for p in l1_pos:
            l2_pos += [p + UP * 0.7 + LEFT * 0.4, p + UP * 0.7 + RIGHT * 0.4]
        l2_lines = VGroup(*[
            Line(l1_pos[i // 2], p, stroke_color=self.C_SCALE, stroke_width=0.7, stroke_opacity=0.3)
            for i, p in enumerate(l2_pos)
        ])
        l2_dots = VGroup(*[
            Dot(p, radius=0.07, color=self.C_SCALE, fill_opacity=0.4)
            for p in l2_pos
        ])
        self.play(Create(l2_lines), run_time=0.35)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in l2_dots], lag_ratio=0.1), run_time=0.4)

        search_tag = Text("search", font_size=15, color=self.C_SCALE)
        search_tag.next_to(l2_dots, RIGHT, buff=0.3)
        self.play(FadeIn(search_tag, shift=LEFT * 0.1), run_time=0.3)
        self.wait(0.2)

        loop_c = RIGHT * 0.8 + DOWN * 2.1
        loop_arc = CurvedArrow(
            loop_c + LEFT * 0.85, loop_c + RIGHT * 0.85,
            color=self.C_SCALE, stroke_width=2.2,
            angle=-TAU / 3,
        )
        loop_tag = Text("self-play", font_size=14, color=self.C_SCALE)
        loop_tag.next_to(loop_arc, DOWN, buff=0.1)
        self.play(Create(loop_arc), FadeIn(loop_tag), run_time=0.6)
        self.wait(0.2)

        compute_anchor = RIGHT * 4.2 + DOWN * 1.2
        blocks = VGroup()
        for row in range(3):
            for col in range(4):
                b = self._make_compute_block()
                b.move_to(compute_anchor + RIGHT * col * 0.41 + DOWN * row * 0.41)
                blocks.add(b)
        compute_tag = Text("compute", font_size=14, color=self.C_SCALE)
        compute_tag.next_to(blocks, DOWN, buff=0.12)
        self.play(LaggedStart(*[GrowFromCenter(b) for b in blocks], lag_ratio=0.04), run_time=0.9)
        self.play(FadeIn(compute_tag), run_time=0.25)
        self.wait(0.3)

        s_meter_bg = Rectangle(
            width=0.52, height=2.8,
            fill_color="#111111", fill_opacity=1.0,
            stroke_color=GRAY_D, stroke_width=1.0,
        )
        s_meter_bg.move_to(LEFT * 2.0 + DOWN * 0.3)
        s_meter_fill = Rectangle(
            width=0.48, height=0.12,
            fill_color=self.C_SCALE, fill_opacity=0.85,
            stroke_width=0,
        )
        s_meter_fill.align_to(s_meter_bg, DOWN).shift(UP * 0.03)
        s_meter_lbl = Text("performance", font_size=13, color=GRAY_C)
        s_meter_lbl.next_to(s_meter_bg, DOWN, buff=0.13)
        slow_tag = Text("slow start", font_size=14, color=GRAY_C)
        slow_tag.next_to(s_meter_bg, LEFT, buff=0.3)

        self.play(FadeIn(s_meter_bg), FadeIn(s_meter_lbl), run_time=0.4)
        self.add(s_meter_fill)
        self.play(FadeIn(slow_tag), run_time=0.3)
        self.wait(0.5)

        self._scale_label = scale_lbl
        self._scale_tree = VGroup(root, root_lbl, l1_dots, l1_lines, l2_dots, l2_lines, search_tag)
        self._scale_loop = VGroup(loop_arc, loop_tag)
        self._scale_compute = VGroup(blocks, compute_tag)
        self._scale_meter = VGroup(s_meter_bg, s_meter_fill, s_meter_lbl, slow_tag)

    def _phase_overtake(self):
        all_detail = VGroup(
            self._scale_label, self._scale_tree,
            self._scale_loop, self._scale_compute, self._scale_meter,
        )
        self.play(FadeOut(all_detail), run_time=0.7)
        self.wait(0.1)

        orig = LEFT * 4.8 + DOWN * 2.6
        aw, ah = 9.0, 4.5

        def pt(t, y):
            return np.array([orig[0] + t * aw, orig[1] + y * ah, 0.0])

        def f_human(t):
            return 0.60 * (1.0 - np.exp(-8.5 * t))

        def f_scale(t):
            return 0.96 * (t ** 1.25)

        x_ax = Arrow(orig, orig + RIGHT * (aw + 0.4),
                     color=self.C_AXIS, stroke_width=2.0, buff=0,
                     max_tip_length_to_length_ratio=0.025)
        y_ax = Arrow(orig, orig + UP * (ah + 0.4),
                     color=self.C_AXIS, stroke_width=2.0, buff=0,
                     max_tip_length_to_length_ratio=0.03)
        x_lbl = Text("Computation / Time", font_size=15, color=GRAY_D)
        x_lbl.next_to(x_ax.get_right(), DOWN, buff=0.2)
        y_lbl = Text("Performance", font_size=15, color=GRAY_D)
        y_lbl.next_to(y_ax.get_top(), UP, buff=0.12)

        self.play(Create(x_ax), Create(y_ax), run_time=0.55)
        self.play(FadeIn(x_lbl), FadeIn(y_lbl), run_time=0.35)

        n = 300
        h_pts = [pt(i / (n - 1), f_human(i / (n - 1))) for i in range(n)]
        s_pts = [pt(i / (n - 1), f_scale(i / (n - 1))) for i in range(n)]

        h_curve = VMobject(color=self.C_HUMAN, stroke_width=3.5)
        h_curve.set_points_smoothly(h_pts)
        s_curve = VMobject(color=self.C_SCALE, stroke_width=3.5)
        s_curve.set_points_smoothly(s_pts)

        h_tag = Text("human knowledge", font_size=15, color=self.C_HUMAN)
        h_tag.move_to(pt(0.22, f_human(0.22)) + UP * 0.30 + RIGHT * 0.1)

        self.play(Create(h_curve), run_time=1.5, rate_func=smooth)
        self.play(FadeIn(h_tag, shift=DOWN * 0.1), run_time=0.4)

        plat_y = f_human(1.0)
        plat = DashedLine(
            pt(0.32, plat_y), pt(1.0, plat_y),
            color=self.C_PLATEAU, stroke_width=1.6,
            dash_length=0.12, stroke_opacity=0.65,
        )
        plat_lbl = Text("plateau", font_size=15, color=self.C_PLATEAU)
        plat_lbl.move_to(pt(0.65, plat_y) + UP * 0.23)
        self.play(Create(plat), FadeIn(plat_lbl), run_time=0.5)
        self.wait(0.4)

        s_tag = Text("search + learning + compute", font_size=15, color=self.C_SCALE)
        s_tag.move_to(pt(0.72, f_scale(0.72)) + RIGHT * 0.1 + DOWN * 0.35)

        self.play(Create(s_curve), run_time=2.2, rate_func=smooth)
        self.play(FadeIn(s_tag, shift=UP * 0.1), run_time=0.4)
        self.wait(0.3)

        # Overtake pulse
        cross_t = 0.71
        cross_point = pt(cross_t, f_human(cross_t))
        ring = Circle(radius=0.22, fill_opacity=0, stroke_color=WHITE, stroke_width=3.0)
        ring.move_to(cross_point)
        self.add(ring)
        self.play(ring.animate.scale(6).set_opacity(0), run_time=0.85, rate_func=ease_out_quad)
        self.remove(ring)

        s_glow = s_curve.copy().set_stroke(color=self.C_SCALE, width=18, opacity=0.22)
        self.play(FadeIn(s_glow), run_time=0.25)

        self.play(
            h_curve.animate.set_stroke(opacity=0.28),
            plat.animate.set_stroke(opacity=0.25),
            plat_lbl.animate.set_opacity(0.25),
            h_tag.animate.set_opacity(0.3),
            run_time=0.7,
        )

        brk_t = 0.91
        brk_point = pt(brk_t, f_scale(brk_t))
        brk_dot = Dot(brk_point, radius=0.10, color=self.C_SCALE)
        brk_lbl = Text("breakthrough", font_size=17, color=self.C_SCALE)
        brk_lbl.next_to(brk_point, UP, buff=0.2)
        self.play(GrowFromCenter(brk_dot), FadeIn(brk_lbl, shift=DOWN * 0.1), run_time=0.55)
        self.wait(2.0)

        self._chart = VGroup(
            x_ax, y_ax, x_lbl, y_lbl,
            h_curve, s_curve, s_glow,
            plat, plat_lbl, h_tag, s_tag,
            brk_dot, brk_lbl,
        )

    def _phase_game_examples(self):
        self.play(
            self._chart.animate.scale(0.47).to_edge(LEFT, buff=0.18).shift(DOWN * 0.2),
            run_time=0.9,
        )

        right_center = RIGHT * 2.8

        chess_title = Text("Chess", font_size=21, color=self.C_HUMAN)
        chess_board = self._make_chess_squares(4, 0.30)
        chess_l1 = Text("hand-crafted evaluation", font_size=13, color=self.C_HUMAN)
        chess_l2 = Text("→ early peak, then plateau", font_size=13, color=self.C_HUMAN)
        chess_block = VGroup(chess_title, chess_board, chess_l1, chess_l2)
        chess_block.arrange(DOWN, buff=0.18, center=True)
        chess_block.move_to(right_center + UP * 1.3)

        go_title = Text("Go  (AlphaZero)", font_size=21, color=self.C_SCALE)
        go_board = self._make_go_board(4, 0.24)
        go_board.scale(0.9)
        go_l1 = Text("search + self-play + compute", font_size=13, color=self.C_SCALE)
        go_l2 = Text("→ superhuman", font_size=13, color=self.C_SCALE)
        go_block = VGroup(go_title, go_board, go_l1, go_l2)
        go_block.arrange(DOWN, buff=0.18, center=True)
        go_block.move_to(right_center + DOWN * 1.3)

        sep = Line(UP * 0.28, DOWN * 0.28, color=GRAY_D, stroke_width=0.8)
        sep.move_to(right_center)

        self.play(
            LaggedStart(
                FadeIn(chess_block, shift=LEFT * 0.12),
                Create(sep),
                FadeIn(go_block, shift=LEFT * 0.12),
                lag_ratio=0.3,
            ),
            run_time=1.4,
        )
        self.wait(2.2)
        self.play(FadeOut(VGroup(chess_block, go_block, sep, self._chart)), run_time=0.9)
        self.wait(0.15)

    def _phase_thesis(self):
        line1 = Text("Methods that scale with computation", font_size=35, color=WHITE)
        line2 = Text("eventually dominate.", font_size=42, color=self.C_SCALE)
        block = VGroup(line1, line2).arrange(DOWN, buff=0.48).move_to(ORIGIN)

        self.play(FadeIn(line1, shift=UP * 0.15), run_time=0.9)
        self.wait(0.3)
        self.play(FadeIn(line2, shift=UP * 0.15), run_time=0.9)
        self.play(line2.animate.set_color(WHITE), run_time=0.3)
        self.play(line2.animate.set_color(self.C_SCALE), run_time=0.35)
        self.wait(3.2)
        self.play(FadeOut(block), run_time=1.0)
