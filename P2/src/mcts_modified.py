from mcts_node import MCTSNode
from p2_t3 import Board
import random
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
    while node is not None:
        node.visits += 1
        if node.child_nodes:
            # Calculate the average and maximum values from children
            avg_weight = 0.8 # weight for avg values
            max_weight = 0.2 # weight for max value
            child_values = [child.wins / child.visits if child.visits > 0 else 0 for child in node.child_nodes.values()]
            avg_value = sum(child_values) / len(child_values) if child_values else 0
            max_value = max(child_values) if child_values else 0
            node.wins = avg_weight * avg_value + max_weight * max_value # value will be a weighted sum of the avg values and the max value seen
        else:
            node.wins += 1 if won else 0
        # won = not won  # Alternate perspective
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
