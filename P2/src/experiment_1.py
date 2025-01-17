import sys
from timeit import default_timer as time
import p2_t3
import mcts_vanilla

# Define the tree sizes to test
tree_sizes = [100, 500, 1000, 2000]
rounds = 100  # Number of games per configuration

# Define players
players = dict(
    mcts_vanilla=mcts_vanilla.think,
)

# Initialize the board
board = p2_t3.Board()
state0 = board.starting_state()

# Store results
results = {}

# Loop through tree sizes for Player 2
for tree_size in tree_sizes:
    print(f"Testing tree size: {tree_size}")
    wins = {'draw': 0, 1: 0, 2: 0}
    
    # Update the number of nodes in the MCTS bot
    mcts_vanilla.num_nodes = tree_size

    start = time()
    for i in range(rounds):
        print(f"Round {i + 1}...")
        
        state = state0
        last_action = None
        current_player = players['mcts_vanilla']

        # Alternate between fixed (Player 1) and varying (Player 2) tree sizes
        while not board.is_ended(state):
            last_action = current_player(board, state)
            state = board.next_state(state, last_action)
            current_player = players['mcts_vanilla'] if current_player != players['mcts_vanilla'] else players['mcts_vanilla']

        final_score = board.points_values(state)
        if final_score[1] == 1:
            wins[1] += 1
        elif final_score[2] == 1:
            wins[2] += 1
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
