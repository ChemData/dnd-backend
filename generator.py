from copy import deepcopy, copy
from typing import Union, List, Optional, Sequence
from random import shuffle, choices
import pandas as pd

import utils
from mob_sets import Mob, ENVIRONMENT_SETS, MOB_SETS, MobSet
from utils import to_numeric_cr


NUMBER_MULTIPLIER = {1: 1, 2:1.5, 3:2, 4:2, 5:2, 6:2, 7:2.5, 8:2.5, 9:2.5, 10:2.5, 11:3, 12:3, 13:3, 14:3, 15:4}
DIFFICULTY_TABLE = pd.DataFrame(
    {'easy': [25, 50, 75, 125, 250, 300, 350, 450, 550, 600, 800, 1000, 1100, 1250, 1400, 1600, 2000, 2100, 2400, 2800],
     'medium': [50, 100, 150, 250, 500, 600, 750, 900, 1100, 1200, 1600, 2000, 2200, 2500, 2800, 3200, 3900, 4200, 4900, 5700],
     'hard': [75, 150, 225, 375, 750, 900, 1100, 1400, 1600, 1900, 2400, 3000, 3400, 3800, 4300, 4800, 5900, 6300, 7300, 8500],
     'deadly': [100, 200, 400, 500, 1100, 1400, 1700, 2100, 2400, 2800, 3600, 4500, 5100, 5700, 6400, 7200, 8800, 9500, 10900, 12700]},
    index=range(1, 21)
)


def bold(text: str):
    return '\033[1m' + text + '\033[0m'


class Group:

    def __init__(self, mobs: Optional[List[Mob]] = None):
        self.mobs = []
        self.xp_total = 0
        if mobs is not None:
            self.add(mobs)

    def __repr__(self):
        if len(self) == 0:
            return 'Group()'
        mob_count = count_values(self.mobs)
        output = 'Group('
        for mob, count in mob_count.items():
            if count > 1:
                output += f'{count}x'
            output += f'{mob}, '
        output = output[:-2] + f')[{self.xp_total}]'
        return output

    def simple_repr(self):
        mob_count = count_values(self.mobs)
        output = ''
        for mob, count in mob_count.items():
            output += f'{count} '
            output += f'{bold(mob.name.capitalize())}'
            if count > 1:
                output += bold('s')
            output += ', '
        output = output[:-2]
        return output

    def add(self, new_mobs: Union[Mob, List[Mob]]):
        if type(new_mobs) == Mob:
            new_mobs = [new_mobs]
        self.mobs += new_mobs
        self.xp_total = sum([mob.xp for mob in self.mobs]) * NUMBER_MULTIPLIER.get(len(self.mobs), 4)
        self.mobs.sort(key=lambda mob: mob.num_cr, reverse=True)

    def __eq__(self, other):
        if tuple(self.mobs) == tuple(other.mobs):
            return True
        return False

    def __hash__(self):
        return hash(tuple(self.mobs))

    def __getitem__(self, index):
        return self.mobs[index]

    def __len__(self):
        return len(self.mobs)

    def html_with_links(self, random_hp=False):
        mob_count = count_values(self.mobs)
        output = []
        for mob, count in mob_count.items():
            if random_hp:
                rolls = [mob.rolled_hp() for _ in range(count)]
                hp_str = f' hp = {rolls}'
            else:
                hp_str = ''
            link = mob.url
            if link is None:
                output.append(f'<p>{count} x {mob.name.capitalize()+ hp_str}</p>')
            else:
                output.append(f'<p>{count} x <a href="{link}" target="_blank">{mob.name.capitalize()}</a>{hp_str}</p>')
            output.append('\n')
        output = ''.join(output)
        output = output[:-1]
        return output


# Need a function that just generates a single group with the desired characteristics

