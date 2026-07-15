import json
import pandas as pd
from obrm.research.capital_flow import METRIC_NET_CAPITAL_FLOW, prepare_capital_flow_frame, save_capital_flow_dataset, verify_dataset_integrity

def test_hash_verification_detects_tampering(tmp_path):
    raw=pd.DataFrame({"date":pd.date_range("2020-01-01",periods=400),"value":range(400)})
    frame=prepare_capital_flow_frame(raw,date_column="date",value_column="value",provider="T",provider_metric="N",metric_kind=METRIC_NET_CAPITAL_FLOW,definition="D",licence_note="L")
    data=tmp_path/"flow.parquet"; meta=tmp_path/"flow.json"
    save_capital_flow_dataset(frame,data_path=data,metadata_path=meta)
    assert verify_dataset_integrity(data,meta)
    payload=json.loads(meta.read_text()); payload["sha256"]="bad"; meta.write_text(json.dumps(payload))
    assert not verify_dataset_integrity(data,meta)
