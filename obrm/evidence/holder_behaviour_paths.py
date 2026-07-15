"""Paths for portable Holder Behaviour research data."""

from obrm.core.paths import DATA_DIR


HOLDER_BEHAVIOUR_DATA_DIR = DATA_DIR / "research" / "holder_behaviour"
HOLDER_BEHAVIOUR_DATA_FILE = HOLDER_BEHAVIOUR_DATA_DIR / "holder_behaviour_daily.parquet"
HOLDER_BEHAVIOUR_METADATA_FILE = (
    HOLDER_BEHAVIOUR_DATA_DIR / "holder_behaviour_daily.metadata.json"
)
