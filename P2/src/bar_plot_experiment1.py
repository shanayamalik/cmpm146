import matplotlib.pyplot as plt
import numpy as np

def plot_tree_size_experiment(tree_sizes, player1_wins, player2_wins):
    plt.figure(figsize=(10, 6))
    
    # Set width for bars
    width = 0.35
    x = np.arange(len(tree_sizes))
    
    # Create bars
    plt.bar(x - width/2, player1_wins, width, label='Player 1 (100 nodes)', 
            color='skyblue', edgecolor='black')
    plt.bar(x + width/2, player2_wins, width, label='Player 2 (Variable nodes)', 
            color='lightcoral', edgecolor='black')
    
    # Customize the plot
    plt.xlabel('Tree Sizes (Player 2)', fontsize=12)
    plt.ylabel('Number of Wins', fontsize=12)
    plt.title('Experiment 1: Tree Size vs Wins', fontsize=14, pad=20)
    
    # Set x-axis ticks
    plt.xticks(x, tree_sizes)
    
    # Add grid
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add legend
    plt.legend()
    
    # Add value labels on top of each bar
    for i in range(len(tree_sizes)):
        plt.text(i - width/2, player1_wins[i] + 1, str(player1_wins[i]), 
                ha='center', va='bottom')
        plt.text(i + width/2, player2_wins[i] + 1, str(player2_wins[i]), 
                ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('experiment_1_bar_plot.png', dpi=300, bbox_inches='tight')
    print("Plot saved as 'experiment_1_bar_plot.png'")
    
    # Show the plot
    plt.show()

# Your actual experimental data
tree_sizes = [100, 250, 500, 750, 1000]
player1_wins = [47, 27, 18, 8, 7]
player2_wins = [53, 73, 82, 92, 93]

# Create the plot
plot_tree_size_experiment(tree_sizes, player1_wins, player2_wins)
