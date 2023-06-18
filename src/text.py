import sys
import re
import os

TEMPLATE = '&{template:default}'
NEWLINE = '$newline'


def cprint(color, string, end=os.linesep, file=sys.stdout):
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


def fprint(string, header, file=sys.stdout):
    if not header:
        print(re.sub(os.linesep, NEWLINE, string), end='', file=file)
    else:
        print(string, end='', file=file)


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


def write_preamble(outfile, title, header=True):
    if outfile == sys.stdout and header:
        print(bar(title))
    elif header:
        print(bar(title, length=80), file=outfile)
    else:
        print('#', file=outfile)

    print(TEMPLATE + '{{name= ' + title + '}}', end='', file=outfile)


def write_cap(outfile, cap='}}}', end=os.linesep):
    if end:
        print(cap + end, file=outfile, end=end)
    else:
        print(cap, file=outfile, end=end)
