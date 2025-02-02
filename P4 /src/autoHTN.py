import pyhop
import json

def make_operator(recipe_name, rule):
    def operator(state, ID):
        if state.time.get(ID, 0) < rule["Time"]:
            return False
            
        if "Requires" in rule:
            for item, qty in rule["Requires"].items():
                if getattr(state, item).get(ID, 0) < qty:
                    return False
                    
        if "Consumes" in rule:
            for item, qty in rule["Consumes"].items():
                if getattr(state, item).get(ID, 0) < qty:
                    return False
        
        state.time[ID] -= rule["Time"]
        
        if "Consumes" in rule:
            for item, qty in rule["Consumes"].items():
                getattr(state, item)[ID] -= qty
                
        for item, qty in rule["Produces"].items():
            if not hasattr(state, item):
                setattr(state, item, {})
            current = getattr(state, item).get(ID, 0)
            getattr(state, item)[ID] = current + qty
            
        return state
    
    operator.__name__ = "op_" + recipe_name.replace(" ", "_")
    return operator

def declare_operators(data):
    operators = []
    for recipe_name, recipe in data["Recipes"].items():
        op = make_operator(recipe_name, recipe)
        operators.append(op)
    pyhop.declare_operators(*operators)

def get_recipe_methods(recipe_name, recipe):
    def method(state, ID):
        subtasks = []
        
        # Check if we already have the required tools
        if "Requires" in recipe:
            for item, qty in recipe["Requires"].items():
                if getattr(state, item).get(ID, 0) < qty:
                    subtasks.append(('have_enough', ID, item, qty))
                    
        # Get consumed materials
        if "Consumes" in recipe:
            for item, qty in recipe["Consumes"].items():
                if getattr(state, item).get(ID, 0) < qty:
                    subtasks.append(('have_enough', ID, item, qty))
                    
        subtasks.append((f"op_{recipe_name.replace(' ', '_')}", ID))
        return subtasks
        
    return method

def check_enough(state, ID, item, num):
    if not hasattr(state, item):
        setattr(state, item, {ID: 0})
    if getattr(state, item).get(ID, 0) >= num:
        return []
    return [('produce', ID, item)]

def check_enough_punch(state, ID, item, num):
    """Special method for getting basic wood"""
    if item == 'wood':
        return [('op_punch_for_wood', ID)]
    return False

def check_enough_wood_tools(state, ID, item, num):
    """Method for using wooden tools"""
    if item == 'wood' and state.wooden_axe.get(ID, 0) > 0:
        return [('op_wooden_axe_for_wood', ID)]
    return False

def get_methods(recipe_name, recipe):
    methods = []
    produced_items = recipe["Produces"].keys()
    for item in produced_items:
        method = get_recipe_methods(recipe_name, recipe)
        method.__name__ = f"produce_{item}_{recipe_name.replace(' ', '_')}"
        methods.append((item, method))
    return methods

def declare_methods(data):
    # Organize recipes by what they produce
    item_methods = {}
    for recipe_name, recipe in data["Recipes"].items():
        for item, method in get_methods(recipe_name, recipe):
            if item not in item_methods:
                item_methods[item] = []
            item_methods[item].append(method)
            
    # Handle wood gathering methods
    pyhop.declare_methods('have_enough', 
                        check_enough_punch,
                        check_enough_wood_tools,
                        check_enough)
    
    # Create specific methods for each item
    for item, methods in item_methods.items():
        for method in methods:
            pyhop.declare_methods(f'produce_{item}', method)
            
    # Create general produce method
    def general_produce(state, ID, item):
        if item == 'wood' and state.wooden_axe.get(ID, 0) == 0:
            return [('op_punch_for_wood', ID)]
        if item == 'plank':
            return [('have_enough', ID, 'wood', 1), ('op_craft_plank', ID)]
        if item == 'bench':
            return [('have_enough', ID, 'plank', 4), ('op_craft_bench', ID)]
        return [(f'produce_{item}', ID)]
        
    pyhop.declare_methods('produce', general_produce)

def add_heuristic(data, ID):
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # Stop if we exceed depth or time
        if depth > 20:  # Increased depth limit for more complex tasks
            return True
        if state.time.get(ID, 0) < 0:
            return True
            
        # Track recipe attempts
        if not hasattr(state, 'attempts'):
            state.attempts = {ID: {}}
            
        task_str = str(curr_task)
        if task_str in state.attempts.get(ID, {}):
            if state.attempts[ID][task_str] > 2:
                return True
            state.attempts[ID][task_str] += 1
        else:
            state.attempts[ID][task_str] = 1
            
        return False
        
    pyhop.add_check(heuristic)

if __name__ == '__main__':
    with open('crafting.json') as f:
        data = json.load(f)
        
    state = pyhop.State('state')
    state.time = {'agent': 175}
    
    # Initialize all required items
    for item in ['cart', 'rail', 'ingot', 'ore', 'coal', 'cobble', 'wood', 'plank', 
                'stick', 'bench', 'furnace', 'wooden_pickaxe', 'stone_pickaxe', 
                'iron_pickaxe', 'wooden_axe', 'stone_axe', 'iron_axe']:
        setattr(state, item, {'agent': 0})
    
    # Define goals - building up incrementally
    goals = [
        ('have_enough', 'agent', 'bench', 1)  # Need wood -> planks -> bench
    ]
    
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    
    print("\nTrying to craft a bench...")
    plan = pyhop.pyhop(state, goals, verbose=3)
    
    if plan:
        print("\nPlan found:")
        for step in plan:
            print(step)
            
        # Verify the plan works
        print("\nVerifying plan...")
        final_state = state
        for step in plan:
            operator = step[0]
            # Find and execute the operator
            for op in pyhop.operators.values():
                if op.__name__ == operator:
                    final_state = op(final_state, 'agent')
                    break
                    
        print("\nFinal state:")
        print(f"Time remaining: {final_state.time['agent']}")
        print(f"Bench: {final_state.bench['agent']}")
        print(f"Wood: {final_state.wood['agent']}")
        print(f"Plank: {final_state.plank['agent']}")
    else:
        print("\nNo plan found.")
