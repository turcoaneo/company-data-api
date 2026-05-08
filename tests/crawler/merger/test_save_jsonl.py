# /tests/crawler/merger/test_save_jsonl.py
import json

# noinspection PyPackageRequirements
import pandas as pd

from crawler.merge_results import merge_dataframes
from crawler.util.async_save import save_jsonl


class TestSaveJsonl:

    def test_save_jsonl_creates_file(self, tmp_path):
        lines = [
            '{"domain": "example.com", "phones": ["123"]}',
            '{"domain": "test.com", "phones": []}'
        ]

        output_path = save_jsonl(lines, output_dir=str(tmp_path))

        assert output_path.exists()

        saved_lines = output_path.read_text().splitlines()
        assert len(saved_lines) == 2

        assert json.loads(saved_lines[0])["domain"] == "example.com"

    def test_missing_fields_become_empty_lists(self):
        df_input = pd.DataFrame({"domain": ["example.com"]})
        df_results = pd.DataFrame({"domain": ["example.com"]})

        merged = merge_dataframes(df_input, df_results)

        assert merged.loc[0, "phones"] == []
        assert merged.loc[0, "emails"] == []
        assert merged.loc[0, "socials"] == []
