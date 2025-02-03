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
        if curr_task in calling_stack:
            return True

        if state.time.get(ID, 0) <= 0:
            return True

        goal_items = set()
        for task in tasks:
            if task[0] == 'have_enough':
                goal_items.add(task[2])

        if curr_task[0] == "produce":
            item_to_produce = curr_task[2]
            if item_to_produce in goal_items:
                return False

        if curr_task[0] == "produce" and curr_task[2] == "bench":
            return False

        # Corrected check for Requires:
        if curr_task[0].startswith("op_"):  # Make sure it's an operator.
            recipe_name = curr_task[0][3:]  # Remove "op_" prefix
            recipe_name = " ".join(recipe_name.split("_"))  # Replace underscores with spaces
            if "Requires" in data["Recipes"].get(recipe_name, {}) or "craft bench" in recipe_name:
                for recipe_name, recipe in data["Recipes"].items():
                    if "bench" in recipe["Produces"]:
                        return False
        elif curr_task[0] == "produce":
            recipe_name = curr_task[2]
            if "Requires" in data["Recipes"].get(recipe_name, {}) or "craft bench" in recipe_name:
                for recipe_name, recipe in data["Recipes"].items():
                    if "bench" in recipe["Produces"]:
                        return False

        return False
    pyhop.add_check(heuristic)

pyhop.declare_methods('have_enough', check_enough)

if __name__ == '__main__':
    with open('crafting.json') as f:
        data = json.load(f)

    declare_operators(data)
    declare_methods(data)
    add_heuristic(data, 'agent')

    test_cases = [
        ({'plank': 1}, {'plank': 1}),
        ({}, {'plank': 1}),
        ({'plank': 3, 'stick': 2}, {'wooden_pickaxe': 1}),
        ({}, {'iron_pickaxe': 1}),
        ({}, {'cart': 1, 'rail': 10}),
        ({}, {'cart': 1, 'rail': 20}),
    ]

    for i, (initial, goal) in enumerate(test_cases):
        print(f"Test Case {i+1}:")
        state = pyhop.State('state')
        state.time = {'agent': 300}
        for item, qty in initial.items():
            setattr(state, item, {'agent': qty})
        goals = [('have_enough', 'agent', item, qty) for item, qty in goal.items()]

        if pyhop.pyhop(state, goals, verbose=0):
            print("Plan found")
        else:
            print("No plan found")
        print("-" * 20)
