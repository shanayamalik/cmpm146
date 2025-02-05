
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
        # Define priority order for gathering materials
        order = ['bench', 'furnace', 'ingot', 'ore', 'coal', 'cobble', 'stick', 'plank', 'wood', 
                'iron_axe', 'stone_axe', 'wooden_axe', 'iron_pickaxe', 'wooden_pickaxe', 'stone_pickaxe']
        
        # Combine both required tools and consumed materials
        needs = rule.get('Requires', {}) | rule.get('Consumes', {})
        
        # Create list to store subtasks
        subtasks = []
        
        # Sort items by their priority in the order list
        items = sorted(needs.items(), key=lambda x: order.index(x[0]) if x[0] in order else len(order))
        
        # Add subtask for each required item
        for item, amount in items:
            subtasks.append(('have_enough', ID, item, amount))
            
        # Finally, add the actual crafting operation
        subtasks.append((("op_" + name).replace(' ', '_'), ID))
        
        return subtasks
    return method

def declare_methods(data):
    # Dictionary to store methods grouped by product
    methods = {}
    
    # Process each recipe
    for recipe_name, recipe_info in data['Recipes'].items():
        cur_time = recipe_info['Time']
        m = make_method(recipe_name, recipe_info)
        m.__name__ = recipe_name.replace(' ', '_')
        
        # Get the product name from the recipe
        cur_m = ("produce_" + list(recipe_info['Produces'].keys())[0]).replace(' ', '_')
        
        # Group methods by what they produce
        if cur_m not in methods:
            methods[cur_m] = [(m, cur_time)]
        else:
            methods[cur_m].append((m, cur_time))
    
    # Declare methods to pyhop, sorted by time (faster methods first)
    for m, info in methods.items():
        methods[m] = sorted(info, key=lambda x: x[1])
        pyhop.declare_methods(m, *[method[0] for method in methods[m]])

def make_operator(rule):
    def operator(state, ID):
        # First check: Do we have enough time?
        if state.time[ID] < rule['Time']:
            return False
            
        # Second check: Do we have required tools?
        if 'Requires' in rule:
            for item, amount in rule['Requires'].items():
                if getattr(state, item)[ID] < amount:
                    return False
                    
        # Third check: Do we have materials to consume?
        if 'Consumes' in rule:
            for item, amount in rule['Consumes'].items():
                if getattr(state, item)[ID] < amount:
                    return False
        
        # If all checks pass, execute the crafting:
        
        # 1. Use up time
        state.time[ID] -= rule['Time']
        
        # 2. Consume materials
        if 'Consumes' in rule:
            for item, amount in rule['Consumes'].items():
                cur_val = getattr(state, item)
                setattr(state, item, {ID: cur_val[ID] - amount})
        
        # 3. Produce new items
        for item, amount in rule['Produces'].items():
            cur_val = getattr(state, item)
            setattr(state, item, {ID: cur_val[ID] + amount})
            
        return state
    return operator

def declare_operators(data):
    ops = []
    for recipe_name, recipe_info in data['Recipes'].items():
        op = make_operator(recipe_info)
        op.__name__ = ("op_" + recipe_name).replace(' ', '_')
        ops.append(op)
    pyhop.declare_operators(*ops)

def add_heuristic(data, ID):
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # 1. Prevent duplicate tool creation
        if curr_task[0] == 'produce' and curr_task[2] in data['Tools']:
            if getattr(state, curr_task[2])[ID] > 0:
                return True
                
        # 2. Optimize wood gathering (don't make axe unless needed)
        if curr_task[0] == 'produce_wooden_axe':
            wood_needed = sum([task[3] for task in tasks if len(task) > 3 and task[2] == 'wood'])
            if wood_needed < 5 and 'wooden_axe' not in data['Goal']:
                return True
                
        # 3. Optimize stone pickaxe creation
        if curr_task[0] == 'produce_stone_pickaxe':
            if 'stone_pickaxe' not in data['Goal']:
                cobble_needed = sum([task[3] for task in tasks if len(task) > 3 and task[2] == 'cobble'])
                if cobble_needed < 5:
                    return True
                    
        # 4. Prevent infinite cycles in tool requirements
        if curr_task[0] == 'have_enough' and curr_task[2] in data['Tools']:
            if tasks.count(curr_task) > 1:
                return True
                
        return False
    
    pyhop.add_check(heuristic)

def set_up_state(data, test_case, ID, time=0):
    state = pyhop.State('state')
    state.time = {ID: test_case.get('Time', time)}
    
    # Initialize everything to zero first
    for item in data['Items']:
        setattr(state, item, {ID: 0})
    for item in data['Tools']:
        setattr(state, item, {ID: 0})
    
    # Set initial quantities from test case
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
    
    # Test case E
    test_case = {
        'Initial': {},
        'Goal': {'cart': 1, 'rail': 10},
        'Time': 175
    }
    
    state = set_up_state(data, test_case, 'agent', test_case['Time'])
    data['Goal'] = test_case['Goal']
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
