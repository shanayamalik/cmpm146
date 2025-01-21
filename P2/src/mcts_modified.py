from mcts_node import MCTSNode
from p2_t3 import Board
import random
from math import sqrt, log

# Number of nodes to simulate and exploration parameter
num_nodes = 1000
explore_faction = 2.0

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """Traverses the tree until the end criterion are met."""
    current_node = node
    current_state = state

    # Continue traversing until we reach a terminal state
    while not board.is_ended(current_state):
        # If we find a node with untried actions, select it for expansion
        if current_node.untried_actions:
            return current_node, current_state

        # Implementation of the selection phase using Upper Confidence Bound (UCB)
        # This helps balance exploration and exploitation during tree traversal
        best_value = float('-inf')
        best_child = None
        best_action = None

        # Evaluate all child nodes using UCB formula
        for action in current_node.child_nodes:
            child = current_node.child_nodes[action]
            # Adjust UCB calculation based on whether it's opponent's turn
            is_opponent = board.current_player(current_state) != bot_identity
            value = ucb(child, is_opponent)
            
            if value > best_value:
                best_value = value
                best_child = child
                best_action = action

        # If no children are available, return current node
        if best_child is None:
            return current_node, current_state

        # Move to the selected child node
        current_node = best_child
        current_state = board.next_state(current_state, best_action)

    return current_node, current_state

def expand_leaf(node: MCTSNode, board: Board, state):
    """Adds a new leaf to the tree by creating a new child node."""
    if board.is_ended(state):
        return node, state

    # Systematic expansion by always trying the first untried action
    # This ensures a more structured exploration of the game tree
    action = node.untried_actions[0]
    new_state = board.next_state(state, action)
    node.untried_actions.remove(action)
    
    # Create new child node with all possible actions from the new state
    child_node = MCTSNode(
        parent=node,
        parent_action=action,
        action_list=board.legal_actions(new_state)
    )
    
    # Add the new child to the tree
    node.child_nodes[action] = child_node
    return child_node, new_state

def heuristic(board: Board, state, prev_action, bot_identity: int):

    score = 0
    opponent_identity = None
    if bot_identity == 1:
        opponent_identity = 2
    else:
        opponent_identity = 1
        
    # Check if the game is over
    if board.is_ended(state):
        points = board.points_values(state)
        if points[bot_identity] == 1:  # Win
            return 999999  # Large positive value for a win
        elif points[opponent_identity] == 1:  # Loss
            return -999999 # Large negative value for a loss
        else:
            return 0  # Draw
        
    # Give small bonus for taking straegic positions (the middle)
    if prev_action[0] == (1, 1):  # Middle big board
        score += 20  # Bonus for targeting the center of the big board
    if prev_action[1] == (1, 1):  # Center of the mini-board
        score += 20  # Bonus for targeting the center of a board

    # Favor states where the bot has winning moves next turn, dont favor states where opponent can win next turn
    for action in board.legal_actions(state):
        next_state = board.next_state(state, action)
        if board.is_ended(next_state):
            points = board.points_values(next_state)
            if points[bot_identity] == 1:  # Current player wins
                score += 999 # Winning is prioritized
            elif points[opponent_identity] == 1:  # Opponent wins
                score -= 999 # Penalize if opponent can win next turn

    return score

def roulette_select(actions, scores):
    """Select an action based on roulette wheel selection."""
    total_score = sum(scores)
    if total_score == 0:
        # If the total score is 0 (all actions are equally bad), select randomly
        return random.choice(actions)
    
    # Normalize scores to form a probability distribution
    probabilities = [score / total_score for score in scores]
    
    # Perform the random selection
    random_value = random.random()
    cumulative_probability = 0.0
    for action, probability in zip(actions, probabilities):
        cumulative_probability += probability
        if random_value <= cumulative_probability:
            return action

    return None

def rollout(board: Board, state):
    """ Simulate the game randomly until a terminal state is reached. """
    bot_identity = board.current_player(state)
    opponent_identity = None
    if bot_identity == 1:
        opponent_identity = 2
    else:
        opponent_identity = 1
    
    while not board.is_ended(state):
        if board.current_player(state) == bot_identity:
            legal_actions = board.legal_actions(state)
            scores = [heuristic(board, board.next_state(state, action), action, bot_identity) for action in legal_actions]
            # Use roulette selection based on heuristic scores
            best_action = roulette_select(legal_actions, scores)
        else:
            legal_actions = board.legal_actions(state)
            scores = [heuristic(board, board.next_state(state, action), action, opponent_identity) for action in legal_actions]
            # Use roulette selection based on heuristic scores
            best_action = roulette_select(legal_actions, scores)
        
        state = board.next_state(state, best_action)
    return state

def backpropagate(node: MCTSNode | None, won: bool):
    """ Update the win and visit counts for nodes from the leaf back to the root. """
    current = node
    while current is not None:
        current.visits += 1
        if won:
            current.wins += 1 
        current = current.parent

def ucb(node: MCTSNode, is_opponent: bool):
    """Calculates the UCB value for the given node."""
    if node.visits == 0:
        return float('inf')  # Ensures unvisited nodes are explored
    
    # Calculate win rate adjusted for current player perspective
    win_rate = node.wins / node.visits
    if is_opponent:
        win_rate = 1 - win_rate  # Invert win rate for opponent's turn
    
    # UCB exploration term - balances exploration vs exploitation
    exploration = explore_faction * sqrt(log(node.parent.visits) / node.visits)
    
    return win_rate + exploration

def get_best_action(root_node: MCTSNode):
    """Selects the best action from the root node in the MCTS tree."""
    best_action = None
    best_value = float('-inf')
    
    # Advanced action selection considering both win rate and visit count
    # This helps choose more reliable moves with sufficient exploration
    for action, child in root_node.child_nodes.items():
        if child.visits == 0:
            continue
            
        # Weighted combination of win rate and visit frequency
        visit_weight = 0.7  # Bias towards more explored nodes
        win_rate = child.wins / child.visits
        visit_rate = child.visits / root_node.visits
        value = (1 - visit_weight) * win_rate + visit_weight * visit_rate
        
        if value > best_value:
            best_value = value
            best_action = action
    
    # Fallback strategy if no action meets criteria
    if best_action is None and root_node.child_nodes:
        best_action = max(root_node.child_nodes.items(), 
                         key=lambda x: x[1].visits)[0]
            
    return best_action

def is_win(board: Board, state, identity_of_bot: int):
    """ Check if the given state is a win for the bot. """
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """Performs MCTS by sampling games and calling the appropriate functions."""
    # Initialize the root of the game tree
    bot_identity = board.current_player(current_state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))

    # Main MCTS loop - builds game tree through repeated simulations
    for _ in range(num_nodes):
        state = current_state
        node = root_node

        # Four phases of MCTS:
        # 1. Selection - Find promising node to expand
        node, state = traverse_nodes(node, board, state, bot_identity)
        
        # 2. Expansion - Add new node to tree
        if not board.is_ended(state):
            node, state = expand_leaf(node, board, state)
        
        # 3. Simulation - Random playthrough to terminal state
        end_state = rollout(board, state)
        
        # 4. Backpropagation - Update statistics along path
        won = is_win(board, end_state, bot_identity)
        backpropagate(node, won)

    # Select final move based on gathered statistics
    best_action = get_best_action(root_node)
    print(f"Action chosen: {best_action}")
    return best_action

