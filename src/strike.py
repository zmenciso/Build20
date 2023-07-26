from src.text import write_preamble, fprint, write_cap
from src.const import RUNES, DEADLY, FATAL


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
        damage = f'[[{STRIKING[item["str"]]}{item["die"]} + {item["damageBonus"]}]] '

        if item['damageType'] in DAMAGE:
            damage = damage + DAMAGE[item['damageType']]

        write_preamble(outfile, f"{item['display']}", header)
        fprint('{{Attack = ?{Attack', header, file=outfile)

        for i in range(3):
            fprint(f'| Attack {i+1}, Attack {i+1} [[d20 + {item["attack"]} - {i * 5}]]',
                   header, file=outfile)
        write_cap(outfile, end='')

        fprint('{{Damage = ' + damage, header, file=outfile)

        if 'Sneak Attack' in data['specials']:
            sneak_damage = ((data['level'] + 1) // 6) + 1
            sneak_damage = f'[[{sneak_damage}d6]] precision'
            fprint('?{Sneak? | Yes, \n' + sneak_damage + '| No, \nNo sneak attack}',
                   header, file=outfile)

        write_cap(outfile, cap='}}', end='')

        if item['name'] in DEADLY:
            deadly_damage = f'{STRIKING[item["str"]]}{DEADLY[item["name"]]}'
            fprint('{{Deadly = ', header, file=outfile)
            fprint(f'[[{deadly_damage}]] additional crit damage',
                   header, file=outfile)
        elif item['name'] in FATAL:
            fatal_damage = f'{STRIKING[item["str"]] + 1}{FATAL[item["name"]]}'
            fatal_damage = fatal_damage + f' + {item["damageBonus"]}'
            fprint('{{Fatal = ', header, file=outfile)
            fprint(f'[[{fatal_damage}]] damage on crit',
                   header, file=outfile)

        if len(item['runes']) > 0:
            write_cap(outfile, cap='}}', end='')

            for rune in item['runes']:
                if rune in RUNES:
                    desc = RUNES[rune]
                else:
                    desc = 'No description'

                fprint('{{' + f'{rune} = ' + desc, header, file=outfile)
                write_cap(outfile, cap='}}', end='')

            write_cap(outfile, cap='')

        else:
            write_cap(outfile, cap='}}')
