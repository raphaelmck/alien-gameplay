from manim import *
from manim.utils.rate_functions import ease_in_out_sine, ease_out_quad
import numpy as np

class Move37ColdOpen(ThreeDScene):
    def construct(self):
        # Configuration and Constants
        self.BOARD_SIZE = 6.0
        self.SPACING = self.BOARD_SIZE / 18
        self.MOVE_37_COORD = (14, 9) # Configurable Move 37 location (O10)
        
        # Colors
        self.BOARD_COLOR = "#DCB35C"
        self.SUPPORT_COLOR = "#8B5A2B"
        self.GRID_COLOR = "#1A1A1A"
        self.BLACK_STONE = "#222222" # Dark grey for better 3D gloss than pure black
        self.WHITE_STONE = "#EEEEEE"
        
        # 1. Setup Scene
        self.set_camera_orientation(phi=65 * DEGREES, theta=45 * DEGREES)
        self.create_and_add_board_elements()
        
        # 2. Start Orbit & Place Stones
        self.begin_ambient_camera_rotation(rate=0.15)
        self.play_first_36_moves()
        self.stop_ambient_camera_rotation()
        
        # 3. Transition to Top-Down 2D
        self.transition_to_top_down()
        
        # 4. Show Heatmap & Reveal Move 37
        heatmap = self.create_heatmap()
        self.play(FadeIn(heatmap), run_time=3, rate_func=smooth)
        self.wait(1)
        
        self.play_move_37()
        self.play(FadeOut(heatmap), run_time=1)
        
        # 5. Labels and Final Zoom
        self.show_labels_and_zoom()


    # ==========================================
    # HELPER FUNCTIONS
    # ==========================================

    def board_to_point(self, i, j, z_offset=0.0):
        """Maps Go coordinates (0-18) to 3D Manim coordinates."""
        x = i * self.SPACING - self.BOARD_SIZE / 2
        y = j * self.SPACING - self.BOARD_SIZE / 2
        return np.array([x, y, z_offset])

    def create_and_add_board_elements(self):
        """Constructs the static board, support, grid, and star points."""
        self.board = self.create_board()
        self.support = self.create_support()
        self.grid = self.create_grid()
        self.star_points = self.create_star_points()
        
        # Add to scene
        self.add(self.support, self.board, self.grid, self.star_points)
        # Small intro fade
        self.play(
            FadeIn(self.board), FadeIn(self.support), 
            Create(self.grid), FadeIn(self.star_points),
            run_time=2
        )

    def create_board(self):
        """Creates the main wooden board plane."""
        # Cube is centered at origin. Scale it to form a flat board.
        board = Cube(fill_color=self.BOARD_COLOR, fill_opacity=1, stroke_width=0)
        board.scale(np.array([self.BOARD_SIZE + 0.4, self.BOARD_SIZE + 0.4, 0.3]))
        # Shift so the top surface is exactly at Z=0
        board.shift(DOWN * 0.15)
        return board

    def create_support(self):
        """Creates the darker cuboid support underneath."""
        support = Cube(fill_color=self.SUPPORT_COLOR, fill_opacity=1, stroke_width=0)
        support.scale(np.array([self.BOARD_SIZE - 0.5, self.BOARD_SIZE - 0.5, 0.8]))
        # Shift down to sit exactly below the board
        support.shift(DOWN * 0.7)
        return support

    def create_grid(self):
        """Creates the 19x19 grid lines."""
        grid = VGroup()
        z_level = 0.01 # Slightly above board to prevent Z-fighting
        
        for i in range(19):
            # Vertical lines
            start_v = self.board_to_point(i, 0, z_offset=z_level)
            end_v = self.board_to_point(i, 18, z_offset=z_level)
            grid.add(Line(start_v, end_v, color=self.GRID_COLOR, stroke_width=2))
            
            # Horizontal lines
            start_h = self.board_to_point(0, i, z_offset=z_level)
            end_h = self.board_to_point(18, i, z_offset=z_level)
            grid.add(Line(start_h, end_h, color=self.GRID_COLOR, stroke_width=2))
            
        return grid

    def create_star_points(self):
        """Creates the 9 standard star points."""
        stars = VGroup()
        z_level = 0.015
        for i in [3, 9, 15]:
            for j in [3, 9, 15]:
                pos = self.board_to_point(i, j, z_offset=z_level)
                stars.add(Dot(pos, radius=0.06, color=self.GRID_COLOR))
        return stars

    def create_stone(self, color, is_black=True):
        """Creates a flattened 3D sphere to represent a Go stone."""
        stone_radius = self.SPACING * 0.48
        # Spheres provide natural 3D highlights
        stone = Sphere(radius=stone_radius, resolution=(12, 12))
        stone.set_color(color)
        
        # Flatten the sphere to look like a biconvex Go stone
        stone.scale(np.array([1, 1, 0.4]))
        
        # Shift it up so it rests precisely on the board (Z=0)
        z_offset = 0.02 + (stone_radius * 0.4)
        stone.shift(OUT * z_offset)
        return stone

    def create_heatmap(self):
        """Creates a soft human-likelihood heatmap over the local fight."""
        heatmap = VGroup()
        centers = [
            (15, 3, 1.5, RED),    # Heavy fight bottom right
            (3, 15, 0.8, ORANGE), # Minor cluster top left
            (15, 15, 0.5, YELLOW) # Corner
        ]
        
        z_level = 0.02
        for cx, cy, radius, color in centers:
            center_pos = self.board_to_point(cx, cy, z_offset=z_level)
            # Create concentric soft circles
            for r in np.linspace(0.2, radius, 6):
                glow_ring = Circle(radius=r, stroke_width=0, fill_color=color, fill_opacity=0.06)
                glow_ring.move_to(center_pos)
                heatmap.add(glow_ring)
                
        return heatmap

    def create_text_labels(self):
        """Creates the commentator labels around the board."""
        labels = VGroup()
        words = ["too early?", "too far?", "mistake?", "brilliant?"]
        
        # Distribute them in empty spots around the board
        positions = [
            (8, 14),   # Top middle
            (3, 8),    # Left middle
            (11, 4),   # Bottom middle
            (16, 12)   # Right middle
        ]
        
        z_level = 0.1 # Float above the stones
        for word, (cx, cy) in zip(words, positions):
            pos = self.board_to_point(cx, cy, z_offset=z_level)
            lbl = Text(word, font_size=24, color=WHITE).move_to(pos)
            labels.add(lbl)
            
        return labels

    # ==========================================
    # ANIMATION SEQUENCES
    # ==========================================

    def play_first_36_moves(self):
        """Animates a realistic cluster of 36 opening moves."""
        # Coordinates mimicking an opening with a fight in the bottom right
        moves = [
            (15, 3), (3, 15), (15, 15), (3, 3), (14, 2), (16, 4), (2, 14),
            (15, 2), (16, 2), (14, 3), (16, 3), (14, 4), (15, 4), (13, 2), 
            (16, 1), (17, 2), (15, 5), (16, 5), (17, 4), (12, 3), (2, 15), 
            (4, 15), (3, 16), (3, 14), (4, 14), (2, 13), (9, 3), (15, 9), 
            (3, 9), (9, 15), (10, 3), (16, 14), (14, 15), (15, 13), (2, 16), (4, 16)
        ]
        
        for i, (cx, cy) in enumerate(moves):
            is_black = (i % 2 == 0)
            color = self.BLACK_STONE if is_black else self.WHITE_STONE
            
            stone = self.create_stone(color, is_black)
            # Position the stone on the board based on coordinates
            target_pos = self.board_to_point(cx, cy)
            # The stone's internal offset is already handled, just move to X,Y
            stone.move_to(np.array([target_pos[0], target_pos[1], stone.get_center()[2]]))
            
            # Start slightly higher and drop in
            stone.save_state()
            stone.shift(OUT * 0.5)
            stone.set_opacity(0)
            
            # Speed up the placements as we go
            rt = max(0.15, 0.4 - (i * 0.008))
            self.play(Restore(stone), run_time=rt, rate_func=ease_in_out_sine)

    def transition_to_top_down(self):
        """Smoothly shifts the camera to a perfect 2D top-down view."""
        self.move_camera(
            phi=0, 
            theta=-90 * DEGREES, 
            run_time=6, 
            rate_func=smooth
        )

    def play_move_37(self):
        """Dramatically places the Move 37 stone."""
        cx, cy = self.MOVE_37_COORD
        move37 = self.create_stone(self.BLACK_STONE, is_black=True)
        target_pos = self.board_to_point(cx, cy)
        move37.move_to(np.array([target_pos[0], target_pos[1], move37.get_center()[2]]))
        
        move37.save_state()
        move37.shift(OUT * 2.0)
        move37.set_opacity(0)
        
        # The stone drops down
        self.play(Restore(move37), run_time=2, rate_func=ease_in_out_sine)
        
        # Expanding highlight halo
        halo = Circle(radius=self.SPACING * 0.48, color=BLUE, stroke_width=6)
        # Place it just above the board to be visible
        halo.move_to(self.board_to_point(cx, cy, z_offset=0.03))
        
        self.play(
            halo.animate.scale(5).set_opacity(0), 
            run_time=2, 
            rate_func=ease_out_quad
        )

    def show_labels_and_zoom(self):
        """Displays flickering commentary labels and zooms into Move 37."""
        labels = self.create_text_labels()
        
        # Fade in all labels simultaneously
        self.play(FadeIn(labels, shift=UP*0.2), run_time=1.5)
        
        # Flicker to signify shock/re-evaluation
        self.play(
            LaggedStart(
                *[Indicate(lbl, color=YELLOW, scale_factor=1.2) for lbl in labels],
                lag_ratio=0.2
            ),
            run_time=2.5
        )
        
        # Final cinematic zoom directly into Move 37
        move_37_pos = self.board_to_point(*self.MOVE_37_COORD, z_offset=0)
        self.move_camera(
            focal_point=move_37_pos,
            zoom=2.5, # Camera zoom parameter
            run_time=6,
            rate_func=smooth
        )
        self.wait(1)
