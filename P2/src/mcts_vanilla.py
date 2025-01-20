from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

# Number of nodes to simulate and exploration parameter
num_nodes = 100  # Number of simulations (tree size)
explore_faction = 2.0  # Exploration parameter for UCB

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """ Traverse the tree until a node with untried actions or a terminal state is reached. """
    while not node.untried_actions and node.child_nodes:
        # Use UCB to select the next node
        action, node = max(
            node.child_nodes.items(),
            key=lambda item: ucb(
                item[1],
                is_opponent=(bot_identity != board.current_player(state))
            )
        )
        # Update the state based on the chosen action
        state = board.next_state(state, action)
    return node, state

def expand_leaf(node: MCTSNode, board: Board, state):
    """ Expand the tree by adding a child node for one of the untried actions. """
    # Select an untried action
    action = node.untried_actions.pop()
    # Generate the new state resulting from the chosen action
    next_state = board.next_state(state, action)
    # Create a child node for the action
    child_node = MCTSNode(
        parent=node,
        parent_action=action,
        action_list=board.legal_actions(next_state)
    )
    # Add the child node to the current node's child nodes
    node.child_nodes[action] = child_node
    return child_node, next_state

def rollout(board: Board, state):
    """ Simulate the game randomly until a terminal state is reached. """
    while not board.is_ended(state):
        # Choose a random legal action
        action = choice(board.legal_actions(state))
        # Update the state with the chosen action
        state = board.next_state(state, action)
    return state  # Return the terminal state after the rollout

def backpropagate(node: MCTSNode | None, won: bool):
    """ Update the win and visit counts for nodes from the leaf back to the root. """
    while node is not None:
        # Increment the visit count for the node
        node.visits += 1
        # Increment the win count if the current player won
        if won:
            node.wins += 1
        # Switch perspective for the opponent
        won = not won
        # Move to the parent node
        node = node.parent

def ucb(node: MCTSNode, is_opponent: bool):
    """ Calculate the UCB value for a node. """
    if node.visits == 0:
        return float('inf')  # Prioritize unvisited nodes
    # Calculate win rate based on whether it's the opponent's turn
    win_rate = (1 - node.wins / node.visits) if is_opponent else (node.wins / node.visits)
    # Add the exploration term to the win rate
    return win_rate + explore_faction * sqrt(log(node.parent.visits) / node.visits)

def get_best_action(root_node: MCTSNode):
    """ Return the action with the most visits from the root node. """
    # Select the action associated with the child node that has the highest visit count
    return max(root_node.child_nodes.items(), key=lambda item: item[1].visits)[0]

def is_win(board: Board, state, identity_of_bot: int):
    """ Check if the given state is a win for the bot. """
    # Get the outcome of the game
    outcome = board.points_values(state)
    # Ensure the state is terminal
    assert outcome is not None, "is_win was called on a non-terminal state"
    # Return True if the bot wins, False otherwise
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """ Perform MCTS and return the best action from the root node. """
    # Identify the current player (bot identity)
    bot_identity = board.current_player(current_state)
    # Initialize the root node with the current state
    root_node = MCTSNode(
        parent=None,
        parent_action=None,
        action_list=board.legal_actions(current_state)
    )

    # Run simulations to build the search tree
    for _ in range(num_nodes):
        # Start from the root node and traverse the tree
        state = current_state
        node = root_node

        # Selection: Traverse to a promising node
        node, state = traverse_nodes(node, board, state, bot_identity)

        # Expansion: Add a new child node if possible
        if node.untried_actions and not board.is_ended(state):
            node, state = expand_leaf(node, board, state)

        # Simulation: Rollout to a terminal state
        final_state = rollout(board, state)

        # Backpropagation: Update the tree with the results
        won = is_win(board, final_state, bot_identity)
        backpropagate(node, won)

    # Return the action with the highest visit count
    best_action = get_best_action(root_node)
    print(f"Action chosen: {best_action}")
    return best_action
