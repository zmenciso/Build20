import os

from src.text import write_preamble, fprint, write_cap
from src import tools


def write_strike(data, modifiers, outfile, header):
    for item in data['weapons']:
        prof = item['prof']
        mod = data['proficiencies'][prof] + data['level'] + item['pot'] + \
            tools.decode_modifier(modifiers, item)

        strength = tools.decode_ability(data, 'str')
        dex = tools.decode_ability(data, 'dex')

        write_preamble(outfile, f"MELEE {item['display']}", header)
        fprint('{{Attack = ?{Attack', header, file=outfile)

        for i in range(3):
            fprint(f'| Attack {i+1}, Attack {i+1} [[d20 + {mod} + {strength} - {i * 5}]]',
                   header, file=outfile)

        write_cap(outfile, end='')
        fprint('{{Damage = ' + f'[[{item["die"]} + {strength}]]' + '}}',
               header, file=outfile)

        write_preamble(outfile, f"RANGED {item['display']}", header)
        fprint('{{Attack = ?{Attack', header, file=outfile)

        for i in range(3):
            print(f'| Attack {i+1}, Attack {i+1} [[d20 + {mod} + {dex} - {i * 5}]]',
                  end='', file=outfile)

        write_cap(outfile, end='')
        fprint('{{Damage = ' + f'[[{item["die"]} + {dex}]]' + '}}' + os.linesep,
               header, file=outfile)
