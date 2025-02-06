import pyhop
import json

def check_enough(state, ID, item, num):
    """Checks if an agent has enough of a specific resource"""
    if getattr(state, item)[ID] >= num: return []
    return False

def produce_enough(state, ID, item, num):
    """Creates tasks to produce and verify required resources"""
    return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods('have_enough', check_enough, produce_enough)

def produce(state, ID, item):
    """Converts general produce tasks into specific item production tasks"""
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('produce', produce)

def make_method(name, rule):
    """Creates a method function for a specific crafting rule"""
    def method(state, ID):
        # Define priority order for optimal crafting
        order = ['bench', 'furnace', 'ingot', 'ore', 'coal', 'cobble', 'stick', 'plank', 'wood', 
                'iron_axe', 'stone_axe', 'wooden_axe', 'iron_pickaxe', 'wooden_pickaxe', 'stone_pickaxe']
        
        # Combine all resource requirements
        needs = {}
        if 'Requires' in rule:
            needs.update(rule['Requires'])
        if 'Consumes' in rule:
            needs.update(rule['Consumes'])
        
        # Create prioritized subtasks
        subtasks = []
        items = sorted(needs.items(), key=lambda x: order.index(x[0]) if x[0] in order else len(order))
        
        for item, amount in items:
            subtasks.append(('have_enough', ID, item, amount))
            
        subtasks.append((("op_" + name).replace(' ', '_'), ID))
        return subtasks
    return method

def declare_methods(data):
    """Declares all crafting methods to pyhop, prioritizing efficient recipes"""
    methods = {}
    
    # Group methods by their products
    for recipe_name, recipe_info in data['Recipes'].items():
        cur_time = recipe_info['Time']
        m = make_method(recipe_name, recipe_info)
        m.__name__ = recipe_name.replace(' ', '_')
        
        cur_m = ("produce_" + list(recipe_info['Produces'].keys())[0]).replace(' ', '_')
        
        if cur_m not in methods:
            methods[cur_m] = [(m, cur_time)]
        else:
            methods[cur_m].append((m, cur_time))
    
    # Declare methods sorted by efficiency
    for m, info in methods.items():
        methods[m] = sorted(info, key=lambda x: x[1])
        pyhop.declare_methods(m, *[method[0] for method in methods[m]])

def make_operator(rule):
    """Creates an operator function from a crafting rule"""
    def operator(state, ID):
        # Check time availability
        if state.time[ID] < rule['Time']:
            return False
            
        # Check tool requirements
        if 'Requires' in rule:
            for item, amount in rule['Requires'].items():
                if getattr(state, item)[ID] < amount:
                    return False
                    
        # Check material requirements
        if 'Consumes' in rule:
            for item, amount in rule['Consumes'].items():
                if getattr(state, item)[ID] < amount:
                    return False
        
        # Execute crafting operation
        state.time[ID] -= rule['Time']
        
        if 'Consumes' in rule:
            for item, amount in rule['Consumes'].items():
                cur_val = getattr(state, item)
                setattr(state, item, {ID: cur_val[ID] - amount})
        
        for item, amount in rule['Produces'].items():
            cur_val = getattr(state, item)
            setattr(state, item, {ID: cur_val[ID] + amount})
            
        return state
    return operator

def declare_operators(data):
    """Creates and declares all operators from crafting rules"""
    ops = []
    for recipe_name, recipe_info in data['Recipes'].items():
        op = make_operator(recipe_info)
        op.__name__ = ("op_" + recipe_name).replace(' ', '_')
        ops.append(op)
    pyhop.declare_operators(*ops)

def add_heuristic(data, ID):
    """Adds optimization heuristics to guide the planning process"""
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # Prevent duplicate tool creation
        if curr_task[0] == 'produce' and curr_task[2] in data['Tools']:
            if getattr(state, curr_task[2])[ID] > 0:
                return True
                
        # Optimize wooden axe creation
        if curr_task[0] == 'produce_wooden_axe':
            wood_needed = sum([task[3] for task in tasks if len(task) > 3 and task[2] == 'wood'])
            if wood_needed < 5 and 'wooden_axe' not in data['Goal']:
                return True
                
        # Optimize stone pickaxe creation
        if curr_task[0] == 'produce_stone_pickaxe':
            if 'stone_pickaxe' not in data['Goal']:
                cobble_needed = sum([task[3] for task in tasks if len(task) > 3 and task[2] == 'cobble'])
                if cobble_needed < 5:
                    return True
                    
        # Prevent infinite tool requirement cycles
        if curr_task[0] == 'have_enough' and curr_task[2] in data['Tools']:
            if tasks.count(curr_task) > 1:
                return True
                
        return False

    pyhop.add_check(heuristic)

def set_up_state(data, ID, time=0):
    """Initializes the game state with given parameters"""
    state = pyhop.State('state')
    state.time = {ID: time}

    for item in data['Items']:
        setattr(state, item, {ID: 0})

    for item in data['Tools']:
        setattr(state, item, {ID: 0})

    for item, num in data['Initial'].items():
        setattr(state, item, {ID: num})

    return state

def set_up_goals(data, ID):
    """Converts goal requirements into planner tasks"""
    goals = []
    for item, num in data['Goal'].items():
        goals.append(('have_enough', ID, item, num))

    return goals

if __name__ == '__main__':
    # Load crafting rules
    with open('crafting.json') as f:
        data = json.load(f)
        
    # Define simpler test case
    test_case = {
        'name': 'Complex Test Case',
        'Initial': {},
        'Goal': {
            'cart': 1,         # Reduced to one cart
            'rail': 28,        # Keep rail requirement
            'iron_pickaxe': 1  # Only one high-tier tool
        },
        'Time': 300
    }
    
    print(f"\nRunning {test_case['name']}")
    print(f"Initial: {test_case['Initial']}")
    print(f"Goal: {test_case['Goal']}")
    print("-"*50)
    
    # Set up planner state and goals
    state = set_up_state(data, 'agent', test_case['Time'])
    data['Goal'] = test_case['Goal']
    goals = [('have_enough', 'agent', item, num) 
             for item, num in test_case['Goal'].items()]
    
    # Initialize planner components
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    
    # Run planner with minimal verbose output to improve speed
    solution = pyhop.pyhop(state, goals, verbose=0)
    print(f"Solution found: {solution is not False}")
    if solution:
        print("Plan length:", len(solution))
