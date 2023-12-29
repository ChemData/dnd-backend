from json import load, loads, dump
from typing import Sequence, Optional
import os
import utils as utils

XP_AMOUNTS = {
    '0':10, '1/8':25, '1/4':50, '1/2':100, '1':200, '2':450, '3':700, '4':1100, '5': 1800, '6': 2300,
    '7': 2900, '8':3900, '9': 5000, '10': 5900, '11': 7200, '12': 8400, '13': 10000, '14': 11500, '15': 13000,
    '16': 15000, '17': 18000, '18': 20000, '19': 22000, '20': 25000, '21': 33000, '22': 41000, '23': 50000,
    '24': 62000, '25': 75000, '26': 90000, '27': 105000,' 28': 120000, '30': 155000, '00': None}


def cleanup_downloaded_json():
    with open('assets/mob_data/stat_blocks/Monster Manual.JSON', 'r', encoding='utf8') as f:
        monsters = load(f)
    output = {}
    for _, monster_data in monsters.items():
        monster = loads(monster_data)
        if type(monster) == list:
            continue
        monster['CR'] = monster['Challenge']
        del monster['Challenge']
        monster['Name'] = monster['Name'].lower()
        monster['size'] = monster['Type'].split(' ')[0].lower()
        monster['category'] = monster['Type'].split(',')[0].split(' ')[1]
        monster['alignment'] = monster['Type'].split(',')[-1]
        monster['Source'] = 'Monster Manual'
        output[monster['Name']] = monster
    with open('assets/mob_data/stat_blocks/mm_monsters.json', 'w') as f:
        dump(output, f, indent=4)


