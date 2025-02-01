import pyhop
import json

def make_operator(recipe_name, rule):
    """Creates an operator function from a crafting rule"""
    def operator(state, ID):
        # Check time
        if state.time.get(ID, 0) < rule["Time"]:
            return False
            
        # Check requirements
        if "Requires" in rule:
            for item, qty in rule["Requires"].items():
                if getattr(state, item).get(ID, 0) < qty:
                    return False
                    
        # Check consumables
        if "Consumes" in rule:
            for item, qty in rule["Consumes"].items():
                if getattr(state, item).get(ID, 0) < qty:
                    return False
        
        # Create new state
        state.time[ID] -= rule["Time"]
        
        # Handle consumption
        if "Consumes" in rule:
            for item, qty in rule["Consumes"].items():
                getattr(state, item)[ID] -= qty
                
        # Handle production
        for item, qty in rule["Produces"].items():
            if not hasattr(state, item):
                setattr(state, item, {})
            current = getattr(state, item).get(ID, 0)
            getattr(state, item)[ID] = current + qty
            
        return state
    
    operator.__name__ = "op_" + recipe_name.replace(" ", "_")
    return operator

def make_method(recipe_name, rule):
    """Creates a method function to decompose tasks into subtasks"""
    produced_item = list(rule["Produces"].keys())[0]
    
    def method(state, ID, item):
        if item != produced_item:
            return False
            
        subtasks = []
        
        # Add requirements
        if "Requires" in rule:
            for item, qty in rule["Requires"].items():
                subtasks.append(('have_enough', ID, item, qty))
                
        # Add consumables
        if "Consumes" in rule:
            for item, qty in rule["Consumes"].items():
                subtasks.append(('have_enough', ID, item, qty))
                
        # Add operation
        subtasks.append((f"op_{recipe_name.replace(' ', '_')}", ID))
        
        return subtasks
        
    method.__name__ = f"produce_{produced_item}_{recipe_name.replace(' ', '_')}"
    return method

def declare_operators(data):
    """Declares all operators from recipes"""
    operators = []
    for recipe_name, recipe in data["Recipes"].items():
        op = make_operator(recipe_name, recipe)
        operators.append(op)
    pyhop.declare_operators(*operators)

def declare_methods(data):
    """Declares all methods from recipes"""
    methods = []
    for recipe_name, recipe in data["Recipes"].items():
        if len(recipe["Produces"]) == 1:
            method = make_method(recipe_name, recipe)
            methods.append(method)
    
    # Sort methods to prefer simpler recipes first
    methods.sort(key=lambda m: "punch" in m.__name__, reverse=True)
    pyhop.declare_methods("produce", *methods)

def check_enough(state, ID, item, num):
    """Checks if we have enough of an item"""
    if not hasattr(state, item):
        return [('produce', ID, item)]
    if getattr(state, item).get(ID, 0) >= num:
        return []
    return [('produce', ID, item)]

def add_heuristic(data, ID):
    """Adds a heuristic to prevent infinite recursion"""
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        if state.time.get(ID, 0) < 0:
            return True
        if depth > 30:  # Prevent too much recursion
            return True
        return False
    pyhop.add_check(heuristic)

pyhop.declare_methods('have_enough', check_enough)

if __name__ == '__main__':
    with open('crafting.json') as f:
        data = json.load(f)
        
    print("\nTesting case (b): Given {}, achieve {'plank': 1} [time <= 300]")
    
    state = pyhop.State('state')
    state.time = {'agent': 300}
    state.wood = {'agent': 0}
    state.plank = {'agent': 0}
    
    goals = [('have_enough', 'agent', 'plank', 1)]
    
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    
    pyhop.pyhop(state, goals, verbose=3)
