#!/usr/bin/env python

import math
import json
import os

from src.const import SKILLS
from src.text import error


def decode_ability(data, ability):
    value = data['abilities'][ability]
    return math.floor((value - 10) / 2)


def decode_skill(data, skill):
    if skill in SKILLS:
        if data['proficiencies'][skill]:
            bonus = data['proficiencies'][skill] + data['level']
        elif 'Untrained Improvisation' in [x[0] for x in data['feats']]:
            bonus = data['proficiencies'][skill] + math.floor(data['level'] / 2)
        else:
            bonus = 0

        modifier = decode_ability(data, SKILLS[skill])

        return modifier + bonus
    else:
        return data['proficiencies'][skill] + data['level']


def decode_modifier(modifiers, field):
    if not modifiers:
        return 0

    if field in modifiers:
        return modifiers[field]
    else:
        return 0


def parse_json(infile):
    try:
        with open(infile) as j:
            data = json.loads(j.read())
    except Exception as e:
        error(f'Could not parse json ({e})', 2)

    if 'build' in data:
        return data['build']
    else:
        error('Input JSON not a valid Pathbuilder2e output', 3)


def query(prompt=None, default=None):
    '''Wait for user to input a y/n, with support for default'''

    valid = {'yes': True, 'y': True, 'ye': True, 'no': False, 'n': False}

    if default is None:
        sel = ' [y/n] '
    elif default == 'yes':
        sel = ' [Y/n] '
    elif default == 'no':
        sel = ' [y/N] '
    else:
        raise ValueError(f'Invalid default answer: {default}')

    while True:
        response = input('\033[93m' + prompt + sel + '\x1b[0m')
        if (default is not None) and len(response) == 0:
            return valid[default]
        elif response.lower() in valid:
            return valid[response.lower()]


def print_format_table():
    """
    prints table of formatted text format options
    """
    for style in range(8):
        for fg in range(30, 38):
            s1 = ''

            for bg in range(40, 48):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)

            print(s1)

        print(os.linesep)
