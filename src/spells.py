import yaml
import re
import requests

from src.text import error, fprint, write_cap, write_preamble
from src.tools import decode_skill, decode_ability, decode_modifier
from src.const import STATS


# TODO: Compile all the regex ahead of time
# TODO: Add support for heightened spells

CLEANER = r'<a style=.*?>|<a href=.*?>|<\/a>'

MATCHES = {
    'Cast': r"<b>Cast<\/b>.*?title='([A-Za-z\s]+)'",
    'Range': r'<b>Range<\/b>\s?([\s0-9A-Za-z\-]+)',
    'Targets': r'<b>Targets<\/b>\s?([\s0-9A-Za-z\-]+)',
    'Area': r'<b>Area<\/b>\s?([\s0-9A-Za-z\-]+)',
    'Duration': r'<b>Duration<\/b>\s?([\s0-9A-Za-z\-]+)',
    'Saving Throw': r'<b>Saving Throw<\/b>\s?([\s0-9A-Za-z\-]+)',
    'Effect': r'<hr \/>(.*)<ul><\/ul><hr \/>'
    }


def parse_yaml(infile):
    try:
        with open(infile) as y:
            data = yaml.safe_load(y)
    except Exception as e:
        error(f'Could not parse yaml ({e})', 10)

    return data


def substitute(string, bonus, dc, data):
    string = re.sub('\\$attack', bonus, string)
    string = re.sub('\\$dc', dc, string)

    for stat in STATS:
        string = re.sub(f'\\${stat}',
                        str(decode_ability(data, stat)), string)

    return string


def compose_spell(URL):
    content = re.sub(CLEANER, '', requests.get(URL).text)
    details = dict()

    for prop, match in MATCHES.items():
        if result := re.search(match, content):
            desc = result.group(1)
        else:
            continue

        desc = re.sub(r'([0-9]d[0-9])', r'[[\1]]', desc)
        desc = re.sub(r'([^\[d0-9][-+]?[0-9]+[^\]d0-9])', '**\\1**', desc)
        desc = re.sub(r'(\S+\sdamage)', '**\\1**', desc)

        desc = re.sub('DC', '**DC $dc**', desc)

        if prop == 'Effect':
            desc = re.sub('spell attack', 'spell attack: [[d20 + $attack]]', desc)
            desc = re.sub(r'<br \/>\s?', '\n', desc)
            desc = re.sub(r'<b>(.*?)<\/b>', '**\\1**', desc)
            desc = re.sub(r'<i>(.*?)<\/i>', '*\\1*', desc)
        else:
            desc = desc.capitalize()

        details[prop] = desc

    return details


def write_spells(infile, stats, modifiers, outfile, header):
    data = parse_yaml(infile)
    casting_stat = data['Character']['Casting_stat'].lower()
    casting_type = 'casting' + data['Character']['Casting_type'].title()

    bonus = decode_skill(stats, casting_type) + \
        decode_ability(stats, casting_stat) + \
        decode_modifier(modifiers, data['Character']['Casting_type'])
    dc = bonus + 10

    bonus = str(bonus)
    dc = str(dc)

    for spell, details in data['Spells'].items():
        if type(details) == str and '2e.aonprd.com' in details:
            details = compose_spell(details)
        elif type(details) == str:
            error(f'Cannot decode URL {details} for spell {spell}')
            continue

        write_preamble(outfile, spell, header)

        for title, content in details.items():
            fprint('{{' + title + '= ', header, file=outfile)
            fprint(substitute(content, bonus, dc, stats), header, file=outfile)
            write_cap(outfile, cap='}}', end='')

        if header:
            print(header, file=outfile)
        else:
            print(file=outfile)
