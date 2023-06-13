import yaml
import re

import text
from tools import decode_ability, decode_skill, decode_modifier
from data import STATS


def parse_yaml(infile):
    try:
        with open(infile) as y:
            data = yaml.safe_load(y)
    except Exception as e:
        text.error(f'Could not parse yaml ({e})', 2)

    return data


def substitute(string, bonus, dc, data):
    string = re.sub('\\$attack', bonus, string)
    string = re.sub('\\$dc', dc, string)

    for stat in STATS:
        string = re.sub(f'\\${stat}', str(decode_ability(data, stat)), string)

    return string


def write_spells(infile, stats, modifiers, outfile):
    data = parse_yaml(infile)
    casting_stat = data['Character']['Casting_stat'].lower()
    casting_type = 'casting' + data['Character']['Casting_type'].title()

    bonus = decode_skill(stats, casting_type) + \
        decode_ability(stats, casting_stat) + \
        decode_modifier(modifiers, data['Character']['Casting_type'])
    dc = bonus + 10

    bonus = str(bonus)
    dc = str(dc)

    for spell, details in data['Spells'].items():
        text.write_preamble(outfile, spell)

        for title, content in details.items():
            print('{{' + title + '= ', end='', file=outfile)
            print(substitute(content, bonus, dc, stats), end='', file=outfile)
            print('}}', end='', file=outfile)
