#!/usr/bin/env python

import sys
import os

from src.tools import parse_json
from src.text import error, cprint
from src.base import write_skills, write_throws, write_healing
from src.strike import write_strike
from src.spells import write_spells

# Globals
OUTFILE = None
HEADER = os.linesep


# Functions
def usage(exitcode):
    print(f'''{sys.argv[0]} [options] INPUT
    -f  --file      FILE    Write output to FILE
    -m  --modfile   FILE    Use the modifications in FILE
    -s  --spells    FILE    Also write macros for spells in FILE
    -n  --noheader          Do not print headers (useful for Roll20 API)
    -h  --help              Print this message''')

    sys.exit(exitcode)


# Main Execution
if __name__ == '__main__':
    args = sys.argv[1:]
    fout = None
    fmod = None
    spellfile = None

    while len(args) and args[0].startswith('-'):
        if args[0] == '-h' or args[0] == '--help':
            usage(0)
        elif args[0] == '-f' or args[0] == '--file':
            fout = args.pop(1)
        elif args[0] == '-m' or args[0] == '--modfile':
            fmod = args.pop(1)
        elif args[0] == '-n' or args[0] == '--noheader':
            HEADER = None
        elif args[0] == '-s' or args[0] == '--spells':
            spellfile = args.pop(1)
        else:
            usage(1)

        args.pop(0)

    if len(args) < 1:
        usage(1)
    else:
        stats = os.path.realpath(args.pop(0))

    if fout:
        try:
            OUTFILE = open(fout, 'w')
        except Exception as e:
            error(f'Could not open file "{fout}" for writing ({e})', 3)
    else:
        OUTFILE = sys.stdout

    data = parse_json(stats)

    if fmod:
        modifiers = {}

        try:
            m = open(fmod)
        except Exception as e:
            error(f'Could not open file "{fmod}" ({e})', 4)

        for line in m:
            line = line.strip().lower()
            if not line.startswith('#') and line:
                try:
                    modifiers[line.split()[0]] = int(line.split()[1])
                except Exception as e:
                    error(f'Unable to decode modifier "{line}" ({e})')

    else:
        modifiers = None

    write_skills(data, modifiers, OUTFILE, HEADER)
    write_throws(data, modifiers, OUTFILE, HEADER)
    write_strike(data, modifiers, OUTFILE, HEADER)
    write_healing(OUTFILE, HEADER)

    if spellfile:
        write_spells(spellfile, data, modifiers, OUTFILE, HEADER)

    if OUTFILE is not sys.stdout:
        cprint('OKGREEN', f'Successfully wrote "{fout}"')
