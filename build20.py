#!/usr/bin/env python

import json
import sys
import os

from src import text
from src import base
from src import strike
from src import spells

# Globals
OUTFILE = None
HEADER = '\n'


# Functions
def parse_json(infile):
    try:
        with open(infile) as j:
            data = json.loads(j.read())
    except Exception as e:
        text.error(f'Could not parse json ({e})', 2)

    if 'build' in data:
        return data['build']
    else:
        text.error('Input JSON not a valid Pathbuilder2e output', 3)


# Main Execution
if __name__ == '__main__':
    args = sys.argv[1:]
    fout = None
    fmod = None
    spellfile = None

    while len(args) and args[0].startswith('-'):
        if args[0] == '-h' or args[0] == '--help':
            text.usage_build(0)
        elif args[0] == '-f' or args[0] == '--file':
            fout = args.pop(1)
        elif args[0] == '-m' or args[0] == '--modfile':
            fmod = args.pop(1)
        elif args[0] == '-n' or args[0] == '--noheader':
            HEADER = None
        elif args[0] == '-s' or args[0] == '--spells':
            spellfile = args.pop(1)
        else:
            text.usage_build(1)

        args.pop(0)

    if len(args) < 1:
        text.usage_build(1)
    else:
        stats = os.path.realpath(args.pop(0))

    if fout:
        try:
            OUTFILE = open(fout, 'w')
        except Exception as e:
            text.error(f'Could not open file "{fout}" for writing ({e})', 3)
    else:
        OUTFILE = sys.stdout

    data = parse_json(stats)

    if fmod:
        modifiers = {}

        try:
            m = open(fmod)
        except Exception as e:
            text.error(f'Could not open file "{fmod}" ({e})', 4)

        for line in m:
            line = line.strip().lower()
            if not line.startswith('#') and line:
                try:
                    modifiers[line.split()[0]] = int(line.split()[1])
                except Exception as e:
                    text.error(f'Unable to decode modifier "{line}" ({e})')

    else:
        modifiers = None

    base.write_skills(data, modifiers, OUTFILE, HEADER)
    base.write_throws(data, modifiers, OUTFILE, HEADER)
    strike.write_strike(data, modifiers, OUTFILE, HEADER)
    text.write_healing(OUTFILE, HEADER)

    if spellfile:
        spells.write_spells(spellfile, data, modifiers, OUTFILE, HEADER)

    if OUTFILE is not sys.stdout:
        text.cprint('OKGREEN', f'Successfully wrote "{fout}"')
