#!/usr/bin/env python

import json
import math
import sys
import os

import tools
import text

# Globals
OUTFILE = None

SAVES = {
    'will': 'wis',
    'fortitude': 'con',
    'reflex': 'dex'
    }

SKILLS = {
    'acrobatics': 'dex',
    'arcana': 'int',
    'athletics': 'str',
    'crafting': 'int',
    'deception': 'cha',
    'diplomacy': 'cha',
    'intimidation': 'cha',
    'lore': 'int',
    'medicine': 'wis',
    'nature': 'wis',
    'occultism': 'int',
    'performance': 'cha',
    'religion': 'wis',
    'society': 'int',
    'stealth': 'dex',
    'survival': 'wis',
    'thievery': 'dex'
    }


# Functions
def parse_json(infile):
    try:
        with open(infile) as j:
            data = json.loads(j.read())
    except Exception as e:
        tools.error(f'Could not parse json ({e})', 2)

    if 'build' in data:
        return data['build']
    else:
        tools.error('Input JSON not a valid Pathbuilder2e output', 3)


def decode_ability(data, ability):
    value = data['abilities'][ability]
    return math.floor((value - 10) / 2)


def decode_skill(data, skill):
    if skill in SKILLS:
        bonus = data['proficiencies'][skill] + data['level']
        modifier = decode_ability(data, SKILLS[skill])
        return modifier + bonus
    else:
        return None


def decode_modifier(modifiers, field):
    if not modifiers:
        return 0

    if field in modifiers:
        return modifiers[field]
    else:
        return 0


def write_throws(data, modifiers):
    text.write_preamble('Save', OUTFILE, 'Saving Throws')
    print('{{Outcome = ?{Save', end='', file=OUTFILE)

    for throw, ability in SAVES.items():
        bonus = data['proficiencies'][throw] + data['level']
        modifier = decode_ability(data, ability)
        value = modifier + bonus + decode_modifier(modifiers, throw)
        print(f'| {throw.title()}, **{throw.title()}** [[d20 + {value}]]', end='', file=OUTFILE)

    text.write_cap(OUTFILE)


def write_skills(data, modifiers):
    text.write_preamble('Skill', OUTFILE, 'Skill Check')
    print('{{Outcome = ?{Skill', end='', file=OUTFILE)

    for skill in data['proficiencies']:
        if skill in SKILLS:
            value = decode_skill(data, skill) + decode_modifier(modifiers, skill)
            print(f'| {skill.title()}, **{skill.title()}** [[d20 + {value}]]', end='', file=OUTFILE)

    text.write_cap(OUTFILE)


def write_strike(data, modifiers):
    for item in data['weapons']:
        prof = item['prof']
        mod = data['proficiencies'][prof] + data['level'] + item['pot']
        strength = decode_ability(data, 'str')
        dex = decode_ability(data, 'dex')

        text.write_preamble('Melee Strike', OUTFILE, item['display'])
        print('{{Attack = ?{Attack', end='', file=OUTFILE)
        for i in range(3):
            print(f'| Attack {i+1}, Attack {i+1} [[d20 + {mod} + {strength} - {i * 5}]]',
                  end='', file=OUTFILE)
        print('}}}', end='', file=OUTFILE)
        print('{{Damage = ' + f'[[{item["die"]} + {strength}]]' + '}}')

        print('\nIf RANGED, use:', file=OUTFILE)
        text.write_preamble('Ranged Strike', OUTFILE, item['display'], header=False)
        print('{{Attack = ?{Attack', end='', file=OUTFILE)
        for i in range(3):
            print(f'| Attack {i+1}, Attack {i+1} [[d20 + {mod} + {dex} - {i * 5}]]',
                  end='', file=OUTFILE)
        print('}}}', end='', file=OUTFILE)
        print('{{Damage = ' + f'[[{item["die"]} + {dex}]]' + '}}\n')


# Main Execution
if __name__ == '__main__':
    args = sys.argv[1:]
    fout = None
    fmod = None

    while len(args) and args[0].startswith('-'):
        if args[0] == '-h' or args[0] == '--help':
            text.usage(0)
        elif args[0] == '-f' or args[0] == '--file':
            fout = args.pop(1)
        elif args[0] == '-m' or args[0] == '--modfile':
            fmod = args.pop(1)
        else:
            text.usage(1)

        args.pop(0)

    if len(args) < 1:
        text.usage(1)
    else:
        stats = os.path.realpath(args.pop(0))

    if fout:
        try:
            OUTFILE = open(fout, 'w')
        except Exception as e:
            tools.error(f'Could not open file "{fout}" for writing ({e})', 3)
    else:
        OUTFILE = sys.stdout

    data = parse_json(stats)

    if fmod:
        modifiers = {}

        try:
            m = open(fmod)
        except Exception as e:
            tools.error(f'Could not open file "{fmod}" ({e})', 4)

        for line in m:
            line = line.strip().lower()
            if not line.startswith('#') and line:
                try:
                    modifiers[line.split()[0]] = int(line.split()[1])
                except Exception as e:
                    tools.error(f'Unable to decode modifier "{line}" ({e})')

    else:
        modifiers = None

    write_skills(data, modifiers)
    write_throws(data, modifiers)
    write_strike(data, modifiers)
    text.write_healing(OUTFILE)

    if OUTFILE is not sys.stdout:
        tools.cprint('OKGREEN', f'Successfully wrote "{fout}"')
