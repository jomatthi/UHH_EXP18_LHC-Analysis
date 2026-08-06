import math

import pytest

from SelectionMetrics import (
    WeightedYield,
    efficiency,
    purity,
)


def test_efficiency_without_additional_selection():
    before = WeightedYield(sumw=100.0, sumw2=100.0)

    result = efficiency(before, before)

    assert result.value == pytest.approx(1.0)
    assert math.isnan(result.stat_uncertainty)
    assert result.note is not None


def test_efficiency_for_weighted_toy_sample():
    before = WeightedYield(sumw=6.0, sumw2=14.0)
    after = WeightedYield(sumw=3.0, sumw2=5.0)

    result = efficiency(before, after)

    assert result.value == pytest.approx(0.5)
    assert result.stat_uncertainty == pytest.approx(
        0.3118047822
    )


def test_purity_for_toy_signal_and_background():
    signal = WeightedYield(sumw=40.0, sumw2=40.0)
    background = WeightedYield(sumw=60.0, sumw2=60.0)

    result = purity(signal, background)

    assert result.value == pytest.approx(0.4)
    assert result.stat_uncertainty == pytest.approx(
        0.0489897949
    )
