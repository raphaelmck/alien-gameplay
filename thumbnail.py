#!/usr/bin/env python3
"""
thumbnail.py — YouTube thumbnail for "The Bitter Lesson".

Output: thumbnail.png  (1920×1080, 4× supersampled then bicubic-downscaled)
Run:    python3 thumbnail.py
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# ─── canvas ────────────────────────────────────────────────────────────────
SCALE = 4
W,  H  = 1920, 1080
WS, HS = W * SCALE, H * SCALE

# ─── colors ────────────────────────────────────────────────────────────────
BG_COL      = (6,   6,  10)
BOARD_COL   = (200, 169, 110)
GRID_COL    = (28,  28,  28)
STAR_COL    = (28,  28,  28)
BLACK_STONE = (18,  18,  18)
WHITE_STONE = (245, 245, 245)
PURPLE      = (130,  55, 195)   # muted violet
TITLE_COL   = (240, 240, 240)

# ─── board moves (37 total, black starts) ─────────────────────────────────
# (i, j): i = col 0–18 left→right, j = row 0–18 near→far
MOVES = [
    (15,15),(3,3),(2,15),(16,3),(14,3),(14,2),(13,2),   # 1–7
    (15,2),(2,5),(5,2),(12,3),(16,5),(8,16),(3,9),       # 8–14
    (15,4),(16,4),(2,3),(2,2),(1,2),(2,4),(1,3),         # 15–21
    (1,4),(3,4),(1,5),(3,2),(4,3),(3,1),(2,6),           # 22–28
    (9,3),(2,12),(4,15),(16,13),(16,14),(15,13),(13,15),(15,10),  # 29–36
    (14,9),                                               # 37
]
MOVE37_IDX   = 36
MOVE37_COORD = (14, 9)
STAR_PTS     = [(i,j) for i in [3,9,15] for j in [3,9,15]]

# ─── font paths ────────────────────────────────────────────────────────────
LM_DIR  = "/usr/local/texlive/2025/texmf-dist/fonts/opentype/public/lm/"
FONT_BD = LM_DIR + "lmroman10-bold.otf"
FONT_RG = LM_DIR + "lmroman10-regular.otf"

# ─── board perspective ─────────────────────────────────────────────────────
# Natural overhead angle (~55° tilt, slight horizontal rotation).
# j=0  = near (bottom, larger)  j=18 = far (top, smaller)
# Top edge ≈ 76 % of bottom edge → moderate, natural-looking perspective.
CORNERS_1X = {
    (0,  18): (990,  100),   # top-left  far
    (18, 18): (1760, 185),   # top-right far
    (18,  0): (1860, 980),   # bot-right near
    (0,   0): (830,  965),   # bot-left  near
}

def _homography(src, dst):
    A = []
    for (xs,ys),(xd,yd) in zip(src,dst):
        A += [[-xs,-ys,-1,0,0,0,xd*xs,xd*ys,xd],
              [0,0,0,-xs,-ys,-1,yd*xs,yd*ys,yd]]
    _,_,V = np.linalg.svd(np.array(A,float))
    M = V[-1].reshape(3,3)
    return M / M[2,2]

_SRC = [(0,0),(18,0),(18,18),(0,18)]
_DST = [(x*SCALE, y*SCALE) for (i,j),(x,y) in sorted(
        CORNERS_1X.items(),
        key=lambda kv: (_SRC[[(0,0),(18,0),(18,18),(0,18)].index(kv[0])],)
    )]
# build DST in the same order as SRC
_DST = [
    (CORNERS_1X[(0, 0)][0]*SCALE,  CORNERS_1X[(0, 0)][1]*SCALE),
    (CORNERS_1X[(18,0)][0]*SCALE,  CORNERS_1X[(18,0)][1]*SCALE),
    (CORNERS_1X[(18,18)][0]*SCALE, CORNERS_1X[(18,18)][1]*SCALE),
    (CORNERS_1X[(0, 18)][0]*SCALE, CORNERS_1X[(0, 18)][1]*SCALE),
]
_H = _homography(_SRC, _DST)

def b2s(i, j):
    """Board grid (i,j) → super-sampled screen (x,y)."""
    v = _H @ np.array([i, j, 1.0])
    return float(v[0]/v[2]), float(v[1]/v[2])

def local_radius(i, j):
    dx = np.linalg.norm(np.subtract(b2s(i+.5,j), b2s(i-.5,j)))
    dy = np.linalg.norm(np.subtract(b2s(i,j+.5), b2s(i,j-.5)))
    return (dx + dy) / 2 * 0.46

# ─── helpers ───────────────────────────────────────────────────────────────

def alpha_ring(img, cx, cy, r, color, width, alpha):
    """Draw a single anti-aliased ring on a transparent layer and composite."""
    layer = Image.new('RGBA', img.size, (0,0,0,0))
    d     = ImageDraw.Draw(layer)
    d.ellipse([cx-r, cy-r, cx+r, cy+r],
              outline=(*color, alpha), width=width)
    img.alpha_composite(layer)

def draw_single_ring(img, cx, cy, stone_r, color):
    """One clean ring just outside the stone edge."""
    ring_width = max(SCALE * 3, int(stone_r * 0.12))
    r          = int(stone_r * 1.90)
    alpha_ring(img, cx, cy, r, color, ring_width, 220)

def draw_board_shadow(img):
    """Soft drop-shadow underneath the near edge for 3-D depth."""
    layer = Image.new('RGBA', img.size, (0,0,0,0))
    d     = ImageDraw.Draw(layer)
    steps = 24
    for k in range(steps, 0, -1):
        off   = int(k * SCALE * 0.8)
        alpha = int(90 * (1 - k/steps) ** 0.7)
        pts   = [
            (int(b2s(0, 0)[0]+off),  int(b2s(0, 0)[1]+off)),
            (int(b2s(18,0)[0]+off),  int(b2s(18,0)[1]+off)),
            (int(b2s(18,18)[0]+off), int(b2s(18,18)[1]+off)),
            (int(b2s(0, 18)[0]+off), int(b2s(0, 18)[1]+off)),
        ]
        d.polygon(pts, fill=(0,0,0,alpha))
    img.alpha_composite(layer)

def draw_board_edge(draw):
    """Dark near-side edge face for physical board thickness."""
    thick = int(14 * SCALE)
    pts   = [
        b2s(0, 0), b2s(18, 0),
        (b2s(18,0)[0], b2s(18,0)[1]+thick),
        (b2s(0, 0)[0], b2s(0, 0)[1]+thick),
    ]
    draw.polygon([(int(x),int(y)) for x,y in pts], fill=(85, 62, 28))

def draw_vignette(img):
    """Subtle edge-darkening to focus the eye on the board."""
    layer = Image.new('RGBA', img.size, (0,0,0,0))
    d     = ImageDraw.Draw(layer)
    steps = 60
    for k in range(steps):
        t  = k / steps
        px = int(WS * 0.10 * t)
        py = int(HS * 0.14 * t)
        a  = int(110 * (1-t) ** 2.0)
        for rect in [
            [0, 0, WS-1, py],
            [0, HS-1-py, WS-1, HS-1],
            [0, 0, px, HS-1],
            [WS-1-px, 0, WS-1, HS-1],
        ]:
            d.rectangle(rect, fill=(0,0,0,a))
    img.alpha_composite(layer)

# ─── main ──────────────────────────────────────────────────────────────────

def main():
    img  = Image.new('RGBA', (WS, HS), (*BG_COL, 255))
    draw = ImageDraw.Draw(img)

    # ── board shadow ─────────────────────────────────────────────────────
    draw_board_shadow(img)
    draw = ImageDraw.Draw(img)

    # ── board near edge ───────────────────────────────────────────────────
    draw_board_edge(draw)

    # ── board surface ─────────────────────────────────────────────────────
    board_poly = [
        (int(b2s(0, 18)[0]),  int(b2s(0, 18)[1])),
        (int(b2s(18,18)[0]),  int(b2s(18,18)[1])),
        (int(b2s(18, 0)[0]),  int(b2s(18, 0)[1])),
        (int(b2s(0,  0)[0]),  int(b2s(0,  0)[1])),
    ]
    draw.polygon(board_poly, fill=BOARD_COL)

    # ── grid lines ────────────────────────────────────────────────────────
    lw = max(1, SCALE)
    for k in range(19):
        draw.line([b2s(k, 0), b2s(k, 18)], fill=GRID_COL, width=lw)
        draw.line([b2s(0, k), b2s(18, k)], fill=GRID_COL, width=lw)

    # ── star points ───────────────────────────────────────────────────────
    for si,sj in STAR_PTS:
        sx,sy = b2s(si,sj)
        sr    = max(2, int(local_radius(si,sj) * 0.22))
        draw.ellipse([sx-sr,sy-sr,sx+sr,sy+sr], fill=STAR_COL)

    # ── stones ────────────────────────────────────────────────────────────
    m37x, m37y = b2s(*MOVE37_COORD)
    m37r        = local_radius(*MOVE37_COORD)

    for idx,(ci,cj) in enumerate(MOVES):
        sx, sy = b2s(ci, cj)
        r      = int(local_radius(ci, cj))
        sw     = max(SCALE, int(r * 0.07))

        if idx == MOVE37_IDX:
            draw.ellipse([sx-r, sy-r, sx+r, sy+r],
                         fill=PURPLE, outline=(90, 38, 150), width=sw)
        elif idx % 2 == 0:
            draw.ellipse([sx-r, sy-r, sx+r, sy+r],
                         fill=BLACK_STONE, outline=(55,55,55), width=sw)
        else:
            draw.ellipse([sx-r, sy-r, sx+r, sy+r],
                         fill=WHITE_STONE, outline=(185,185,185), width=sw)

    # ── single ring around move 37 ────────────────────────────────────────
    draw_single_ring(img, m37x, m37y, int(m37r), PURPLE)
    draw = ImageDraw.Draw(img)

    # ── title text: "The Bitter Lesson" in Latin Modern Roman ────────────
    font_title = ImageFont.truetype(FONT_BD, int(128 * SCALE))

    text_x = int(68 * SCALE)
    y      = int(288 * SCALE)

    for line in ["The Bitter", "Lesson"]:
        # Soft shadow
        draw.text((text_x + int(3*SCALE), y + int(3*SCALE)),
                  line, font=font_title, fill=(0,0,0,160))
        draw.text((text_x, y), line, font=font_title, fill=TITLE_COL)
        bbox = draw.textbbox((text_x, y), line, font=font_title)
        y   += (bbox[3] - bbox[1]) + int(16 * SCALE)

    # ── vignette ─────────────────────────────────────────────────────────
    draw_vignette(img)

    # ── downscale to final resolution ─────────────────────────────────────
    final = img.convert('RGB').resize((W, H), Image.LANCZOS)
    final.save("thumbnail.png", 'PNG')
    print(f"Saved thumbnail.png  ({W}×{H})")

if __name__ == '__main__':
    main()
