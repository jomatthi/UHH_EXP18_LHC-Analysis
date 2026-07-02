from collections import OrderedDict


class Histograms(object):
    """
    A collection of histograms.
    """
    def __init__(self, name):
        self.name = name

        if not hasattr(self, "hists"):
            self.hists = OrderedDict()

        self.is_init = False
        self.initialize_histograms()


    def initialize_histograms(self):
        if self.is_init:
            raise ValueError("Histograms already initialized.")

        for hist in self.hists.values():
            hist.SetName(f"{self.name}_{hist.GetName()}")
            hist.Sumw2()

        self.is_init = True

    def fill(self, event):
        """
        Fill histograms.

        Has to be implemented by actual implemenation of Histograms.
        """
        raise NotImplementedError()
