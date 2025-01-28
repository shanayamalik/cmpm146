def if_neutral_planet_available(state):
    return any(p for p in state.neutral_planets() 
              if not any(f.destination_planet == p.ID for f in state.my_fleets()))

def is_under_attack(state):
    return any(fleet.destination_planet == planet.ID 
              for planet in state.my_planets() 
              for fleet in state.enemy_fleets())

def have_vulnerable_enemy_planet(state):
    my_strongest = max(state.my_planets(), key=lambda p: p.num_ships, default=None)
    if not my_strongest:
        return False

    enemy_planets = state.enemy_planets()
    
    for target in enemy_planets:
        distance = state.distance(my_strongest.ID, target.ID)
        required_ships = target.num_ships + distance * target.growth_rate + 1
        if my_strongest.num_ships > required_ships * 1.2:  # 20% safety margin
            return True
    return False

