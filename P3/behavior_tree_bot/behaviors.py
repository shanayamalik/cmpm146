# behaviors.py
import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

# Main behavior functions that determine bot actions
# Each function checks fleet availability and returns False if fleet exists
# Ships are only sent when sufficient numbers are available
# Most functions use a buffer of 10-20 ships for safety

def defend_weakest_planet(state):
   """Send reinforcements to planets under attack
   Returns False if:
   - Fleet already exists
   - No planets or enemy fleets
   - Not enough ships to send (less than 20)"""
   if len(state.my_fleets()) >= 1:
       return False
   
   my_planets = state.my_planets()
   enemy_fleets = state.enemy_fleets()

   if (len(my_planets) < 2) or not enemy_fleets:
       return False

   weakest_planet = min(my_planets, key=lambda p: p.num_ships)
   strongest_planet = max(my_planets, key=lambda p: p.num_ships)

   if strongest_planet.num_ships > 20:
       ships_to_send = 20
       return issue_order(state, strongest_planet.ID, weakest_planet.ID, ships_to_send)
   return False

def spread_to_strongest_neutral_planet(state):
   """Target neutral planets with highest growth rate
   Prioritizes planets that will produce more ships over time
   Uses 10 ship buffer when attacking"""
   if len(state.my_fleets()) >= 1:
       return False
   
   neutral_planets = state.neutral_planets()
   if not neutral_planets:
       return False

   target_planet = max(neutral_planets, key=lambda p: p.growth_rate)
   my_strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships)

   if my_strongest_planet.num_ships > target_planet.num_ships + 10:
       ships_to_send = target_planet.num_ships + 10
       return issue_order(state, my_strongest_planet.ID, target_planet.ID, ships_to_send)
   return False

def attack_enemy_weakpoint(state):
   """Attack weakest enemy planet
   Only attacks if we have significant numerical advantage
   Uses 20 ship buffer for stronger attack force"""
   if len(state.my_fleets()) >= 1:
       return False
   
   enemy_planets = state.enemy_planets()
   if not enemy_planets:
       return False

   weakest_enemy = min(enemy_planets, key=lambda p: p.num_ships)
   my_strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships)

   if my_strongest_planet.num_ships > weakest_enemy.num_ships + 20:
       ships_to_send = weakest_enemy.num_ships + 20
       return issue_order(state, my_strongest_planet.ID, weakest_enemy.ID, ships_to_send)
   return False

def spread_to_closest_neutral_planet(state):
   """Expand to closest neutral planet
   Uses distance calculation to find nearest target
   Maintains 10 ship buffer for capturing neutral planets"""
   if len(state.my_fleets()) >= 1:
       return False
   
   my_planets = state.my_planets()
   neutral_planets = state.neutral_planets()

   if not my_planets or not neutral_planets:
       return False

   my_strongest_planet = max(my_planets, key=lambda p: p.num_ships)
   closest_neutral = min(neutral_planets, key=lambda p: state.distance(my_strongest_planet.ID, p.ID))

   if my_strongest_planet.num_ships > closest_neutral.num_ships + 10:
       ships_to_send = closest_neutral.num_ships + 10
       return issue_order(state, my_strongest_planet.ID, closest_neutral.ID, ships_to_send)
   return False

def spread_to_weakest_neutral_planet(state):
    # (1) If we currently have a fleet in flight, just do nothing.
    if len(state.my_fleets()) >= 1:
        return False

    # (2) Find my strongest planet.
    strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)

    # (3) Find the weakest neutral planet.
    weakest_planet = min(state.neutral_planets(), key=lambda p: p.num_ships, default=None)

    if not strongest_planet or not weakest_planet:
        # No legal source or destination
        return False
    else:
        # (4) Send half the ships from my strongest planet to the weakest enemy planet.
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, strongest_planet.num_ships / 2)
    
def defend_weakest_planet(state):
    """
    Send reinforcements to the planet under attack with the fewest ships.
    """
    if len(state.my_fleets()) >= 1:
        return False
    
    my_planets = state.my_planets()
    enemy_fleets = state.enemy_fleets()

    if not my_planets or not enemy_fleets:
        return False

    weakest_planet = min(my_planets, key=lambda p: p.num_ships)
    strongest_planet = max(my_planets, key=lambda p: p.num_ships)

    if strongest_planet.num_ships > 20:
        ships_to_send = 20
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, ships_to_send)
    return False

def ambush_incoming_fleets(state):
    """
    Redirect fleets to intercept enemy fleets heading toward owned planets.
    """
    if len(state.my_fleets()) >= 1:
        return False
    
    my_planets = state.my_planets()
    enemy_fleets = state.enemy_fleets()

    for fleet in enemy_fleets:
        target_planet = next((p for p in my_planets if p.ID == fleet.destination_planet), None)
        if target_planet and target_planet.num_ships < fleet.num_ships:
            reinforcements = max(my_planets, key=lambda p: p.num_ships)
            if reinforcements.num_ships > fleet.num_ships:
                ships_to_send = fleet.num_ships + 10
                return issue_order(state, reinforcements.ID, target_planet.ID, ships_to_send)

    return False

def consolidate_fleets(state):
    """
    Send ships from multiple planets to the strongest planet to form a large fleet.
    """
    if len(state.my_fleets()) >= 1:
        return False
    
    my_planets = state.my_planets()
    if len(my_planets) < 2:
        return False

    strongest_planet = max(my_planets, key=lambda p: p.num_ships)
    success = False

    for planet in my_planets:
        if planet.ID != strongest_planet.ID and planet.num_ships > 10:
            ships_to_send = planet.num_ships // 2
            success |= issue_order(state, planet.ID, strongest_planet.ID, ships_to_send)

    return success

def focus_fire_on_strong_enemy_planet(state):
    """
    Attack an enemy planet with high growth but weak defenses.
    """
    if len(state.my_fleets()) >= 1:
        return False


    enemy_planets = state.enemy_planets()
    if not enemy_planets:
        return False

    target_planet = max(enemy_planets, key=lambda p: (p.growth_rate / max(p.num_ships, 1)))
    my_strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships)

    if my_strongest_planet.num_ships > target_planet.num_ships + 20:
        ships_to_send = target_planet.num_ships + 20
        return issue_order(state, my_strongest_planet.ID, target_planet.ID, ships_to_send)
    return False

def target_high_growth_planet(state):
    """
    Target a neutral planet with the highest growth rate.
    """
    if len(state.my_fleets()) >= 1:
        return False
    
    neutral_planets = state.neutral_planets()
    if not neutral_planets:
        return False

    target_planet = max(neutral_planets, key=lambda p: p.growth_rate)
    my_strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships)

    if my_strongest_planet.num_ships > target_planet.num_ships + 10:
        ships_to_send = target_planet.num_ships + 10
        return issue_order(state, my_strongest_planet.ID, target_planet.ID, ships_to_send)
    return False