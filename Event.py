class Event(object):
    """
    A collision event. Holding all important physics object required
    for the LHC analysis.
    """
    def __init__(self):
        self.muons = []
        self.jets = []
        self.b_jets = []
        self.met = None
        self.trigger = {}
        self.weight = 1.0
        self.top_mass = 0.0

    def n_jets(self):
        """
        returns number of jets.
        """
        return len(self.jets)

    def n_muons(self):
        """
        returns number of muons.
        """
        return len(self.muons)

    def n_b_jets(self):
        """
        returns number of b-tagged jets.
        """
        return len(self.b_jets)
