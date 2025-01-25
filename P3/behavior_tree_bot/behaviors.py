import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

def defend_weakest_planet(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)
    if not my_planets:
        return False

    def planet_strength(planet):
        incoming_friendly = sum(f.num_ships for f in state.my_fleets() 
                              if f.destination_planet == planet.ID)
        incoming_enemy = sum(f.num_ships for f in state.enemy_fleets() 
                           if f.destination_planet == planet.ID)
        return planet.num_ships + incoming_friendly - incoming_enemy

    weakest = min(my_planets, key=planet_strength)
    if planet_strength(weakest) < 0:
        strongest = max(my_planets, key=lambda p: p.num_ships)
        needed = abs(planet_strength(weakest)) + 1
        if strongest.num_ships > needed:
            return issue_order(state, strongest.ID, weakest.ID, needed)
    return False

def spread_to_strongest_neutral_planet(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)
    neutral_planets = [p for p in state.neutral_planets() 
                      if not any(f.destination_planet == p.ID for f in state.my_fleets())]
    
    if not my_planets or not neutral_planets:
        return False

    neutral_planets.sort(key=lambda p: (p.num_ships, -p.growth_rate))
    
    for source in my_planets:
        for target in neutral_planets:
            needed = target.num_ships + 1
            if source.num_ships > needed:
                return issue_order(state, source.ID, target.ID, needed)
            
    return False

def attack_enemy_weakpoint(state):
    my_planets = sorted(state.my_planets(), key=lambda p: p.num_ships)
    enemy_planets = [p for p in state.enemy_planets() 
                    if not any(f.destination_planet == p.ID for f in state.my_fleets())]
    
    if not my_planets or not enemy_planets:
        return False

    enemy_planets.sort(key=lambda p: p.num_ships + p.growth_rate * 2)
    source = max(my_planets, key=lambda p: p.num_ships)
    target = enemy_planets[0]
    
    needed = target.num_ships + state.distance(source.ID, target.ID) * target.growth_rate + 1
    if source.num_ships > needed + 1:
        return issue_order(state, source.ID, target.ID, needed)
    return False

def spread_to_closest_neutral_planet(state):
    my_planets = list(state.my_planets())
    neutral_planets = [p for p in state.neutral_planets() 
                      if not any(f.destination_planet == p.ID for f in state.my_fleets())]
    
    if not my_planets or not neutral_planets:
        return False

    neutral_planets.sort(key=lambda p: p.num_ships)
    my_planets.sort(key=lambda p: p.num_ships, reverse=True)

    for source in my_planets:
        for target in neutral_planets:
            needed = target.num_ships + 1
            if source.num_ships > needed:
                return issue_order(state, source.ID, target.ID, needed)
    return False
