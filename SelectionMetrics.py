"""Helpers for efficiency, purity and MC-statistical uncertainties.

This file is intentionally structured as a student exercise:
all data handling, validation and boundary cases are implemented already.
Only the compact formulas marked with TODO must be completed.

Assumptions
-----------
* All event weights are non-negative.
* ``after`` is a subset of ``before`` for an efficiency calculation.
* Signal and background samples are statistically independent.
* Only MC-statistical uncertainties are considered.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class WeightedYield:
    """Weighted yield W = sum(w) and its variance estimator V = sum(w²)."""

    sumw: float
    sumw2: float
    raw_events: int | None = None

    def __post_init__(self):
        if not math.isfinite(self.sumw):
            raise ValueError("sumw must be finite.")

        if not math.isfinite(self.sumw2) or self.sumw2 < 0.0:
            raise ValueError("sumw2 must be finite and non-negative.")

    @property
    def stat_uncertainty(self) -> float:
        """MC-statistical uncertainty of the weighted yield."""
        return math.sqrt(self.sumw2)


@dataclass(frozen=True)
class Measurement:
    """A result with a symmetric MC-statistical uncertainty.

    For boundary cases (0% or 100%), ``stat_uncertainty`` is ``nan`` because
    a symmetric Gaussian error is not a meaningful confidence interval.
    """

    value: float
    stat_uncertainty: float
    note: str | None = None


def cut_yield(cutflow, cut_name: str) -> WeightedYield:
    """Read one named selection cut from a Cutflow object."""
    return WeightedYield(
        sumw=float(cutflow.weighted_yield(cut_name)),
        sumw2=float(cutflow.sumw2(cut_name)),
        raw_events=int(cutflow.raw_events(cut_name))
    )


def combine_yields(*yields: WeightedYield) -> WeightedYield:
    """Combine statistically independent MC samples."""
    return WeightedYield(
        sumw=sum(yield_.sumw for yield_ in yields),
        sumw2=sum(yield_.sumw2 for yield_ in yields),
    )


def _validate_nested_selection(
    before: WeightedYield,
    after: WeightedYield,
) -> None:
    """Check that a cut can be a subset of an earlier cut."""
    if before.sumw <= 0.0:
        raise ValueError(
            "Efficiency requires a positive weighted yield before the cut."
        )

    tolerance = 1e-12 * max(1.0, before.sumw, before.sumw2)

    if after.sumw < -tolerance:
        raise ValueError("The selected weighted yield must not be negative.")

    if after.sumw > before.sumw + tolerance:
        raise ValueError(
            "The selected weighted yield is larger than before the cut. "
            "The cuts are probably not nested."
        )

    if after.sumw2 > before.sumw2 + tolerance:
        raise ValueError(
            "The selected sumw2 is larger than before the cut. "
            "The cuts are probably not nested."
        )


def efficiency(
    before: WeightedYield,
    after: WeightedYield,
) -> Measurement:
    """Calculate selection efficiency and its MC-statistical uncertainty.

    Define:
        W_total = sum of weights before the cut
        W_pass  = sum of weights after the cut
        V_pass  = sum of squared weights after the cut
        V_fail  = sum of squared weights of rejected events

    The numerator and denominator of an efficiency are correlated. Therefore
    the uncertainty must be calculated from the statistically independent
    passing and failing subsets, not by treating W_pass and W_total as
    independent quantities.
    """
    _validate_nested_selection(before, after)

    total = before.sumw
    passed = after.sumw
    failed = max(0.0, before.sumw - after.sumw)
    variance_passed = after.sumw2
    variance_failed = max(0.0, before.sumw2 - after.sumw2)

    # Boundary cases need one-sided intervals rather than symmetric errors.
    if math.isclose(passed, 0.0, abs_tol=1e-15):
        return Measurement(
            value=0.0,
            stat_uncertainty=math.nan,
            note=(
                "No MC event weight survives this cut; "
                "a one-sided upper limit is required."
            ),
        )

    if math.isclose(passed, total, rel_tol=1e-12, abs_tol=1e-15):
        return Measurement(
            value=1.0,
            stat_uncertainty=math.nan,
            note=(
                "No MC event weight is rejected by this cut; "
                "a one-sided lower limit is required."
            ),
        )

    # TODO 1: Implement epsilon = W_pass / (W_pass + W_fail).
    value = None

    # TODO 2: Implement Var(epsilon) from V_pass and V_fail.
    #
    # Hint: the two independent pieces are the passing and failing events.
    # The result must have dimensions of a squared dimensionless quantity.
    variance = None

    if value is None or variance is None:
        raise NotImplementedError(
            "Complete the two TODOs in efficiency()."
        )

    if variance < 0.0:
        raise RuntimeError("Calculated a negative variance.")

    return Measurement(
        value=value,
        stat_uncertainty=math.sqrt(variance),
    )


def purity(
    signal: WeightedYield,
    background: WeightedYield,
) -> Measurement:
    """Calculate signal purity and its MC-statistical uncertainty.

    Define:
        S   = weighted signal yield
        B   = weighted background yield
        V_S = sum of squared signal weights
        V_B = sum of squared background weights

    Signal and background are independent MC samples.
    """
    if signal.sumw < 0.0 or background.sumw < 0.0:
        raise ValueError(
            "Purity requires non-negative signal and background yields."
        )

    total = signal.sumw + background.sumw
    S = signal.sumw
    B = background.sumw
    V_S = signal.sumw2
    V_B = background.sumw2

    if total <= 0.0:
        raise ValueError(
            "Purity requires a positive total signal-plus-background yield."
        )

    if math.isclose(S, 0.0, abs_tol=1e-15):
        return Measurement(
            value=0.0,
            stat_uncertainty=math.nan,
            note=(
                "No signal MC event weight survives this cut; "
                "purity is not meaningfully constrained."
            ),
        )

    if math.isclose(B, 0.0, abs_tol=1e-15):
        return Measurement(
            value=1.0,
            stat_uncertainty=math.nan,
            note=(
                "No background MC event weight survives this cut; "
                "a one-sided upper limit on the background is required."
            ),
        )

    # TODO 3: Implement P = S / (S + B).
    value = None

    # TODO 4: Implement Var(P) using V_S and V_B.
    #
    # Hint: propagate the independent MC-statistical uncertainties of S and B.
    variance = None

    if value is None or variance is None:
        raise NotImplementedError(
            "Complete the two TODOs in purity()."
        )

    if variance < 0.0:
        raise RuntimeError("Calculated a negative variance.")

    return Measurement(
        value=value,
        stat_uncertainty=math.sqrt(variance),
    )


def format_measurement(measurement: Measurement) -> str:
    """Return a readable representation for terminal output."""
    if math.isfinite(measurement.stat_uncertainty):
        return (
            f"{measurement.value:.3%} "
            f"+/- {measurement.stat_uncertainty:.3%}"
        )

    return f"{measurement.value:.3%} ({measurement.note})"
