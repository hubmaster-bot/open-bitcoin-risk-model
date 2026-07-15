import pandas as pd
from .core import (CapitalFlowMetadata, build_capital_flow_analytics,
                   load_capital_flow_dataset, prepare_capital_flow_frame,
                   save_capital_flow_dataset, verify_dataset_integrity)
from .paths import CAPITAL_FLOW_DATA_FILE, CAPITAL_FLOW_METADATA_FILE

def import_capital_flow_csv(raw: pd.DataFrame, **kwargs) -> tuple[pd.DataFrame, CapitalFlowMetadata]:
    canonical = prepare_capital_flow_frame(raw, **kwargs)
    meta = save_capital_flow_dataset(canonical, data_path=CAPITAL_FLOW_DATA_FILE,
                                     metadata_path=CAPITAL_FLOW_METADATA_FILE)
    return build_capital_flow_analytics(canonical), meta

def load_capital_flow_analytics() -> pd.DataFrame:
    if not verify_dataset_integrity(CAPITAL_FLOW_DATA_FILE, CAPITAL_FLOW_METADATA_FILE):
        raise ValueError("Capital-flow dataset integrity verification failed.")
    return build_capital_flow_analytics(load_capital_flow_dataset(CAPITAL_FLOW_DATA_FILE))
