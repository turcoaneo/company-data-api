# /tests/crawler/merger/test_merge_dataframes.py

# noinspection PyPackageRequirements
import pandas as pd

from crawler.merge_results import merge_dataframes


class TestMergeDataframes:

    def test_merge_handles_www_in_input(self):
        df_input = pd.DataFrame({
            "domain": ["www.example.com"],
            "company_commercial_name": ["Example Co"]
        })

        df_results = pd.DataFrame({
            "domain": ["example.com"],
            "phones": [["123"]],
            "socials": [["fb.com/example"]]
        })

        merged = merge_dataframes(df_input, df_results)

        assert merged.loc[0, "phones"] == ["123"]
        assert merged.loc[0, "socials"] == ["fb.com/example"]

    def test_merge_handles_www_in_results(self):
        df_input = pd.DataFrame({
            "domain": ["example.com"],
            "company_commercial_name": ["Example Co"]
        })

        df_results = pd.DataFrame({
            "domain": ["www.example.com"],
            "phones": [["123"]],
            "socials": [["fb.com/example"]]
        })

        merged = merge_dataframes(df_input, df_results)

        assert merged.loc[0, "phones"] == ["123"]
        assert merged.loc[0, "socials"] == ["fb.com/example"]

    def test_merge_includes_scraped_fields(self):
        df_input = pd.DataFrame({
            "domain": ["example.com"],
            "company_commercial_name": ["Example Co"]
        })

        df_results = pd.DataFrame({
            "domain": ["example.com"],
            "phones": [["123"]],
            "socials": [["fb.com/example"]]
        })

        merged = merge_dataframes(df_input, df_results)

        assert merged.loc[0, "phones"] == ["123"]
        assert merged.loc[0, "socials"] == ["fb.com/example"]

    def test_missing_fields_become_empty_lists(self):
        df_input = pd.DataFrame({"domain": ["example.com"]})
        df_results = pd.DataFrame({"domain": ["example.com"]})

        merged = merge_dataframes(df_input, df_results)

        assert merged.loc[0, "phones"] == []
        assert merged.loc[0, "socials"] == []
