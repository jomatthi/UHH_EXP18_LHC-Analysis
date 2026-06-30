import pytest

from SelectionMetrics import (
    WeightedYield,
    efficiency,
    purity,
)


def test_efficiency_without_additional_selection():
    before = WeightedYield(sumw=100.0, sumw2=100.0)

    value, uncertainty = efficiency(before, before)

    assert value == pytest.approx(1.0)
    assert uncertainty == pytest.approx(0.0)


def test_efficiency_for_weighted_toy_sample():
    before = WeightedYield(sumw=6.0, sumw2=14.0)
    after = WeightedYield(sumw=3.0, sumw2=5.0)

    value, uncertainty = efficiency(before, after)

    assert value == pytest.approx(0.5)
    assert uncertainty == pytest.approx(0.3118047822)


def test_purity_for_toy_signal_and_background():
    signal = WeightedYield(sumw=40.0, sumw2=40.0)
    background = WeightedYield(sumw=60.0, sumw2=60.0)

    assert purity(signal, background) == pytest.approx(0.4)
