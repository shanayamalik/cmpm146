import pyhop
import json

#############################################
# Operator Generation (from crafting.json)
#############################################
def make_operator(recipe_name, rule):
    def operator(state, ID):
        # Check if enough time is available.
        if state.time.get(ID, 0) < rule.get("Time", 0):
            return False

        # Check nonconsumable requirements.
        if "Requires" in rule:
            for item, qty in rule["Requires"].items():
                if getattr(state, item).get(ID, 0) < qty:
                    return False

        # Check consumable requirements.
        if "Consumes" in rule:
            for item, qty in rule["Consumes"].items():
                if getattr(state, item).get(ID, 0) < qty:
                    return False

        # Deduct time.
        state.time[ID] -= rule.get("Time", 0)

        # Deduct consumed items.
        if "Consumes" in rule:
            for item, qty in rule["Consumes"].items():
                getattr(state, item)[ID] -= qty

        # Add produced items.
        for item, qty in rule["Produces"].items():
            if not hasattr(state, item):
                setattr(state, item, {})
            current = getattr(state, item).get(ID, 0)
            getattr(state, item)[ID] = current + qty

        return state

    operator.__name__ = "op_" + recipe_name.replace(" ", "_")
    return operator

def declare_operators(data):
    global RECIPES
    RECIPES = data["Recipes"]
    ops = []
    for name, recipe in data["Recipes"].items():
        op = make_operator(name, recipe)
        ops.append(op)
    pyhop.declare_operators(*ops)

#############################################
# Method Generation (from crafting.json)
#############################################
def make_method(recipe_name, rule, produced_item):
    """
    Returns a method function for a recipe that produces produced_item.
    It returns subtasks that first ensure that all requirements and consumptions
    are available (using have_enough) and then calls the corresponding operator.
    """
    def method(state, ID):
        subtasks = []
        if "Requires" in rule:
            for req_item, qty in rule["Requires"].items():
                subtasks.append(('have_enough', ID, req_item, qty))
        if "Consumes" in rule:
            for cons_item, qty in rule["Consumes"].items():
                subtasks.append(('have_enough', ID, cons_item, qty))
        subtasks.append((f"op_{recipe_name.replace(' ', '_')}", ID))
        return subtasks
    method.__name__ = "produce_" + recipe_name.replace(" ", "_")
    return method

def declare_methods(data):
    # Group recipes by each produced item.
    methods_for_item = {}
    for recipe_name, recipe in data["Recipes"].items():
        for produced_item in recipe["Produces"]:
            task_name = "produce_" + produced_item
            m = make_method(recipe_name, recipe, produced_item)
            if task_name not in methods_for_item:
                methods_for_item[task_name] = []
            methods_for_item[task_name].append(m)
    # Declare these methods with Pyhop.
    for task_name, method_list in methods_for_item.items():
        pyhop.declare_methods(task_name, *method_list)
    # Create a dispatcher for the generic 'produce' task.
    def produce_dispatch(state, ID, item):
        # For most items, dispatch to the specific task
        return [('produce_' + item, ID)]
    pyhop.declare_methods('produce', produce_dispatch)

#############################################
# Custom Method for Producing Cobble
#############################################
def custom_produce_cobble(state, ID):
    """
    Domain knowledge: any pickaxe can produce cobble.
    If the agent has any pickaxe, choose the fastest available recipe.
    (Here we assume: iron_pickaxe for cobble takes 1 time unit,
    stone_pickaxe for cobble takes 2, and wooden_pickaxe for cobble takes 4.)
    If no pickaxe is available, this method fails so that the planner must
    plan to produce a pickaxe.
    """
    if state.iron_pickaxe.get(ID, 0) >= 1:
        return [('op_iron_pickaxe_for_cobble', ID)]
    elif state.stone_pickaxe.get(ID, 0) >= 1:
        return [('op_stone_pickaxe_for_cobble', ID)]
    elif state.wooden_pickaxe.get(ID, 0) >= 1:
        return [('op_wooden_pickaxe_for_cobble', ID)]
    else:
        return False

# Override the methods for producing cobble.
pyhop.declare_methods('produce_cobble', custom_produce_cobble)

#############################################
# Utility Method: have_enough
#############################################
def check_enough(state, ID, item, num):
    if not hasattr(state, item):
        setattr(state, item, {ID: 0})
    if getattr(state, item).get(ID, 0) >= num:
        return []
    return [('produce', ID, item)]
pyhop.declare_methods('have_enough', check_enough)

#############################################
# Heuristic to Prune Cyclic Production
#############################################
def my_heuristic(state, curr_task, tasks, plan, depth, calling_stack):
    # Basic cutoffs.
    if depth > 50:
        return True
    if state.time.get('agent', 0) < 0:
        return True

    # For tasks 'produce' and 'have_enough', count how many times the same resource appears.
    if curr_task[0] in ['produce', 'have_enough']:
        resource = curr_task[2]
        # For raw resources, allow a higher threshold.
        allowed_threshold = {"cobble": 10, "ore": 10, "coal": 10}
        threshold = allowed_threshold.get(resource, 2)
        count = sum(1 for t in calling_stack if t[0] in ['produce', 'have_enough'] and t[2] == resource)
        if count >= threshold:
            return True
    return False

pyhop.add_check(my_heuristic)

#############################################
# Main Execution
#############################################
if __name__ == '__main__':
    # Load the crafting JSON.
    with open('crafting.json') as f:
        data = json.load(f)

    # Initialize state.
    state = pyhop.State('state')
    state.time = {'agent': 100}
    for item in data["Items"]:
        setattr(state, item, {'agent': 0})
    for tool in data["Tools"]:
        setattr(state, tool, {'agent': 0})

    # Define the goal: obtain at least one iron_pickaxe.
    goals = [('have_enough', 'agent', 'iron_pickaxe', 1)]

    # Declare operators and methods.
    declare_operators(data)
    declare_methods(data)
    # (Note: our custom method for producing cobble is already declared.)

    # Run the planner.
    result = pyhop.pyhop(state, goals, verbose=3)
    print("\nFinal result:", result)
