# checks.py
def is_under_attack(state):
    """Check if any planets are under attack"""
    for fleet in state.enemy_fleets():
        for planet in state.my_planets():
            if planet.ID == fleet.destination_planet:
                return True
    return False

def have_strong_fleet(state):
    """Check if fleet is 20% stronger than enemy"""
    my_ships = sum(p.num_ships for p in state.my_planets())
    enemy_ships = sum(p.num_ships for p in state.enemy_planets())
    return my_ships > enemy_ships * 1.2

def safe_to_spread(state):
    """Check if safe to expand"""
    return not is_under_attack(state) and len(state.my_planets()) > 0

def if_neutral_planet_available(state):
    """Check for available neutral planets"""
    return any(state.neutral_planets())

def have_largest_fleet(state):
    """Compare total fleet sizes"""
    my_total = sum(p.num_ships for p in state.my_planets()) + sum(f.num_ships for f in state.my_fleets())
    enemy_total = sum(p.num_ships for p in state.enemy_planets()) + sum(f.num_ships for f in state.enemy_fleets())
    return my_total > enemy_total
