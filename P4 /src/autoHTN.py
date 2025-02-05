import pyhop
import json

def check_enough(state, ID, item, num):
    """Check if we have enough of a specific item."""
    if getattr(state, item)[ID] >= num: return []
    return False

def produce_enough(state, ID, item, num):
    """Creates a sequence of tasks to produce an item and verify we have enough."""
    return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods('have_enough', check_enough, produce_enough)

def produce(state, ID, item):
    """Creates a task to produce a specific item."""
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('produce', produce)

def make_method(name, rule):
    """Creates an HTN method for producing an item based on crafting rules."""
    def method(state, ID):
        # Priority order for materials
        order = ['bench', 'furnace', 'ingot', 'ore', 'coal', 'cobble', 
                'stick', 'plank', 'wood', 'iron_axe', 'stone_axe', 
                'wooden_axe', 'iron_pickaxe', 'wooden_pickaxe', 'stone_pickaxe']
        
        # Combine requirements
        needs = {}
        if 'Requires' in rule:
            needs.update(rule['Requires'])
        if 'Consumes' in rule:
            needs.update(rule['Consumes'])
        
        # Sort items by priority
        items = sorted(needs.items(), 
                      key=lambda x: order.index(x[0]) if x[0] in order 
                      else len(order))
        
        # Build subtasks
        subtasks = []
        for item, amount in items:
            subtasks.append(('have_enough', ID, item, amount))
        
        # Add the crafting operation
        subtasks.append((f"op_{name.replace(' ', '_')}", ID))
        
        return subtasks
    return method

def declare_methods(data):
    """Declares all crafting methods to pyhop."""
    methods = {}
    
    for name, rule in data['Recipes'].items():
        m = make_method(name, rule)
        m.__name__ = name.replace(' ', '_')
        
        # Group methods by what they produce
        product = list(rule['Produces'].keys())[0]
        method_name = f"produce_{product}"
        
        if method_name not in methods:
            methods[method_name] = [(m, rule['Time'])]
        else:
            methods[method_name].append((m, rule['Time']))
    
    # Declare methods, faster ones first
    for method_name, method_list in methods.items():
        sorted_methods = sorted(method_list, key=lambda x: x[1])
        pyhop.declare_methods(method_name, *[m[0] for m in sorted_methods])

def make_operator(rule):
    """Creates a pyhop operator for primitive crafting actions."""
    def operator(state, ID):
        # Check time
        if state.time[ID] < rule['Time']:
            return False
        
        # Check required tools
        if 'Requires' in rule:
            for item, amount in rule['Requires'].items():
                if getattr(state, item)[ID] < amount:
                    return False
        
        # Check materials
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
    """Declares all operators to pyhop."""
    operators = []
    for name, rule in data['Recipes'].items():
        op = make_operator(rule)
        op.__name__ = f"op_{name.replace(' ', '_')}"
        operators.append(op)
    pyhop.declare_operators(*operators)

def add_heuristic(data, ID):
    """Adds search optimization heuristics."""
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # Prevent duplicate tool creation
        if curr_task[0] == 'produce' and curr_task[2] in data['Tools']:
            if getattr(state, curr_task[2])[ID] > 0:
                return True
        
        # Don't make wooden_axe for small wood tasks
        if curr_task[0] == 'produce_wooden_axe':
            wood_needed = sum(task[3] for task in tasks 
                            if len(task) > 3 and task[2] == 'wood')
            if wood_needed < 5 and 'wooden_axe' not in data['Goal']:
                return True
        
        # Prevent cycles in tool requirements
        if curr_task[0] == 'have_enough' and curr_task[2] in data['Tools']:
            if tasks.count(curr_task) > 1:
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
    
    for item, num in data['Initial'].items():
        getattr(state, item)[ID] = num
    
    return state

def set_up_goals(data, ID):
    """Set up planning goals."""
    return [('have_enough', ID, item, num) 
            for item, num in data['Goal'].items()]

if __name__ == '__main__':
    with open('crafting.json') as f:
        data = json.load(f)
    
    state = set_up_state(data, 'agent', time=300)  # Set time for test case b
    goals = set_up_goals(data, 'agent')
    
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    
    solution = pyhop.pyhop(state, goals, verbose=3)
    print("\nSolution found:", solution is not False)
    if solution:
        print("\nPlan:")
        for step in solution:
            print(f"  {step}")
