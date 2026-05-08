# /tests/crawler/merger/test_load_input_df.py
from crawler.merge_results import load_input_df


class TestLoadInputDf:

    def test_load_input_df_normalizes_domains(self, tmp_path):
        csv_path = tmp_path / "input.csv"
        csv_path.write_text("domain\nhttps://Example.com/\n")

        df = load_input_df(str(csv_path))

        assert df.loc[0, "domain"] == "example.com"
