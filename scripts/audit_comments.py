"""Check interface documentation presence; this is not a measure of comment quality.

Python scope: top-level public functions/classes and their public methods in
tools/, vpx_scorbit/ and scripts/. Constructors/private/nested callables are
excluded; class documentation describes ownership. VBS scope: non-private
Sub/Function/Property declarations in vbs/ and assets/, with an adjacent comment
before the declaration or as its first body line. Tests, generated code and
third-party source are excluded. Manual review must still check contract accuracy.
"""

import ast
import json
import re
import sys
from pathlib import Path


def audit(root):
    """Return interface counts and missing locations without executing inspected code."""
    result = {"python": {"total": 0, "documented": 0}, "vbscript": {"total": 0, "documented": 0}, "missing": []}
    for folder in ("tools", "vpx_scorbit", "scripts"):
        for path in sorted((root / folder).glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            nodes = []
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and not node.name.startswith(
                    "_"
                ):
                    nodes.append((node.name, node))
                    if isinstance(node, ast.ClassDef):
                        nodes.extend(
                            (node.name + "." + method.name, method)
                            for method in node.body
                            if isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef))
                            and not method.name.startswith("_")
                        )
            for name, node in nodes:
                result["python"]["total"] += 1
                if ast.get_docstring(node):
                    result["python"]["documented"] += 1
                else:
                    result["missing"].append(f"{path.relative_to(root)}:{node.lineno} {name}")
    declaration = re.compile(r"^\s*(?:Public\s+)?(?:Sub|Function|Property\s+(?:Get|Set|Let))\s+(\w+)", re.I)
    for folder in ("vbs", "assets"):
        for path in sorted((root / folder).glob("*.vbs")):
            lines = path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines):
                match = declaration.match(line)
                if not match:
                    continue
                result["vbscript"]["total"] += 1
                adjacent = [lines[i].strip() for i in (index - 1, index + 1) if 0 <= i < len(lines)]
                if any(text.startswith("'") and len(text) > 1 for text in adjacent):
                    result["vbscript"]["documented"] += 1
                else:
                    result["missing"].append(f"{path.relative_to(root)}:{index + 1} {match[1]}")
    if not result["python"]["total"] or not result["vbscript"]["total"]:
        result["missing"].append("Expected Python and VBScript interfaces; scan scope is empty")
    return result


if __name__ == "__main__":
    report = audit(Path(__file__).resolve().parents[1])
    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(report["missing"]))
