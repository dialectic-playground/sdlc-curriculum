"""Portable child process for the dp-env black-box tests.

Run as ``{PYTHON} child.py [WORD]...``. Each WORD is handled in order:

* ``@cwd``     prints ``cwd=<base name of the current working directory>``
* ``@exit=N``  sets the exit status to N (default 0)
* ``NAME``     prints ``NAME=<value>``, or ``NAME=<unset>`` when NAME is not in the environment

Output is UTF-8 with LF line endings on every platform.
"""

import os
import sys

status = 0
lines = []
for word in sys.argv[1:]:
    if word == "@cwd":
        lines.append("cwd=" + os.path.basename(os.getcwd()))
    elif word.startswith("@exit="):
        status = int(word[len("@exit="):])
    else:
        lines.append(word + "=" + os.environ.get(word, "<unset>"))
sys.stdout.buffer.write("".join(line + "\n" for line in lines).encode("utf-8", "surrogateescape"))
sys.stdout.buffer.flush()
sys.exit(status)
