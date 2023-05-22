#!/usr/bin/env python

import json
import math
import sys
import os
import tools

# Globals
OUTFILE = None
MODFILE = None
HEADER = '&{template:default}'

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
def usage(exitcode):
    print(f'''{sys.argv[0]} [options] INPUT
    -f  --file      FILE    Write output to FILE
    -m  --modfile   FILE    Use the modifications in FILE
    -h  --help              Print this message''')

    sys.exit(exitcode)


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
    if not OUTFILE:
        print(tools.bar('Saving Throws'))
    else:
        print(tools.bar('Saving Throws', length=80), file=OUTFILE)

    print(HEADER + '{{name= Saving Throws}} {{Result = ?{Save', end='', file=OUTFILE)

    for throw, ability in SAVES.items():
        bonus = data['proficiencies'][throw] + data['level']
        modifier = decode_ability(data, ability)
        value = modifier + bonus + decode_modifier(modifiers, throw)
        print(f'| {throw.title()}, **{throw.title()}** [[d20 + {value}]]', end='', file=OUTFILE)

    print('}}}\n', file=OUTFILE)


def write_skills(data, modifiers):
    if not OUTFILE:
        print(tools.bar('Skills'))
    else:
        print(tools.bar('Skills', length=80), file=OUTFILE)

    print(HEADER + '{{name= Skill Check}} {{Result = ?{Skill', end='', file=OUTFILE)

    for skill in data['proficiencies']:
        if skill in SKILLS:
            value = decode_skill(data, skill) + decode_modifier(modifiers, skill)
            print(f'| {skill.title()}, **{skill.title()}** [[d20 + {value}]]', end='', file=OUTFILE)

    print('}}}\n', file=OUTFILE)


# Main Execution
if __name__ == '__main__':
    args = sys.argv[1:]

    while len(args) and args[0].startswith('-'):
        if args[0] == '-h' or args[0] == '--help':
            usage(0)
        elif args[0] == '-f' or args[0] == '--file':
            OUTFILE = args.pop(1)
        elif args[0] == '-m' or args[0] == '--modfile':
            MODFILE = args.pop(1)
        else:
            usage(1)

        args.pop(0)

    if len(args) < 1:
        usage(1)
    else:
        stats = os.path.realpath(args.pop(0))

    if OUTFILE:
        try:
            OUTFILE = open(OUTFILE, 'w')
        except Exception as e:
            tools.error(f'Could not open {OUTFILE} for writing ({e})', 3)
    else:
        OUTFILE = sys.stdout

    data = parse_json(stats)

    if MODFILE:
        modifiers = {}

        with open('mods.txt') as m:
            for line in m:
                line = line.strip().lower()
                if not line.startswith('#') and ' ' in line:
                    try:
                        modifiers[line.split()[0]] = int(line.split()[1])
                    except Exception as e:
                        tools.error(f'Unable to decode modifier {line} ({e})')
    else:
        modifiers = None

    write_skills(data, modifiers)
    write_throws(data, modifiers)
