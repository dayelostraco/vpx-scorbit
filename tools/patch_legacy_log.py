"""Replace the recognized legacy Scorbit log allocation in an explicit script.

Writes a new file only. Preserves source encoding and all other bytes. Does not
deploy tables. Stage/capture and back up the target before any installation.
"""

import argparse
import hashlib
import re
from pathlib import Path


def patch(source):
    """Return patched script bytes, preserving all bytes outside the recognized buffer.

    Reject absent/ambiguous/already-patched ScorbitIF classes. This pure transform
    never deploys a table; the CLI separately writes a new file without overwrite.
    """
    matches = list(re.finditer(rb"(?is)Class ScorbitIF\b.*?End Class", source))
    if len(matches) != 1:
        raise ValueError("Expected exactly one recognized ScorbitIF class")
    match = matches[0]
    body = match.group()
    declaration = b"Private LOGFILE(10000000)"
    assignment = b"\t\t\tLOGFILE(LogIdx)="
    if body.count(declaration) != 1 or body.count(assignment) != 1:
        raise ValueError("Unrecognized or already-patched log buffer")
    growth = (
        b"\t\t\tIf LogIdx = 0 Then\r\n"
        b"\t\t\t\tReDim LOGFILE(1023)\r\n"
        b"\t\t\tElseIf LogIdx > UBound(LOGFILE) Then\r\n"
        b"\t\t\t\tReDim Preserve LOGFILE(UBound(LOGFILE) + 1024)\r\n"
        b"\t\t\tEnd If\r\n" + assignment
    )
    body = body.replace(declaration, b"Private LOGFILE()").replace(assignment, growth)
    return source[: match.start()] + body + source[match.end() :]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = patch(args.source.read_bytes())
    with args.output.open("xb") as stream:
        stream.write(result)
    print("Patched script SHA-256: " + hashlib.sha256(result).hexdigest())
