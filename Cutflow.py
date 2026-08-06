import csv
import math
from collections import OrderedDict
from pathlib import Path


class Cutflow:
    """Store raw and weighted yields for named selection cuts."""

    def __init__(self):
        self._cuts = OrderedDict()
    
    def register_cut(self, cut_name):
        """Register a cut even if no event ever passes it."""
        if not isinstance(cut_name, str) or not cut_name.strip():
            raise ValueError("Cutflow cut names must be non-empty strings.")

        if cut_name not in self._cuts:
            self._cuts[cut_name] = {
                "raw_events": 0,
                "weighted_yield": 0.0,
                "sumw2": 0.0,
            }

    def record(self, cut_name, weight):
        self.register_cut(cut_name)

        weight = float(weight)

        if not math.isfinite(weight):
            raise ValueError("Event weights must be finite.")

        self._cuts[cut_name]["raw_events"] += 1
        self._cuts[cut_name]["weighted_yield"] += weight
        self._cuts[cut_name]["sumw2"] += weight * weight

    def cut_names(self):
        return tuple(self._cuts.keys())

    def weighted_yield(self, cut_name):
        return self._cuts[cut_name]["weighted_yield"]

    def raw_events(self, cut_name):
        return self._cuts[cut_name]["raw_events"]

    def sumw2(self, cut_name):
        return self._cuts[cut_name]["sumw2"]

    def yield_statistical_uncertainty(self, cut_name):
        return math.sqrt(self.sumw2(cut_name))

    def rows(self):
        if not self._cuts:
            return []

        first_cut = next(iter(self._cuts))

        rows = []

        for cut_name, values in self._cuts.items():

            rows.append(
                {
                    "cut": cut_name,
                    "raw_events": values["raw_events"],
                    "weighted_yield": values["weighted_yield"],
                    "sumw2": values["sumw2"],
                    "yield_statistical_uncertainty": self.yield_statistical_uncertainty(cut_name),
                }
            )

        return rows

    def write_csv(self, output_path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "cut",
            "raw_events",
            "weighted_yield",
            "sumw2",
            "yield_statistical_uncertainty",
        ]

        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.rows())

    def format_table(self, dataset_name):
        lines = [
            f"Cutflow for {dataset_name}",
            (
                f"{'cut':<24}"
                f"{'raw events':>14}"
                f"{'weighted yield':>20}"
                f"{'statistical uncertainty':>30}"
            ),
        ]

        for row in self.rows():

            lines.append(
                f"{row['cut']:<24}"
                f"{row['raw_events']:>14d}"
                f"{row['weighted_yield']:>20.4f}"
                f"{row['yield_statistical_uncertainty']:>30.4f}"
            )

        return "\n".join(lines)

