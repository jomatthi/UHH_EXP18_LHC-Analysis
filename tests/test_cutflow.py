import pytest

from Cutflow import Cutflow


def test_cutflow_preserves_cut_order_yields_and_sumw2():
    cutflow = Cutflow()

    cutflow.record("total", 2.0)
    cutflow.record("total", 3.0)
    cutflow.record("trigger", 1.5)

    assert cutflow.cut_names() == ("total", "trigger")

    assert cutflow.raw_events("total") == 2
    assert cutflow.weighted_yield("total") == pytest.approx(5.0)
    assert cutflow.sumw2("total") == pytest.approx(13.0)

    assert cutflow.raw_events("trigger") == 1
    assert cutflow.weighted_yield("trigger") == pytest.approx(1.5)
    assert cutflow.sumw2("trigger") == pytest.approx(2.25)


def test_registered_empty_cut_is_kept_in_cutflow():
    cutflow = Cutflow()

    cutflow.register_cut("total")
    cutflow.register_cut("bjet_n")
    cutflow.record("total", 2.0)

    assert cutflow.cut_names() == ("total", "bjet_n")

    assert cutflow.raw_events("bjet_n") == 0
    assert cutflow.weighted_yield("bjet_n") == pytest.approx(0.0)
    assert cutflow.sumw2("bjet_n") == pytest.approx(0.0)


def test_non_finite_weights_are_rejected():
    cutflow = Cutflow()

    with pytest.raises(ValueError, match="finite"):
        cutflow.record("total", float("nan"))
