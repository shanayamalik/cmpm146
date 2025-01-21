import matplotlib.pyplot as plt
import numpy as np

def plot_experiment_results():
    # Data points
    tree_sizes = [100, 250, 500, 750, 1000]
    player1_wins = [47, 27, 18, 8, 7]
    player2_wins = [53, 73, 82, 92, 93]
    
    # Create figure and axis with larger size
    plt.figure(figsize=(12, 8))
    
    # Plot lines
    plt.plot(tree_sizes, player1_wins, 'b-o', label='Player 1 (100 nodes)', linewidth=2, markersize=8)
    plt.plot(tree_sizes, player2_wins, 'r-o', label='Player 2 (Variable nodes)', linewidth=2, markersize=8)
    
    # Customize the plot
    plt.title('MCTS Performance vs Tree Size', fontsize=14, pad=20)
    plt.xlabel('Player 2 Tree Size (nodes)', fontsize=12)
    plt.ylabel('Number of Wins', fontsize=12)
    
    # Add grid
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Add legend
    plt.legend(fontsize=10)
    
    # Add value labels on the points
    for i, (p1, p2) in enumerate(zip(player1_wins, player2_wins)):
        plt.text(tree_sizes[i], p1-2, str(p1), ha='center', va='bottom')
        plt.text(tree_sizes[i], p2+2, str(p2), ha='center', va='top')
    
    # Set y-axis limits with some padding
    plt.ylim(0, 100)
    
    # Save the plot
    plt.savefig('experiment_1_results.png', dpi=300, bbox_inches='tight')
    print("Plot saved as 'experiment_1_results.png'")

if __name__ == "__main__":
    plot_experiment_results()
