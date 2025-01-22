import sys
from timeit import default_timer as timer
import p2_t3
import mcts_vanilla_timelimited as mcts_vanilla
import mcts_modified_timelimited as mcts_modified
from mcts_node import MCTSNode
import random_bot
import rollout_bot
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np

def count_tree_nodes(node):
    """Recursively count the number of nodes in the MCTS tree."""
    if not node.child_nodes:
        return 1
    return 1 + sum(count_tree_nodes(child) for child in node.child_nodes.values())

def run_game(player1, player2, board, time_limit):
    """Run a single game between two players with specified time limit."""
    state = board.starting_state()
    moves_p1 = 0
    moves_p2 = 0
    tree_sizes_p1 = []
    tree_sizes_p2 = []
    
    while not board.is_ended(state):
        # Player 1's turn
        if board.current_player(state) == 1:
            action, tree = player1(board, state, max_time=time_limit)
            moves_p1 += 1
            tree_sizes_p1.append(count_tree_nodes(tree))
        # Player 2's turn
        else:
            action, tree = player2(board, state, max_time=time_limit)
            moves_p2 += 1
            tree_sizes_p2.append(count_tree_nodes(tree))
            
        state = board.next_state(state, action)
    
    # Get final score
    points = board.points_values(state)
    
    # Calculate average tree sizes
    avg_tree_size_p1 = sum(tree_sizes_p1) / len(tree_sizes_p1) if tree_sizes_p1 else 0
    avg_tree_size_p2 = sum(tree_sizes_p2) / len(tree_sizes_p2) if tree_sizes_p2 else 0
    
    return {
        'winner': 1 if points[1] > points[2] else 2 if points[2] > points[1] else 0,
        'points': points,
        'moves_p1': moves_p1,
        'moves_p2': moves_p2,
        'avg_tree_size_p1': avg_tree_size_p1,
        'avg_tree_size_p2': avg_tree_size_p2
    }

def run_experiment(n_games=50):
    """Run the complete experiment with different time limits."""
    board = p2_t3.Board()
    time_limits = [0.1, 0.5, 1.0, 1.5]  # Time limits in seconds
    results = defaultdict(list)
    
    print("\nRunning Experiment 3 - Time as a Constraint")
    print("===========================================")
    
    for time_limit in time_limits:
        print(f"\nTesting with time limit: {time_limit} seconds")
        vanilla_wins = 0
        modified_wins = 0
        draws = 0
        total_tree_size_vanilla = 0
        total_tree_size_modified = 0
        
        for game in range(n_games):
            print(f"\nGame {game + 1}/{n_games}")
            # Alternate who plays first
            if game % 2 == 0:
                players = (mcts_vanilla.think, mcts_modified.think)
                print("Vanilla (P1) vs Modified (P2)")
            else:
                players = (mcts_modified.think, mcts_vanilla.think)
                print("Modified (P1) vs Vanilla (P2)")
            
            game_result = run_game(players[0], players[1], board, time_limit)
            
            # Record results
            if game % 2 == 0:  # Vanilla is P1
                if game_result['winner'] == 1:
                    vanilla_wins += 1
                elif game_result['winner'] == 2:
                    modified_wins += 1
                else:
                    draws += 1
                total_tree_size_vanilla += game_result['avg_tree_size_p1']
                total_tree_size_modified += game_result['avg_tree_size_p2']
            else:  # Modified is P1
                if game_result['winner'] == 1:
                    modified_wins += 1
                elif game_result['winner'] == 2:
                    vanilla_wins += 1
                else:
                    draws += 1
                total_tree_size_modified += game_result['avg_tree_size_p1']
                total_tree_size_vanilla += game_result['avg_tree_size_p2']
        
        # Calculate averages
        avg_tree_size_vanilla = total_tree_size_vanilla / n_games
        avg_tree_size_modified = total_tree_size_modified / n_games
        
        # Store results
        results['time_limits'].append(time_limit)
        results['vanilla_wins'].append(vanilla_wins)
        results['modified_wins'].append(modified_wins)
        results['draws'].append(draws)
        results['avg_tree_size_vanilla'].append(avg_tree_size_vanilla)
        results['avg_tree_size_modified'].append(avg_tree_size_modified)
        
        print(f"\nResults for time limit {time_limit}s:")
        print(f"Vanilla wins: {vanilla_wins}")
        print(f"Modified wins: {modified_wins}")
        print(f"Draws: {draws}")
        print(f"Average tree size - Vanilla: {avg_tree_size_vanilla:.1f} nodes")
        print(f"Average tree size - Modified: {avg_tree_size_modified:.1f} nodes")
    
    return results

def plot_results(results):
    """Create visualizations of the experimental results."""
    # Plot 1: Win rates
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    x = np.arange(len(results['time_limits']))
    width = 0.25
    
    plt.bar(x - width, results['vanilla_wins'], width, label='Vanilla wins')
    plt.bar(x, results['draws'], width, label='Draws')
    plt.bar(x + width, results['modified_wins'], width, label='Modified wins')
    
    plt.xlabel('Time limit (seconds)')
    plt.ylabel('Number of games')
    plt.title('Game Outcomes vs Time Limit')
    plt.xticks(x, results['time_limits'])
    plt.legend()
    
    # Plot 2: Tree sizes
    plt.subplot(1, 2, 2)
    plt.plot(results['time_limits'], results['avg_tree_size_vanilla'], 
             'b-o', label='Vanilla MCTS')
    plt.plot(results['time_limits'], results['avg_tree_size_modified'], 
             'r-o', label='Modified MCTS')
    
    plt.xlabel('Time limit (seconds)')
    plt.ylabel('Average tree size (nodes)')
    plt.title('Tree Size vs Time Limit')
    plt.legend()
    
    plt.tight_layout()
    plt.savefig('experiment3_results.png')
    plt.close()

def main():
    results = run_experiment()
    plot_results(results)
    print("\nExperiment complete! Results have been saved to experiment3_results.png")

if __name__ == "__main__":
    main()
