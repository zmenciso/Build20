#   Build20

Convert Pathbuilder 2e JSON output to Roll20 macros!


##  Requirements

  - Python 3.9
  - PyYAML 6.0

> Note: This script was tested on BSD 13.1 and Linux 6.1.


##  Build20 Usage

Invoke the script like so:

```
./build20.py [options] INPUT
    -f  --file      FILE    Write output to FILE
    -m  --modfile   FILE    Use the modifications in FILE
    -s  --spells    FILE    Also write macros for spells in FILE
    -n  --noheader          Do not print headers (useful for Roll20 API)
    -h  --help              Print this message
```

The `INPUT` should be a Pathbuilder 2e formatted JSON file ("Menu" > "Export" >
"Export JSON").  You can also paste the JSON in by not specifying an input file.

Copy the macro after each header into a new Roll20 macro.

### Spells

Build20 can also generate spell macros by using a YAML file.  Copy
`template.yaml` and fill in your caster stat (e.g. "Wis") and your casting type
("e.g. Divine").  Then, add your spells after the `Spells:` key.  Spells consist
of arbitrary key/value pairs (nesting not supported) **OR** a single AoN URL.
Build20 will attempt to write the spell for you using the URL.  The following is
an example spell:

```yaml
Spells:
  Ignite Fireworks:
    Range: "60 ft"
    Area: |-
      ?{Metamagic| None, 10 ft burst | Widened, **Widened** 15 ft burst}
    Save: |-
      **REFLEX** DC [[$dc]]
    Damage: |-
      [[1d8]] fire damage
      [[1d8]] sonic damage
    Effect: |-
      **Critical Success** The creature is unaffected.
      **Success** The creature takes half damage and is dazzled for [[1]] round.
      **Failure** The creature takes full damage and is dazzled for [[3]] rounds.
      **Critical Failure** The creature takes double damage, takes [[1d4]] persistent fire damage, and is dazzled for [[1]] minute.
  Tanglefoot: "https://2e.aonprd.com/Spells.aspx?ID=330"
```

#### Substitutions

The spells YAML format currently supports three substitutions:
  - `$attack` will be replaced by your caster attack bonus (caster stat +
    proficiency bonus)
  - `$dc` will be replaced by your caster DC
  - `$[STAT]` will be replaced by your bonus for `STAT` (e.g. `$cha` will be
    replaced by your charisma bonus)

### Modifications File

Any field (skill check, saving throw, etc.) can be **modified** with an integer
value by using the `-m` or `--modfile` switch and supplying a **modifications
file**.  Each modification is of the form `FIELD MODIFICATION`, where `FIELD` is
the name of the field and `MODIFICATION` is an integer value.  This file must be
line-delimited, and lines starting with `#` are treated as comments.  Make sure
the `FIELD` exactly matches the Pathbuilder JSON output.  For example, this file
might look like:

```
# Clumsy -1
acrobatics -1
stealth -1
thievery -1
reflex -1
```

To modify spells, use the caster type (e.g. "castingDivine").  To modify attack rolls,
use the name of the weapon (e.g. "Large +1 Greatsword").

##  `heal.py`

`heal.py` is a simple script for doing party medicine.  To use it, first write
an input file (each character on its own line, fields space-delimited).

Lines that begin with `healer` denote a character that can use the Treat Wounds
ability.  Specify their Medicine modifier and the desired proficiency to roll
against.  

Lines that begin with `injured` denote a party member that should be the target
of healing.  Specify their name, current HP, and maximum HP.

Your input file may look like so:

```
# Healer MEDICINE DESIRED_PROF
healer 15 expert
healer 8 trained

# Injured NAME CURR_HP MAX_HP
injured char1 54 80
injured char2 23 40
injured char3 55 60
```

Then, invoke the script as follows:

```
./heal.py [options] INPUT
    -t  --time      VALUE   Maximum amount of time (hours)
    -h  --help              Print this message
```

> `injured` party members do not need to be missing HP.  Feel free to mark your
> entire party down at full health and only modify relevant PCs.
