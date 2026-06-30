import math

import pytest

from FourMomentum import FourMomentum


def test_sum_is_a_four_momentum_with_expected_components():
    p = FourMomentum(1.0, 2.0, 3.0, 5.0)
    q = FourMomentum(4.0, -1.0, 2.0, 6.0)

    result = p + q

    assert isinstance(result, FourMomentum), (
        "p + q muss einen neuen FourMomentum zurückgeben."
    )
    assert (result.px, result.py, result.pz, result.E) == pytest.approx(
        (5.0, 1.0, 5.0, 11.0)
    )


def test_scalar_product_of_two_known_vectors():
    p = FourMomentum(1.0, 2.0, 3.0, 5.0)
    q = FourMomentum(4.0, -1.0, 2.0, 6.0)

    assert p * q == pytest.approx(22.0)


def test_particle_at_rest_has_mass_equal_to_energy():
    particle = FourMomentum(0.0, 0.0, 0.0, 5.0)

    assert particle.m() == pytest.approx(5.0)


def test_scalar_multiplication_is_preserved():
    p = FourMomentum(1.0, -2.0, 3.0, 4.0)

    result = 2.0 * p

    assert (result.px, result.py, result.pz, result.E) == pytest.approx(
        (2.0, -4.0, 6.0, 8.0)
    )


def test_transverse_momentum_and_phi_are_unchanged():
    p = FourMomentum(3.0, 4.0, 0.0, 5.0)

    assert p.pt() == pytest.approx(5.0)
    assert p.phi() == pytest.approx(math.atan2(4.0, 3.0))
