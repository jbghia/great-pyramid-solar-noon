"""Check preserved source text, syntax and provenance; no ephemeris run."""
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    items = json.loads((ROOT / "data/source_manifest.json").read_text())
    for item in items:
        path = ROOT / item["path"]
        data = path.read_bytes()
        text = data.decode("utf-8-sig").replace("\r\n", "\n").rstrip("\n") + "\n"
        actual = hashlib.sha256(text.encode()).hexdigest()
        if actual != item["repository_text_sha256"]:
            raise SystemExit(f"Source text mismatch: {path}")
        ast.parse(text, filename=str(path))
    print(f"PASS: {len(items)} source text hashes and syntax checks")
    print("Not a numerical reproduction or historical ephemeris validation.")


if __name__ == "__main__":
    main()
