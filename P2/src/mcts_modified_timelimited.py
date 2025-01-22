from mcts_node import MCTSNode
from p2_t3 import Board
import random
from math import sqrt, log
from timeit import default_timer as timer

# Configuration parameters
explore_faction = 2.0
# Default time limit in seconds if not specified
time_limit = 1.0

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """Traverses the tree until the end criterion are met."""
    current_node = node
    current_state = state

    while not board.is_ended(current_state):
        if current_node.untried_actions:
            return current_node, current_state

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

        if best_child is None:
            return current_node, current_state

        current_node = best_child
        current_state = board.next_state(current_state, best_action)

    return current_node, current_state

def expand_leaf(node: MCTSNode, board: Board, state):
    """Adds a new leaf to the tree by creating a new child node."""
    if board.is_ended(state):
        return node, state

    action = node.untried_actions[0]
    new_state = board.next_state(state, action)
    node.untried_actions.remove(action)
   
    child_node = MCTSNode(
        parent=node,
        parent_action=action,
        action_list=board.legal_actions(new_state)
    )
   
    node.child_nodes[action] = child_node
    return child_node, new_state

def heuristic(board: Board, state, prev_action, bot_identity: int):
    """Evaluates the state using heuristic rules."""
    score = 0
    opponent_identity = 2 if bot_identity == 1 else 1
       
    # Check if the game is over
    if board.is_ended(state):
        points = board.points_values(state)
        if points[bot_identity] == 1:  # Win
            return 999999  # Large positive value for a win
        elif points[opponent_identity] == 1:  # Loss
            return -999999 # Large negative value for a loss
        else:
            return 0  # Draw
       
    # Give bonus for taking strategic positions (the middle)
    if prev_action[0] == (1, 1):  # Middle big board
        score += 20  # Bonus for targeting the center of the big board
    if prev_action[1] == (1, 1):  # Center of the mini-board
        score += 20  # Bonus for targeting the center of a board

    # Favor states where the bot has winning moves next turn, penalize states where opponent can win next turn
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
        # If all actions are equally bad, select randomly
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
    """ Simulate the game using heuristic-guided rollout until a terminal state is reached. """
    bot_identity = board.current_player(state)
    opponent_identity = 2 if bot_identity == 1 else 1
   
    while not board.is_ended(state):
        if board.current_player(state) == bot_identity:
            legal_actions = board.legal_actions(state)
            scores = [heuristic(board, board.next_state(state, action), action, bot_identity) 
                     for action in legal_actions]
            # Use roulette selection based on heuristic scores
            best_action = roulette_select(legal_actions, scores)
        else:
            legal_actions = board.legal_actions(state)
            scores = [heuristic(board, board.next_state(state, action), action, opponent_identity) 
                     for action in legal_actions]
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
        return float('inf')
   
    win_rate = node.wins / node.visits
    if is_opponent:
        win_rate = 1 - win_rate
   
    exploration = explore_faction * sqrt(log(node.parent.visits) / node.visits)
   
    return win_rate + exploration

def get_best_action(root_node: MCTSNode):
    """Selects the best action from the root node in the MCTS tree."""
    best_action = None
    best_value = float('-inf')
   
    for action, child in root_node.child_nodes.items():
        if child.visits == 0:
            continue
           
        visit_weight = 0.7
        win_rate = child.wins / child.visits
        visit_rate = child.visits / root_node.visits
        value = (1 - visit_weight) * win_rate + visit_weight * visit_rate
       
        if value > best_value:
            best_value = value
            best_action = action
   
    if best_action is None and root_node.child_nodes:
        best_action = max(root_node.child_nodes.items(),
                         key=lambda x: x[1].visits)[0]
           
    return best_action, root_node

def is_win(board: Board, state, identity_of_bot: int):
    """ Check if the given state is a win for the bot. """
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state, max_time=time_limit):
    """Performs MCTS by sampling games within the time limit.
    
    Args:
        board: The game board instance
        current_state: The current game state
        max_time: Maximum time in seconds to spend on tree search (default: 1.0)
    """
    bot_identity = board.current_player(current_state)
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))

    start_time = timer()
    num_iterations = 0

    # Continue building the tree until we exceed the time limit
    while (timer() - start_time) < max_time:
        state = current_state
        node = root_node

        # Selection
        node, state = traverse_nodes(node, board, state, bot_identity)
       
        # Expansion
        if not board.is_ended(state):
            node, state = expand_leaf(node, board, state)
       
        # Simulation with heuristic-guided rollout
        end_state = rollout(board, state)
       
        # Backpropagation
        won = is_win(board, end_state, bot_identity)
        backpropagate(node, won)
        
        num_iterations += 1

    time_used = timer() - start_time
    print(f"Time used: {time_used:.3f} seconds")
    print(f"Iterations completed: {num_iterations}")

    best_action = get_best_action(root_node)
    print(f"Action chosen: {best_action}")
    return best_action
