"""Build the common, hash-pinned LOCAL development helper bundle.

Does not run helpers, modify an installation, or collect per-table credentials.
Public release requires verifying upstream redistribution terms separately.
"""

import argparse
import hashlib
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def build(source, output, lock_path=ROOT / "packaging/helpers.lock.json"):
    """Write a new local ZIP of hash-matched allowlisted helpers; return their names.

    Validate every payload before creating output. Never execute a helper or copy
    directory contents wholesale. Hashes establish identity, not redistribution rights.
    """
    lock = json.loads(Path(lock_path).read_text())
    payload = {}
    for helper in lock["helpers"]:
        name = helper["name"]
        if Path(name).name != name or "/" in name or "\\" in name:
            raise ValueError("Helper must be a plain filename")
        data = (Path(source) / name).read_bytes()
        if hashlib.sha256(data).hexdigest() != helper["sha256"]:
            raise ValueError(f"Unrecognized helper: {name}; review before updating lock")
        payload[name] = data
    # Validate every input before creating anything. Never replace an existing bundle.
    with Path(output).open("xb") as target:
        with ZipFile(target, "w", ZIP_DEFLATED) as archive:
            for name, data in payload.items():
                archive.writestr("Tables/" + name, data)
            archive.writestr("helpers.lock.json", json.dumps(lock, indent=2))
            archive.writestr(
                "README.txt",
                "LOCAL DEVELOPMENT BUNDLE - redistribution not yet verified.\n"
                "These helpers are shared by tables; they do not install a Python/native SDK.\n"
                "Extract to staging first. Preserve existing helpers unless hashes match.\n"
                "No table identities, ROMs, device tokens, or account state are included.\n"
                "Integration runtime and MM/AFM gameplay validation are still in progress.\n",
            )
    return list(payload)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print("Packaged: " + ", ".join(build(args.source, args.output)))
