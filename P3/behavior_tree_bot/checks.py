# checks.py
# Collection of check functions that evaluate game state
# Used by behavior tree to make strategic decisions
# Each function returns boolean based on specific condition

def if_neutral_planet_available(state):
    """Check if any neutral planets exist
    Used to determine if expansion is possible"""
    return any(state.neutral_planets())

def have_largest_fleet(state):
    """Compare total fleet size with enemy
    Includes both planet garrisons and ships in flight"""
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())

def is_under_attack(state):
    """Check if any planets are targeted by enemy fleets
    Determines if defensive actions are needed"""
    for fleet in state.enemy_fleets():
        if any(planet.ID == fleet.destination_planet for planet in state.my_planets()):
            return True
    return False

def have_strong_fleet(state):
    """Check if fleet is 50% stronger than enemy
    Used to determine if aggressive actions are safe"""
    my_ships = sum(p.num_ships for p in state.my_planets())
    enemy_ships = sum(p.num_ships for p in state.enemy_planets())
    return my_ships > enemy_ships * 1.5

def safe_to_spread(state):
    """Check if safe to expand based on:
    - No incoming enemy fleets
    - Have at least one planet"""
    return not is_under_attack(state) and len(state.my_planets()) > 0

def safe_to_expand(state):
    """
    Check if there are no immediate threats, making it safe to expand.
    """
    my_planets = state.my_planets()
    enemy_fleets = state.enemy_fleets()

    # If any of my planets are under threat, it's not safe to expand
    for fleet in enemy_fleets:
        if any(planet.ID == fleet.destination_planet for planet in my_planets):
            return False
    return True

def has_vulnerable_enemy_planet(state):
    """
    Check if there's an enemy planet with fewer ships than a potential attacking fleet.
    """
    my_strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    enemy_planets = state.enemy_planets()

    if not my_strongest_planet or not enemy_planets:
        return False

    for planet in enemy_planets:
        if my_strongest_planet.num_ships > planet.num_ships + 20:  # Add buffer for safety
            return True
    return False

def can_consolidate_fleets(state):
    """
    Check if multiple owned planets are close enough to consolidate fleets.
    """
    my_planets = state.my_planets()

    if len(my_planets) < 2:
        return False

    for planet in my_planets:
        for other_planet in my_planets:
            if planet.ID != other_planet.ID and state.distance(planet.ID, other_planet.ID) < 10:
                return True
    return False
