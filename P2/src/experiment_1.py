import sys
from timeit import default_timer as time
import p2_t3
import mcts_vanilla

# Define the tree sizes to test
tree_sizes = [100, 110, 120, 130]  # Different tree sizes for Player 2
rounds = 100  # Number of games per configuration

# Define players
# Player 1 will have a fixed tree size
fixed_tree_size_for_player1 = 500

# Initialize the board
board = p2_t3.Board()
state0 = board.starting_state()

# Store results
results = {}

# Loop through tree sizes for Player 2
for tree_size in tree_sizes:
    print(f"Testing tree size: {tree_size}")
    wins = {'draw': 0, 1: 0, 2: 0}

    start = time()
    for i in range(rounds):
        print(f"Round {i + 1}...")

        state = state0
        last_action = None

        # Define Player 1 and Player 2 with their respective tree sizes
        mcts_vanilla.num_nodes = fixed_tree_size_for_player1  # Set fixed tree size for Player 1
        player1 = lambda board, state: mcts_vanilla.think(board, state)

        mcts_vanilla.num_nodes = tree_size  # Set varying tree size for Player 2
        player2 = lambda board, state: mcts_vanilla.think(board, state)

        current_player = player1

        while not board.is_ended(state):
            # Get the action from the current player bot
            last_action = current_player(board, state)
            # Update the state with the chosen action
            state = board.next_state(state, last_action)
            # Switch between Player 1 and Player 2
            current_player = player1 if current_player == player2 else player2

        # Determine the winner and update the win counts
        final_score = board.points_values(state)
        if final_score[1] == 1:
            wins[1] += 1  # Player 1 wins
        elif final_score[2] == 1:
            wins[2] += 1  # Player 2 wins
        else:
            wins['draw'] += 1  # Draw

    end = time()
    # Store the results for the current tree size
    results[tree_size] = wins
    print(f"Results for tree size {tree_size}: {wins}")
    print(f"Time taken: {end - start:.2f} seconds")

# Output the results
print("\nFinal results:")
for tree_size, result in results.items():
    print(f"Tree size {tree_size}: {result}")
