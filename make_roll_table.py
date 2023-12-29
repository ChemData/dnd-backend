from generator import format_roll_table_for_homebrewery
from mob_sets import MOB_SETS, ENVIRONMENT_SETS

"""
Example showing how to generate a roll table.
"""

party = [3, 3, 3, 3]
mob_sets = {k: MOB_SETS[k] for k in ENVIRONMENT_SETS['southern plains']}
mob_sets = {k: MOB_SETS[k] for k in ['ankhegs']}


b = make_roll_table(mob_sets, party, max_mobs=None, difficulties=(('easy', 5), ('medium', 5), ('hard', 5), ('deadly', 5)), start_roll=1)


z = format_roll_table_for_homebrewery(b, 'Southern Plains', 11)

print(z)