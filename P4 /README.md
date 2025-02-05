# CMPM146: Programming Assignment IV
# HTN Planning for Minecraft

## File Overview
manualHTN.py: Implements manual HTN operators and methods for wood gathering
autoHTN.py: Contains programmatic HTN generation from JSON recipes
crafting.json: Defines recipes, items, tools, and crafting rules
pyhop.py: Core HTN planning implementation
custom_case.txt: Extra credit - defines a complex custom test case

## Implementation Details

### Heuristic Design
The planner implements several heuristics to optimize performance and prevent infinite loops:

1. Tool Creation Control
- Prevents redundant tool crafting by tracking existing tools
- Only creates tools when necessary based on task requirements
- Avoids duplicate tool creation if one already exists
- Prioritizes efficient tool progression paths

2. Resource Optimization
- Evaluates whether tools are needed based on resource quantity requirements
- Creates wooden axe only when significant wood gathering is needed
- Prioritizes faster gathering methods when tools are available
- Optimizes resource usage based on recipe requirements

3. Search Space Management
- Prevents circular dependencies in material requirements
- Implements strict priority ordering for crafting prerequisites
- Groups related methods by their output products
- Orders methods by time efficiency within groups

4. Path Pruning
- Prevents infinite cycles in tool requirements
- Avoids unnecessary crafting paths
- Optimizes tool progression sequences
- Reduces search space by eliminating unproductive branches

### Key Design Decisions

1. Resource Management
- Maintains accurate tracking of all resources and tools
- Implements strict time accounting for operations
- Verifies resource availability before operations
- Ensures efficient resource allocation

2. Task Organization
- Uses priority ordering for crafting prerequisites
- Groups related tasks for improved efficiency
- Implements strategic task decomposition
- Handles both direct crafting and preparation tasks

3. Method Implementation
- Groups methods by what they produce
- Sorts methods by time efficiency within groups
- Handles complex dependency chains
- Implements intelligent task sequencing

4. State Handling
- Maintains accurate resource counting
- Implements efficient state updates
- Ensures proper time management
- Tracks multiple concurrent resource states

The implementation demonstrates effective HTN planning by:
- Successfully handling all test cases within time constraints
- Intelligently managing tool progression
- Optimizing resource gathering and crafting
- Maintaining efficient time usage throughout operations
