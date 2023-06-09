#!/usr/bin/env python

import sys
from random import randint

from src.text import cprint, error


# Globals

STEP = False
TIME = 12
PROFICIENCY = {
    'trained': (15, 0),
    'expert': (20, 10),
    'master': (30, 30),
    'legendary': (40, 50)
    }
HEALERS = dict()
INJURED = dict()


def usage(exitcode):
    print(f'''{sys.argv[0]} [options] INPUT
    -t  --time      VALUE   Maximum amount of time (hours)
    -h  --help              Print this message''')

    sys.exit(exitcode)


def treat_wounds(prof='trained', skill=0, persist=1):
    dc, bonus = PROFICIENCY[prof]
    roll = randint(1, 20) + skill

    # Critical success
    if roll >= dc + 10:
        return persist * ((4 * randint(1, 8)) + bonus)
    elif roll >= dc:
        return persist * ((2 * randint(1, 8)) + bonus)
    else:
        return 0


def injuries_present():
    injuries = [x[1][1] - x[1][0] for x in INJURED.items()]
    return sum(injuries) > 0


def parse_input(file):
    try:
        fin = open(file)
    except Exception as e:
        error(f'Could not open {file} for reading ({e})', 2)

    for line in fin:
        if line.lower().startswith('healer'):
            skill, prof = line.strip().split()[1:]
            HEALERS[int(skill)] = prof
        elif line.lower().startswith('injured'):
            name, curr_hp, max_hp = line.strip().split()[1:]
            INJURED[name] = [int(curr_hp), int(max_hp), int(curr_hp)]


def update_injuries(char, healer, persist):
    INJURED[char][0] = min(INJURED[char][1],
                           INJURED[char][0] +
                           treat_wounds(HEALERS[healer], healer, persist))


def strategic_treat():
    # Prioritize largest gap in HP
    avail_healers = sorted(HEALERS.keys(), reverse=True)
    injured = [x[0]
               for x in sorted(INJURED.items(),
                               key=lambda x: x[1][1] - x[1][0], reverse=True)
               if x[1][1] - x[1][0] > 0]

    # Triage
    if len(injured) > len(avail_healers):
        t = 0
        while t < 60 and injured:
            char = injured.pop(0)
            healer = avail_healers.pop(0)
            update_injuries(char, healer, 1)

            if not avail_healers:
                avail_healers = sorted(HEALERS.keys(), reverse=True)
                t = t + 10

    # Fully treat
    else:
        while injured:
            char = injured.pop(0)
            healer = avail_healers.pop(0)
            update_injuries(char, healer, 2)

    return 1


# Main Execution
if __name__ == '__main__':
    args = sys.argv[1:]

    # Parse command line arguments
    while len(args) and args[0].startswith('-'):
        if args[0] == '-h' or args[0] == '--help':
            usage(0)
        elif args[0] == '-t' or args[0] == '--time':
            TIME = int(args.pop(1))
        elif args[0] == '-s' or args[0] == '--step':
            STEP = True
        else:
            usage(1)

        args.pop(0)

    if len(args) != 1:
        usage(1)

    parse_input(args[0])

    e_time = 0
    while TIME - e_time > 0 and injuries_present():
        e_time = e_time + strategic_treat()

    cprint('OKBLUE', f'Time elapsed: {e_time} hours')
    print()

    for char in INJURED:
        start = INJURED[char][2]
        end = INJURED[char][0]

        print(f'{char} | {start} --> {end} (regained {end - start} HP)')
