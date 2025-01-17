import sys
from timeit import default_timer as time
import p2_t3
import mcts_vanilla
import mcts_modified

# Define the tree sizes to test
tree_sizes = [100, 500, 1000]
rounds = 100  # Number of games per configuration

# Define players
players = dict(
    mcts_vanilla=mcts_vanilla.think,
    mcts_modified=mcts_modified.think
)

# Initialize the board
board = p2_t3.Board()
state0 = board.starting_state()

# Store results
results = {}

# Loop through tree sizes
for tree_size in tree_sizes:
    print(f"Testing tree size: {tree_size}")
    wins = {'draw': 0, 'vanilla': 0, 'modified': 0}

    # Update the number of nodes in both MCTS bots
    mcts_vanilla.num_nodes = tree_size
    mcts_modified.num_nodes = tree_size

    start = time()
    for i in range(rounds):
        print(f"Round {i + 1}...")

        state = state0
        last_action = None
        current_player = players['mcts_vanilla']

        # Alternate between vanilla and modified bots
        while not board.is_ended(state):
            last_action = current_player(board, state)
            state = board.next_state(state, last_action)
            current_player = players['mcts_modified'] if current_player == players['mcts_vanilla'] else players['mcts_vanilla']

        final_score = board.points_values(state)
        if final_score[1] == 1:
            wins['vanilla'] += 1
        elif final_score[2] == 1:
            wins['modified'] += 1
        else:
            wins['draw'] += 1

    end = time()
    results[tree_size] = wins
    print(f"Results for tree size {tree_size}: {wins}")
    print(f"Time taken: {end - start:.2f} seconds")

# Output the results
print("\nFinal results:")
for tree_size, result in results.items():
    print(f"Tree size {tree_size}: {result}")
