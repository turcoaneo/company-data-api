# scripts/convert_for_meili.py

import json
import base64

from app.utils.env_vars import PATHS

inp = PATHS["path_final_result"]
out = PATHS["path_meili_final"]


def run_meili_converter():
    with open(inp, "r", encoding="utf-8") as fin, open(out, "w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
            except Exception as e:
                print(f"{line} is not good: {e}")
                continue

            domain = obj.get("domain")

            if not isinstance(domain, str) or not domain.strip():
                print(f"Skipping invalid domain: {domain}")
                continue

            # URL-safe Base64 WITHOUT padding (=)
            encoded_id = base64.urlsafe_b64encode(domain.encode()).decode().rstrip("=")

            # Add helper numeric fields for Meili custom ranking
            phones = obj.get("phones", [])
            socials = obj.get("socials", [])

            obj["phones_count"] = len(phones) if isinstance(phones, list) else 0
            obj["socials_count"] = len(socials) if isinstance(socials, list) else 0

            # Insert ID at the beginning
            new_obj = {"id": encoded_id}
            new_obj.update(obj)

            fout.write(json.dumps(new_obj, ensure_ascii=False) + "\n")

    print("Created:", out)


if __name__ == "__main__":
    run_meili_converter()
