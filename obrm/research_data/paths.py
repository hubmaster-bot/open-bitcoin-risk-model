"""Paths for canonical research datasets."""

from obrm.core.paths import DATA_DIR


RESEARCH_DATA_DIR = DATA_DIR / "research"
ONCHAIN_DATA_DIR = RESEARCH_DATA_DIR / "onchain"
ONCHAIN_CATALOG_FILE = ONCHAIN_DATA_DIR / "coinmetrics_btc_catalog.json"
ONCHAIN_AVAILABILITY_FILE = (
    ONCHAIN_DATA_DIR / "coinmetrics_btc_availability.json"
)
ONCHAIN_DATA_FILE = ONCHAIN_DATA_DIR / "coinmetrics_btc_daily.parquet"
ONCHAIN_METADATA_FILE = (
    ONCHAIN_DATA_DIR / "coinmetrics_btc_daily.metadata.json"
)
