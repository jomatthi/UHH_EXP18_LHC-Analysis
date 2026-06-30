# from Event import Event
# from uhhObjects import MET, Muon, Jet


# class EventBuilder(object):
#     """
#     Class to build events from
#     """
#     def __init__(self, options):
#         self.tree = None
#         self.btag_threshold = 1.74

#         # parse options
#         jec_factor = 1.0
#         if 'JEC' in options.keys():
#             if options['JEC'].lower() == 'up':
#                 jec_factor = 1.05
#             elif options['JEC'].lower() == 'down':
#                 jec_factor = 0.95
#         self.JEC = jec_factor

#         self.muon_isolation_threshold = 0.1
#         if 'muon_isolation' in options.keys():
#             self.muon_isolation_thresold = options['muon_isolation']

#     def build_event(self, tree):
#         event = Event()
#         self.tree = tree

#         event.weight = tree.EventWeight  # set event weight
#         event.trigger['IsoMu24'] = tree.triggerIsoMu24  # set trigger
#         event.met = MET(
#             tree.MET_px,
#             tree.MET_py
#             )  # set MET
#         # set muons
#         for i in range(0, tree.NMuon):
#             muon = Muon(
#                 tree.Muon_Px[i],
#                 tree.Muon_Py[i],
#                 tree.Muon_Pz[i],
#                 tree.Muon_E[i]
#                 )
#             muon.charge = tree.Muon_Charge[i]
#             muon.iso = tree.Muon_Iso[i]/muon.pt()
#             if muon.iso < self.muon_isolation_threshold:
#                 event.muons.append(muon)

#         # set jets
#         for i in range(0, tree.NJet):
#             jet = Jet(
#                 tree.Jet_Px[i],
#                 tree.Jet_Py[i],
#                 tree.Jet_Pz[i],
#                 tree.Jet_E[i]
#                 )
#             jet = self.JEC * jet
#             jet.has_b_tag = tree.Jet_btag[i] > self.btag_threshold
#             event.jets.append(jet)
#             if jet.has_b_tag:
#                 event.b_jets.append(jet)
#         return event

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

        self.btag_threshold = 1.74

        jec_mode = str(options.get("JEC", "nominal")).lower()
        if jec_mode not in self.JEC_FACTORS:
            allowed = ", ".join(self.JEC_FACTORS)
            raise ValueError(
                f"Unknown JEC mode '{jec_mode}'. "
                f"Choose one of: {allowed}."
            )

        self.JEC = self.JEC_FACTORS[jec_mode]

        self.muon_isolation_threshold = float(
            options.get("muon_isolation", 0.1)
        )

        if self.muon_isolation_threshold < 0.0:
            raise ValueError(
                "Muon-isolation threshold must be non-negative."
            )

    def build_event(self, tree):
        event = Event()

        event.weight = tree.EventWeight
        event.trigger["IsoMu24"] = tree.triggerIsoMu24
        event.met = MET(tree.MET_px, tree.MET_py)

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

            if muon.iso < self.muon_isolation_threshold:
                event.muons.append(muon)

        for i in range(tree.NJet):
            jet = Jet(
                self.JEC * tree.Jet_Px[i],
                self.JEC * tree.Jet_Py[i],
                self.JEC * tree.Jet_Pz[i],
                self.JEC * tree.Jet_E[i],
            )
            jet.has_b_tag = tree.Jet_btag[i] > self.btag_threshold

            event.jets.append(jet)

            if jet.has_b_tag:
                event.b_jets.append(jet)

        return event
