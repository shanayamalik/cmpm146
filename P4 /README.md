# CMPM146: Programming Assignment 4 - HTN Planning for Minecraft

### File Overview
- `manualHTN.py`: Implements manual HTN operators and methods for wood gathering
- `autoHTN.py`: Contains programmatic HTN generation from JSON recipes
- `custom_case.txt`: Extra credit implementation with a complex test case

### Running the Program
1. Manual HTN Test (Wood Gathering):
   ```bash
   python3.10 manualHTN.py
   ```

2. Automated HTN Tests:
   ```bash
   python3.10 autoHTN.py
   ```

3. Extra Credit Custom Case:

### Heuristic Implementation
The planner has several heuristics to optimize performance, including the following.

## Tool Creation Control
- Prevents duplicate tool creation by tracking existing tools
- Creates tools only when required by upcoming tasks

## Resource Gathering Optimization
- Makes wooden axe only when significant wood gathering is required
- Prioritizes more efficient gathering methods when tools are available

## Crafting Priority Management
- Orders crafting prerequisites (bench, furnace first)
- Prioritizes base materials before complex items

## Search Space Pruning
- Prevents infinite loops in tool requirements
- Avoids redundant resource gathering
- Handles circular dependencies in recipes
