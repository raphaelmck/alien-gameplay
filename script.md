> **Games became AI laboratories because they turn intelligence into an algorithmic problem: search a tree, approximate value, improve through self-play, and scale computation.**

---

1. **Cold open: Move 37**
2. **Games as mathematical objects**
3. **Minimax: the first algorithmic intelligence**
4. **The tree explosion**
5. **Evaluation functions: approximating value**
6. **Alpha-beta pruning: useful ignorance**
7. **The Bitter Lesson**
8. **AlphaGo: policy, value, search**
9. **Self-play: learning from synthetic civilization**
10. **Why the moves feel alien**

---

## Scene 0 — Cold open: Move 37

**Voiceover:**

> intro about go and complexity, large possible state space, human intuition/how scientists thought it would be hard for machines to play well, etc.

> In 2016, one of the greatest Go players alive was sitting across from a machine.

> For the first 36 moves, the game looked almost normal.

> Then the machine played move 37.

> The commentators paused.
> The professionals were confused.
> The move looked too far away, too quiet, almost like a mistake.

> But many moves later, it became clear: the machine had seen something humans had not.

> That is the strange thing about game-playing AI.

> It does not just play better than us.
> Sometimes, it plays like it came from somewhere else.

**Manim visual:**

* 19×19 Go board.
* Human attention heatmap lights up the local fight.
* AlphaGo move appears outside the bright region.
* Text:

```text
Human prior: unlikely
Machine value: high
```

This immediately introduces the scientific question:

> How can an algorithm find a move that human intuition almost excludes?

---

## Scene 1 — Games as mathematical objects

This is the biggest upgrade. Make the video more mathematical early.

**Voiceover:**

> To a human, a game is a struggle of plans and ideas.
>
> To an algorithm, a game is something colder:
> a set of states, a set of legal actions, a transition rule, and a reward.
>
> A position is a state, usually called `s`.
> A move is an action, `a`.
> The rules tell you the next state.
> And at the end, someone gets a reward: win, loss, or draw.
>
> Once you write a game this way, intelligence becomes a problem of choosing actions.

**On screen:**

```text
State:        s
Action:       a
Transition:   s' = T(s, a)
Reward:       r ∈ {-1, 0, +1}
Goal:         choose a good a
```

**Manim visual:**

* Board position morphs into abstract notation:

```text
board → s
move → a
new board → T(s, a)
win/loss → r
```

This makes the video feel immediately more rigorous.

---

## Scene 2 — Minimax: intelligence as recursion

This should be the first major algorithmic explanation.

**Voiceover:**

> In a two-player zero-sum game, your gain is your opponent’s loss.
>
> So the first great idea is recursive.
>
> On my turn, I choose the move with the highest future value.
> On your turn, you choose the move with the lowest future value for me.
>
> This is minimax.

**On screen:**

```text
V(s) = max_a V(T(s, a))        my turn

V(s) = min_a V(T(s, a))        opponent's turn
```

Then:

```text
choose a* = argmax_a V(T(s, a))
```

**Manim visual:**

* Small game tree.
* Leaf values: `+1`, `0`, `-1`.
* Values propagate upward.
* Max nodes choose largest child.
* Min nodes choose smallest child.

**Engaging line:**

> A good move is not the move with the best dream.
> It is the move with the best nightmare.

This line should stay.

---

## Scene 3 — The tree explosion

Make this more quantitative.

**Voiceover:**

> The problem is that minimax is correct in a world where you can search everything.
>
> But real games are too large.
>
> If each position has about `b` legal moves, and you search `d` moves ahead, the tree has roughly:

**On screen:**

```text
1 + b + b² + b³ + ... + bᵈ ≈ bᵈ
```

**Voiceover:**

> That exponential is the wall every game-playing AI runs into.

**Manim visual:**

* Tree grows with branching factor `b`.
* Show:

