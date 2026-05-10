# /tests/crawler/merger/test_dataframe_to_jsonl_lines.py

import json

# noinspection PyPackageRequirements
import pandas as pd

from crawler.merge_results import dataframe_to_jsonl_lines


class TestDataframeToJsonlLines:

    def test_jsonl_conversion(self):
        df = pd.DataFrame({
            "domain": ["example.com"],
            "phones": [["123"]],
            "socials": [[]]
        })

        lines = dataframe_to_jsonl_lines(df)

        assert len(lines) == 1

        obj = json.loads(lines[0])
        assert obj["domain"] == "example.com"
        assert obj["phones"] == ["123"]
