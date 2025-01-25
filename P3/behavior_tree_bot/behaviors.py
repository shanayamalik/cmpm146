import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

def defend_weakest_planet(state):
    if len(state.my_fleets()) >= 3:
        return False
    
    my_planets = state.my_planets()
    enemy_fleets = state.enemy_fleets()

    if not my_planets or not enemy_fleets:
        return False

    weakest_planet = min(my_planets, key=lambda p: p.num_ships)
    strongest_planet = max(my_planets, key=lambda p: p.num_ships)
    
    # Send 50% of ships for defense, matching easy_bot's strategy
    ships_to_send = strongest_planet.num_ships // 2
    if ships_to_send > 0:
        return issue_order(state, strongest_planet.ID, weakest_planet.ID, ships_to_send)
    return False

def spread_to_strongest_neutral_planet(state):
    if len(state.my_fleets()) >= 3:
        return False
    
    my_planets = state.my_planets()
    neutral_planets = state.neutral_planets()
    
    if not my_planets or not neutral_planets:
        return False

    strongest_planet = max(my_planets, key=lambda p: p.num_ships)
    weakest_neutral = min(neutral_planets, key=lambda p: p.num_ships)
    
    # Send 50% of ships
    ships_to_send = strongest_planet.num_ships // 2
    if ships_to_send > weakest_neutral.num_ships:
        return issue_order(state, strongest_planet.ID, weakest_neutral.ID, ships_to_send)
    return False

def attack_enemy_weakpoint(state):
    if len(state.my_fleets()) >= 3:
        return False
    
    my_planets = state.my_planets()
    enemy_planets = state.enemy_planets()
    
    if not my_planets or not enemy_planets:
        return False

    strongest_planet = max(my_planets, key=lambda p: p.num_ships)
    weakest_enemy = min(enemy_planets, key=lambda p: p.num_ships)
    
    # Send 60% of ships for attack
    ships_to_send = int(strongest_planet.num_ships * 0.6)
    if ships_to_send > weakest_enemy.num_ships:
        return issue_order(state, strongest_planet.ID, weakest_enemy.ID, ships_to_send)
    return False

def spread_to_closest_neutral_planet(state):
    if len(state.my_fleets()) >= 3:
        return False
    
    my_planets = state.my_planets()
    neutral_planets = state.neutral_planets()
    
    if not my_planets or not neutral_planets:
        return False

    strongest_planet = max(my_planets, key=lambda p: p.num_ships)
    closest_neutral = min(neutral_planets, 
                         key=lambda p: state.distance(strongest_planet.ID, p.ID))
    
    # Send 50% of ships
    ships_to_send = strongest_planet.num_ships // 2
    if ships_to_send > closest_neutral.num_ships:
        return issue_order(state, strongest_planet.ID, closest_neutral.ID, ships_to_send)
    return False
