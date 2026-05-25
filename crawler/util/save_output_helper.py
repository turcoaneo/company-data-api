# crawler/util/save_output_helper.py

import asyncio
from datetime import datetime, UTC
from functools import partial


def save_jsonl(lines: list[str], output_dir: str = "data") -> str:
    """
    Save JSONL lines to either local FS or S3 (depending on APP_ENV).
    Returns the path/key as a string.
    """
    ts = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
    output_path = f"{output_dir}/results_{ts}.jsonl"

    from app.utils.file_loader import FileLoader
    fl = FileLoader()

    with fl.open_file(output_path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line + "\n")

    return output_path


async def async_save_jsonl(lines, output_dir):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        partial(save_jsonl, lines, output_dir)
    )