```text
depth 1: b
depth 2: b²
depth 3: b³
depth d: bᵈ
```

* The tree becomes too dense and fades into fog.

**Key visual:**

A depth limit line cuts the tree.

```text
Search stops here.
But the game does not.
```

This sets up evaluation.

---

## Scene 4 — Evaluation: approximating the value function

This is where you make the video more ML/math flavored.

**Voiceover:**

> Since the algorithm cannot search to the end, it needs an approximation.
>
> Instead of computing the true value `V(s)`, it learns or designs an estimate:

**On screen:**

```text
true value:       V(s)
estimated value:  V̂(s)
```

or

```text
V̂θ(s) ≈ V(s)
```

**Voiceover:**

> In old chess engines, this estimate was built from human concepts: material, king safety, pawn structure, mobility.
>
> In modern systems, more of this evaluation is learned from data.
>
> Either way, the role is the same: compress a huge future into one number.

**Manim visual:**

Board position goes into a black box:

```text
position s → V̂θ(s) → +0.73
```

Then show two versions of the black box:

```text
hand-coded features
```

and

```text
learned neural network
```

**Beautiful visual:**

The giant future tree collapses into a single scalar:

```text
V̂θ(s) = +0.73
```

This is a strong scientific metaphor.

---

## Scene 5 — Alpha-beta pruning: mathematically useful ignorance

Keep this because it is one of the best algorithmic visuals.

**Voiceover:**

> Search also becomes stronger when the algorithm learns what not to search.
>
> Alpha-beta pruning is based on a simple fact:
> if a branch cannot change the final decision, its exact value no longer matters.

**On screen:**

```text
current best = 5
this branch can be at most 3
therefore: prune
```

**Manim visual:**

* Tree with minimax values.
* Some branches disappear before being expanded.
* Label:

```text
not wrong
not impossible
just irrelevant
```

**Stronger mathematical phrasing:**

> Alpha-beta does not change the minimax answer.
> It changes how much of the tree you need to inspect to find it.

That line makes it more precise.

---

## Scene 6 — The Bitter Lesson

This should be a dedicated but short scene, maybe 60–75 seconds.

**Voiceover:**

> This pattern shows up again and again in AI.
>
> Researchers first try to build in human knowledge: chess principles, Go concepts, linguistic rules, visual features.
>
> That often works at first.
>
> But in the long run, the biggest jumps tend to come from general methods that scale with computation.
>
> Richard Sutton called this the Bitter Lesson.
>
> The lesson is bitter because human insight feels meaningful, elegant, and satisfying.
> But the methods that keep winning are often simpler and more brutal: search and learning.

**Manim visual:**

Two paths:

```text
Path 1:
human concepts → clever rules → early progress → plateau

Path 2:
search + learning + compute → slow start → scaling → breakthrough
```

Make Path 1 rise quickly then flatten.
Make Path 2 start lower, then overtake.

**On-screen thesis:**

```text
The Bitter Lesson:
Methods that scale with computation eventually dominate.
```

**Tie back to games:**

> Chess and Go are almost perfect examples.
> The winning systems did not become superhuman by perfectly imitating human thought.
> They became superhuman by searching, learning, and scaling.

This connects directly to the previous outline’s point that game AIs feel alien because they search, evaluate, and learn differently from humans. 

---

## Scene 7 — AlphaGo as the synthesis

This replaces separate long scenes on Go, Monte Carlo Tree Search, policy networks, and value networks.

**Voiceover:**

> AlphaGo combined three ingredients.
>
> First, a policy network:

**On screen:**

```text
πθ(a | s)
```

**Voiceover:**

> Given a board position, it predicts which moves are promising.

**On screen:**

```text
πθ(a | s) = probability of move a in position s
```

**Voiceover:**

> Second, a value network:

```text
Vθ(s)
```

> Given a position, it estimates who is likely to win.
>
> Third, Monte Carlo Tree Search: a planning algorithm that uses the policy to decide where to search and the value function to evaluate what it finds.

