#!/usr/bin/env python

import json
import sys
import os

import tools
import text
from base import write_skills, write_throws
from strike import write_strike
from spells import write_spells

# Globals
OUTFILE = None


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

    if spellfile:
        pass

    if OUTFILE is not sys.stdout:
        tools.cprint('OKGREEN', f'Successfully wrote "{fout}"')
