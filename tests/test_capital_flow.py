import numpy as np
import pandas as pd
import pytest
from obrm.research.capital_flow import (
    CapitalFlowConfig, METRIC_CAPITAL_INFLOW, METRIC_CAPITAL_OUTFLOW,
    METRIC_CUSTOM, build_capital_flow_analytics, prepare_capital_flow_frame,
    validation_view,
)

def raw(rows=800):
    return pd.DataFrame({"day":pd.date_range("2020-01-01",periods=rows),"value":np.linspace(1,100,rows)})

def canonical(kind=METRIC_CAPITAL_INFLOW, direction=None):
    return prepare_capital_flow_frame(raw(),date_column="day",value_column="value",
        provider="Test",provider_metric="Flow",metric_kind=kind,
        definition="Documented flow",licence_note="Test use",custom_positive_direction=direction)

def cfg(): return CapitalFlowConfig(percentile_min_periods=50,smoothing_days=5,change_days=30,yearly_window=100,acceleration_days=10)

def test_inflow_score_rises_with_high_values():
    out=build_capital_flow_analytics(canonical(),cfg()); assert out.capital_flow_research_score.dropna().iloc[-1] > .9

def test_outflow_score_is_inverted():
    out=build_capital_flow_analytics(canonical(METRIC_CAPITAL_OUTFLOW),cfg()); assert out.capital_flow_research_score.dropna().iloc[-1] < .1

def test_required_outputs_and_validation_hook():
    called=[]
    def hook(df): called.append("capital_flow_acceleration" in df)
    out=build_capital_flow_analytics(canonical(),cfg(),validation_hooks=(hook,))
    assert called == [True]
    assert {"capital_flow_percentile_expanding","capital_flow_smoothed_30d","capital_flow_change_90d","capital_flow_percentile_1y","capital_flow_trend_direction","capital_flow_acceleration","capital_flow_research_score"} <= set(out)
    assert not validation_view(out).empty

def test_custom_requires_direction():
    with pytest.raises(ValueError,match="positive direction"):
        canonical(METRIC_CUSTOM)

def test_gross_flow_rejects_negative_values():
    data=raw(); data.loc[0,"value"]=-1
    with pytest.raises(ValueError,match="non-negative"):
        prepare_capital_flow_frame(data,date_column="day",value_column="value",provider="T",provider_metric="F",metric_kind=METRIC_CAPITAL_INFLOW,definition="D",licence_note="L")