**Manim visual:**

One central Go position splits into three components:

```text
Go position s
   ├── policy network πθ(a | s) → move heatmap
   ├── value network Vθ(s) → win probability
   └── tree search → explored futures
```

Then recombine:

```text
policy + value + search → move
```

**Optional formula for MCTS selection:**

Use a simplified version:

```text
score(s, a) = value so far + exploration bonus
```

If you want the more mathematical version:

```text
Q(s,a) + c · P(s,a) · √N(s) / (1 + N(s,a))
```

But be careful: do not over-explain it. You can say:

> The exact formula matters less than the idea: balance moves that already look good with moves that have not been explored enough.

**Manim visual:**

* Policy heatmap suggests candidate moves.
* MCTS tree grows mostly around high-probability moves.
* Value network evaluates leaf positions.
* Visit counts accumulate.
* Final move selected by most visited / highest confidence branch.

This is scientific, algorithmic, and visual.

---

## Scene 8 — Self-play as data generation

This is where the “alien” theme becomes serious.

**Voiceover:**

> But where does the training data come from?
>
> The most important answer is self-play.
>
> The system plays against itself.
> The search produces improved move probabilities.
> The final result of the game gives a training signal.
> Then the network is updated to imitate the stronger search and better predict the winner.

**On screen:**

```text
For each position sₜ:

target policy:   πₜ
game outcome:    z ∈ {-1, +1}

train:
πθ(· | sₜ) ≈ πₜ
Vθ(sₜ) ≈ z
```

**Voiceover:**

> This is the algorithmic heart of the alien feeling.
>
> The machine is not learning only from human games.
> It is generating its own curriculum.

**Manim visual:**

Circular training loop:

```text
current network
      ↓
self-play games
      ↓
tree search improves moves
      ↓
training examples
      ↓
new network
```

After each loop, the network glows brighter.

**Stronger visual:**

Show a library of human games on the left.

```text
Human games: finite cultural history
```

Show an expanding synthetic library on the right.

```text
Self-play games: generated experience
```

This keeps the “private civilization” image, but now it is grounded in training targets.

---

## Scene 9 — Why alien moves happen

This should be the climax.

**Voiceover:**

> Now Move 37 is no longer mysterious.
>
> The machine was not asking:
> would a human play this?
>
> It was asking something colder:
>
> If I search from here, guided by my policy, evaluated by my value network, trained through self-play, does this move increase the probability of winning?

**On screen:**

```text
Human question:
Does this look natural?

Machine question:
Does this improve Vθ(s)?
```

**Voiceover:**

> That is why the move can look wrong and still be strong.
>
> Human concepts are compressed from human experience.
> The machine’s concepts are compressed from optimization.

**Manim visual:**

Return to the Go board from the opening.

Now overlay:

```text
πθ(a | s): low human-like probability
Vθ(T(s,a)): high long-term value
MCTS visits: unexpectedly high
```

Then future influence lines appear across the board.

**Best line:**

> The move is not alien because it is random.
> It is alien because it is optimized for a geometry of the game we do not naturally see.

Keep this.

---

## Scene 10 — Ending: the Bitter Lesson of games

**Voiceover:**

> Board games taught AI a bitter lesson.
>
> For a while, it seemed natural to build machines that used human ideas: chess principles, Go patterns, expert rules.
>
> But the systems that changed history leaned harder on general methods: search, learning, self-play, and computation.
>
> That does not make human insight worthless.
> It means human insight is often not the ceiling.
>
> A machine can discover powerful strategies without inheriting our concepts, our style, or our sense of what looks natural.
>
> And that is why playing against it feels so strange.
>
> You are not just playing a stronger opponent.
> You are playing against a different way of turning computation into judgment.

**Final on-screen text:**

```text
Search + Learning + Compute
```

then transform into:

