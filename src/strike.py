from src.text import write_preamble, fprint, write_cap


# TODO: Add support for extra damage (sneak, deadly, etc.)

RUNES = {
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
        damage = f'[[{RUNES[item["str"]]}{item["die"]} + {item["damageBonus"]}]] '

        if item['damageType'] in DAMAGE:
            damage = damage + DAMAGE[item['damageType']]

        write_preamble(outfile, f"{item['display']}", header)
        fprint('{{Attack = ?{Attack', header, file=outfile)

        for i in range(3):
            fprint(f'| Attack {i+1}, Attack {i+1} [[d20 + {item["attack"]} - {i * 5}]]',
                   header, file=outfile)
        write_cap(outfile, end='')

        fprint('{{Damage = ' + damage, header, file=outfile)
        write_cap(outfile, cap='}}')
