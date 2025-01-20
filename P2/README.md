# Ultimate Tic-Tac-Toe with Monte Carlo Tree Search

## Team Members
- Member 1: [Your Name] (responsible for `mcts_vanilla.py` and Experiment 1)
- Member 2: [Partner's Name] (responsible for `mcts_modified.py` and Experiment 2)

## Overview
This project implements Monte Carlo Tree Search (MCTS) to play Ultimate Tic-Tac-Toe. It includes:
1. A vanilla MCTS bot that uses random rollouts.
2. A modified MCTS bot with a heuristic-based rollout strategy.

We also conduct experiments to analyze the performance of these bots under various configurations.

---

## Files
### Code:
1. `mcts_vanilla.py`: Implements the vanilla MCTS bot.
2. `mcts_modified.py`: Implements the modified MCTS bot with a heuristic rollout strategy.
3. `p2_play.py`: Allows interactive gameplay between bots or human players.
4. `p2_sim.py`: Simulates multiple games between bots for experiments.
5. `mcts_node.py`: Defines the structure of MCTS nodes.
6. `p2_t3.py`: Contains the game board implementation and utility functions.
7. `random_bot.py`: Implements a random bot that selects actions randomly.
8. `rollout_bot.py`: Implements a bot that evaluates all possible moves with random rollouts.

### Experiment Reports:
1. `experiment1.pdf`: Analyzes the effect of tree size on the performance of the vanilla MCTS bot.
2. `experiment2.pdf`: Evaluates the heuristic improvements in `mcts_modified.py`.

---

## How to Run
1. Interactive gameplay can be used to play against or between bots, allowing direct observation of their strategies.
2. Simulations allow for automated gameplay and data collection for experiments.

---

## Experiments
### Experiment 1: Tree Size Analysis
- Objective: Compare win rates of vanilla MCTS with different tree sizes.
- Setup: Fix Player 1 with a small tree size and vary Player 2's tree size over several values.
- Execution: Simulate multiple games between Player 1 and Player 2.
- Analysis: Plot win rates for different tree sizes and document observations in `experiment1.pdf`.

### Experiment 2: Heuristic Improvement
- Objective: Compare `mcts_modified.py` and `mcts_vanilla.py` with equal tree sizes.
- Setup: Use the same tree size for both bots and simulate multiple games.
- Execution: Simulate games between the vanilla and modified bots.
- Analysis: Document win rates and observations in `experiment2.pdf`.

### Experiment 3 (Extra Credit): Time Constraint
- Objective: Evaluate the effect of a time constraint on tree growth and performance.
- Setup: Modify both bots to grow the tree within a fixed time budget. Run simulations at varying time limits.
- Execution: Compare tree sizes and win rates for both bots under time constraints.
- Analysis: Document results, including differences in tree sizes, win rates, and execution time.

---

## Notes
- Parameters such as tree size and exploration factors are adjustable in the respective bot files.
- Experiments with larger tree sizes may require significant time; adjust configurations if needed.
- Additional bonus points can be achieved by parallelizing simulations for improved performance.

---

## References
- MCTS Survey Paper: Monte Carlo Tree Search: A Review of Recent Developments (http://diego-perez.net/papers/MCTSSurvey.pdf)
