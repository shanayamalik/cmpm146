#!/usr/bin/env python
import pyhop

# OPERATORS

def op_punch_for_wood(state, ID):
    # Produces 1 wood; costs 4 time.
    if state.time.get(ID, 0) >= 4:
        state.wood[ID] = state.wood.get(ID, 0) + 1
        state.time[ID] -= 4
        return state
    return False

def op_craft_plank(state, ID):
    # Consumes 1 wood; produces 4 planks; costs 1 time.
    if state.wood.get(ID, 0) >= 1:
        state.plank[ID] = state.plank.get(ID, 0) + 4
        state.wood[ID] -= 1
        state.time[ID] -= 1
        return state
    return False

def op_craft_stick(state, ID):
    # Consumes 2 planks; produces 4 sticks; costs 1 time.
    if state.plank.get(ID, 0) >= 2:
        state.stick[ID] = state.stick.get(ID, 0) + 4
        state.plank[ID] -= 2
        state.time[ID] -= 1
        return state
    return False

def op_craft_bench(state, ID):
    # Consumes 4 planks; produces 1 bench; costs 1 time.
    if state.plank.get(ID, 0) >= 4:
        state.bench[ID] = state.bench.get(ID, 0) + 1
        state.plank[ID] -= 4
        state.time[ID] -= 1
        return state
    return False

def op_craft_wooden_axe(state, ID):
    # Requires 3 planks, 2 sticks, and 1 bench; costs 1 time.
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
    # Produces 1 wood; costs 2 time; requires an axe.
    if state.time.get(ID, 0) >= 2 and state.wooden_axe.get(ID, 0) >= 1:
        state.wood[ID] = state.wood.get(ID, 0) + 1
        state.time[ID] -= 2
        return state
    return False

pyhop.declare_operators(op_punch_for_wood, op_craft_plank, op_craft_stick,
                        op_craft_bench, op_craft_wooden_axe, op_chop_for_wood)

# METHODS

def produce_wood(state, ID):
    # If we already have 12 wood, we are done.
    if state.wood.get(ID, 0) >= 12:
        return []
    # Force production of the axe first.
    if state.wooden_axe.get(ID, 0) < 1:
        return [('produce', ID, 'wooden_axe'),
                ('produce', ID, 'wood')]
    # With an axe, use the fast chop operator.
    if state.time.get(ID, 0) >= 2:
        return [('op_chop_for_wood', ID),
                ('produce', ID, 'wood')]
    if state.time.get(ID, 0) >= 4:
        return [('op_punch_for_wood', ID),
                ('produce', ID, 'wood')]
    return False

def produce_plank(state, ID):
    # If no wood is available, get wood by punching then craft a plank.
    if state.wood.get(ID, 0) < 1:
        return [('op_punch_for_wood', ID),
                ('op_craft_plank', ID)]
    return [('op_craft_plank', ID)]

def produce_stick(state, ID):
    # Ensure at least 2 planks exist before crafting sticks.
    return [('have_enough', ID, 'plank', 2),
            ('op_craft_stick', ID)]

def produce_bench(state, ID):
    if state.bench.get(ID, 0) >= 1:
        return []
    if state.plank.get(ID, 0) < 4:
        # Produce enough planks first, then try producing the bench.
        return [('produce', ID, 'plank'), ('produce', ID, 'bench')]
    return [('op_craft_bench', ID)]

def produce_wooden_axe(state, ID):
    # Force production of bench, sticks, and planks before crafting the axe.
    return [('have_enough', ID, 'bench', 1),
            ('have_enough', ID, 'stick', 2),
            ('have_enough', ID, 'plank', 3),
            ('op_craft_wooden_axe', ID)]

def produce(state, ID, item):
    method_map = {
        'wood': produce_wood,
        'plank': produce_plank,
        'stick': produce_stick,
        'bench': produce_bench,
        'wooden_axe': produce_wooden_axe
    }
    if item in method_map:
        result = method_map[item](state, ID)
        # An empty list [] is a valid (successful) result, so check explicitly.
        if result is not False:
            return result
        else:
            return False
    return False

def check_enough(state, ID, item, num):
    if state.__dict__[item].get(ID, 0) >= num:
        return []
    if state.time.get(ID, 0) < 4:
        return False
    return [('produce', ID, item)]

pyhop.declare_methods('produce', produce)
pyhop.declare_methods('have_enough', check_enough)

# INITIAL STATE

state = pyhop.State('state')
state.stone_axe   = {'agent': 0}
state.wood        = {'agent': 0}
state.plank       = {'agent': 0}
state.stick       = {'agent': 0}
state.bench       = {'agent': 0}
state.wooden_axe  = {'agent': 0}
state.time        = {'agent': 46}

goal = [('have_enough', 'agent', 'wood', 12)]

pyhop.pyhop(state, goal, verbose=3)
