# behaviors.py
import sys
sys.path.insert(0, '../')
from planet_wars import issue_order

def defend_weakest_planet(state):
   """Send reinforcements to planets under attack"""
   if len(state.my_fleets()) >= 1:
       return False
   
   my_planets = state.my_planets()
   enemy_fleets = state.enemy_fleets()

   if not my_planets or not enemy_fleets:
       return False

   weakest_planet = min(my_planets, key=lambda p: p.num_ships)
   strongest_planet = max(my_planets, key=lambda p: p.num_ships)

   if strongest_planet.num_ships > 20:
       return issue_order(state, strongest_planet.ID, weakest_planet.ID, 20)
   return False

def spread_to_strongest_neutral_planet(state):
   """Target neutral planets with highest growth rate"""
   if len(state.my_fleets()) >= 1:
       return False
   
   neutral_planets = state.neutral_planets()
   if not neutral_planets:
       return False

   target_planet = max(neutral_planets, key=lambda p: p.growth_rate)
   my_strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships)

   if my_strongest_planet.num_ships > target_planet.num_ships + 10:
       ships_to_send = target_planet.num_ships + 10
       return issue_order(state, my_strongest_planet.ID, target_planet.ID, ships_to_send)
   return False

def attack_enemy_weakpoint(state):
   """Attack the weakest enemy planet"""
   if len(state.my_fleets()) >= 1:
       return False
   
   enemy_planets = state.enemy_planets()
   if not enemy_planets:
       return False

   weakest_enemy = min(enemy_planets, key=lambda p: p.num_ships)
   my_strongest_planet = max(state.my_planets(), key=lambda p: p.num_ships)

   if my_strongest_planet.num_ships > weakest_enemy.num_ships + 20:
       ships_to_send = weakest_enemy.num_ships + 20
       return issue_order(state, my_strongest_planet.ID, weakest_enemy.ID, ships_to_send)
   return False

def spread_to_closest_neutral_planet(state):
   """Expand to closest neutral planet"""
   if len(state.my_fleets()) >= 1:
       return False
   
   my_planets = state.my_planets()
   neutral_planets = state.neutral_planets()

   if not my_planets or not neutral_planets:
       return False

   my_strongest_planet = max(my_planets, key=lambda p: p.num_ships)
   closest_neutral = min(neutral_planets, key=lambda p: state.distance(my_strongest_planet.ID, p.ID))

   if my_strongest_planet.num_ships > closest_neutral.num_ships + 10:
       ships_to_send = closest_neutral.num_ships + 10
       return issue_order(state, my_strongest_planet.ID, closest_neutral.ID, ships_to_send)
   return False
