from Analyzer import Analyzer
from uhhHists import DefaultHistograms, TopMassHist
from TopReco import TopReco


class TTbarAnalyzer(Analyzer):
    """
    Analyzer for the ttbar cross-section and mass measurement.
    Derived from Analyzer base class.
    """

    def __init__(self, dataset_name, file_name, event_options={}):
        ################
        # DO NOT TOUCH #
        # initialize base class functionality
        super(TTbarAnalyzer, self).__init__(dataset_name, file_name, event_options)
        ################

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Add the Histograms you want to use here for the selection
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        self.attach_histogram(DefaultHistograms(dataset_name+"_total"), "total")
        self.attach_histogram(DefaultHistograms(dataset_name+"_trigger"), "trigger")

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Creating the class that will reconstruct the top mass
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # TopReco(x,y,z)
        # x = max allowed mass difference between leptonic and hadronic top quark
        # y = minimum number of jets used for reconstruction.
        # z = maximum number of jets used for reconstruction
        # y=z is possible.
        # The default values are x=10.0, y=2, z=4

        self.TopReconstruction = TopReco(10.0, 2, 4)

        # add the histogram to plot the top mass
        self.attach_histogram(TopMassHist(dataset_name+"_top_mass"), "top_mass")

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Here you can define your own variables
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        self.n_total = 0.0

    def process(self, event):
        """
        This method is called for each event.
        You can fill all attatched histograms using self.fill_histograms(event, <hist_name>).
        """

        # increase weighted total number of events for processed dataset
        self.n_total += 1 * event.weight
        # fill initial histogram
        self.fill_histograms(event, "total")

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Exercise 1: Properties of ttbar quark events
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # Event selection:

        # check if event fulfills the "IsoMu24" trigger and don't process the event if it doesn't
        if not event.trigger["IsoMu24"]:
            return
        # remember to increase the number of events passing the trigger selection
        # fill histograms for all events passing the trigger selection
        self.fill_histograms(event, "trigger")

        # Have a look at your histograms and compare the different samples.
        # Try to enrich the fraction of ttbar events by cutting on any of the distributions.
        # Plot all variables after every cut you introduce. Therefore define a new set of Histogramms at the top of this program.

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Exercise 2: Measurement of the ttbar production cross section
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # Once you have optimized your event selection, calculate the selection efficiency after each selection step.
        # Now include also the 'Data' sample when running the analysis.
        # Calculate the production cross section and error on it with the given formula.
        # Rerun the analysis with the JEC variations to get the systematic error on your measurement.

        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        # Exercise 3: Reconstruction of the top quark mass
        # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        # Uncomment the following part to enable the top quark reconstruction.

        # mass = self.TopReconstruction.calculateTopMass(event.jets, event.met, event.muons[0])

        # if (mass > 0):
        #     event.top_mass = mass
        #     self.fill_histograms(event, "top_mass")

        # Uncomment the lines responsible for fitting the top mass in 'my_analysis.py'. You may modify the variables x,y in fit(x,y)
