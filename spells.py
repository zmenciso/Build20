import yaml
import tools


def parse_yaml(infile):
    try:
        with open(infile) as y:
            data = yaml.safe_load(y)
    except Exception as e:
        tools.error(f'Could not parse yaml ({e})', 2)

    return data


def write_spells(infile, outfile):
    data = parse_yaml(infile)

    for spell, details in data.items():

