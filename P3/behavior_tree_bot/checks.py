def if_neutral_planet_available(state):
    return any(p for p in state.neutral_planets() 
              if not any(f.destination_planet == p.ID for f in state.my_fleets()))

def have_largest_fleet(state):
    my_ships = sum(p.num_ships for p in state.my_planets())
    my_fleets = sum(f.num_ships for f in state.my_fleets())
    enemy_ships = sum(p.num_ships for p in state.enemy_planets())
    enemy_fleets = sum(f.num_ships for f in state.enemy_fleets())
    return (my_ships + my_fleets) > (enemy_ships + enemy_fleets)

def is_under_attack(state):
    return any(fleet.destination_planet == planet.ID 
              for planet in state.my_planets() 
              for fleet in state.enemy_fleets())

def have_strong_fleet(state):
    my_ships = sum(p.num_ships for p in state.my_planets()) + sum(f.num_ships for f in state.my_fleets())
    enemy_ships = sum(p.num_ships for p in state.enemy_planets()) + sum(f.num_ships for f in state.enemy_fleets())
    return my_ships > enemy_ships * 1.3

def safe_to_spread(state):
    my_planets = state.my_planets()
    if not my_planets:
        return False
    under_attack = is_under_attack(state)
    total_ships = sum(p.num_ships for p in my_planets)
    avg_ships = total_ships / len(my_planets)
    return not under_attack and avg_ships > 30
