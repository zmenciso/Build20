import text
from tools import decode_ability

def write_strike(data, modifiers, outfile):
    for item in data['weapons']:
        prof = item['prof']
        mod = data['proficiencies'][prof] + data['level'] + item['pot']
        strength = decode_ability(data, 'str')
        dex = decode_ability(data, 'dex')

        text.write_preamble(outfile, item['display'])
        print('{{Attack = ?{Attack', end='', file=outfile)
        for i in range(3):
            print(f'| Attack {i+1}, Attack {i+1} [[d20 + {mod} + {strength} - {i * 5}]]',
                  end='', file=outfile)
        print('}}}', end='', file=outfile)
        print('{{Damage = ' + f'[[{item["die"]} + {strength}]]' + '}}')

        print('\nIf RANGED, use:', file=outfile)
        text.write_preamble(outfile, item['display'], header=False)
        print('{{Attack = ?{Attack', end='', file=outfile)
        for i in range(3):
            print(f'| Attack {i+1}, Attack {i+1} [[d20 + {mod} + {dex} - {i * 5}]]',
                  end='', file=outfile)
        print('}}}', end='', file=outfile)
        print('{{Damage = ' + f'[[{item["die"]} + {dex}]]' + '}}\n')