def unique_group(
        mobs: Sequence[Mob],
        party: list[int],
        difficulty: str,
        max_num: Optional[int] = 20,
        min_cr: Optional[str] = None,
        existing_groups: Optional[List[Group]] = None) -> (List[Group], int):
    """Generate a single Group of Mobs that fits the desired characteristics and is different from
        other provided Groups."""
    if len(mobs) == 0:
        raise ValueError('No encounter can be generated because mobs is empty. There must be at least one.')
    if existing_groups is None:
        existing_groups = set()
    else:
        existing_groups = set(existing_groups)
    min_val, max_val = difficulty_range(party, difficulty)
    if min_cr is not None:
        mobs = [mob for mob in mobs if mob.num_cr >= to_numeric_cr(min_cr)]
    redundant_generations = 0
    while redundant_generations < 500:
        try:
            new_group = add_mobs(Group(), mobs, min_val, max_val, max_num)
            if new_group not in existing_groups:
                return new_group
        except NoLegalGroups:
            pass
        redundant_generations += 1
    raise NoUniqueGroup


def add_mobs(group: Group, mobs: List[Mob], min_val, max_val, max_num: Optional[int]=None):
    if max_num is not None and len(group) > max_num:
        raise NoLegalGroups
    options = copy(mobs)
    if group.xp_total >= min_val:
        options += [None]
    shuffle(options)
    for pick in options:
        if pick is None:
            return group
        new_group = deepcopy(group)
        new_group.add(pick)
        if new_group.xp_total > max_val:
            continue
        else:
            complete_group = add_mobs(new_group, mobs, min_val, max_val, max_num)
            return complete_group
    raise NoLegalGroups


class NoLegalGroups(Exception):

    def __init__(self):
        pass


class NoUniqueGroup(Exception):

    def __init__(self):
        pass


def enumerate_groups(
        mobs: List[Mob],
        party: List[int],
        difficulty: str,
        max_num: int = 20,
        min_cr: Optional[str] = None) -> List[Group]:
    xp_lower_limit, xp_upper_limit = difficulty_range(party, difficulty)
    if min_cr is not None:
        mobs = [mob for mob in mobs if mob.num_cr >= to_numeric_cr(min_cr)]

    active = {Group()}
    finished = set()
    while len(active) > 0:
        add_to = active.pop()
        for mob in mobs:
            new = deepcopy(add_to)
            new.add(copy(mob))
            if xp_lower_limit <= new.xp_total <= xp_upper_limit and new not in finished:
                finished.add(new)
            if new.xp_total < xp_upper_limit and new not in active:
                if max_num is None or len(new.mobs) < max_num:
                    active.add(new)
    finished = list(finished)
    finished.sort(key=lambda x: x.xp_total, reverse=True)
    return finished


def difficulty_range(party: List[int], difficulty: str) -> (float, float):
    """Return the lower and upper """
    xp_lower_limit = DIFFICULTY_TABLE.loc[party, difficulty].sum()
    if difficulty == 'easy':
        xp_upper_limit = DIFFICULTY_TABLE.loc[party, 'medium'].sum()
    if difficulty == 'medium':
        xp_upper_limit = DIFFICULTY_TABLE.loc[party, 'hard'].sum()
    if difficulty == 'hard':
        xp_upper_limit = DIFFICULTY_TABLE.loc[party, 'deadly'].sum()
    if difficulty == 'deadly':
        xp_upper_limit = xp_lower_limit * 1.6
    xp_upper_limit -= 1
    return xp_lower_limit, xp_upper_limit


def count_values(list_to_count):
    output = {}
    for v in list_to_count:
        output[v] = output.get(v, 0) + 1
    return output


