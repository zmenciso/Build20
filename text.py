import sys
import tools

HEADER = '&{template:default}'


def usage(exitcode):
    print(f'''{sys.argv[0]} [options] INPUT
    -f  --file      FILE    Write output to FILE
    -m  --modfile   FILE    Use the modifications in FILE
    -h  --help              Print this message''')

    sys.exit(exitcode)


def write_preamble(outfile, title, header=True):
    if outfile == sys.stdout and header:
        print(tools.bar(title))
    elif header:
        print(tools.bar(title, length=80), file=outfile)

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
Regain [[8d8+30]] HP}}}''')
