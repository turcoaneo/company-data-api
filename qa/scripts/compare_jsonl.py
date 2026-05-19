import json
from pathlib import Path


def load_jsonl(path: str) -> list[dict]:
    """
    Load a JSONL file into a list of dicts.
    Ignores blank lines.
    """
    records = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))
    return records


def normalize_domain(value: str) -> str:
    """
    Normalize domain: lowercase, strip whitespace, remove leading www.
    """
    if not value:
        return ""

    d = value.strip().lower()
    if d.startswith("www."):
        d = d[4:]
    return d


def extract_domain(record: dict) -> str:
    """
    Extract domain from a JSONL record.
    """
    return normalize_domain(record.get("domain", ""))


def compare_jsonl(file1: str, file2: str) -> list[str]:
    """
    Return domains that appear in file2 but not in file1.
    """
    domains1 = {extract_domain(r) for r in load_jsonl(file1)}
    domains2 = {extract_domain(r) for r in load_jsonl(file2)}

    # Remove empty domains
    domains1.discard("")
    domains2.discard("")

    return sorted(domains2 - domains1)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python compare_jsonl_domains.py file1.jsonl file2.jsonl")
        sys.exit(1)

    file1, file2 = sys.argv[1], sys.argv[2]
    extras = compare_jsonl(file1, file2)

    print("\nExtra domains in second file:")
    for d in extras:
        print(d)
