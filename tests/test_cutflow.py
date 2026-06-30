from collections import OrderedDict
from types import SimpleNamespace

import pytest

from Cutflow import Cutflow, selection_summary


def make_analyzer(total_yield, trigger_yield):
    cutflow = Cutflow()
    cutflow.record("total", total_yield)
    cutflow.record("trigger", trigger_yield)

    return SimpleNamespace(cutflow=cutflow)


def test_cutflow_preserves_stage_order_and_yields():
    cutflow = Cutflow()

    cutflow.record("total", 2.0)
    cutflow.record("total", 3.0)
    cutflow.record("trigger", 1.5)

    assert cutflow.stage_names() == ("total", "trigger")
    assert cutflow.raw_events("total") == 2
    assert cutflow.weighted_yield("total") == pytest.approx(5.0)

    rows = cutflow.rows()

    assert rows[1]["efficiency_from_total"] == pytest.approx(0.3)


def test_selection_summary_calculates_efficiency_and_purity():
    analyzers = OrderedDict(
        [
            ("QCD", make_analyzer(100.0, 10.0)),
            ("TTbar", make_analyzer(50.0, 25.0)),
            ("W+jets", make_analyzer(50.0, 15.0)),
        ]
    )

    rows = selection_summary(analyzers)

    trigger = rows[1]

    assert trigger["signal_efficiency"] == pytest.approx(0.5)
    assert trigger["background_yield"] == pytest.approx(25.0)
    assert trigger["purity"] == pytest.approx(0.5)
    assert trigger["dominant_background"] == "W+jets"