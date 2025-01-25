def if_neutral_planet_available(state):
    return bool(state.neutral_planets())

def have_largest_fleet(state):
    my_ships = sum(p.num_ships for p in state.my_planets())
    enemy_ships = sum(p.num_ships for p in state.enemy_planets())
    return my_ships > enemy_ships

def is_under_attack(state):
    return any(fleet.destination_planet == planet.ID 
              for planet in state.my_planets() 
              for fleet in state.enemy_fleets())

def have_strong_fleet(state):
    my_ships = sum(p.num_ships for p in state.my_planets())
    enemy_ships = sum(p.num_ships for p in state.enemy_planets())
    return my_ships > enemy_ships * 1.2

def safe_to_spread(state):
    return not is_under_attack(state) and len(state.my_planets()) > 0
