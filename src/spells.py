import re
import requests
import os

from src.text import fprint, write_cap, write_preamble
from src.tools import decode_skill, decode_ability, decode_modifier, parse_yaml
from src.const import CONDITIONS, TIME, CLEANER


# TODO: Compile all the regex ahead of time
# TODO: Add support for heightened spells

MATCHES = {
    'Cast': re.compile(r"<b>Cast<\/b>.*?title='([A-Za-z\s]+)'"),
    'Cost': re.compile(r'<b>Cost<\/b>\s*([\s0-9A-Za-z\-<>\/]+)<br'),
    'Range': re.compile(r'<b>Range<\/b>\s?([\s0-9A-Za-z\-]+)'),
    'Targets': re.compile(r'<b>Targets<\/b>\s?([\s0-9A-Za-z\-]+)'),
    'Area': re.compile(r'<b>Area<\/b>\s?([\s0-9A-Za-z\-]+)'),
    'Duration': re.compile(r'<b>Duration<\/b>\s?([\s0-9A-Za-z\-]+)'),
    'Saving Throw': re.compile(r'<b>Saving Throw<\/b>\s?([\s0-9A-Za-z\-]+)'),
    'Effect': re.compile(r'<hr \/>(.*)<ul><\/ul><'),
    }

SUB = {
    'general': {
        re.compile(r'([0-9]d[0-9\.]+)'): r'[[\1]]',
        re.compile(r'(\S+\sdamage)'): '**\\1**',
        re.compile(r'\*\*and damage\*\*'): 'and damage',
        re.compile(r'([0-9+-]*\s[a-zA-z]+\sbonus)'): '**\\1**',
        re.compile(r'([0-9+-]*\s[a-zA-z]+\spenalty)'): '**\\1**',
        re.compile(r'<b>(.*?)<\/b>'): '**\\1**',
        re.compile(r'<i>(.*?)<\/i>'): '*\\1*',
        re.compile('DC'): '**DC $dc**'
        },
    'effect': {
        re.compile('spell attack'): 'spell attack: [[d20 + $attack]]',
        re.compile('\\]\\] [your+\\s]+? spellcasting [ability]+? modifier'): ' + $mod]]',
        re.compile('([your]+? spellcasting [ability]+? modifier)'): '\\1 (**$mod**)',
        re.compile(r'<br \/>\s?'): '\n',
        re.compile(r'<[\/uli]+?><[\/uli]+?>'): os.linesep
        }
    }

SPELL_LIST = requests.get('https://2e.aonprd.com/SpellLists.aspx').text


def find_spell(spell_list, name):
    spell_search = r'<a href="Spells\.aspx\?ID=([0-9]+)"><b><u>' + name
    spell_id = re.search(spell_search, spell_list)

    if spell_id:
        return 'https://2e.aonprd.com/Spells.aspx?ID=' + spell_id.group(1)

    return spell_id


def substitute(string, bonus, dc, mod, data):
    string = re.sub('\\$attack', bonus, string)
    string = re.sub('\\$dc', dc, string)
    string = re.sub('\\$mod', mod, string)

    return string


def compose_spell(URL):
    content = re.sub(CLEANER, '', requests.get(URL).text)
    details = dict()

    for prop, match in MATCHES.items():
        if result := match.search(content):
            desc = result.group(1)
        else:
            continue

        for m, sub in SUB['general'].items():
            desc = m.sub(sub, desc)

        for condition in CONDITIONS:
            if condition in desc.lower():
                desc = re.sub(f'({condition}\\s?[0-9]?)', '**\\1**',
                              desc, flags=re.IGNORECASE)

        for t in TIME:
            if t in desc.lower():
                desc = re.sub(f'([0-9]+\\s{t}[s]?)', '**\\1**',
                              desc, flags=re.IGNORECASE)

        if prop == 'Effect':
            for m, sub in SUB['effect'].items():
                desc = m.sub(sub, desc)
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

    if 'img' in details:
        write_preamble(outfile, spell, header, details.pop('img'))
    else:
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
