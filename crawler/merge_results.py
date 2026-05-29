# /crawler/merge_results.py

import json

import pandas as pd

from app.utils.file_loader import FileLoader
from crawler.pipeline import normalize_domain


# ---------------------------------------------------------
# 1. Pure function: convert scraper results → DataFrame
# ---------------------------------------------------------
def build_results_df(results: list) -> pd.DataFrame:
    df_results = pd.DataFrame(results)

    if "url" not in df_results.columns:
        df_results["url"] = None

    df_results["domain"] = df_results["url"].apply(normalize_domain)
    return df_results


# ---------------------------------------------------------
# 2. Pure function: load and normalize input CSV (LOCAL + S3)
# ---------------------------------------------------------
def load_input_df(input_csv: str) -> pd.DataFrame:
    fl = FileLoader()
    with fl.open_file(input_csv, "r", encoding="utf-8") as f:
        df = pd.read_csv(f)
    df["domain"] = df["domain"].apply(normalize_domain)
    return df


# ---------------------------------------------------------
# 3. Pure function: merge input + results
# ---------------------------------------------------------
def _normalize_domain_series(s: pd.Series) -> pd.Series:
    # lower + remove a single leading 'www.' only
    return s.str.lower().str.replace(r"^www\.", "", regex=True)


def merge_dataframes(df_input: pd.DataFrame, df_results: pd.DataFrame) -> pd.DataFrame:
    df_input["domain"] = _normalize_domain_series(df_input["domain"])
    df_results["domain"] = _normalize_domain_series(df_results["domain"])

    merged = df_input.merge(df_results, on="domain", how="left")

    for col in ["phones", "socials"]:
        if col not in merged.columns:
            merged[col] = [[] for _ in range(len(merged))]
        else:
            merged[col] = merged[col].apply(lambda x: x if isinstance(x, list) else [])

    return merged


# ---------------------------------------------------------
# 4. Pure function: convert merged DF → JSONL lines
# ---------------------------------------------------------
def dataframe_to_jsonl_lines(df: pd.DataFrame) -> list[str]:
    drop_cols = ["url"]
    df = df.drop(columns=[c for c in drop_cols if c in df.columns])

    return [row.to_json() for _, row in df.iterrows()]


# ---------------------------------------------------------
# 5. High-level orchestrator (LOCAL + S3)
# ---------------------------------------------------------
def merge_scraper_results(input_csv: str, results: list, output_dir: str = "data") -> str:
    df_input = load_input_df(input_csv)
    df_results = build_results_df(results)
    merged = merge_dataframes(df_input, df_results)
    lines = dataframe_to_jsonl_lines(merged)

    # Use the unified S3/local writer with timestamp
    from crawler.util.save_output_helper import save_jsonl
    return save_jsonl(lines, output_dir)


# ---------------------------------------------------------
# 6. Async wrapper
# ---------------------------------------------------------
async def async_merge_scraper_results(input_csv: str, results: list, output_dir: str = "data") -> str:
    import asyncio
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: merge_scraper_results(input_csv, results, output_dir))


# ---------------------------------------------------------
# 7. Merge two runs (LOCAL + S3)
# ---------------------------------------------------------
def _normalize_host(value: str) -> str:
    if not value:
        return ""
    value = value.strip().lower()

    if value.startswith("http://"):
        value = value[7:]
    elif value.startswith("https://"):
        value = value[8:]

    value = value.split("/", 1)[0]

    if value.startswith("www."):
        value = value[4:]

    return value


def _extract_domain(rec: dict) -> str:
    dom = rec.get("domain")
    if isinstance(dom, str) and dom.strip():
        return _normalize_host(dom)

    url = rec.get("url", "")
    return _normalize_host(url)


def merge_two_runs(first_path: str, second_results: list[dict], final_path: str) -> None:
    from app.utils.file_loader import FileLoader
    fl = FileLoader()

    first: dict[str, dict] = {}

    # Load first-pass
    with fl.open_file(first_path, "r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            key = _extract_domain(rec)
            if not key:
                continue

            rec["domain"] = key
            rec.pop("url", None)
            first[key] = rec

    # Merge second-pass
    for rec in second_results:
        key = _extract_domain(rec)
        if not key:
            continue

        domain = key
        second_clean = {
            "domain": domain,
            "phones": rec.get("phones", []),
            "socials": rec.get("socials", []),
        }

        if domain in first:
            merged = first[domain].copy()
            if second_clean["phones"]:
                merged["phones"] = second_clean["phones"]
            if second_clean["socials"]:
                merged["socials"] = second_clean["socials"]
            first[domain] = merged
        else:
            first[domain] = second_clean

    # Write final JSONL
    with fl.open_file(final_path, "w", encoding="utf-8") as f:
        for rec in first.values():
            f.write(json.dumps(rec) + "\n")
