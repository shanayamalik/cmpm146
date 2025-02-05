import pyhop
import json

def check_enough(state, ID, item, num):
    if getattr(state, item)[ID] >= num: return []
    return False

def produce_enough(state, ID, item, num):
    return [('produce', ID, item), ('have_enough', ID, item, num)]

pyhop.declare_methods('have_enough', check_enough, produce_enough)

def produce(state, ID, item):
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('produce', produce)

def make_method(name, rule):
    def method(state, ID):
        # Updated priority order to match working version
        order = ['bench', 'furnace', 'ingot', 'ore', 'coal', 'cobble', 'stick', 'plank', 'wood',
                'iron_axe', 'stone_axe', 'wooden_axe', 'iron_pickaxe', 'wooden_pickaxe', 'stone_pickaxe']
        
        # Use dict union operator for Python 3.9+
        needs = rule.get('Requires', {}) | rule.get('Consumes', {})
        
        subtasks = []
        
        # Sort by order list index
        items = sorted(needs.items(), key=lambda x: order.index(x[0]) if x[0] in order else len(order))
        
        for item, amount in items:
            subtasks.append(('have_enough', ID, item, amount))
            
        subtasks.append((f"op_{name.replace(' ', '_')}", ID))
        return subtasks
    return method

def declare_methods(data):
    methods = {}
    
    for name, rule in data['Recipes'].items():
        m = make_method(name, rule)
        m.__name__ = name.replace(' ', '_')
        
        product = list(rule['Produces'].keys())[0]
        method_name = f"produce_{product}"
        
        if method_name not in methods:
            methods[method_name] = [(m, rule.get('Time', 0))]
        else:
            methods[method_name].append((m, rule.get('Time', 0)))
    
    for method_name, method_list in methods.items():
        sorted_methods = sorted(method_list, key=lambda x: x[1])
        pyhop.declare_methods(method_name, *[m[0] for m in sorted_methods])

def make_operator(rule):
    def operator(state, ID):
        # Check time constraint
        if state.time[ID] < rule['Time']:
            return False
            
        # Check required tools
        if 'Requires' in rule:
            for item, amount in rule['Requires'].items():
                if getattr(state, item)[ID] < amount:
                    return False
                    
        # Check consumables
        if 'Consumes' in rule:
            for item, amount in rule['Consumes'].items():
                if getattr(state, item)[ID] < amount:
                    return False
        
        # Update state - deduct time first
        state.time[ID] -= rule['Time']
        
        # Consume materials
        if 'Consumes' in rule:
            for item, amount in rule['Consumes'].items():
                cur_val = getattr(state, item)
                setattr(state, item, {ID: cur_val[ID] - amount})
        
        # Produce items
        for item, amount in rule['Produces'].items():
            cur_val = getattr(state, item)
            setattr(state, item, {ID: cur_val[ID] + amount})
            
        return state
    return operator

def declare_operators(data):
    ops = []
    for name, rule in data['Recipes'].items():
        op = make_operator(rule)
        op.__name__ = f"op_{name.replace(' ', '_')}"
        ops.append(op)
    pyhop.declare_operators(*ops)

def add_heuristic(data, ID):
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # Prevent duplicate tool creation
        if curr_task[0] == 'produce' and curr_task[2] in data['Tools']:
            if getattr(state, curr_task[2])[ID] > 0:
                return True
                
        # Don't make wooden axe unless needed for large wood quantities
        if curr_task[0] == 'produce_wooden_axe':
            wood_needed = sum([task[3] for task in tasks if len(task) > 3 and task[2] == 'wood'])
            if wood_needed < 5 and 'wooden_axe' not in data.get('Goal', {}):
                return True
                
        # Prevent infinite cycles in tool requirements
        if curr_task[0] == 'have_enough' and curr_task[2] in data['Tools']:
            if tasks.count(curr_task) > 1:
                return True
                
        return False
    
    pyhop.add_check(heuristic)

def set_up_state(data, test_case, ID):
    state = pyhop.State('state')
    state.time = {ID: test_case.get('Time', 0)}
    
    # Initialize everything to zero
    for item in data['Items']:
        setattr(state, item, {ID: 0})
    for item in data['Tools']:
        setattr(state, item, {ID: 0})
    
    # Set initial values
    for item, num in test_case['Initial'].items():
        setattr(state, item, {ID: num})
    
    return state

def set_up_goals(test_case, ID):
    return [('have_enough', ID, item, num) 
            for item, num in test_case['Goal'].items()]

if __name__ == '__main__':
    # Load crafting rules
    with open('crafting.json') as f:
        data = json.load(f)
    
    # Test case C
    test_case = {
        'Initial': {'plank': 3, 'stick': 2},
        'Goal': {'wooden_pickaxe': 1},
        'Time': 10
    }
    
    state = set_up_state(data, test_case, 'agent')
    data['Goal'] = test_case['Goal']  # Important for heuristic
    goals = set_up_goals(test_case, 'agent')
    
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    
    solution = pyhop.pyhop(state, goals, verbose=3)
    print("\nSolution found:", solution is not False)
    if solution:
        print("\nPlan:")
        for step in solution:
            print(f"  {step}")
