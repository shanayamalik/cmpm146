from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

# Number of nodes to simulate and exploration parameter
num_nodes = 100
explore_faction = 2.0

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """ Traverse the tree until a node with untried actions or a terminal state is reached. """
    while not node.untried_actions and node.child_nodes:
        # Use UCB to select the next node
        action, node = max(node.child_nodes.items(), key=lambda item: ucb(item[1], is_opponent=(bot_identity != board.current_player(state))))
        state = board.next_state(state, action)
    return node, state

def expand_leaf(node: MCTSNode, board: Board, state):
    """ Expand the tree by adding a child node for one of the untried actions. """
    action = node.untried_actions.pop()
    next_state = board.next_state(state, action)
    child_node = MCTSNode(parent=node, parent_action=action, action_list=board.legal_actions(next_state))
    node.child_nodes[action] = child_node
    return child_node, next_state

def rollout(board: Board, state):
    """ Simulate the game randomly until a terminal state is reached. """
    while not board.is_ended(state):
        action = choice(board.legal_actions(state))
        state = board.next_state(state, action)
    return state

def backpropagate(node: MCTSNode | None, won: bool):
    """ Update the win and visit counts for nodes from the leaf back to the root. """
    while node is not None:
        node.visits += 1
        if won:
            node.wins += 1
        won = not won  # Alternate perspective for the opponent
        node = node.parent

def ucb(node: MCTSNode, is_opponent: bool):
    """ Calculate the UCB value for a node. """
    if node.visits == 0:
        return float('inf')  # Ensure unvisited nodes are prioritized
    win_rate = (1 - node.wins / node.visits) if is_opponent else (node.wins / node.visits)
    return win_rate + explore_faction * sqrt(log(node.parent.visits) / node.visits)

def get_best_action(root_node: MCTSNode):
    """ Return the action with the most visits from the root node. """
    return max(root_node.child_nodes.items(), key=lambda item: item[1].visits)[0]

def is_win(board: Board, state, identity_of_bot: int):
    """ Check if the given state is a win for the bot. """
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """ Perform MCTS and return the best action from the root node. """
    bot_identity = board.current_player(current_state)  # Determine which bot is playing
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))

    for _ in range(num_nodes):
        # Start from the root and traverse the tree
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
