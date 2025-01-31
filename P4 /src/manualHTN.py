import pyhop

'''begin operators'''
def op_punch_for_wood(state, ID):
    if state.time[ID] >= 4:
        state.wood[ID] += 1
        state.time[ID] -= 4
        return state
    return False

pyhop.declare_operators(op_punch_for_wood)
'''end operators'''

def check_enough(state, ID, item, num):
    if getattr(state, item)[ID] >= num:
        return []
    return False

def produce_enough(state, ID, item, num):
    # Calculate how much more we need
    current = getattr(state, item)[ID]
    needed = num - current
    
    # For wood, check if we have enough time
    if item == 'wood':
        time_needed = needed * 4  # 4 time units per wood
        if state.time[ID] < time_needed:
            return False
            
    return [('produce', ID, item), ('have_enough', ID, item, num)]

def produce(state, ID, item):
    if item == 'wood':
        return [('produce_wood', ID)]
    return False

def punch_for_wood(state, ID):
    return [('op_punch_for_wood', ID)]

# Declare methods
pyhop.declare_methods('have_enough', check_enough, produce_enough)
pyhop.declare_methods('produce', produce)
pyhop.declare_methods('produce_wood', punch_for_wood)

# declare state
state = pyhop.State('state')
state.wood = {'agent': 0}
state.time = {'agent': 48}  # Increased time slightly to ensure we can get all 12 wood

# Try to get 12 wood
pyhop.pyhop(state, [('have_enough', 'agent', 'wood', 12)], verbose=3)
