#!/usr/bin/env python

import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from behavior_tree_bot.behaviors import *
from behavior_tree_bot.checks import *
from behavior_tree_bot.bt_nodes import Selector, Sequence, Action, Check
from planet_wars import PlanetWars, finish_turn

# You have to improve this tree or create an entire new one that is capable
# of winning against all the 5 opponent bots
def setup_behavior_tree():
   # Top-down construction of behavior tree
   root = Selector(name='High Level Strategy')

   # Added defensive strategy to protect our planets
   defensive_plan = Sequence(name='Defensive Strategy')
   under_attack = Check(is_under_attack)
   defend = Action(defend_weakest_planet)
   defensive_plan.child_nodes = [under_attack, defend]

   # Modified production strategy to target valuable planets
   production_plan = Sequence(name='Production Strategy')
   neutral_available = Check(if_neutral_planet_available)
   strongest_neutral = Action(spread_to_strongest_neutral_planet)
   production_plan.child_nodes = [neutral_available, strongest_neutral]

   # New aggressive strategy when we have superior forces
   aggressive_plan = Sequence(name='Aggressive Strategy')
   strong_fleet = Check(have_strong_fleet)
   strong_attack = Action(attack_enemy_weakpoint)
   aggressive_plan.child_nodes = [strong_fleet, strong_attack]

   # Safe expansion as fallback
   fallback_plan = Sequence(name='Fallback Strategy')
   safe_to_spread = Check(safe_to_spread)
   spread = Action(spread_to_closest_neutral_planet)
   fallback_plan.child_nodes = [safe_to_spread, spread]

   root.child_nodes = [defensive_plan, production_plan, aggressive_plan, fallback_plan]
   
   logging.info('\n' + root.tree_to_string())
   return root

# You don't need to change this function
def do_turn(state):
   behavior_tree.execute(planet_wars)

if __name__ == '__main__':
   logging.basicConfig(filename=__file__[:-3] + '.log', filemode='w', level=logging.DEBUG)

   behavior_tree = setup_behavior_tree()
   try:
       map_data = ''
       while True:
           current_line = input()
           if len(current_line) >= 2 and current_line.startswith("go"):
               planet_wars = PlanetWars(map_data)
               do_turn(planet_wars)
               finish_turn()
               map_data = ''
           else:
               map_data += current_line + '\n'

   except KeyboardInterrupt:
       print('ctrl-c, leaving ...')
   except Exception:
       traceback.print_exc(file=sys.stdout)
       logging.exception("Error in bot.")
