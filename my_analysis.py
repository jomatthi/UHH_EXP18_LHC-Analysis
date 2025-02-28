from TTbarAnalyzer import TTbarAnalyzer
from Plotter import Plotter
from collections import OrderedDict
from Fitter import Fitter

if __name__ == "__main__":
    """
    Main analysis script. Here you run the analysis and evaluate the results.
    """

    # Choose run mode ('False' as default to design & optimize the analysis):
    run_all = False  # only run the Monte Carlo simulation.
    # run_all = True  # run both Data and Monte Carlo simulation.

    # List of datasets to be analyzed
    if run_all:
        datasets = OrderedDict(
            [
                ('Data', 'data.root'),
                ('QCD', 'qcd.root'),
                ('Diboson', 'diboson.root'),
                ('DY+jets', 'dy.root'),
                ('single top', 'single_top.root'),
                ('TTbar', 'ttbar.root'),
                ('W+jets', 'wjets.root'),
            ]
        )
    else:
        datasets = OrderedDict(
            [
                ('QCD', 'qcd.root'),
                ('Diboson', 'diboson.root'),
                ('DY+jets', 'dy.root'),
                ('single top', 'single_top.root'),
                ('TTbar', 'ttbar.root'),
                ('W+jets', 'wjets.root'),
            ]
        )

    # Options for the event builder
    event_options = {
        # Jet Energy corrections: "up" or "down" to evaluate the syst. error
        'JEC': 'nominal',
        # muon isolation, you can leave this at the default value
        'muon_isolation': 0.1
        }

    analyzers = OrderedDict()

    # Analyze datasets:
    for name, file_name in datasets.items():
        # create an Analyzer for each dataset
        analyzer = TTbarAnalyzer(name, file_name, event_options)
        # run the Analyzer
        analyzer.run()
        # store the results
        analyzers[name] = analyzer

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Exercise 1: Properties of ttbar quark events
    # Exercise 2: Measurement of the ttbar production cross section
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # You can access variables from TTbarAnalyzer like this:
    # total number of events in the TTbar sample
    n_ttbar_total = analyzers['TTbar'].n_total

    # total number of events in the background samples
    n_background_total = sum(
        [
            # Sum total number of all events, except 'Data' and 'TTbar'
            an.n_total for key, an in analyzers.items() if not (key == 'Data' or key == 'TTbar')  # noqa
        ]
    )

    # print numbers in the terminal
    print(f"Total number of ttbar events: {n_ttbar_total}")
    # you can also reduce the numbers of digits
    print(f"Total number of background events: {n_background_total:.4f}")

    # Plot all histograms filled in the Analysis
    plotter = Plotter(analyzers)
    plotter.process()

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Exercise 3: Reconstruction of the top quark mass
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Uncomment to fit the top mass distribution
    # fitter = Fitter(analyzers)
    # fitter.fit(130., 210.)  # fitter.fit(x,y) with (x,y) fit range
