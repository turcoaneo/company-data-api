# noinspection PyPackageRequirements
import pandas as pd
from datetime import datetime, UTC
from pathlib import Path

from crawler.pipeline import normalize_domain


def merge_scraper_results(input_csv: str, results: list, output_dir: str = "data") -> Path:
    df = pd.read_csv(input_csv)

    df_results = pd.DataFrame(results)
    df_results["domain"] = df_results["url"].apply(normalize_domain)
    df["domain"] = df["domain"].apply(normalize_domain)

    merged = df.merge(df_results, on="domain", how="left")

    # Normalize missing fields
    for col in ["phones", "emails", "socials"]:
        if col not in merged.columns:
            merged[col] = [[] for _ in range(len(merged))]
        else:
            merged[col] = merged[col].apply(
                lambda x: x if isinstance(x, list) else []
            )

    # Timestamp
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_path = Path(output_dir) / f"results_{ts}.jsonl"

    # Write JSONL
    with open(output_path, "w", encoding="utf-8") as f:
        for _, row in merged.iterrows():
            f.write(row.to_json() + "\n")

    return output_path
