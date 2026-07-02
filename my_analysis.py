from TTbarAnalyzer import TTbarAnalyzer
from Plotter import Plotter
from collections import OrderedDict
from Fitter import Fitter
from SelectionMetrics import (
    combine_yields,
    cut_yield,
)

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
    # Here, you can retrieve the yields of the signal and background samples before and after the cuts.

    # list of background datasets (excluding signal and data)
    background_names = [
        name for name in analyzers if name != 'TTbar' and name != 'Data'
    ]

    # name of the last cut in the selection chain to evaluate the yields, efficiency, and purity for
    cut_name = 'trigger'

    # retrieve the yields for the signal sample before and after the cuts
    signal_before_cuts = cut_yield(analyzers['TTbar'].cutflow, 'total')
    signal_after_cuts = cut_yield(analyzers['TTbar'].cutflow, cut_name)

    # retrieve the yields for the background samples before and after the cuts
    background_yields_before_cuts = [
        cut_yield(analyzers[name].cutflow, "total")
        for name in background_names
    ]
    # combine all background yields before cuts
    background_before_cuts = combine_yields(*background_yields_before_cuts)

    # retrieve the yields for the background samples after the cuts
    background_yields_after_cuts = [
        cut_yield(analyzers[name].cutflow, cut_name)
        for name in background_names
    ]
    # combine all background yields after cuts
    background_after_cuts = combine_yields(*background_yields_after_cuts)

    # print selection summary for the specified cut
    print("")
    print("=" * 90)
    print(f"Selection cut: {cut_name}")
    print("Signal yields:")
    print(f"{signal_before_cuts.sumw:.3f} ± {signal_before_cuts.stat_uncertainty:.3f} -> {signal_after_cuts.sumw:.3f} ± {signal_after_cuts.stat_uncertainty:.3f}")
    print("Background yields:")
    print(f"{background_before_cuts.sumw:.3f} ± {background_before_cuts.stat_uncertainty:.3f} -> {background_after_cuts.sumw:.3f} ± {background_after_cuts.stat_uncertainty:.3f}")

    # if the analysis is run with data, print the data yields as well
    if run_all:
        data_before_cuts = cut_yield(analyzers['Data'].cutflow, 'total')
        data_after_cuts = cut_yield(analyzers['Data'].cutflow, cut_name)
        print("Data yields:")
        print(f"{data_before_cuts.sumw:.3f} ± {data_before_cuts.stat_uncertainty:.3f} -> {data_after_cuts.sumw:.3f} ± {data_after_cuts.stat_uncertainty:.3f}")

    # calculate the selection efficiency and purity
    # uncomment the following lines after implementing the efficiency and purity functions in SelectionMetrics.py
    # from SelectionMetrics import efficiency, purity
    # signal_efficiency = efficiency(signal_before_cuts, signal_after_cuts)
    # selection_purity = purity(signal_after_cuts, background_after_cuts)

    # print(f"Signal efficiency: {signal_efficiency.value:.2%} ± {signal_efficiency.stat_uncertainty:.2%}")
    # print(f"Selection purity: {selection_purity.value:.2%} ± {selection_purity.stat_uncertainty:.2%}")
    # if run_all:
    #     data_efficiency = efficiency(data_before_cuts, data_after_cuts)
    #     print(f"Data efficiency: {data_efficiency.value:.2%} ± {data_efficiency.stat_uncertainty:.2%}")

    # Plot all histograms filled in the Analysis
    plotter = Plotter(analyzers)
    plotter.process()

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Exercise 3: Reconstruction of the top quark mass
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Uncomment to fit the top mass distribution
    # from Fitter import Fitter
    # fitter = Fitter(analyzers)
    # fitter.fit(130., 300.)  # fitter.fit(x,y) with (x,y) fit range

    print("=" * 90)
    print("Analysis completed.")
