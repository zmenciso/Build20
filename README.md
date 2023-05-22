#   Build20

Convert Pathbuilder 2e JSON output to Roll20 macros!


##  Requirements

  - Python 3.9

> Note: This script was tested on BSD 13.1 and Linux 6.1.


##  Usage

Invoke the script like so:

```
./build20.py [options] INPUT
    -f  --file      FILE    Write output to FILE
    -m  --modfile   FILE    Use the modifications in FILE
    -h  --help              Print this message
```

The `INPUT` should be a Pathbuilder 2e formatted JSON file ("Menu" > "Export" >
"Export JSON").

Copy the macro after each header into a new Roll20 macro.

### Modifications File

Any field (skill check, saving throw, etc.) can be **modified** with an integer
value by using the `-m` or `--modfile` switch and supplying a **modifications
file**.  Each modification is of the form `FIELD MODIFICATION`, where `FIELD` is
the name of the field and `MODIFICATION` is an integer value.  This file must be
line-delimited, and lines starting with `#` are treated as comments.  For
example, this file might look like:

```
# Clumsy -1
acrobatics -1
stealth -1
thievery -1

# Dank power
reflex 2
```
