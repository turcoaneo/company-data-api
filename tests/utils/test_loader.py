# noinspection PyPackageRequirements
import pandas as pd
import pytest

from app.utils.loader import load_sites_from_config


class TestLoader:

    @pytest.fixture
    def sample_csv(self, tmp_path):
        csv_path = tmp_path / "sample_sites.csv"

        df = pd.DataFrame({
            "domain": [
                "bostonzen.org",
                "mazautoglass.com",
                "top-salon-hair-salon.business.site",
                None,  # invalid
            ],
            "company_commercial_name": [
                "Greater Boston Zen Center",
                "MAZ Auto Glass",
                "Top salon Hair Salon",
                "Bad Row",
            ],
            "company_legal_name": ["", "", "", ""],
            "company_all_available_names": ["", "", "", ""],
        })

        df.to_csv(csv_path, index=False)
        return csv_path

    def test_load_sites_valid(self, sample_csv):
        sites = load_sites_from_config(str(sample_csv))

        assert sites == [
            "bostonzen.org",
            "mazautoglass.com",
            "top-salon-hair-salon.business.site",
        ]

    def test_load_sites_invalid_rows(self, sample_csv, caplog):
        load_sites_from_config(str(sample_csv))

        warnings = [
            rec.message for rec in caplog.records
            if rec.levelname == "WARNING"
        ]

        # invalid rows: None
        assert len(warnings) == 1
