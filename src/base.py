from src.text import write_cap, write_preamble, fprint
from src.const import SKILLS, SAVES
from src import tools


def write_throws(data, modifiers, outfile, header):
    write_preamble(outfile, 'Saving Throws', header)
    fprint('{{Outcome = ?{Save', header, file=outfile)

    for throw, ability in SAVES.items():
        bonus = data['proficiencies'][throw] + data['level']
        modifier = tools.decode_ability(data, ability)
        value = modifier + bonus + tools.decode_modifier(modifiers, throw)
        fprint(f'| {throw.title()}, **{throw.title()}** [[d20 + {value}]]',
               header, file=outfile)

    write_cap(outfile, end=header)


def write_skills(data, modifiers, outfile, header):
    write_preamble(outfile, 'Skill Check', header)
    fprint('{{Outcome = ?{Skill', header, file=outfile)

    for skill in data['proficiencies']:
        if skill in SKILLS:
            value = tools.decode_skill(data, skill) + \
                    tools.decode_modifier(modifiers, skill)
            fprint(f'| {skill.title()}, **{skill.title()}** [[d20 + {value}]]',
                   header, file=outfile)

    write_cap(outfile, end=header)


def write_healing(outfile, header):
    write_preamble(outfile, 'Healing Potion', header)

    fprint('''{{Effect = ?{Potion| Minor, **Minor Healing Potion**
Regain [[1d8]] HP | Lesser, **Lesser Healing Potion**
Regain [[2d8+5]] HP | Moderate, **Moderate Healing Potion**
Regain [[3d8+10]] HP | Greater, **Greater Healing Potion**
Regain [[6d8+20]] HP | Major, **Major Healing Potion**
Regain [[8d8+30]] HP''', header, file=outfile)

    write_cap(outfile, end=header)
