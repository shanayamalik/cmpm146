#!/usr/bin/env python
import pyhop

# Operators
def op_punch_for_wood(state, ID):
    """
    Basic wood gathering operation - slower but requires no tools
    Input: current state and agent ID
    Effect: +1 wood, -4 time units
    """
    if state.time.get(ID, 0) >= 4:
        state.wood[ID] = state.wood.get(ID, 0) + 1
        state.time[ID] -= 4
        return state
    return False

def op_craft_plank(state, ID):
    """
    Converts wood into planks at 1:4 ratio
    Input: current state and agent ID
    Requirements: 1 wood
    Effect: -1 wood, +4 planks, -1 time unit
    """
    if state.wood.get(ID, 0) >= 1:
        state.plank[ID] = state.plank.get(ID, 0) + 4
        state.wood[ID] -= 1
        state.time[ID] -= 1
        return state
    return False

def op_craft_stick(state, ID):
    """
    Creates sticks from planks - essential for tool crafting
    Input: current state and agent ID
    Requirements: 2 planks
    Effect: -2 planks, +4 sticks, -1 time unit
    """
    if state.plank.get(ID, 0) >= 2:
        state.stick[ID] = state.stick.get(ID, 0) + 4
        state.plank[ID] -= 2
        state.time[ID] -= 1
        return state
    return False

def op_craft_bench(state, ID):
    """
    Creates a crafting bench - required for advanced recipes
    Input: current state and agent ID
    Requirements: 4 planks
    Effect: -4 planks, +1 bench, -1 time unit
    """
    if state.plank.get(ID, 0) >= 4:
        state.bench[ID] = state.bench.get(ID, 0) + 1
        state.plank[ID] -= 4
        state.time[ID] -= 1
        return state
    return False

def op_craft_wooden_axe(state, ID):
    """
    Creates wooden axe - enables faster wood gathering
    Input: current state and agent ID
    Requirements: 3 planks, 2 sticks, 1 bench
    Effect: -3 planks, -2 sticks, +1 wooden_axe, -1 time unit
    """
    if (state.plank.get(ID, 0) >= 3 and 
        state.stick.get(ID, 0) >= 2 and 
        state.bench.get(ID, 0) >= 1):
        state.wooden_axe[ID] = 1
        state.plank[ID] -= 3
        state.stick[ID] -= 2
        state.time[ID] -= 1
        return state
    return False

def op_chop_for_wood(state, ID):
    """
    Enhanced wood gathering using axe - faster than punching
    Input: current state and agent ID
    Requirements: wooden_axe, 2 time units
    Effect: +1 wood, -2 time units
    """
    if state.time.get(ID, 0) >= 2 and state.wooden_axe.get(ID, 0) >= 1:
        state.wood[ID] = state.wood.get(ID, 0) + 1
        state.time[ID] -= 2
        return state
    return False

# Register all operators with the planner
pyhop.declare_operators(op_punch_for_wood, op_craft_plank, op_craft_stick,
                        op_craft_bench, op_craft_wooden_axe, op_chop_for_wood)

# Methods
def produce_wood(state, ID):
    """
    Strategic wood production method
    - First ensures we have an axe for efficiency
    - Then uses appropriate gathering method based on available tools
    Returns: List of subtasks to produce wood
    """
    # Base case: already have enough wood
    if state.wood.get(ID, 0) >= 12:
        return []
    # First priority: get an axe for efficiency
    if state.wooden_axe.get(ID, 0) < 1:
        return [('produce', ID, 'wooden_axe'),
                ('produce', ID, 'wood')]
    # Use axe if we have enough time for chopping
    if state.time.get(ID, 0) >= 2:
        return [('op_chop_for_wood', ID),
                ('produce', ID, 'wood')]
    # Fall back to punching if we have enough time
    if state.time.get(ID, 0) >= 4:
        return [('op_punch_for_wood', ID),
                ('produce', ID, 'wood')]
    return False

def produce_plank(state, ID):
    """
    Plank production strategy
    - Ensures wood availability before crafting
    Returns: List of subtasks to produce planks
    """
    if state.wood.get(ID, 0) < 1:
        return [('op_punch_for_wood', ID),
                ('op_craft_plank', ID)]
    return [('op_craft_plank', ID)]

def produce_stick(state, ID):
    """
    Stick production method using have_enough subtask
    Returns: List of subtasks to produce sticks
    """
    return [('have_enough', ID, 'plank', 2),
            ('op_craft_stick', ID)]

def produce_bench(state, ID):
    """
    Crafting bench production strategy
    - Checks current inventory
    - Ensures sufficient planks before crafting
    Returns: List of subtasks to produce bench
    """
    if state.bench.get(ID, 0) >= 1:
        return []
    if state.plank.get(ID, 0) < 4:
        return [('produce', ID, 'plank'), ('produce', ID, 'bench')]
    return [('op_craft_bench', ID)]

def produce_wooden_axe(state, ID):
    """
    Wooden axe production strategy
    - Ensures all prerequisites (bench, sticks, planks) before crafting
    Returns: List of subtasks to produce wooden_axe
    """
    return [('have_enough', ID, 'bench', 1),
            ('have_enough', ID, 'stick', 2),
            ('have_enough', ID, 'plank', 3),
            ('op_craft_wooden_axe', ID)]

def produce(state, ID, item):
    """
    Generic production method that routes to specific production methods
    based on item type. Acts as a dispatcher for the planner.
    Returns: List of subtasks for the requested item
    """
    method_map = {
        'wood': produce_wood,
        'plank': produce_plank,
        'stick': produce_stick,
        'bench': produce_bench,
        'wooden_axe': produce_wooden_axe
    }
    if item in method_map:
        result = method_map[item](state, ID)
        # Handle empty list (success) case explicitly
        if result is not False:
            return result
        else:
            return False
    return False

def check_enough(state, ID, item, num):
    """
    Utility method to verify resource availability
    - Checks if we have enough of an item
    - Triggers production if we don't
    Returns: Empty list if sufficient, otherwise production subtasks
    """
    if state.__dict__[item].get(ID, 0) >= num:
        return []
    if state.time.get(ID, 0) < 4:
        return False
    return [('produce', ID, item)]

# Register methods with the planner
pyhop.declare_methods('produce', produce)
pyhop.declare_methods('have_enough', check_enough)

# Initial State
state = pyhop.State('state')
state.stone_axe   = {'agent': 0}
state.wood        = {'agent': 0}
state.plank       = {'agent': 0}
state.stick       = {'agent': 0}
state.bench       = {'agent': 0}
state.wooden_axe  = {'agent': 0}
state.time        = {'agent': 46}  # Time limit for the task

# Define goal: obtain 12 wood within time limit
goal = [('have_enough', 'agent', 'wood', 12)]

# Run the planner with verbose output for debugging
pyhop.pyhop(state, goal, verbose=3)