class Mob:
    def __init__(self, Name, CR, **kwargs):
        self.name = Name
        self.cr = str(CR)
        self.num_cr = utils.to_numeric_cr(CR)
        self.xp = XP_AMOUNTS[str(CR)]
        self.stat_block = kwargs

    def __repr__(self):
        return f"{self.name}(cr {self.cr})"

    def __hash__(self):
        return hash(f'{self.name}{self.cr}')

    def __eq__(self, other):
        if self.name == other.name and self.cr == other.cr:
            return True
        return False

    @property
    def url(self) -> Optional[str]:
        if self.stat_block['Source'] == 'Monster Manual':
            url_name = self.name.replace(' ', '%20')
            full_url = f"https://5e.tools/bestiary.html#{url_name}_mm"
            return full_url
        elif self.stat_block['Source'] == 'DSO Homebrew':
            url_name = self.name.replace(' ', '_')
            full_url = f"http://192.168.4.106:8800/doku.php?id=statblock:{url_name}"
            return full_url
        return None

    def add_to_homebrew(self):
        with open('homebrew_monsters.json', 'r') as f:
            hb = load(f)
        hb[self.stat_block['Id']] = self.stat_block
        with open('homebrew_monsters.json', 'w') as f:
            dump(hb, f, indent=4)

    def to_homebrewery(self):
        b = self.stat_block
        output = "{{monster,frame,wide\n"
        output += f"## {self.name.capitalize()}\n"
        output += f"*{b['Type']}*\n___\n"
        output += f"**Armor Class** :: {b['AC']['Value']}"
        if b['AC']['Notes'] != "":
            output += f" {b['AC']['Notes']}"
        output += f"\n**Hit Points**  :: {b['HP']['Value']}{b['HP']['Notes']}\n"
        output += f"**Speed**  :: {', '.join(b['Speed'])}\n___\n"
        output += "| STR | DEX | CON | INT | WIS | CHA |\n|:-----:|:-----:|:-----:|:-----:|:-----:|:-----:|\n"
        output += f"|{self.stat_to_modifier(b['Abilities']['Str'])}|{self.stat_to_modifier(b['Abilities']['Dex'])}|" \
                  f"{self.stat_to_modifier(b['Abilities']['Con'])}|{self.stat_to_modifier(b['Abilities']['Int'])}|" \
                  f"{self.stat_to_modifier(b['Abilities']['Wis'])}|{self.stat_to_modifier(b['Abilities']['Cha'])}|\n___\n"
        if len(b['Saves']) > 0:
            output += f"**Saves** :: {', '.join([s['Name'] + ' +' + str(s['Modifier']) for s in b['Saves']])}\n"
        if len(b['Skills']) > 0:
            output += f"**Skills** :: {', '.join([s['Name'] + ' +' + str(s['Modifier']) for s in b['Skills']])}\n"
        if len(b['DamageVulnerabilities']) > 0:
            output += f"**Vulnerabilities** :: {', '.join(b['DamageVulnerabilities'])}\n"
        if len(b['DamageResistances']) > 0:
            output += f"**Damage Resistances** :: {', '.join(b['DamageResistances'])}"
        if len(b['DamageImmunities']) > 0:
            output += f"**Damage Immunities** :: {', '.join(b['DamageImmunities'])}\n"
        if len(b['ConditionImmunities']) > 0:
            output += f"**Condition Immunities** :: {', '.join(b['ConditionImmunities'])}\n"
        if len(b['Senses']) > 0:
            output += f"**Senses** :: {', '.join(b['Senses'])}\n"
        if len(b['Languages']) > 0:
            output += f"**Languages** :: {', '.join(b['Languages'])}\n"
        output += f"**Challenge** :: {self.cr} ({self.xp} XP)\n___\n"
        output += ':\n'.join([f"***{trait['Name']}.*** {trait['Content']}\n" for trait in b['Traits']])

        if len(b['Actions']) > 0:
            output += "### Actions\n"
            output += ':\n'.join([f"***{action['Name']}.*** {action['Content']}\n" for action in b['Actions']])
        if len(b['Reactions']) > 0:
            output += "### Reactions\n"
            output += ':\n'.join([f"***{reaction['Name']}.*** {reaction['Content']}\n" for reaction in b['Reactions']])
        if len(b['LegendaryActions']) > 0:
            output += "### Legendary Actions\n"
            output += ':\n'.join([f"***{action['Name']}.*** {action['Content']}\n" for action in b['LegendaryActions']])
        output += "}}"
        return output

    def to_wiki(self):
        b = self.stat_block
        output = f"====== {self.name.title()} ======\n"
        output += f"//{b['Type']}//\n"
        output += "----\n"
        output += f"**Armor Class** {b['AC']['Value']}"
        if b['AC']['Notes'] != "":
            output += f" {b['AC']['Notes']}"
        output += f"\n\n**Hit Points** {b['HP']['Value']} {b['HP']['Notes']}\n\n"
        output += f"**Speed** {', '.join(b['Speed'])}\n"
        output += "----\n"
        output += "^ STR ^ DEX  ^ CON ^ INT ^ WIS ^ CHA ^\n"
        output += f"| {self.stat_to_modifier(b['Abilities']['Str'])} | {self.stat_to_modifier(b['Abilities']['Dex'])} |" \
                  f" {self.stat_to_modifier(b['Abilities']['Con'])} | {self.stat_to_modifier(b['Abilities']['Int'])} |" \
                  f" {self.stat_to_modifier(b['Abilities']['Wis'])} | {self.stat_to_modifier(b['Abilities']['Cha'])} |\n\n"
        output += "----\n"
        if len(b['Saves']) > 0:
            output += f"**Saves** {', '.join([s['Name'] + ' +' + str(s['Modifier']) for s in b['Saves']])}\n\n"
        if len(b['Skills']) > 0:
            output += f"**Skills** {', '.join([s['Name'] + ' +' + str(s['Modifier']) for s in b['Skills']])}\n\n"
        if len(b['DamageVulnerabilities']) > 0:
            output += f"**Vulnerabilities** {', '.join(b['DamageVulnerabilities'])}\n\n"
        if len(b['DamageResistances']) > 0:
            output += f"**Damage Resistances** {', '.join(b['DamageResistances'])}\n\n"
        if len(b['DamageImmunities']) > 0:
            output += f"**Damage Immunities** {', '.join(b['DamageImmunities'])}\n\n"
        if len(b['ConditionImmunities']) > 0:
            output += f"**Condition Immunities** {', '.join(b['ConditionImmunities'])}\n\n"
        if len(b['Senses']) > 0:
            output += f"**Senses** {', '.join(b['Senses'])}\n\n"
        if len(b['Languages']) > 0:
            output += f"**Languages** {', '.join(b['Languages'])}\n\n"
        output += f"**Challenge** {self.cr} ({self.xp} XP)\n\n----\n\n"
        output += '\n'.join([f"**{trait['Name']}.** {trait['Content']}\n" for trait in b['Traits']])

        sections = {'Actions': 'Actions', 'Reactions': 'Reactions', 'Legendary Actions': 'LegendaryActions',
                    'Lair Actions': 'LairActions', 'Regional Effects': 'RegionalEffects'}
        for section_name, section_key in sections.items():
            if section_key in b and len(b[section_key]) > 0:
                output += f"===== {section_name} =====\n"
                output += '\n'.join([f"**{item['Name']}.** {item['Content']}\n" for item in b[section_key]])

        output += "===== Lore =====\n\n"
        output += "===== Notes and Comments =====\n\n"
        return self.provide_link(self.italicize(output))

    @staticmethod
    def italicize(text):
        phrases = [
            "Melee or Ranged Weapon Attack",
            "Melee Weapon Attack",
            "Ranged Weapon Attack",
            "Melee Spell Attack",
            "Ranged Spell Attack",
            "Hit"]
        for phrase in phrases:
            text = text.replace(phrase, f"//{phrase}//")
        return text

    @staticmethod
    def provide_link(text):
        conditions = [
            "blinded", "charmed", "deafened", "frightened", "grappled", "incapacitated", "invisible", "paralyzed",
            "petrified", "poisoned", "prone", "restrained", "stunned", "unconscious", "exhaustion"]
        condition_url = "https://roll20.net/compendium/dnd5e/Conditions#content"
        for condition in conditions:
            text = text.replace(condition, f"[[{condition_url}|{condition}]]", 1)
        return text

    def stat_to_modifier(self, val):
        mod = (val - 10) // 2
        return f"{val}({'+' if mod >= 0 else ''}{mod})"

    def rolled_hp(self):
        try:
            dice_to_roll = self.stat_block['HP']['Notes']
        except KeyError:
            return self.stat_block['HP']['Value']
        dice_to_roll = dice_to_roll[1:-1]
        return utils.roll_dice(dice_to_roll)


