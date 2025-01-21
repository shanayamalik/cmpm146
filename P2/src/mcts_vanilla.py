from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

num_nodes = 100
explore_faction = 2.

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """Traverses the tree until the end criterion are met."""
    current_node = node
    current_state = state

    while not board.is_ended(current_state):
        # Return if we find a node that has untried actions
        if current_node.untried_actions:
            return current_node, current_state

        # Select child using UCB
        best_value = float('-inf')
        best_child = None
        best_action = None

        for action in current_node.child_nodes:
            child = current_node.child_nodes[action]
            is_opponent = board.current_player(current_state) != bot_identity
            value = ucb(child, is_opponent)
            
            if value > best_value:
                best_value = value
                best_child = child
                best_action = action

        if best_child is None:  # No children available
            return current_node, current_state

        current_node = best_child
        current_state = board.next_state(current_state, best_action)

    return current_node, current_state

def expand_leaf(node: MCTSNode, board: Board, state):
    """Adds a new leaf to the tree by creating a new child node."""
    if board.is_ended(state):
        return node, state

    action = choice(node.untried_actions)
    new_state = board.next_state(state, action)
    node.untried_actions.remove(action)
    
    child_node = MCTSNode(
        parent=node,
        parent_action=action,
        action_list=board.legal_actions(new_state)
    )
    
    node.child_nodes[action] = child_node
    return child_node, new_state

def rollout(board: Board, state):
    """Given the state of the game, the rollout plays out the remainder randomly."""
    rollout_state = state
    
    while not board.is_ended(rollout_state):
        action = choice(board.legal_actions(rollout_state))
        rollout_state = board.next_state(rollout_state, action)
    
    return rollout_state

def backpropagate(node: MCTSNode|None, won: bool):
    """Navigates the tree from a leaf node to the root, updating the win and visit count."""
    current = node
    while current is not None:
        current.visits += 1
        current.wins += 1 if won else 0
        current = current.parent

def ucb(node: MCTSNode, is_opponent: bool):
    """Calculates the UCB value for the given node."""
    if node.visits == 0:
        return float('inf')
    
    # Win rate from the perspective of the bot
    win_rate = node.wins / node.visits
    if is_opponent:
        win_rate = 1 - win_rate  # Invert win rate for opponent's turn
    
    # Exploration term
    exploration = explore_faction * sqrt(log(node.parent.visits) / node.visits)
    
    return win_rate + exploration

def get_best_action(root_node: MCTSNode):
    """Selects the best action from the root node in the MCTS tree."""
    best_action = None
    best_value = float('-inf')
    
    # Choose action with highest win rate
    for action, child in root_node.child_nodes.items():
        value = child.wins / child.visits if child.visits > 0 else 0
        if value > best_value:
            best_value = value
            best_action = action
            
    return best_action

def is_win(board: Board, state, identity_of_bot: int):
    """Checks if state is a win state for identity_of_bot."""
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """Performs MCTS by sampling games and calling the appropriate functions to construct the game tree."""
    bot_identity = board.current_player(current_state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))

    for _ in range(num_nodes):
        state = current_state
        node = root_node

        # Selection
        node, state = traverse_nodes(node, board, state, bot_identity)
        
        # Expansion
        if not board.is_ended(state):
            node, state = expand_leaf(node, board, state)
        
        # Simulation/Rollout
        end_state = rollout(board, state)
        
        # Backpropagation
        won = is_win(board, end_state, bot_identity)
        backpropagate(node, won)

    best_action = get_best_action(root_node)
    print(f"Action chosen: {best_action}")
    return best_action
