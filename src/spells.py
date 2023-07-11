import yaml
import re
import requests
import os

from src.text import error, fprint, write_cap, write_preamble
from src.tools import decode_skill, decode_ability, decode_modifier
from src.const import STATS, CONDITIONS, TIME


# TODO: Compile all the regex ahead of time
# TODO: Add support for heightened spells
# TODO: Focus spells

CLEANER = r'<a style=.*?>|<a href=.*?>|<\/a>'

MATCHES = {
    'Cast': r"<b>Cast<\/b>.*?title='([A-Za-z\s]+)'",
    'Cost': r'<b>Cost<\/b>\s*([\s0-9A-Za-z\-<>\/]+)<br',
    'Range': r'<b>Range<\/b>\s?([\s0-9A-Za-z\-]+)',
    'Targets': r'<b>Targets<\/b>\s?([\s0-9A-Za-z\-]+)',
    'Area': r'<b>Area<\/b>\s?([\s0-9A-Za-z\-]+)',
    'Duration': r'<b>Duration<\/b>\s?([\s0-9A-Za-z\-]+)',
    'Saving Throw': r'<b>Saving Throw<\/b>\s?([\s0-9A-Za-z\-]+)',
    'Effect': r'<hr \/>(.*)<ul><\/ul><',
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


def substitute(string, bonus, dc, mod, data):
    string = re.sub('\\$attack', bonus, string)
    string = re.sub('\\$dc', dc, string)
    string = re.sub('\\$mod', mod, string)

    return string


def compose_spell(URL):
    content = re.sub(CLEANER, '', requests.get(URL).text)
    details = dict()

    for prop, match in MATCHES.items():
        if result := re.search(match, content):
            desc = result.group(1)
        else:
            continue

        desc = re.sub(r'([0-9]d[0-9\.]+)', r'[[\1]]', desc)
        desc = re.sub(r'(\S+\sdamage)', '**\\1**', desc)
        desc = re.sub(r'\*\*and damage\*\*', 'and damage', desc)
        desc = re.sub(r'([0-9+-]*\s[a-zA-z]+\sbonus)', '**\\1**', desc)
        desc = re.sub(r'([0-9+-]*\s[a-zA-z]+\spenalty)', '**\\1**', desc)
        desc = re.sub(r'<b>(.*?)<\/b>', '**\\1**', desc)
        desc = re.sub(r'<i>(.*?)<\/i>', '*\\1*', desc)

        desc = re.sub('DC', '**DC $dc**', desc)

        for condition in CONDITIONS:
            if condition in desc.lower():
                desc = re.sub(f'({condition}\\s?[0-9]?)', '**\\1**',
                              desc, flags=re.IGNORECASE)

        for t in TIME:
            if t in desc.lower():
                desc = re.sub(f'([0-9]+\\s{t}[s]?)', '**\\1**',
                              desc, flags=re.IGNORECASE)

        if prop == 'Effect':
            desc = re.sub('spell attack', 'spell attack: [[d20 + $attack]]', desc)
            desc = re.sub(']] .* spellcasting modifier', ' + $mod]]', desc)
            desc = re.sub(r'<br \/>\s?', '\n', desc)
            desc = re.sub(r'<[\/uli]+?><[\/uli]+?>', os.linesep, desc)
        else:
            desc = desc.capitalize()

        if prop == 'Saving Throw' and 'DC' not in desc:
            desc = desc + ' **DC $dc**'

        details[prop] = desc

    return details


def print_spell_details(spell, data, bonus, mod, stats, outfile, header):
    dc = str(bonus + 10)
    bonus = str(bonus)

    if data and spell in data:
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
        fprint(substitute(content, bonus, dc, str(mod), stats), header, file=outfile)
        write_cap(outfile, cap='}}', end='')

    if header:
        print(header, file=outfile)
    else:
        print(file=outfile)


def write_spells(infile, stats, modifiers, outfile, header):
    if infile:
        data = parse_yaml(infile)
    else:
        data = None

    for caster in stats['spellCasters']:
        casting_stat = caster['ability']
        tradition = caster['magicTradition']
        casting_type = 'casting' + tradition.capitalize()

        bonus = decode_skill(stats, casting_type) + \
            decode_ability(stats, casting_stat) + \
            decode_modifier(modifiers, tradition)

        spells = set(sum([spell['list'] for spell in caster['spells']], []))

        for spell in spells:
            print_spell_details(spell,
                                data,
                                bonus,
                                decode_ability(stats, casting_stat),
                                stats,
                                outfile,
                                header)


def write_focus(infile, stats, modifiers, outfile, header):
    if infile:
        data = parse_yaml(infile)
    else:
        data = None

    for tradition, caster in stats['focus'].items():
        casting_stat = list(caster.keys())[0]
        casting_type = 'casting' + tradition.capitalize()

        caster = caster[casting_stat]

        bonus = decode_skill(stats, casting_type) + \
            decode_ability(stats, casting_stat) + \
            decode_modifier(modifiers, tradition)

        spells = caster['focusSpells']

        for spell in spells:
            print_spell_details(spell,
                                data,
                                bonus,
                                decode_ability(stats, casting_stat),
                                stats,
                                outfile,
                                header)
