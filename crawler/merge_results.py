# /crawler/merge_results.py

import json
from pathlib import Path

import pandas as pd

from crawler.pipeline import normalize_domain
from crawler.util.save_output_helper import save_jsonl


# ---------------------------------------------------------
# 1. Pure function: convert scraper results → DataFrame
# ---------------------------------------------------------
def build_results_df(results: list) -> pd.DataFrame:
    df_results = pd.DataFrame(results)

    # Ensure url column exists
    if "url" not in df_results.columns:
        df_results["url"] = None

    # Normalize domain
    df_results["domain"] = df_results["url"].apply(normalize_domain)

    return df_results


# ---------------------------------------------------------
# 2. Pure function: load and normalize input CSV
# ---------------------------------------------------------
def load_input_df(input_csv: str) -> pd.DataFrame:
    df = pd.read_csv(input_csv)
    df["domain"] = df["domain"].apply(normalize_domain)
    return df


# ---------------------------------------------------------
# 3. Pure function: merge input + results
# ---------------------------------------------------------
def merge_dataframes(df_input: pd.DataFrame, df_results: pd.DataFrame) -> pd.DataFrame:
    df_input["domain"] = df_input["domain"].str.lower().str.lstrip("www.")
    df_results["domain"] = df_results["domain"].str.lower().str.lstrip("www.")
    merged = df_input.merge(df_results, on="domain", how="left")

    # Normalize missing fields
    for col in ["phones", "socials"]:
        if col not in merged.columns:
            merged[col] = [[] for _ in range(len(merged))]
        else:
            merged[col] = merged[col].apply(
                lambda x: x if isinstance(x, list) else []
            )

    return merged


# ---------------------------------------------------------
# 4. Pure function: convert merged DF → JSONL string list
# ---------------------------------------------------------
def dataframe_to_jsonl_lines(df: pd.DataFrame) -> list[str]:
    # Remove unwanted columns before serialization
    drop_cols = ["url"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    lines = []
    for _, row in df.iterrows():
        lines.append(row.to_json())
    return lines


# ---------------------------------------------------------
# 5. High-level orchestrator (still pure)
# ---------------------------------------------------------
def merge_scraper_results(input_csv: str, results: list, output_dir: str = "data") -> Path:
    df_input = load_input_df(input_csv)
    df_results = build_results_df(results)
    merged = merge_dataframes(df_input, df_results)
    lines = dataframe_to_jsonl_lines(merged)
    return save_jsonl(lines, output_dir)


async def async_merge_scraper_results(input_csv: str, results: list, output_dir: str = "data") -> Path:
    import asyncio
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: merge_scraper_results(input_csv, results, output_dir)
    )


# ---------------------------------------------------------
# 5. Merging two runs
# ---------------------------------------------------------

def _normalize_host(value: str) -> str:
    if not value:
        return ""
    value = value.strip().lower()

    # strip protocol
    if value.startswith("http://"):
        value = value[7:]
    elif value.startswith("https://"):
        value = value[8:]

    # strip path
    value = value.split("/", 1)[0]

    # strip www
    if value.startswith("www."):
        value = value[4:]

    return value


def _extract_domain(rec: dict) -> str:
    dom = rec.get("domain")
    if isinstance(dom, str) and dom.strip():
        return _normalize_host(dom)

    url = rec.get("url", "")
    return _normalize_host(url)


# def _clean_record(rec: dict) -> dict:
#     """
#     Produce a clean record for final JSONL.
#     Removes url, normalizes domain, keeps only allowed fields.
#     """
#     domain = _extract_domain(rec)
#
#     clean = {
#         "domain": domain,
#         "phones": rec.get("phones", []),
#         "socials": rec.get("socials", []),
#     }
#
#     # Preserve company fields if present
#     for field in (
#             "company_commercial_name",
#             "company_legal_name",
#             "company_all_available_names",
#     ):
#         if field in rec:
#             clean[field] = rec[field]
#
#     return clean


def merge_two_runs(first_path: str, second_results: list[dict], final_path: str) -> None:
    """
    Merge first-pass JSONL with second-pass results.
    Preserve company fields from first pass.
    Only override phones/socials when second pass has data.
    Never write 'url'.
    """
    first: dict[str, dict] = {}

    # -------------------------
    # Load first-pass
    # -------------------------
    with open(first_path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            key = _extract_domain(rec)
            if not key:
                continue

            # Normalize domain
            rec["domain"] = key

            # Remove url
            rec.pop("url", None)

            first[key] = rec

    # -------------------------
    # Merge second-pass
    # -------------------------
    for rec in second_results:
        key = _extract_domain(rec)
        if not key:
            continue

        # Normalize domain
        domain = key

        # Build a clean second-pass record
        second_clean = {
            "domain": domain,
            "phones": rec.get("phones", []),
            "socials": rec.get("socials", []),
        }

        # If first-pass exists, merge fields
        if domain in first:
            merged = first[domain].copy()

            # Override phones only if second-pass has phones
            if second_clean["phones"]:
                merged["phones"] = second_clean["phones"]

            # Override socials only if second-pass has socials
            if second_clean["socials"]:
                merged["socials"] = second_clean["socials"]

            first[domain] = merged

        else:
            # No first-pass record → use second-pass clean record
            first[domain] = second_clean

    # -------------------------
    # Write final JSONL
    # -------------------------
    with open(final_path, "w", encoding="utf-8") as f:
        for rec in first.values():
            f.write(json.dumps(rec) + "\n")
