import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

def defend_weakest_planet(state):
    my_planets = list(state.my_planets())
    if not my_planets:
        return False

    # Calculate total incoming threat to each planet
    def planet_threat(planet):
        incoming_friendly = sum(f.num_ships for f in state.my_fleets()
                              if f.destination_planet == planet.ID)
        incoming_enemy = sum(f.num_ships for f in state.enemy_fleets()
                              if f.destination_planet == planet.ID)
        # Consider growth over time until enemy arrives
        min_turns = min((f.turns_remaining for f in state.enemy_fleets()
                        if f.destination_planet == planet.ID), default=0)
        future_growth = planet.growth_rate * min_turns
        return planet.num_ships + incoming_friendly + future_growth - incoming_enemy

    weakest = min(my_planets, key=planet_threat)
    strongest = max(my_planets, key=lambda p: p.num_ships)

    threat_level = planet_threat(weakest)
    if threat_level < 20:  # Only defend if actually threatened
        needed = abs(threat_level) + 15  # Dynamic defense size
        if strongest.num_ships > needed * 1.5:  # Ensure we keep enough reserve
            return issue_order(state, strongest.ID, weakest.ID, needed)
    return False

def attack_enemy_weakpoint(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    if not my_planets:
        return False

    target_planets = [p for p in state.enemy_planets()
                     if not any(f.destination_planet == p.ID for f in state.my_fleets())]
    if not target_planets:
        return False

    # Sort targets by lowest (ships_needed / growth_rate) ratio
    def target_value(target):
        distance = state.distance(my_planets[0].ID, target.ID)
        ships_needed = target.num_ships + distance * target.growth_rate + 1
        return ships_needed / (target.growth_rate + 1)  # +1 to avoid division by zero

    target_planets.sort(key=target_value)

    success = False
    for source in my_planets[:2]:  # Try to use top 2 strongest planets
        for target in target_planets[:2]:  # Consider top 2 most efficient targets
            distance = state.distance(source.ID, target.ID)
            needed = target.num_ships + distance * target.growth_rate + 1

            if source.num_ships > needed * 1.3:  # Only attack with 30% more ships than needed
                success |= issue_order(state, source.ID, target.ID, needed)

    return success

def spread_to_strongest_neutral_planet(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    if not my_planets:
        return False

    neutral_planets = [p for p in state.neutral_planets()
                      if not any(f.destination_planet == p.ID
                               for f in state.my_fleets() + state.enemy_fleets())]
    if not neutral_planets:
        return False

    # Value = growth_rate / (ships_needed * distance)
    def planet_value(neutral):
        distance = min(state.distance(p.ID, neutral.ID) for p in my_planets)
        return neutral.growth_rate / (neutral.num_ships * distance + 1)

    neutral_planets.sort(key=planet_value, reverse=True)

    success = False
    for source in my_planets[:2]:  # Try using top 2 strongest planets
        for target in neutral_planets[:2]:  # Try capturing top 2 most valuable planets
            needed = target.num_ships + 2
            if source.num_ships > needed * 1.3:
                success |= issue_order(state, source.ID, target.ID, needed)

    return success


