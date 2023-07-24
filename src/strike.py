from src.text import write_preamble, fprint, write_cap
from src.const import RUNES


# TODO: Add support for extra damage (sneak, deadly, etc.)
# TODO: Deal with crits better
# TODO: Add support for agile, finesse

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

SNEAK = {
    0: '[[1d6]] precision',
    1: '[[2d6]] precision',
    2: '[[3d6]] precision',
    3: '[[4d6]] precision'
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
            sneak_damage = SNEAK[(data['level'] + 1) // 6]
            fprint('?{Sneak? | Yes, \n' + sneak_damage + '| No, \nNo sneak attack}',
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
