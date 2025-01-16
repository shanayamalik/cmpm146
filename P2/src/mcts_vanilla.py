from mcts_node import MCTSNode
from p2_t3 import Board
from random import choice
from math import sqrt, log

num_nodes = 100
explore_faction = 2.0

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """ Traverses the tree until the end criterion is met. """
    while not node.untried_actions and node.child_nodes:
        # Select the child node with the highest UCB value
        node = max(
            node.child_nodes.values(),
            key=lambda child: ucb(child, is_opponent=(board.current_player(state) != bot_identity))
        )
        state = board.next_state(state, node.parent_action)
    return node, state

def expand_leaf(node: MCTSNode, board: Board, state):
    """ Adds a new leaf node to the tree. """
    action = node.untried_actions.pop()
    new_state = board.next_state(state, action)
    new_node = MCTSNode(parent=node, parent_action=action, action_list=board.legal_actions(new_state))
    node.child_nodes[action] = new_node
    return new_node, new_state

def rollout(board: Board, state):
    """ Plays out the game randomly until a terminal state is reached. """
    while not board.is_ended(state):
        action = choice(board.legal_actions(state))
        state = board.next_state(state, action)
    return state

def backpropagate(node: MCTSNode | None, won: bool):
    """ Updates the win and visit counts from leaf to root. """
    while node is not None:
        node.visits += 1
        if won:
            node.wins += 1
        node = node.parent
        won = not won  # Alternate perspective for opponent

def ucb(node: MCTSNode, is_opponent: bool):
    """ Calculates the UCB value for the given node. """
    if node.visits == 0:
        return float('inf')  # Prioritize unexplored nodes
    win_rate = node.wins / node.visits
    if is_opponent:
        win_rate = 1 - win_rate  # Invert win rate for opponent's perspective
    return win_rate + explore_faction * sqrt(log(node.parent.visits) / node.visits)

def get_best_action(root_node: MCTSNode):
    """ Selects the action with the highest visit count. """
    return max(root_node.child_nodes.items(), key=lambda item: item[1].visits)[0]

def is_win(board: Board, state, identity_of_bot: int):
    """ Checks if the current state is a win for the bot. """
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """ Performs MCTS to decide the best action to take. """
    bot_identity = board.current_player(current_state)  # 1 or 2
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))

    for _ in range(num_nodes):
        state = current_state
        node = root_node

        # Selection
        node, state = traverse_nodes(node, board, state, bot_identity)

        # Expansion
        if node.untried_actions:
            node, state = expand_leaf(node, board, state)

        # Simulation
        final_state = rollout(board, state)

        # Backpropagation
        won = is_win(board, final_state, bot_identity)
        backpropagate(node, won)

    # Return the most visited action
    best_action = get_best_action(root_node)
    print(f"Action chosen: {best_action}")
    return best_action
