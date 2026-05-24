# scripts/convert_for_meili.py

import json
import base64

from app.utils.env_vars import PATHS

inp = PATHS["path_final_result"]
out = PATHS["path_meili_final"]

top_inp = PATHS["path_top_result"]
top_out = PATHS["path_meili_top"]


def convert_files():
    run_meili_converter(inp, out)
    run_meili_converter(top_inp, top_out)


def run_meili_converter(input_file, output_file):
    from app.utils.file_loader import FileLoader
    with (FileLoader().open_file(input_file, "r", encoding="utf-8") as file_in,
          FileLoader().open_file(output_file, "w", encoding="utf-8") as file_out):
        for line in file_in:
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

            file_out.write(json.dumps(new_obj, ensure_ascii=False) + "\n")

    print("Created:", output_file)


if __name__ == "__main__":
    convert_files()
