# Upstream parser

`pinmame_nvmaps/nvram_parser.py`, `__init__.py` and `LICENSE` are unmodified
files from https://github.com/tomlogic/py-pinmame-nvmaps at
`4a8d77c39badb8fd893672238b90b541ed056581`.

Copyright Tom Collins, LGPL-3.0-or-later. Kept as readable, replaceable Python
source with the original notices/license; no compiled or modified fork is
bundled. The wrapper in vpx_scorbit/memory.py supplies MAPS_ROOT and performs
additional strict live-score validation. Memory maps/platform data carry their
own ODbL/DbCL notices under maps/.

On Windows, the upstream curses.ascii import requires windows-curses. The
project venv has version 2.4.2; import and decode tests run on Windows x64.
