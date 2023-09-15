from src.text import write_preamble, fprint, write_cap
from src.const import RUNES, DEADLY, FATAL, AGILE


STRIKING = {
    '': 1,
    'striking': 2,
    'greaterStriking': 3,
    'majorStriking': 4
    }

DAMAGE = {
    'S': 'slashing',
    'P': 'piercing',
    'B': 'bludgeoning'
    }


def write_strike(data, modifiers, outfile, header):
    for item in data['weapons']:
        damage = f'[[{STRIKING[item["str"]]}{item["die"]} + {item["damageBonus"]}[BONUS]]]'
        mc_pen = 4 if item['name'] in AGILE else 5

        if item['damageType'] in DAMAGE:
            damage = damage + ' ' + DAMAGE[item['damageType']]

        write_preamble(outfile, f"{item['display']}", header)
        fprint('{{Attack = ?{Attack', header, file=outfile)

        for i in range(3):
            fprint(f'| Attack {i+1}, Attack {i+1} [[d20 + {item["attack"]}[MODIFIER] - {i * mc_pen}[MULTIATTACK]]]',
                   header, file=outfile)
        write_cap(outfile, end='')

        fprint('{{Damage = ' + damage, header, file=outfile)

        if 'Sneak Attack' in data['specials']:
            sneak_damage = ((data['level'] + 1) // 6) + 1
            sneak_damage = f'[[{sneak_damage}d6]] precision'
            fprint('?{Sneak? | Yes, \n' + sneak_damage + '| No, \nNo sneak attack}',
                   header, file=outfile)

        if item['name'] in DEADLY:
            write_cap(outfile, cap='}}', end='')
            deadly_damage = f'{STRIKING[item["str"]]}{DEADLY[item["name"]]}'
            fprint('{{Deadly = ', header, file=outfile)
            fprint(f'[[{deadly_damage}]] additional crit damage',
                   header, file=outfile)
        elif item['name'] in FATAL:
            write_cap(outfile, cap='}}', end='')
            fatal_damage = f'{STRIKING[item["str"]]}{FATAL[item["name"]]} * 2'
            fprint('{{Fatal = ', header, file=outfile)
            fprint(f'[[({fatal_damage}) + {FATAL[item["name"]]}]] damage on crit',
                   header, file=outfile)

        if len(item['runes']) > 0:

            for rune in item['runes']:
                write_cap(outfile, cap='}}', end='')
                if rune in RUNES:
                    desc = RUNES[rune]
                else:
                    desc = 'No description'

                fprint('{{' + f'{rune} = ' + desc, header, file=outfile)

        write_cap(outfile, cap='}}', end=header)
