import pyhop
import json

# Basic helper methods for resource management
def check_enough(state, ID, item, num):
    """
    Checks if an agent has enough of a specific resource
    Returns empty list (success) if enough resources exist, False otherwise
    """
    if getattr(state, item)[ID] >= num: return []
    return False

def produce_enough(state, ID, item, num):
    """
    Creates a sequence of tasks to produce required resources
    Returns a list containing production task and verification task
    """
    return [('produce', ID, item), ('have_enough', ID, item, num)]

# Register the resource management methods with pyhop
pyhop.declare_methods('have_enough', check_enough, produce_enough)

def produce(state, ID, item):
    """
    Generic production method that creates specific production tasks
    Converts generic 'produce' into specific 'produce_<item>' tasks
    """
    return [('produce_{}'.format(item), ID)]

pyhop.declare_methods('produce', produce)

def make_method(name, rule):
    """
    Creates a method function for a specific crafting rule
    Parameters:
        name: String identifier for the method
        rule: Dictionary containing recipe requirements and outputs
    Returns:
        method: A function that generates appropriate subtasks
    """
    def method(state, ID):
        # Priority order helps optimize resource gathering and tool creation
        # Items earlier in the list are processed first
        order = ['bench', 'furnace', 'ingot', 'ore', 'coal', 'cobble', 'stick', 'plank', 'wood', 
                'iron_axe', 'stone_axe', 'wooden_axe', 'iron_pickaxe', 'wooden_pickaxe', 'stone_pickaxe']
        
        # Combine requirements and consumed materials to get total needs
        needs = {}
        if 'Requires' in rule:  # Tools and facilities needed
            needs.update(rule['Requires'])
        if 'Consumes' in rule:  # Materials consumed in crafting
            needs.update(rule['Consumes'])
        
        # Create list to store ordered subtasks
        subtasks = []
        
        # Sort items based on priority order to optimize crafting sequence
        items = sorted(needs.items(), key=lambda x: order.index(x[0]) if x[0] in order else len(order))
        
        # Generate subtasks for gathering each required item
        for item, amount in items:
            subtasks.append(('have_enough', ID, item, amount))
            
        # Add the final crafting operation
        subtasks.append((("op_" + name).replace(' ', '_'), ID))
        
        return subtasks
    return method

def declare_methods(data):
    """
    Processes recipe data to create and declare all crafting methods
    Groups methods by what they produce and sorts them by time efficiency
    """
    # Dictionary to store methods grouped by product
    methods = {}
    
    # Process each recipe from the data
    for recipe_name, recipe_info in data['Recipes'].items():
        cur_time = recipe_info['Time']
        m = make_method(recipe_name, recipe_info)
        m.__name__ = recipe_name.replace(' ', '_')
        
        # Create method name based on what it produces
        cur_m = ("produce_" + list(recipe_info['Produces'].keys())[0]).replace(' ', '_')
        
        # Group methods that produce the same item
        if cur_m not in methods:
            methods[cur_m] = [(m, cur_time)]
        else:
            methods[cur_m].append((m, cur_time))
    
    # Declare methods to pyhop, prioritizing faster methods
    for m, info in methods.items():
        methods[m] = sorted(info, key=lambda x: x[1])  # Sort by time efficiency
        pyhop.declare_methods(m, *[method[0] for method in methods[m]])

def make_operator(rule):
    """
    Creates an operator function from a crafting rule
    Handles resource checks, time management, and state updates
    """
    def operator(state, ID):
        # Sequence of checks before crafting
        
        # Time check - ensure we have enough time units
        if state.time[ID] < rule['Time']:
            return False
            
        # Tool check - verify required tools are available
        if 'Requires' in rule:
            for item, amount in rule['Requires'].items():
                if getattr(state, item)[ID] < amount:
                    return False
                    
        # Resource check - verify we have materials to consume
        if 'Consumes' in rule:
            for item, amount in rule['Consumes'].items():
                if getattr(state, item)[ID] < amount:
                    return False
        
        # Execute crafting operation
        
        # Update time remaining
        state.time[ID] -= rule['Time']
        
        # Consume required materials
        if 'Consumes' in rule:
            for item, amount in rule['Consumes'].items():
                cur_val = getattr(state, item)
                setattr(state, item, {ID: cur_val[ID] - amount})
        
        # Create new items
        for item, amount in rule['Produces'].items():
            cur_val = getattr(state, item)
            setattr(state, item, {ID: cur_val[ID] + amount})
            
        return state
    return operator

