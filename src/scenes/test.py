from manim import *

class AlphaGoLogo(Scene):
    def construct(self):
        logo = SVGMobject("src/scenes/alphago.svg")
        logo.set(width=6)

        # Preserve SVG fills, only ensure they are visible
        for part in logo.family_members_with_points():
            part.set_fill(opacity=1)

        self.play(DrawBorderThenFill(logo), run_time=3)
        self.wait()
