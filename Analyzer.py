from collections import OrderedDict
from pathlib import Path

import ROOT

from EventBuilder import EventBuilder
from Cutflow import Cutflow


class Analyzer:
    def __init__(self, dataset_name, file_name, event_options=None):
        event_options = dict(event_options or {})

        self.max_events = event_options.pop("max_events", -1)
        self.event_builder = EventBuilder(event_options)

        self.dataset_name = dataset_name
        self.file_name = file_name
        self.histograms = OrderedDict()
        self.working_dataset = None
        self.cutflow = Cutflow()

    def attach_histogram(self, histogram, name):
        self.histograms[name] = histogram

    def detach_histogram(self, name):
        del self.histograms[name]

    def fill_histograms(self, event, name):
        self.histograms[name].fill(event)
    
    def write_output(self):
        """Write all attached histograms to a ROOT output file."""
        output_path = (
            Path(__file__).resolve().parent
            / f"output_{self.file_name}"
        )

        root_file = ROOT.TFile.Open(str(output_path), "RECREATE")

        if not root_file or root_file.IsZombie():
            raise OSError(
                f"Could not create ROOT output file: {output_path}"
            )

        try:
            for name, histogram_group in self.histograms.items():
                output_dir = root_file.mkdir(name)

                if not output_dir:
                    raise RuntimeError(
                        f"Could not create output directory '{name}'."
                    )

                output_dir.cd()

                for histogram in histogram_group.hists.values():
                    histogram.Write()
        finally:
            root_file.Close()

        print(f"Wrote output to {output_path}")
    
    def record_cut(self, stage_name, event):
        """Record one event passing a named selection stage."""
        self.cutflow.record(stage_name, event.weight)
    
    def write_cutflow(self):
        output_path = (
            Path(__file__).resolve().parent
            / f"cutflow_{Path(self.file_name).stem}.csv"
        )

        self.cutflow.write_csv(output_path)

        print()
        print(self.cutflow.format_table(self.dataset_name))
        print(f"Wrote cutflow to {output_path}")

    def run(self):
        """Process all events in this dataset."""
        print(f"Start processing {self.dataset_name}.")

        input_path = Path(__file__).resolve().parent / "files" / self.file_name
        root_file = ROOT.TFile.Open(str(input_path), "READ")

        if not root_file or root_file.IsZombie():
            raise OSError(f"Could not open ROOT file: {input_path}")

        try:
            tree = root_file.Get("events")

            if not tree:
                available = [
                    (key.GetName(), key.GetClassName())
                    for key in root_file.GetListOfKeys()
                ]
                raise KeyError(
                    f"Could not find TTree 'events' in {input_path}.\n"
                    f"Available objects: {available}"
                )

            if not tree.InheritsFrom("TTree"):
                raise TypeError(
                    f"Object 'events' is not a TTree, but {tree.ClassName()}."
                )

            n_event = 0

            for event_data in tree:
                if 0 <= self.max_events <= n_event:
                    break

                n_event += 1

                if n_event % 10_000 == 0:
                    print(f"{n_event} events processed")

                event = self.event_builder.build_event(event_data)
                self.process(event)

        finally:
            root_file.Close()

        print(f"Done. Processed {n_event} events.")
        self.write_output()
        self.write_cutflow()
