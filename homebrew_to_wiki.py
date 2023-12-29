import os
import warnings
from sys import exit
from mob_sets import MOBS

"""
Dumps all the homebrew monsters as wiki pages
"""

if not os.path.exists('../DokuWikiStick/dokuwiki/data/pages'):
    warnings.warn('There does not appear to be a directory for DokuWiki. Please add that and try again.')
    exit()


statblock_path = '../DokuWikiStick/dokuwiki/data/pages/statblock'

for name in MOBS:
    mob = MOBS[name]
    if mob.stat_block['Source'] != 'DSO Homebrew':
        continue
    wiki_text = mob.to_wiki()
    os.makedirs(statblock_path, exist_ok=True)
    name = mob.name.replace(' ', '_')
    with open(os.path.join(statblock_path, f'{name}.txt'), 'w') as f:
        f.write(wiki_text)
