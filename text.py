import sys
import tools

HEADER = '&{template:default}'


def usage(exitcode):
    print(f'''{sys.argv[0]} [options] INPUT
    -f  --file      FILE    Write output to FILE
    -m  --modfile   FILE    Use the modifications in FILE
    -h  --help              Print this message''')

    sys.exit(exitcode)


def write_preamble(prompt, outfile, title=None, header=True):
    if not title:
        title = prompt

    if not outfile and header:
        print(tools.bar(title))
    elif header:
        print(tools.bar(title, length=80), file=outfile)

    print(HEADER + '{{name= ' + title + '}}', end='', file=outfile)


def write_cap(outfile, cap='}}}'):
    print(cap + '\n', file=outfile)
