from src import text
from src import tools


def write_strike(data, modifiers, outfile, header):
    for item in data['weapons']:
        prof = item['prof']
        mod = data['proficiencies'][prof] + data['level'] + item['pot'] + \
            tools.decode_modifier(modifiers, item)

        strength = tools.decode_ability(data, 'str')
        dex = tools.decode_ability(data, 'dex')

        text.write_preamble(outfile, f"MELEE {item['display']}", header)
        print('{{Attack = ?{Attack', end='', file=outfile)
        for i in range(3):
            print(f'| Attack {i+1}, Attack {i+1} [[d20 + {mod} + {strength} - {i * 5}]]',
                  end='', file=outfile)
        print('}}}', end='', file=outfile)
        print('{{Damage = ' + f'[[{item["die"]} + {strength}]]' + '}}')

        text.write_preamble(outfile, f"RANGED {item['display']}", header)
        print('{{Attack = ?{Attack', end='', file=outfile)
        for i in range(3):
            print(f'| Attack {i+1}, Attack {i+1} [[d20 + {mod} + {dex} - {i * 5}]]',
                  end='', file=outfile)
        print('}}}', end='', file=outfile)
        print('{{Damage = ' + f'[[{item["die"]} + {dex}]]' + '}}\n')
