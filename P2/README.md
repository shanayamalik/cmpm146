# README: Monte Carlo Tree Search for Ultimate Tic-Tac-Toe

## Team Members
- Matthew Streib
- Shanaya Malik

## Overview
This project implements a Monte Carlo Tree Search (MCTS) bot for playing Ultimate Tic-Tac-Toe. Two versions of the MCTS bot were developed:
1. **Vanilla MCTS**: Implements the standard MCTS algorithm with random rollouts.
2. **Modified MCTS**: Enhances the vanilla implementation with heuristic rollouts and additional improvements.

## Modifications in `mcts_modified.py`
The following modifications were made to improve upon the vanilla MCTS implementation:

1. **Heuristic Rollout Strategy**:
   - Replaced the random rollout strategy from `mcts_vanilla.py` with a heuristic-based approach.
   - The heuristic prioritizes moves that increase the likelihood of winning sub-games and completing rows, columns, or diagonals in the larger game board. This allows the bot to evaluate game states more intelligently during rollouts.

2. **Dynamic Exploration Parameter**:
   - Adjusted the exploration parameter in the UCB formula dynamically based on the current game phase. Early in the game, a higher exploration factor was used to encourage broader exploration. In the late game, the factor was reduced to focus on exploitation.

3. **Node Selection Enhancements**:
   - Improved the selection phase by incorporating additional heuristics to favor nodes with higher potential for game-changing moves. This adjustment reduces the likelihood of exploring suboptimal branches.

4. **Efficiency Improvements**:
   - Optimized the data structure for tracking child nodes to reduce overhead during the selection and expansion phases.
   - Parallelized portions of the rollout phase to improve performance during computationally intensive simulations.

5. **Detailed Statistics Tracking**:
   - Added functionality to track and log additional statistics about the tree, such as average depth and branching factor. This was useful for debugging and analysis.

## Results Summary
The modifications in `mcts_modified.py` were evaluated against the vanilla implementation in a series of experiments. While the heuristic rollouts provided a strategic advantage in some cases, the additional computational cost limited the number of nodes explored within time constraints. These results highlight the tradeoff between computational complexity and strategic depth in MCTS-based bots.

## File List
- `mcts_vanilla.py`: Implements the vanilla MCTS algorithm.
- `mcts_modified.py`: Implements the modified MCTS algorithm with heuristic rollouts and additional enhancements.
- `experiment_1_results.txt`: Results and analysis for Experiment 1 (Tree Size vs Wins).
- `experiment_2_results.txt`: Results and analysis for Experiment 2 (Heuristic Improvements).
- `experiment_3_results.txt`: Results and analysis for Experiment 3 (Time as a Constraint).
- `experiment_1_bar_plot.png`: Bar plot for Experiment 1 results.
- `README.md`: Project overview and details on modifications.

## Instructions
This repository contains all files required to run and evaluate the MCTS bots. For more details about running the code or reproducing the experiments, please refer to the assignment prompt and the experiment result files.
