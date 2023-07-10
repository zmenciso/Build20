import yaml
import re
import requests

from src.text import error, fprint, write_cap, write_preamble
from src.tools import decode_skill, decode_ability, decode_modifier
from src.const import STATS


# TODO: Compile all the regex ahead of time
# TODO: Add support for heightened spells
# TODO: Focus spells

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

SPELL_LIST = requests.get('https://2e.aonprd.com/SpellLists.aspx').text


def find_spell(spell_list, name):
    spell_search = r'<a href="Spells\.aspx\?ID=([0-9]+)"><b><u>' + name
    spell_id = re.search(spell_search, spell_list)

    if spell_id:
        return 'https://2e.aonprd.com/Spells.aspx?ID=' + spell_id.group(1)

    return spell_id


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


def print_spell_details(spell, data, bonus, stats, outfile, header):
    dc = str(bonus + 10)
    bonus = str(bonus)

    if spell in data:
        details = data[spell]
    else:
        url = find_spell(SPELL_LIST, spell)

        if url:
            details = compose_spell(url)
        else:
            return

    write_preamble(outfile, spell, header)

    for title, content in details.items():
        fprint('{{' + title + '= ', header, file=outfile)
        fprint(substitute(content, bonus, dc, stats), header, file=outfile)
        write_cap(outfile, cap='}}', end='')

    if header:
        print(header, file=outfile)
    else:
        print(file=outfile)


def write_spells(infile, stats, modifiers, outfile, header):
    if infile:
        data = parse_yaml(infile)

    for caster in stats['spellCasters']:
        casting_stat = caster['ability']
        tradition = caster['magicTradition']
        casting_type = 'casting' + tradition.capitalize()

        bonus = decode_skill(stats, casting_type) + \
            decode_ability(stats, casting_stat) + \
            decode_modifier(modifiers, tradition)

        spells = set(sum([spell['list'] for spell in stats['spellCasters'][0]['spells']], []))

        for spell in spells:
            print_spell_details(spell, data, bonus, stats, outfile, header)


def write_focus(infile, stats, modifiers, outfile, header):
    if infile:
        data = parse_yaml(infile)

    for tradition, caster in stats['focus'].items():
        casting_stat = list(caster.keys())[0]
        casting_type = 'casting' + tradition.capitalize()

        caster = caster[casting_stat]

        bonus = decode_skill(stats, casting_type) + \
            decode_ability(stats, casting_stat) + \
            decode_modifier(modifiers, tradition)

        spells = caster['focusSpells']

        for spell in spells:
            print_spell_details(spell, data, bonus, stats, outfile, header)
