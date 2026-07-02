from Event import Event
from uhhObjects import MET, Muon, Jet


class EventBuilder:
    """Build physics-event objects from the input ROOT tree."""

    JEC_FACTORS = {
        "nominal": 1.0,
        "up": 1.05,
        "down": 0.95,
    }

    def __init__(self, options=None):
        options = dict(options or {})
        unknown_options = set(options) - {"JEC"}

        if unknown_options:
            unknown = ", ".join(sorted(unknown_options))
            raise ValueError(
                f"Unknown EventBuilder option(s): {unknown}. "
                "Muon isolation belongs to the analysis selection, "
                "not to EventBuilder."
            )

        self.btag_threshold = 1.74

        jec_mode = str(options.get("JEC", "nominal")).lower()
        if jec_mode not in self.JEC_FACTORS:
            allowed = ", ".join(self.JEC_FACTORS)
            raise ValueError(
                f"Unknown JEC mode '{jec_mode}'. "
                f"Choose one of: {allowed}."
            )

        self.JEC = self.JEC_FACTORS[jec_mode]

    def build_event(self, tree):
        event = Event()

        event.weight = tree.EventWeight
        event.trigger["IsoMu24"] = tree.triggerIsoMu24

        for i in range(tree.NMuon):
            muon = Muon(
                tree.Muon_Px[i],
                tree.Muon_Py[i],
                tree.Muon_Pz[i],
                tree.Muon_E[i],
            )
            muon.charge = tree.Muon_Charge[i]

            if muon.pt() == 0.0:
                muon.iso = float("inf")
            else:
                muon.iso = tree.Muon_Iso[i] / muon.pt()

            event.muons.append(muon)

        met_px = float(tree.MET_px)
        met_py = float(tree.MET_py)

        delta_jet_px = 0.0
        delta_jet_py = 0.0
        for i in range(tree.NJet):
            nominal_px = tree.Jet_Px[i]
            nominal_py = tree.Jet_Py[i]
            nominal_pz = tree.Jet_Pz[i]
            nominal_E = tree.Jet_E[i]

            varied_px = self.JEC * nominal_px
            varied_py = self.JEC * nominal_py
            varied_pz = self.JEC * nominal_pz
            varied_E = self.JEC * nominal_E

            delta_jet_px += varied_px - nominal_px
            delta_jet_py += varied_py - nominal_py

            jet = Jet(
                varied_px,
                varied_py,
                varied_pz,
                varied_E,
            )

            jet.has_b_tag = (
                tree.Jet_btag[i] > self.btag_threshold
            )

            event.jets.append(jet)

            if jet.has_b_tag:
                event.b_jets.append(jet)
        
        event.met = MET(
            met_px - delta_jet_px,
            met_py - delta_jet_py,
        )

        return event
