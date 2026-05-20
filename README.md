# Alien Gameplay

[![YouTube Video](https://img.shields.io/badge/Watch%20on-YouTube-red?logo=youtube)](https://www.youtube.com/watch?v=rk-s8Rw7qlM)

A Manim animation explaining why game-playing AI makes moves that feel alien — and what that reveals about intelligence, search, and learning.

The video covers:
- Move 37: the moment AlphaGo played something no human would choose
- Games as mathematical objects: states, actions, transitions, rewards
- Minimax: defining intelligence as recursive value propagation
- The exponential tree explosion and why exact search is impossible
- Evaluation functions: approximating the unknowable future with a single number
- Alpha-beta pruning: mathematically useful ignorance
- The Bitter Lesson: why search and learning beat human intuition at scale
- AlphaGo: policy networks, value networks, and Monte Carlo Tree Search combined
- Self-play: generating a synthetic civilization of experience
- Why alien moves happen: optimized for a geometry of the game we don't naturally see

## Watch

> Click on the link above to watch on YouTube

## Run the animations

```bash
manim -pql src/scenes/s00_intro.py
```

## Project structure

```
src/scenes/   # Manim scene files (one per section)
src/style.py  # Shared style and helpers
media/        # Rendered output (auto-generated, not committed)
```
