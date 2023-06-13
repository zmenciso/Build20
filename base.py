import text
from data import SKILLS, SAVES
from tools import decode_ability, decode_modifier, decode_skill


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
