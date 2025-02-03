
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

def make_method(recipe_name, rule):
    produced_item = list(rule["Produces"].keys())[0]
    
    def method(state, ID, item):
        if item != produced_item:
            return False
            
        subtasks = []
        
        if "Requires" in rule:
            for item, qty in rule["Requires"].items():
                subtasks.append(('have_enough', ID, item, qty))
                
        if "Consumes" in rule:
            for item, qty in rule["Consumes"].items():
                subtasks.append(('have_enough', ID, item, qty))
                
        subtasks.append((f"op_{recipe_name.replace(' ', '_')}", ID))
        
        return subtasks
        
    method.__name__ = f"produce_{produced_item}_{recipe_name.replace(' ', '_')}"
    return method

def declare_operators(data):
    operators = []
    for recipe_name, recipe in data["Recipes"].items():
        op = make_operator(recipe_name, recipe)
        operators.append(op)
    pyhop.declare_operators(*operators)

def declare_methods(data):
    methods = []
    for recipe_name, recipe in data["Recipes"].items():
        if len(recipe["Produces"]) == 1:
            method = make_method(recipe_name, recipe)
            methods.append(method)
    methods.sort(key=lambda m: ("punch" in m.__name__, len(m.__name__)))
    pyhop.declare_methods("produce", *methods)

def check_enough(state, ID, item, num):
    if not hasattr(state, item):
        setattr(state, item, {ID: 0})
    if getattr(state, item).get(ID, 0) >= num:
        return []
    return [('produce', ID, item)]

def add_heuristic(data, ID):
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        return state.time.get(ID, 0) < 0 or depth > 30
    pyhop.add_check(heuristic)

pyhop.declare_methods('have_enough', check_enough)

if __name__ == '__main__':
    with open('crafting.json') as f:
        data = json.load(f)
        
    state = pyhop.State('state')
    state.time = {'agent': 100}
    state.wood = {'agent': 0}
    state.iron_pickaxe = {'agent': 0}
    
    goals = [('have_enough', 'agent', 'iron_pickaxe', 1)]
    
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    
    pyhop.pyhop(state, goals, verbose=3)