```text
A different way of seeing the future.
```

---

# The revised thesis

Use this near the beginning:

> The story of game-playing AI is one of the cleanest examples of the Bitter Lesson: systems became superhuman not by copying human intuition more perfectly, but by using general methods — search and learning — that scale with computation.

That is much stronger than the original thesis.

---

# The new central diagram

You should make one diagram that appears multiple times and evolves.

Start simple:

```text
s → choose a
```

Then minimax:

```text
s → search tree → best a
```

Then evaluation:

```text
s → search tree → V̂(s) → best a
```

Then AlphaGo:

```text
s
├── πθ(a | s)  policy
├── Vθ(s)      value
└── MCTS       search
        ↓
      best a
```

Then Bitter Lesson:

```text
human knowledge  → helps early
search + learning + compute → scales
```

This gives the video coherence.

---

# What makes it more scientific

Add these ingredients:

## 1. Formal notation, but lightly

Use notation as visual compression, not as lecture clutter.

Good notation:

```text
s = state
a = action
T(s,a) = next state
V(s) = value
π(a|s) = policy
```

Avoid too much:

```text
Bellman optimality equations
full UCT derivation
full reinforcement learning loss
```

You can include one compact training loss if you want:

```text
loss = policy error + value error
```

or:

```text
L(θ) = (z - Vθ(s))² - πᵀ log pθ(·|s)
```

But only show it briefly.

## 2. Use algorithm boxes

For minimax:

```text
Minimax(s):
    if game over: return outcome
    if my turn: return max value of children
    if opponent turn: return min value of children
```

For self-play:

```text
repeat:
    play games using search
    store positions, search policies, outcomes
    train network
```

These make the video feel more algorithmic.

## 3. Show approximations

The scientific story is really:

```text
exact solution impossible
→ approximate search
→ approximate value
→ learned policy
→ iterative improvement
```

That is a clean technical arc.

---

# What makes it shorter

Use this compressed scene list:

| Scene |                           Topic | Length |
| ----- | ------------------------------: | -----: |
| 0     |               Move 37 cold open |   0:45 |
| 1     | Games as states/actions/rewards |   1:00 |
| 2     |                         Minimax |   1:30 |
| 3     |      Exponential tree explosion |   1:00 |
| 4     |            Evaluation functions |   1:15 |
| 5     |              Alpha-beta pruning |   1:00 |
| 6     |                   Bitter Lesson |   1:10 |
| 7     |    AlphaGo: policy/value/search |   1:45 |
| 8     |                       Self-play |   1:20 |
| 9     |            Alien moves + ending |   1:30 |

Total: about **12 minutes**.

---

# Stronger opening after revisions

> In 2016, AlphaGo played a move that almost no human would have chosen.
>
> It looked too far away from the fight.
> It violated the shape of human expectation.
>
> But many moves later, the board began to explain it.
>
> The machine had not made a mistake.
> It had evaluated the future differently.
>
> To understand how that happens, we need to stop thinking of a game as a board with pieces, and start thinking of it as a mathematical object: states, actions, transitions, and rewards.
>
> From there, the alien move becomes less like magic and more like a consequence of one of the deepest lessons in AI: search and learning scale better than human intuition.

---

# Stronger Bitter Lesson transition

Use this after evaluation/pruning, before AlphaGo:

> For decades, AI researchers tried to make game-playing programs smarter by giving them more human knowledge.
>
> Better chess features. Better Go patterns. Better expert rules.
>
> And often, that helped.
>
> But the largest jumps came from something less romantic: methods that could absorb more computation.
>
> Search deeper. Learn from more games. Improve through self-play.
>
> This is the Bitter Lesson.
>
> The bitter part is that our own concepts are not useless, but they are often not what scales.

---

# Best final line

> The alien was not built by adding mystery.
>
> It was built by removing human assumptions, then scaling search and learning until the game revealed patterns we had never named.

