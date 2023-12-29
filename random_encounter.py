from random import random
import sys
import getopt
from mob_sets import MOB_SETS, ENVIRONMENT_SETS


# Default values
environment = None
main_enemy = None
difficulty = 'medium'
party = [3, 3, 3, 3]

argv = sys.argv[1:]
opts, args = getopt.getopt(argv, 'e:m:d:p:', ['environment=', 'main_enemy=', 'difficulty=', 'party_levels='])

for opt, arg in opts:
    if opt == '-e':
        environment = arg
    elif opt == '-m':
        main_enemy = arg
    elif opt == '-d':
        difficulty = arg
    elif opt == '-p':
        party = [int(x) for x in arg.split(',')]

if environment is None and main_enemy is None:
    raise(ValueError('Either an environment or main enemy must be specified.'))
if environment is None and main_enemy is not None:
    mob_sets = {k: MOB_SETS[k] for k in [main_enemy]}
elif main_enemy is not None:
    mob_sets = {k: MOB_SETS[k] for k in ENVIRONMENT_SETS[environment]}
else:
    if random() > 0.5:
        mob_sets = {k: MOB_SETS[k] for k in [main_enemy]}
    else:
        mob_sets = {k: MOB_SETS[k] for k in ENVIRONMENT_SETS[environment]}

enemies = make_roll_table(mob_sets, party, max_mobs=None, difficulties=((difficulty, 1),), start_roll=1)[0]
print(enemies[0].simple_repr(), '|', enemies[2])