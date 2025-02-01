import pyhop
import json

def make_operator(recipe_name, rule):
    def operator(state, ID):
        if state.time.get(ID, 0) < rule.get("Time", 0):
            return False
            
        if "Requires" in rule:
            for item, qty in rule["Requires"].items():
                if getattr(state, item).get(ID, 0) < qty:
                    return False
                    
        if "Consumes" in rule:
            for item, qty in rule["Consumes"].items():
                if getattr(state, item).get(ID, 0) < qty:
                    return False

        state.time[ID] -= rule.get("Time", 0)
        
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

def produce_method(state, ID, item):
    """Generic production method"""
    for recipe_name, recipe in RECIPES.items():
        if item in recipe["Produces"]:
            subtasks = []
            if "Requires" in recipe:
                for req_item, qty in recipe["Requires"].items():
                    subtasks.append(('have_enough', ID, req_item, qty))
            if "Consumes" in recipe:
                for cons_item, qty in recipe["Consumes"].items():
                    subtasks.append(('have_enough', ID, cons_item, qty))
            subtasks.append((f"op_{recipe_name.replace(' ', '_')}", ID))
            return subtasks
    return False

def declare_operators(data):
    global RECIPES
    RECIPES = data["Recipes"]
    operators = []
    for name, recipe in data["Recipes"].items():
        op = make_operator(name, recipe)
        operators.append(op)
    pyhop.declare_operators(*operators)

def check_enough(state, ID, item, num):
    if not hasattr(state, item):
        setattr(state, item, {ID: 0})
    if getattr(state, item).get(ID, 0) >= num:
        return []
    return [('produce', ID, item)]

def add_heuristic(data, ID):
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        if depth > 50:
            return True
        if state.time.get(ID, 0) < 0:
            return True
        
        # Track tool progression
        tools = []
        for task in calling_stack:
            task_str = str(task)
            if 'wooden' in task_str:
                tools.append('wooden')
            elif 'stone' in task_str:
                tools.append('stone')
            elif 'iron' in task_str:
                tools.append('iron')
                
        if 'iron' in tools and not ('wooden' in tools and 'stone' in tools):
            return True
            
        return False
        
    pyhop.add_check(heuristic)

pyhop.declare_methods('have_enough', check_enough)
pyhop.declare_methods('produce', produce_method)

if __name__ == '__main__':
    with open('crafting.json') as f:
        data = json.load(f)
        
    state = pyhop.State('state')
    state.time = {'agent': 100}
    
    # Initialize all items and tools
    for item in data["Items"]:
        setattr(state, item, {'agent': 0})
    for tool in data["Tools"]:
        setattr(state, tool, {'agent': 0})
    
    goals = [('have_enough', 'agent', 'iron_pickaxe', 1)]
    
    declare_operators(data)
    add_heuristic(data, 'agent')
    
    pyhop.pyhop(state, goals, verbose=3)