def single_encounter(
        difficulty: utils.Difficulty | utils.DifficultySet,
        party: List[int],
        mob_sets: Sequence[MobSet],
        set_weights: Optional[Sequence[float]] = None,
        max_mobs: Optional[int] = None,
        min_cr: Optional[str] = None
) -> tuple[Group, str, str]:
    """
    Generate a single encounter. The encounter will consist of a single mob set.
    :param difficulty: How hard the encounter is. Can either be a specific difficulty or a named distribution.
    :param party: List of levels of the party members.
    :param mob_sets: Which mob sets to pick from. The Key is the name of the mob set, the value is a list of mobs
        in that set.
    :param set_weights: A list of weights to apply to the mob sets when picking which to use. If None, will pick
        from them equally.
    :param max_mobs: The maximum number of mobs to include in the encounter. If None, there is no upper limit.
    :param min_cr: The minimum CR of mobs to include in the encounter. If None, no limit is applied.
    :return:
    """
    if set_weights is None:
        set_weights = [1] * len(mob_sets)
    mob_set = choices(list(mob_sets), set_weights)[0]
    distributions = {
        'peaceful': [10, 0, 0, 0],
        'tamed': [7, 3, 0, 0],
        'untamed': [4, 3, 2, 1],
        'dangerous': [1, 3, 4, 2],
        'inhospitable': [1, 2, 5, 2],
        'alien': [1, 1, 4, 4]
    }
    if difficulty in utils.DifficultySets:
        difficulty = choices(['easy', 'medium', 'hard', 'deadly'], distributions[difficulty])[0]
    group = unique_group(mob_set.mobs, party, difficulty, max_mobs, min_cr)
    return group, difficulty, mob_set.name


def hex_encounter(
        difficulty: utils.Difficulty | utils.DifficultySet,
        party: List[int],
        primary_enemy: Optional[str] = None,
        environment_type: Optional[str] = None,
        max_mobs: Optional[int] = None,
        min_cr: Optional[str] = None
) -> (Group, str, str):
    """
    Generate a single encounter. The encounter will consist of a single mob set.
    :param difficulty: How hard the encounter is: 'easy', 'medium', 'hard', 'deadly', or 'random'. Random
        picks a difficulty from a distribution.
    :param party: List of levels of the party members.
    :param primary_enemy: The name of the main enemy type in the hex. If not None, it will picked half the time
        if there is also an environment specified.
    :param environment_type: The name of the environment to pull mob sets from. If not None, one of these will be
        picked half the time if there is also a primary_enemy specified.
    :param max_mobs: The maximum number of mobs to include in the encounter. If None, there is no upper limit.
    :param min_cr: The minimum CR of mobs to include in the encounter. If None, no limit is applied.
    :return: The group of mobs
    :return: The difficulty of the encounter (this is useful if the difficulty was selected randomly)
    :return: The name of the mob set that was used.
    """
    if primary_enemy is None and environment_type is None:
        raise ValueError('Either primary_enemy or environment_type must be non-None.')
    mob_sets = []
    weights = []
    if environment_type is not None:
        mob_sets = [MOB_SETS[set_name] for set_name in ENVIRONMENT_SETS[environment_type]['mob_sets']]
        weights = [1] * len(mob_sets)
    if primary_enemy is not None:
        mob_sets += [MOB_SETS[primary_enemy]]
        weights += [max(1, len(weights))]

    return single_encounter(difficulty, party, mob_sets, weights, max_mobs, min_cr)


def format_roll_table_for_homebrewery(table: List, table_name: str, table_start: int = 1):
    output = f"{{{{wide\n##### {table_name}\n"
    output += "| Roll | Encounter | Difficulty | Theme |\n|:---|:---------------------:|:-------:|:-------:|\n"
    for row in table:
        output += f"|{table_start}\t|{row[0].simple_repr()}\t|{row[1].capitalize()}\t|{row[2].capitalize()}\t|\n"
        table_start += 1
    output += "}}\n"
    return output


def combat_difficulty(party: List[int], mob_set):
    if type(mob_set[0]) == int or type(mob_set[0]) == str:
        mob_set = Group([Mob(f'cr{x}', x) for x in mob_set])
    for difficulty in ['easy', 'medium', 'hard', 'deadly']:
        low_xp, high_xp = difficulty_range(party, difficulty)
        if difficulty == 'easy' and mob_set.xp_total < low_xp:
            return 'so easy'
        if low_xp <= mob_set.xp_total <= high_xp:
            return difficulty
    return 'beyond deadly'
