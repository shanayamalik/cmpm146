import pyhop
import json

def check_enough(state, ID, item, num):
    """Check if we have enough of a specific item."""
    if getattr(state, item)[ID] >= num: return []
    return False

def produce_enough(state, ID, item, num):
    """Create tasks to produce an item and verify quantity."""
    return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods('have_enough', check_enough, produce_enough)

def produce(state, ID, item):
    """Create task to produce a specific item."""
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('produce', produce)

def make_method(name, rule):
    """Create HTN method for producing an item based on crafting rules."""
    def method(state, ID):
        # Priority order for materials
        materials_order = ['bench', 'stick', 'plank', 'wood']
        
        # Combine requirements
        requirements = {}
        if 'Requires' in rule:
            requirements.update(rule['Requires'])
        if 'Consumes' in rule:
            requirements.update(rule['Consumes'])
            
        # Create subtasks list
        subtasks = []
        
        # Sort items by priority
        sorted_requirements = sorted(requirements.items(), 
                                  key=lambda x: materials_order.index(x[0]) 
                                  if x[0] in materials_order else len(materials_order))
        
        # Add requirements as subtasks
        for item, amount in sorted_requirements:
            subtasks.append(('have_enough', ID, item, amount))
            
        # Add crafting operation
        subtasks.append((f"op_{name.replace(' ', '_')}", ID))
        
        return subtasks
    return method

def declare_methods(data):
    """Declare crafting methods to pyhop."""
    # Group methods by product
    method_groups = {}
    
    for name, rule in data['Recipes'].items():
        method = make_method(name, rule)
        method.__name__ = name.replace(' ', '_')
        
        # Get product name
        product = list(rule['Produces'].keys())[0]
        method_name = f"produce_{product}"
        
        if method_name not in method_groups:
            method_groups[method_name] = []
        method_groups[method_name].append((method, rule['Time']))
    
    # Declare methods sorted by time
    for method_name, methods in method_groups.items():
        sorted_methods = sorted(methods, key=lambda x: x[1])
        pyhop.declare_methods(method_name, *[m[0] for m in sorted_methods])

def make_operator(rule):
    """Create operator for primitive crafting action."""
    def operator(state, ID):
        # Check time
        if state.time[ID] < rule['Time']:
            return False
            
        # Check requirements
        if 'Requires' in rule:
            for item, amount in rule['Requires'].items():
                if getattr(state, item)[ID] < amount:
                    return False
        
        # Check consumed materials
        if 'Consumes' in rule:
            for item, amount in rule['Consumes'].items():
                if getattr(state, item)[ID] < amount:
                    return False
        
        # Apply time cost
        state.time[ID] -= rule['Time']
        
        # Consume materials
        if 'Consumes' in rule:
            for item, amount in rule['Consumes'].items():
                getattr(state, item)[ID] -= amount
        
        # Produce items
        for item, amount in rule['Produces'].items():
            getattr(state, item)[ID] += amount
            
        return state
    return operator

def declare_operators(data):
    """Declare all operators to pyhop."""
    operators = []
    for name, rule in data['Recipes'].items():
        op = make_operator(rule)
        op.__name__ = f"op_{name.replace(' ', '_')}"
        operators.append(op)
    pyhop.declare_operators(*operators)

def add_heuristic(data, ID):
    """Add search optimization heuristics."""
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # Prevent tool duplication
        if curr_task[0].startswith('produce_') and curr_task[0][8:] in data['Tools']:
            tool = curr_task[0][8:]
            if getattr(state, tool)[ID] > 0:
                return True
                
        # Prevent infinite recursion
        if curr_task in calling_stack[:-1]:
            return True
            
        return False
        
    pyhop.add_check(heuristic)

def set_up_state(data, ID, time=0):
    """Initialize game state."""
    state = pyhop.State('state')
    state.time = {ID: time}
    
    for item in data['Items']:
        setattr(state, item, {ID: 0})
    for item in data['Tools']:
        setattr(state, item, {ID: 0})
    
    # Set initial values from data
    for item, num in data['Initial'].items():
        getattr(state, item)[ID] = num
        
    return state

def set_up_goals(data, ID):
    """Set up planning goals."""
    return [('have_enough', ID, item, num) 
            for item, num in data['Goal'].items()]

if __name__ == '__main__':
    # Load crafting rules
    with open('crafting.json') as f:
        data = json.load(f)
        
    # Set up test case (a)
    test_case = {
        'Initial': {'plank': 1},
        'Goal': {'plank': 1},
        'Time': 0
    }
    
    # Initialize state with test case
    state = set_up_state(data, 'agent', test_case['Time'])
    for item, num in test_case['Initial'].items():
        getattr(state, item)['agent'] = num
        
    # Set up goals
    goals = set_up_goals(test_case, 'agent')
    
    # Initialize planner
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    
    # Run planner
    solution = pyhop.pyhop(state, goals, verbose=3)
    print("Solution found:", solution is not False)
