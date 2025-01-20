from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

# Increased number of nodes for better performance
num_nodes = 100
# Adjusted exploration factor
explore_faction = 1.414  # sqrt(2) is a common choice for UCT

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """Traverses the tree until the end criterion are met."""
    while not board.is_ended(state) and not node.untried_actions:
        if node.child_nodes:
            max_ucb = float('-inf')
            next_node = None
            next_state = None
            
            # Break ties randomly for equal UCB values
            max_nodes = []
            max_states = []
            
            for action, child in node.child_nodes.items():
                is_opponent = board.current_player(state) != bot_identity
                current_ucb = ucb(child, is_opponent)
                
                if current_ucb > max_ucb:
                    max_ucb = current_ucb
                    max_nodes = [child]
                    max_states = [board.next_state(state, action)]
                elif current_ucb == max_ucb:
                    max_nodes.append(child)
                    max_states.append(board.next_state(state, action))
            
            # Randomly select among best nodes
            idx = choice(range(len(max_nodes)))
            node = max_nodes[idx]
            state = max_states[idx]
        else:
            return node, state
            
    return node, state

def expand_leaf(node: MCTSNode, board: Board, state):
    """Adds a new leaf to the tree by creating a new child node."""
    if not board.is_ended(state) and node.untried_actions:
        # Choose action based on potential immediate wins
        action = None
        for possible_action in node.untried_actions:
            next_state = board.next_state(state, possible_action)
            if board.is_ended(next_state):
                action = possible_action
                break
        
        # If no winning move, choose randomly
        if action is None:
            action = choice(node.untried_actions)
            next_state = board.next_state(state, action)
        
        node.untried_actions.remove(action)
        
        child_node = MCTSNode(
            parent=node,
            parent_action=action,
            action_list=board.legal_actions(next_state)
        )
        
        node.child_nodes[action] = child_node
        return child_node, next_state
        
    return node, state

def evaluate_state(board: Board, state, bot_identity: int):
    """Evaluates the current state similar to rollout bot's evaluation."""
    owned_boxes = board.owned_boxes(state)
    game_points = board.points_values(state)
    
    if game_points is not None:
        # Use game points if game is ended
        score = game_points[bot_identity]
        return score > 0
    
    # Count boxes owned by each player
    bot_boxes = len([v for v in owned_boxes.values() if v == bot_identity])
    opp_boxes = len([v for v in owned_boxes.values() if v != 0 and v != bot_identity])
    
    return bot_boxes > opp_boxes

def rollout(board: Board, state):
    """Plays out the remainder of the game with improved rollout strategy."""
    current_state = state
    
    # Use a depth limit similar to rollout bot
    for _ in range(5):  # MAX_DEPTH from rollout bot
        if board.is_ended(current_state):
            break
            
        actions = board.legal_actions(current_state)
        
        # Check for winning moves
        for action in actions:
            next_state = board.next_state(current_state, action)
            if board.is_ended(next_state):
                return next_state
        
        # If no winning move, choose randomly
        action = choice(actions)
        current_state = board.next_state(current_state, action)
    
    return current_state

def backpropagate(node: MCTSNode|None, won: bool):
    """Updates the win and visit count of each node along the path."""
    while node is not None:
        node.visits += 1
        if won:
            node.wins += 1
        node = node.parent

def ucb(node: MCTSNode, is_opponent: bool):
    """Calculates the UCB value for the given node."""
    if node.visits == 0:
        return float('inf')
    
    # Win rate from perspective of the bot
    win_rate = node.wins / node.visits
    if is_opponent:
        win_rate = 1 - win_rate
    
    # Exploration term with adjusted exploration factor
    exploration = explore_faction * sqrt(log(node.parent.visits) / node.visits)
    
    return win_rate + exploration

def get_best_action(root_node: MCTSNode):
    """Selects the best action from the root node."""
    best_action = None
    best_value = float('-inf')
    
    # Use win rate instead of visit count for final selection
    for action, child in root_node.child_nodes.items():
        if child.visits == 0:
            continue
        
        win_rate = child.wins / child.visits
        if win_rate > best_value:
            best_value = win_rate
            best_action = action
            
    # Fallback to most visited if no wins
    if best_action is None:
        best_action = max(root_node.child_nodes.items(), 
                         key=lambda x: x[1].visits)[0]
            
    return best_action

def is_win(board: Board, state, identity_of_bot: int):
    """Checks if state is a win state for identity_of_bot."""
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """Performs MCTS by sampling games and calling the appropriate functions."""
    bot_identity = board.current_player(current_state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))
    
    for _ in range(num_nodes):
        state = current_state
        node = root_node
        
        # Selection
        node, state = traverse_nodes(node, board, state, bot_identity)
        
        # Expansion
        node, state = expand_leaf(node, board, state)
        
        # Simulation
        final_state = rollout(board, state)
        
        # Backpropagation
        if board.is_ended(final_state):
            won = is_win(board, final_state, bot_identity)
        else:
            # Use state evaluation for non-terminal states
            won = evaluate_state(board, final_state, bot_identity)
        backpropagate(node, won)
    
    best_action = get_best_action(root_node)
    print(f"MCTS bot picking {best_action}")
    return best_action
