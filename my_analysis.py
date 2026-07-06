from Plotter import Plotter
from collections import OrderedDict
from SelectionMetrics import (
    combine_yields,
    cut_yield,
)
import argparse
from TTbarAnalyzer import run_variation

JEC_MODES = ("nominal", "up", "down")


def resolve_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--jec",
        choices=JEC_MODES,
        default="nominal",
        help="Choose the JEC variation to run (default: nominal)."
    )
    parser.add_argument(
        "--run-all",
        action="store_true",
        default=False,
        help="Run the analysis on all datasets, including data (default: False)."
    )
    parser.add_argument(
        "--skip-plots",
        action="store_true",
        default=False,
        help="Skip creating PDF plots (default: False)."
    )
    return parser.parse_args()


if __name__ == "__main__":
    """
    Main analysis script. Here you run the analysis and evaluate the results.
    You can choose the JEC variation to run, whether to include data in the analysis, and whether to skip creating PDF plots.
    The script will print the yields of the signal and background samples before and after the cuts, and can also calculate the
    selection efficiency and purity if the corresponding functions are implemented in SelectionMetrics.py.
    Additionally, you can fit the top mass distribution by uncommenting the relevant lines and providing the fit range.
    """
    # resolve command-line arguments
    args = resolve_args()
    jec_mode = args.jec
    run_all = args.run_all
    skip_plots = args.skip_plots

    # List of datasets to be analyzed
    if run_all:
        datasets = OrderedDict(
            [
                ('Data', 'data.root'),
                ('TTbar', 'ttbar.root'),
                ('QCD', 'qcd.root'),
                ('Diboson', 'diboson.root'),
                ('DY+jets', 'dy.root'),
                ('single top', 'single_top.root'),
                ('W+jets', 'wjets.root'),
            ]
        )
    else:
        datasets = OrderedDict(
            [
                ('TTbar', 'ttbar.root'),
                ('QCD', 'qcd.root'),
                ('Diboson', 'diboson.root'),
                ('DY+jets', 'dy.root'),
                ('single top', 'single_top.root'),
                ('W+jets', 'wjets.root'),
            ]
        )

    print(f"\nRunning JEC variation: {jec_mode}")
    analyzers = run_variation(datasets, jec_mode)
    print("")

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Exercise 1: Properties of ttbar quark events
    # Exercise 2: Measurement of the ttbar production cross section
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # print out selection chain for the signal sample to see which cuts are available
    # cut1 -> cut2 -> cut3 -> ... -> cutN
    list_of_cuts = list(analyzers['TTbar'].cutflow.cut_names())
    for i, cut in enumerate(list_of_cuts):
        print(f"Cut {i+1}: {cut}")

    # name of the last cut in the selection chain to evaluate the yields, efficiency, and purity for
    cut_name = list_of_cuts[-1]

    # retrieve the yields for the signal sample before and after the cuts
    signal_before_cuts = cut_yield(analyzers['TTbar'].cutflow, 'total')
    signal_after_cuts = cut_yield(analyzers['TTbar'].cutflow, cut_name)

    # list of background datasets (excluding signal and data)
    background_names = [
        name for name in analyzers if name != 'TTbar' and name != 'Data'
    ]

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

    # calculate the selection efficiency and purity
    # uncomment the following lines after implementing the efficiency and purity functions in SelectionMetrics.py
    # from SelectionMetrics import efficiency, purity
    # signal_efficiency = efficiency(signal_before_cuts, signal_after_cuts)
    # selection_purity = purity(signal_after_cuts, background_after_cuts)

    # print(f"Signal efficiency: {signal_efficiency.value:.2%} ± {signal_efficiency.stat_uncertainty:.2%}")
    # print(f"Selection purity: {selection_purity.value:.2%} ± {selection_purity.stat_uncertainty:.2%}")

    # Plot all histograms filled in the Analysis
    if not skip_plots:
        plotter = Plotter(analyzers)
        plotter.process()
    print("=" * 90)
    print("")

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Exercise 3: Reconstruction of the top quark mass
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # Uncomment to fit the top mass distribution
    # from Fitter import Fitter
    # fitter = Fitter(analyzers)
    # fitter.fit(130., 300.)  # fitter.fit(x,y) with (x,y) fit range

    print("=" * 90)
    print("")
    print("Analysis completed.")
