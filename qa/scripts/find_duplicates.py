import json
from collections import defaultdict

path = "meili_top.jsonl"

seen = defaultdict(list)

with open(path, "r", encoding="utf-8") as f:
    for i, line in enumerate(f, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except Exception:
            continue

        key = obj.get("id") or obj.get("domain")
        if key:
            seen[key].append(i)

# Print duplicates
for key, lines in seen.items():
    if len(lines) > 1:
        print(f"Duplicate '{key}' on lines: {lines}")
