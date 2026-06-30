from TTbarAnalyzer import TTbarAnalyzer
from Plotter import Plotter
from collections import OrderedDict
from Fitter import Fitter
from Cutflow import write_selection_summary

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
    # print out the selection summary to a CSV file
    write_selection_summary(analyzers)

    # Plot all histograms filled in the Analysis
    plotter = Plotter(analyzers)
    plotter.process()

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Exercise 3: Reconstruction of the top quark mass
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Uncomment to fit the top mass distribution
    # fitter = Fitter(analyzers)
    # fitter.fit(130., 210.)  # fitter.fit(x,y) with (x,y) fit range
