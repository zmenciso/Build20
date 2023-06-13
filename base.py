import text
from tools import decode_ability, decode_modifier, decode_skill


SAVES = {
    'will': 'wis',
    'fortitude': 'con',
    'reflex': 'dex'
    }

SKILLS = {
    'acrobatics': 'dex',
    'arcana': 'int',
    'athletics': 'str',
    'crafting': 'int',
    'deception': 'cha',
    'diplomacy': 'cha',
    'intimidation': 'cha',
    'lore': 'int',
    'medicine': 'wis',
    'nature': 'wis',
    'occultism': 'int',
    'performance': 'cha',
    'religion': 'wis',
    'society': 'int',
    'stealth': 'dex',
    'survival': 'wis',
    'thievery': 'dex'
    }


def write_throws(data, modifiers, outfile):
    text.write_preamble(outfile, 'Saving Throws')
    print('{{Outcome = ?{Save', end='', file=outfile)

    for throw, ability in SAVES.items():
        bonus = data['proficiencies'][throw] + data['level']
        modifier = decode_ability(data, ability)
        value = modifier + bonus + decode_modifier(modifiers, throw)
        print(f'| {throw.title()}, **{throw.title()}** [[d20 + {value}]]',
              end='', file=outfile)

    text.write_cap(outfile)


def write_skills(data, modifiers, outfile):
    text.write_preamble(outfile, 'Skill Check')
    print('{{Outcome = ?{Skill', end='', file=outfile)

    for skill in data['proficiencies']:
        if skill in SKILLS:
            value = decode_skill(data, skill) + decode_modifier(modifiers, skill)
            print(f'| {skill.title()}, **{skill.title()}** [[d20 + {value}]]',
                  end='', file=outfile)

    text.write_cap(outfile)
