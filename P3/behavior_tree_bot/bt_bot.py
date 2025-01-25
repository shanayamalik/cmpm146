#!/usr/bin/env python

import logging, traceback, sys, os, inspect
logging.basicConfig(filename=__file__[:-3] +'.log', filemode='w', level=logging.DEBUG)
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

from checks import (
    if_neutral_planet_available,
    have_largest_fleet,
    is_under_attack,
    have_strong_fleet,
    safe_to_spread
)

from behaviors import (
    defend_weakest_planet,
    spread_to_strongest_neutral_planet,
    attack_enemy_weakpoint,
    spread_to_closest_neutral_planet
)

from bt_nodes import Selector, Sequence, Action, Check
from planet_wars import PlanetWars, finish_turn

def setup_behavior_tree():
    root = Selector(name='High Level Strategy')

    defensive_plan = Sequence(name='Defensive Strategy')
    under_attack = Check(is_under_attack)
    defend = Action(defend_weakest_planet)
    defensive_plan.child_nodes = [under_attack, defend]

    production_plan = Sequence(name='Production Strategy')
    neutral_available = Check(if_neutral_planet_available)
    strongest_neutral = Action(spread_to_strongest_neutral_planet)
    production_plan.child_nodes = [neutral_available, strongest_neutral]

    aggressive_plan = Sequence(name='Aggressive Strategy')
    strong_fleet = Check(have_strong_fleet)
    strong_attack = Action(attack_enemy_weakpoint)
    aggressive_plan.child_nodes = [strong_fleet, strong_attack]

    fallback_plan = Sequence(name='Fallback Strategy')
    safe_to_spread_check = Check(safe_to_spread)
    spread = Action(spread_to_closest_neutral_planet)
    fallback_plan.child_nodes = [safe_to_spread_check, spread]

    root.child_nodes = [defensive_plan, production_plan, aggressive_plan, fallback_plan]

    logging.info('\n' + root.tree_to_string())
    return root

def do_turn(state):
    behavior_tree.execute(state)

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
