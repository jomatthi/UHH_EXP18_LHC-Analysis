import argparse
from collections import OrderedDict
from pathlib import Path

from Plotter import Plotter
from TTbarAnalyzer import TTbarAnalyzer


DATASETS = OrderedDict(
    [
        ("Data", "data.root"),
        ("QCD", "qcd.root"),
        ("Diboson", "diboson.root"),
        ("DY+jets", "dy.root"),
        ("single top", "single_top.root"),
        ("TTbar", "ttbar.root"),
        ("W+jets", "wjets.root"),
    ]
)


def main():
    parser = argparse.ArgumentParser(
        description="Run a short end-to-end analysis smoke test."
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=10,
        help="Maximum number of events per dataset (default: 10).",
    )
    args = parser.parse_args()

    if args.max_events < 1:
        parser.error("--max-events must be at least 1.")

    event_options = {
        "JEC": "nominal",
        "max_events": args.max_events,
    }

    print(
        "Starting smoke test: "
        f"{len(DATASETS)} datasets, "
        f"at most {args.max_events} events each."
    )

    analyzers = OrderedDict()

    for dataset_name, file_name in DATASETS.items():
        analyzer = TTbarAnalyzer(
            dataset_name,
            file_name,
            event_options,
        )
        analyzer.run()
        analyzers[dataset_name] = analyzer

    expected_outputs = [
        Path(f"output_{file_name}")
        for file_name in DATASETS.values()
    ]

    missing_outputs = [
        str(path)
        for path in expected_outputs
        if not path.is_file() or path.stat().st_size == 0
    ]

    if missing_outputs:
        raise RuntimeError(
            "Smoke test failed: missing or empty output files:\n"
            + "\n".join(missing_outputs)
        )

    plotter = Plotter(analyzers)
    plotter.process()

    print("Smoke test finished successfully.")


if __name__ == "__main__":
    main()
