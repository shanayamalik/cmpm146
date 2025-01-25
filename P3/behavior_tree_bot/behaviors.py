import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

def defend_weakest_planet(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)
    if not my_planets:
        return False

    enemy_fleets = [f for f in state.enemy_fleets() 
                   if any(p.ID == f.destination_planet for p in my_planets)]
    
    if not enemy_fleets:
        return False

    target = min(my_planets, key=lambda p: p.num_ships)
    threat = sum(f.num_ships for f in enemy_fleets if f.destination_planet == target.ID)
    
    if threat > 0:
        strongest = max(my_planets, key=lambda p: p.num_ships)
        ships_needed = threat + target.growth_rate * state.distance(strongest.ID, target.ID)
        if strongest.num_ships > ships_needed + 5:
            return issue_order(state, strongest.ID, target.ID, ships_needed)
    return False

def spread_to_strongest_neutral_planet(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    neutral_planets = [p for p in state.neutral_planets() 
                      if not any(f.destination_planet == p.ID for f in state.my_fleets())]
    
    if not my_planets or not neutral_planets:
        return False

    neutral_planets.sort(key=lambda p: p.num_ships)
    for source in my_planets:
        for target in neutral_planets:
            required_ships = target.num_ships + 1
            if source.num_ships > required_ships + 5:
                return issue_order(state, source.ID, target.ID, required_ships)
    return False

def attack_enemy_weakpoint(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    enemy_planets = [p for p in state.enemy_planets() 
                    if not any(f.destination_planet == p.ID for f in state.my_fleets())]
    
    if not my_planets or not enemy_planets:
        return False

    enemy_planets.sort(key=lambda p: p.num_ships + p.growth_rate * 5)
    for source in my_planets:
        for target in enemy_planets:
            required_ships = target.num_ships + \
                           state.distance(source.ID, target.ID) * target.growth_rate + 1
            if source.num_ships > required_ships + 10:
                return issue_order(state, source.ID, target.ID, required_ships)
    return False

def spread_to_closest_neutral_planet(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships, reverse=True)
    neutral_planets = [p for p in state.neutral_planets() 
                      if not any(f.destination_planet == p.ID for f in state.my_fleets())]
    
    if not my_planets or not neutral_planets:
        return False

    for source in my_planets:
        closest = min(neutral_planets, 
                     key=lambda p: state.distance(source.ID, p.ID) * (p.num_ships + 1))
        required_ships = closest.num_ships + 1
        if source.num_ships > required_ships + 5:
            return issue_order(state, source.ID, closest.ID, required_ships)
    return False
