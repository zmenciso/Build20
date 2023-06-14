import sys
import os

HEADER = '&{template:default}'


def cprint(color, string, end='\n', file=sys.stdout):
    bcolors = {
        'HEADER': '\033[95m',
        'OKBLUE': '\033[94m',
        'OKCYAN': '\033[96m',
        'OKGREEN': '\033[92m',
        'WARNING': '\033[93m',
        'FAIL': '\033[91m',
        'ENDC': '\033[0m',
        'BOLD': '\033[1m',
        'UNDERLINE': '\033[4m'
    }

    if color.upper() in bcolors:
        head = bcolors[color.upper()]
    else:
        head = f'\x1b[{color}m'

    tail = '\x1b[0m'

    print(head + string + tail, end=end, file=file)


def error(message, exitcode=None):
    cprint('0;31;40', f'ERROR: {message}', file=sys.stderr)

    if exitcode:
        sys.exit(exitcode)


def bar(header=None, char='#', length=os.get_terminal_size()[0]):
    output = ''

    if header:
        output += (length*char + '\n')
        output += (char + header.center(length-2) + char + '\n')

    output += (length*char + '\n')
    return output


def usage_build(exitcode):
    print(f'''{sys.argv[0]} [options] INPUT
    -f  --file      FILE    Write output to FILE
    -m  --modfile   FILE    Use the modifications in FILE
    -s  --spells    FILE    Also write macros for spells in FILE
    -h  --help              Print this message''')

    sys.exit(exitcode)


def usage_heal(exitcode):
    print(f'''{sys.argv[0]} [options] INPUT
    -t  --time      VALUE   Maximum amount of time (hours)
    -h  --help              Print this message''')

    sys.exit(exitcode)


def write_preamble(outfile, title, header=True):
    if outfile == sys.stdout and header:
        print(bar(title))
    elif header:
        print(bar(title, length=80), file=outfile)

    print(HEADER + '{{name= ' + title + '}}', end='', file=outfile)


def write_cap(outfile, cap='}}}'):
    print(cap + '\n', file=outfile)


def write_healing(outfile):
    write_preamble(outfile, 'Healing Potion')
    print('''{{Effect = ?{Potion| Minor, **Minor Healing Potion**
Regain [[1d8]] HP | Lesser, **Lesser Healing Potion**
Regain [[2d8+5]] HP | Moderate, **Moderate Healing Potion**
Regain [[3d8+10]] HP | Greater, **Greater Healing Potion**
Regain [[6d8+20]] HP | Major, **Major Healing Potion**
Regain [[8d8+30]] HP}}}''', file=outfile)