def _load_mobs() -> dict[str, Mob]:
    if not os.path.exists('assets/mob_data/stat_blocks/mm_monsters.json'):
        cleanup_downloaded_json()
    with open('assets/mob_data/stat_blocks/mm_monsters.json', 'r') as f:
        mm_mobs = load(f)

    with open('assets/mob_data/stat_blocks/homebrew_monsters.json', 'r') as f:
        homebrew_mobs = load(f)

    all_mobs = homebrew_mobs | mm_mobs
    output = {}
    for _, mob_data in all_mobs.items():
        output[mob_data['Name']] = Mob(**mob_data)

    return output


MOBS = _load_mobs()

with open('assets/mob_data/environment_sets.json', 'r') as f:
    ENVIRONMENT_SETS = load(f)

class MobSet:

    def __init__(self, name: str, mobs: Sequence[Mob]):
        self.name = name
        self.mobs = mobs

    def __repr__(self):
        return f'{self.name}({[str(x) for x in self.mobs]})'


with open('assets/mob_data/mob_sets.json', 'r') as f:
    _mob_sets = load(f)
    MOB_SETS: dict[str, MobSet] = {}
    for set_key, value in _mob_sets.items():
        set_name = value['name']
        set_mobs = [MOBS[mob_name] for mob_name in value['mobs'] if mob_name in MOBS]
        MOB_SETS[set_key] = MobSet(set_name, set_mobs)

