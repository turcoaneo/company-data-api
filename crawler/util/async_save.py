import asyncio
from functools import partial
from datetime import datetime, UTC
from pathlib import Path


def save_jsonl(lines: list[str], output_dir: str = "data") -> Path:
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_path = Path(output_dir) / f"results_{ts}.jsonl"

    with open(output_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    return output_path


async def async_save_jsonl(lines, output_dir):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        partial(save_jsonl, lines, output_dir)
    )
