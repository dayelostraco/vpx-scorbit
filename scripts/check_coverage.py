"""Fail if any measured first-party Python file misses 80% lines or branches."""

import json
import sys
from pathlib import Path


def failures(report):
    """Return per-file 80% line/branch gate failures from coverage.py JSON.

    Empty reports fail; zero-statement/zero-branch denominators are vacuously
    accepted. This checks measured Python coverage, not VBS or comment coverage.
    """
    result = []
    for path, entry in report["files"].items():
        summary = entry["summary"]
        for label, covered, total in [
            ("lines", "covered_lines", "num_statements"),
            ("branches", "covered_branches", "num_branches"),
        ]:
            if summary[total] and summary[covered] / summary[total] < 0.8:
                result.append(f"{path}: {label} {summary[covered]}/{summary[total]} below 80%")
    if not report["files"]:
        result.append("No measured files")
    return result


if __name__ == "__main__":
    problems = failures(json.loads(Path(sys.argv[1]).read_text()))
    print("\n".join(problems) if problems else "Per-file 80% line and branch coverage gate passed.")
    raise SystemExit(bool(problems))
