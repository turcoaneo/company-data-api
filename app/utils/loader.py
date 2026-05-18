# app/utils/loader.py

from typing import List

# noinspection PyPackageRequirements
import pandas as pd

from app.utils.logger_util import get_logger

logger = get_logger()


def load_sites_from_config(config_path: str = None) -> List[str]:
    if config_path is None:
        from app.utils.env_vars import PATHS
        config_path = PATHS["path_data_sample"]

    sites = []

    df = pd.read_csv(config_path, quotechar='"')
    for i, row in df.iterrows():
        domain_ = row["domain"]
        if not isinstance(domain_, str):
            logger.warning(f"⚠️ Row {i + 2} has non-string fields:\n{row}\n")
        else:
            sites.append(domain_)

    return sites
