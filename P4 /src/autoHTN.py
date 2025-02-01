import pyhop
import json

def make_operator(rule):
    """Creates an operator function from a crafting rule"""
    def operator(state, ID):
        if 'Time' in rule and state.time.get(ID, 0) < rule['Time']:
            return False
        return state
    return operator

def make_method(name, rule):
    """Creates a method function that decomposes a task into subtasks"""
    def method(state, ID):
        if name == 'plank' and getattr(state, 'plank').get(ID, 0) >= 1:
            return []
        return False
    return method

def declare_operators(data):
    operators = []
    for name, rule in data['Recipes'].items():
        if 'plank' in name:
            op_name = f"op_{name}"
            operator = make_operator(rule)
            operator.__name__ = op_name
            operators.append(operator)
    
    if operators:
        pyhop.declare_operators(*operators)

def declare_methods(data):
    for name, rule in data['Recipes'].items():
        if 'plank' in name:
            method = make_method(name, rule)
            method.__name__ = f"produce_{name}"
            pyhop.declare_methods(f"produce_{name}", method)

def add_heuristic(data, ID):
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        return state.time.get(ID, 0) < 0
    pyhop.add_check(heuristic)

def check_enough(state, ID, item, num):
    if getattr(state, item)[ID] >= num:
        return []
    return False

def produce_enough(state, ID, item, num):
    return [('produce', ID, item), ('have_enough', ID, item, num)]

def produce(state, ID, item):
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('have_enough', check_enough, produce_enough)
pyhop.declare_methods('produce', produce)

if __name__ == '__main__':
    with open('crafting.json') as f:
        data = json.load(f)
    
    state = pyhop.State('state')
    state.time = {'agent': 0}
    state.plank = {'agent': 1}
    
    goals = [('have_enough', 'agent', 'plank', 1)]
    
    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')
    
    pyhop.pyhop(state, goals, verbose=3)
