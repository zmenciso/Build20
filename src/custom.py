import re

from src.tools import parse_yaml, decode_ability, decode_modifier, decode_skill
from src.text import write_preamble, write_cap, fprint

MATCHES = {
    'abilities': re.compile(r'(\$abl_[A-Za-z]+)'),
    'skills': re.compile(r'(\$skl_[A-Za-z]+)'),
    'mods': re.compile(r'(\$mod_[A-Za-z]+)'),
    'weapons': re.compile(r'(\$wep_[0-9]+_[A-Za-z]+)')
    }


def substitute(string, data, modifiers):
    # Abilities
    abilities = MATCHES['abilities'].findall(string)
    for m in abilities:
        abl = m.split('_')[1]
        string = re.sub(re.escape(m), str(decode_ability(data, abl)), string)

    # Skills
    skills = MATCHES['skills'].findall(string)
    for m in skills:
        skl = m.split('_')[1]
        string = re.sub(re.escape(m), str(decode_skill(data, skl)), string)

    # Modifiers
    mods = MATCHES['mods'].findall(string)
    for m in mods:
        mod = m.split('_')[1]
        string = re.sub(re.escape(m), str(decode_modifier(modifiers, mod)), string)

    # Weapons
    weapons = MATCHES['weapons'].findall(string)
    for m in weapons:
        weap_id, weap_prop = m.split('_')[1:]
        weap_id = int(weap_id)

        string = re.sub(re.escape(m), str(data['weapons'][weap_id][weap_prop]), string)
        pass

    return string


def write_custom(infile, stats, modifiers, outfile, header):
    data = parse_yaml(infile)

    for custom, details in data.items():
        if 'img' in details:
            write_preamble(outfile, custom, header, details.pop('img'))
        else:
            write_preamble(outfile, custom, header)

        for title, content in details.items():
            fprint('{{' + title + '= ', header, file=outfile)
            fprint(substitute(content, stats, modifiers), header, file=outfile)
            write_cap(outfile, cap='}}', end='')

        if header:
            print(header, file=outfile)
        else:
            print(file=outfile)
