from Analyzer import Analyzer
from uhhHists import DefaultHistograms, TopMassHist
from TopReco import TopReco
from pathlib import Path
from collections import OrderedDict


class TTbarAnalyzer(Analyzer):
    """
    Analyzer for the ttbar cross-section and mass measurement.
    Derived from Analyzer base class.
    """

    def __init__(
        self,
        dataset_name,
        file_name,
        event_options=None,
        output_dir=None,
    ):
        ################
        # DO NOT TOUCH #
        # initialize base class functionality
        super(TTbarAnalyzer, self).__init__(
            dataset_name,
            file_name,
            event_options=event_options,
            output_dir=output_dir,
        )
        ################

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Add the Histograms you want to use here for the selection
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        self.attach_histogram(
            DefaultHistograms(dataset_name + "_total"),
            "total"
        )
        self.attach_histogram(
            DefaultHistograms(dataset_name + "_trigger"),
            "trigger"
        )

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Creating the class that will reconstruct the top mass
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # TopReco(mass_diff, n_jet_min, n_jet_max)
        # mass_diff = max allowed mass difference between leptonic and hadronic top
        # n_jet_min = minimum number of jets used for reconstruction.
        # n_jet_max = maximum number of jets used for reconstruction
        # n_jet_min=n_jet_max is possible.

        # The default values are mass_diff=1.0, n_jet_min=2, n_jet_max=3, which are far from optimal.
        # You need to change them to optimize the reconstruction.
        mass_diff = 1.0
        n_jet_min = 2
        n_jet_max = 3

        self.TopReconstruction = TopReco(mass_diff, n_jet_min, n_jet_max)

        # add the histogram to plot the top mass
        self.attach_topmass_histogram(
            TopMassHist(dataset_name + "_top_mass"),
            "top_mass"
        )

    def process(self, event):
        """
        This method is called for each event.
        You can fill all attatched histograms using
        self.fill_histograms(event, <hist_name>).
        """

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Initial step (no cuts, total number of events)
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # fill initial histogram
        self.fill_histograms(event, "total")
        # increase weighted total number of events for processed dataset
        self.record_cut(event, "total")

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Exercise 1: Properties of ttbar quark events
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # Event selection:

        # First selection step as example:
        # check if event fulfills the "IsoMu24" trigger
        # don't process the event if it doesn't
        if not event.trigger["IsoMu24"]:
            return
        # fill histograms for all events passing the trigger selection
        self.fill_histograms(event, "trigger")
        # remember to increase the selection statistics of events passing the trigger step
        self.record_cut(event, "trigger")

        # Have a look at your histograms and compare the different samples.
        # Try to enrich the fraction of ttbar events by cutting on any of
        # the distributions. Plot all variables after every cut you introduce.
        # Therefore define a new set of Histogramms at the top of this program,
        # in addition to the cuts implemented here.

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Exercise 2: Measurement of the ttbar production cross section
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # Implement the selection efficiency and purity calculations in 'SelectionMetrics.py'.
        # Try to optimize your selection to get the best efficiency and purity.

        # Once you have optimized your event selection, include also the 'Data' sample when running the analysis,
        # by calling the script with the '--run_all' option.
        # Calculate the production cross section and error on it with
        # the given formula.
        # Rerun the analysis with the JEC variations to get the systematic
        # error on your measurement. This can be done by calling the script with the '--jec up/down' option.
        # You can now skip the plotting of the histograms by calling the script with the '--skip-plots' option.

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Exercise 3: Reconstruction of the top quark mass
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # Uncomment the following part to enable the top quark reconstruction.
        # mass = self.calculateTopMass(event)

        # if mass > 0:
        #     event.top_mass = mass
        #     self.fill_histograms(event, "top_mass")

        # Uncomment the lines responsible for fitting the top mass in
        # 'my_analysis.py'. You may modify the variables x,y in fit(x,y)


def run_variation(datasets, jec_mode="nominal", smoke_test=False, n_events=None):
    # set the output directory for the results of this JEC variation
    if smoke_test:
        output_dir = Path("results") / "smoke_test"
    else:
        output_dir = Path("results") / f"jec_{jec_mode}"

    event_options = {
        "JEC": jec_mode,
    }
    if n_events is not None:
        event_options["max_events"] = n_events

    analyzers = OrderedDict()

    for name, file_name in datasets.items():
        # create an instance of the TTbarAnalyzer for each dataset
        analyzer = TTbarAnalyzer(
            name,
            file_name,
            event_options,
            output_dir=output_dir,
        )
        # run the analysis for this dataset
        analyzer.run()
        analyzers[name] = analyzer

    return analyzers
