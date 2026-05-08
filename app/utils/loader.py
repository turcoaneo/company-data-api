# app/utils/loader.py

# noinspection PyPackageRequirements
import pandas as pd
from typing import List

from app.utils.logger_util import get_logger
from app.utils.path_util import get_project_root

logger = get_logger()


def load_sites_from_config(config_path: str = None) -> List[str]:
    if config_path is None:
        config_path = get_project_root() / "data" / "small-sample-websites-company-names.csv"

    sites = []

    df = pd.read_csv(config_path, quotechar='"')
    for i, row in df.iterrows():
        domain_ = row["domain"]
        if not isinstance(domain_, str):
            logger.warning(f"⚠️ Row {i + 2} has non-string fields:\n{row}\n")
        else:
            sites.append(domain_)

    return sites