def declare_operators(data):
    """
    Creates and declares all operators from recipe data
    Each recipe becomes a unique operator function
    """
    ops = []
    for recipe_name, recipe_info in data['Recipes'].items():
        op = make_operator(recipe_info)
        op.__name__ = ("op_" + recipe_name).replace(' ', '_')
        ops.append(op)
    pyhop.declare_operators(*ops)

def add_heuristic(data, ID):
    """
    Adds optimization heuristics to the planner
    Prevents infinite loops and optimizes tool usage
    """
    def heuristic(state, curr_task, tasks, plan, depth, calling_stack):
        # Optimization rules
        
        # Prevent creating duplicate tools
        if curr_task[0] == 'produce' and curr_task[2] in data['Tools']:
            if getattr(state, curr_task[2])[ID] > 0:
                return True
                
        # Only make wooden_axe if significant wood needed
        if curr_task[0] == 'produce_wooden_axe':
            wood_needed = sum([task[3] for task in tasks if len(task) > 3 and task[2] == 'wood'])
            if wood_needed < 5 and 'wooden_axe' not in data['Goal']:
                return True
                
        # Only make stone_pickaxe if significant cobble needed
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

def set_up_state(data, test_case, ID, time=0):
    """
    Initializes the game state for a test case
    Sets up resources, tools, and time limit
    """
    state = pyhop.State('state')
    state.time = {ID: test_case.get('Time', time)}
    
    # Initialize all items and tools to zero
    for item in data['Items']:
        setattr(state, item, {ID: 0})
    for item in data['Tools']:
        setattr(state, item, {ID: 0})
    
    # Set initial quantities from test case
    for item, num in test_case['Initial'].items():
        setattr(state, item, {ID: num})
            
    return state

def set_up_goals(test_case, ID):
    """
    Converts test case goals into planner goals
    Returns a list of 'have_enough' tasks
    """
    return [('have_enough', ID, item, num) 
            for item, num in test_case['Goal'].items()]

# Main execution block with test cases
if __name__ == '__main__':
    # Load crafting rules from JSON file
    with open('crafting.json') as f:
        data = json.load(f)
        
    # Define test cases with varying complexity
    test_cases = [
        {
            'name': 'Test Case A',
            'Initial': {'plank': 1},
            'Goal': {'plank': 1},
            'Time': 0
        },
        {
            'name': 'Test Case B',
            'Initial': {},
            'Goal': {'plank': 1},
            'Time': 300
        },
        {
            'name': 'Test Case C',
            'Initial': {'plank': 3, 'stick': 2},
            'Goal': {'wooden_pickaxe': 1},
            'Time': 10
        },
        {
            'name': 'Test Case D',
            'Initial': {},
            'Goal': {'iron_pickaxe': 1},
            'Time': 100
        },
        {
            'name': 'Test Case E',
            'Initial': {},
            'Goal': {'cart': 1, 'rail': 10},
            'Time': 175
        },
        {
            'name': 'Test Case F',
            'Initial': {},
            'Goal': {'cart': 1, 'rail': 20},
            'Time': 250
        }
    ]
    
    # Run test cases and display results
    print("\nTesting HTN Planner for Minecraft Construction Tasks")
    print("="*50)
    
    for test_case in test_cases:
        print(f"\nRunning {test_case['name']}")
        print(f"Initial: {test_case['Initial']}")
        print(f"Goal: {test_case['Goal']}")
        print("-"*50)
        
        # Set up planner state and goals
        state = set_up_state(data, test_case, 'agent', test_case['Time'])
        data['Goal'] = test_case['Goal']
        goals = set_up_goals(test_case, 'agent')
        
        # Initialize planner components
        declare_operators(data)
        declare_methods(data)
        add_heuristic(data, 'agent')
        
        # Run planner and show results
        solution = pyhop.pyhop(state, goals, verbose=0)
        print(f"Solution found: {solution is not False}")
