from types import SimpleNamespace

import pytest

from EventBuilder import EventBuilder
from uhhObjects import Jet


def make_tree(muons=(), jets=()):
    """
    muons: (px, py, pz, E, charge, absolute_isolation)
    jets:  (px, py, pz, E, btag_discriminator)
    """
    return SimpleNamespace(
        EventWeight=1.0,
        triggerIsoMu24=True,
        MET_px=15.0,
        MET_py=-5.0,
        NMuon=len(muons),
        Muon_Px=[muon[0] for muon in muons],
        Muon_Py=[muon[1] for muon in muons],
        Muon_Pz=[muon[2] for muon in muons],
        Muon_E=[muon[3] for muon in muons],
        Muon_Charge=[muon[4] for muon in muons],
        Muon_Iso=[muon[5] for muon in muons],
        NJet=len(jets),
        Jet_Px=[jet[0] for jet in jets],
        Jet_Py=[jet[1] for jet in jets],
        Jet_Pz=[jet[2] for jet in jets],
        Jet_E=[jet[3] for jet in jets],
        Jet_btag=[jet[4] for jet in jets],
    )


def test_configured_muon_isolation_threshold_is_used():
    # pT = 10 GeV, relative isolation = 2 / 10 = 0.2
    tree = make_tree(
        muons=[(10.0, 0.0, 0.0, 10.0, 1, 2.0)]
    )

    loose_event = EventBuilder(
        {"muon_isolation": 0.3}
    ).build_event(tree)

    strict_event = EventBuilder(
        {"muon_isolation": 0.1}
    ).build_event(tree)

    assert loose_event.n_muons() == 1
    assert loose_event.muons[0].iso == pytest.approx(0.2)
    assert strict_event.n_muons() == 0


def test_jec_scaling_preserves_jet_type_and_b_tagging():
    tree = make_tree(
        jets=[(100.0, 20.0, 30.0, 110.0, 2.0)]
    )

    event = EventBuilder({"JEC": "up"}).build_event(tree)
    jet = event.jets[0]

    assert isinstance(jet, Jet)
    assert jet.px == pytest.approx(105.0)
    assert jet.py == pytest.approx(21.0)
    assert jet.pz == pytest.approx(31.5)
    assert jet.E == pytest.approx(115.5)
    assert jet.has_b_tag is True
    assert event.b_jets == [jet]


def test_invalid_jec_mode_is_rejected():
    with pytest.raises(ValueError, match="JEC"):
        EventBuilder({"JEC": "sideways"})
