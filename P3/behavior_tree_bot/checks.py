def have_strong_fleet(state):
    """
    Check if your total fleet strength (planets + fleets) is significantly higher than the enemy's.
    """
    my_total_ships = sum(planet.num_ships for planet in state.my_planets()) + \
                     sum(fleet.num_ships for fleet in state.my_fleets())
    enemy_total_ships = sum(planet.num_ships for planet in state.enemy_planets()) + \
                        sum(fleet.num_ships for fleet in state.enemy_fleets())

    # Consider 'strong' if 1.5x more ships than the enemy
    return my_total_ships > 1.5 * enemy_total_ships

def is_under_attack(state):
    """
    Check if any of your planets are being targeted by enemy fleets.
    """
    my_planets = state.my_planets()
    enemy_fleets = state.enemy_fleets()

    for fleet in enemy_fleets:
        if any(planet.ID == fleet.destination_planet for planet in my_planets):
            return True
    return False

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


def if_neutral_planet_available(state):
    return any(state.neutral_planets())


def have_largest_fleet(state):
    return sum(planet.num_ships for planet in state.my_planets()) \
             + sum(fleet.num_ships for fleet in state.my_fleets()) \
           > sum(planet.num_ships for planet in state.enemy_planets()) \
             + sum(fleet.num_ships for fleet in state.enemy_fleets())
