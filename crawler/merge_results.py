import pandas as pd
from pathlib import Path

from crawler.pipeline import normalize_domain
from crawler.util.async_save import save_jsonl


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
    merged = df_input.merge(df_results, on="domain", how="left")

    # Normalize missing fields
    for col in ["phones", "emails", "socials"]:
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
