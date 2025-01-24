# Planet Wars Bot - Behavior Tree Implementation

## Overview
Implementation of a bot that plays Planet Wars using behavior trees. The bot competes against 5 opponent bots using defensive, production, and aggressive strategies.

## Components
- bt_bot.py: Main bot implementation with behavior tree setup
- behaviors.py: Action functions for game moves
- checks.py: Conditional checks for decision making

## Strategy
Bot uses a 4-tier strategy:
1. Defense: Protect planets under attack
2. Production: Capture high-value neutral planets
3. Attack: Target enemy weak points when strong
4. Fallback: Safe expansion to nearby planets

## Requirements
- Python 3.x
- Java Runtime Environment

## Running
Run matches against all opponent bots: python run.py

## Structure
- Behavior tree uses Selector and Sequence nodes
- Actions execute game moves
- Checks validate conditions before moves
- Each strategy has defined conditions and corresponding actions

## Testing
Bot tested against:
- easy_bot
- spread_bot
- aggressive_bot
- defensive_bot
- production_bot

## Implementation Details
### Behavior Tree
- Root selector for high-level strategy
- Defensive sequence for protecting planets
- Production sequence for expansion
- Aggressive sequence for attacks
- Fallback sequence for safe growth

# Planet Wars Bot - Behavior Tree Implementation

## Overview
Implementation of a bot that plays Planet Wars using behavior trees. The bot competes against 5 opponent bots using defensive, production, and aggressive strategies.

## Components
- bt_bot.py: Main bot implementation with behavior tree setup
- behaviors.py: Action functions for game moves
- checks.py: Conditional checks for decision making

## Strategy
Bot uses a 4-tier strategy:
1. Defense: Protect planets under attack
2. Production: Capture high-value neutral planets
3. Attack: Target enemy weak points when strong
4. Fallback: Safe expansion to nearby planets

## Requirements
- Python 3.x
- Java Runtime Environment

## Running
Run matches against all opponent bots: python run.py

## Structure
- Behavior tree uses Selector and Sequence nodes
- Actions execute game moves
- Checks validate conditions before moves
- Each strategy has defined conditions and corresponding actions

## Testing
Bot tested against:
- easy_bot
- spread_bot
- aggressive_bot
- defensive_bot
- production_bot

## Implementation Details
### Behavior Tree
- Root selector for high-level strategy
- Defensive sequence for protecting planets
- Production sequence for expansion
- Aggressive sequence for attacks
- Fallback sequence for safe growth

### Actions
- defend_weakest_planet
- spread_to_strongest_neutral_planet
- attack_enemy_weakpoint
- spread_to_closest_neutral_planet

### Checks
- is_under_attack
- have_strong_fleet
- safe_to_spread
- has_neutral_growth_planets
