import csv
import math
from collections import OrderedDict
from pathlib import Path


class Cutflow:
    """Store raw and weighted yields for named selection stages."""

    def __init__(self):
        self._stages = OrderedDict()

    def record(self, stage_name, weight):
        if not isinstance(stage_name, str) or not stage_name.strip():
            raise ValueError("Cutflow stage names must be non-empty strings.")

        weight = float(weight)

        if not math.isfinite(weight):
            raise ValueError("Event weights must be finite.")

        if stage_name not in self._stages:
            self._stages[stage_name] = {
                "raw_events": 0,
                "weighted_yield": 0.0,
            }

        self._stages[stage_name]["raw_events"] += 1
        self._stages[stage_name]["weighted_yield"] += weight

    def stage_names(self):
        return tuple(self._stages.keys())

    def weighted_yield(self, stage_name):
        return self._stages[stage_name]["weighted_yield"]

    def raw_events(self, stage_name):
        return self._stages[stage_name]["raw_events"]

    def rows(self):
        if not self._stages:
            return []

        first_stage = next(iter(self._stages))
        initial_yield = self.weighted_yield(first_stage)

        rows = []

        for stage_name, values in self._stages.items():
            if initial_yield == 0.0:
                efficiency = float("nan")
            else:
                efficiency = (
                    values["weighted_yield"] / initial_yield
                )

            rows.append(
                {
                    "stage": stage_name,
                    "raw_events": values["raw_events"],
                    "weighted_yield": values["weighted_yield"],
                    "efficiency_from_total": efficiency,
                }
            )

        return rows

    def write_csv(self, output_path):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fieldnames = [
            "stage",
            "raw_events",
            "weighted_yield",
            "efficiency_from_total",
        ]

        with output_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.rows())

    def format_table(self, dataset_name):
        lines = [
            f"Cutflow for {dataset_name}",
            (
                f"{'stage':<24}"
                f"{'raw events':>14}"
                f"{'weighted yield':>20}"
                f"{'efficiency':>14}"
            ),
        ]

        for row in self.rows():
            efficiency = row["efficiency_from_total"]

            efficiency_text = (
                f"{efficiency:>13.3%}"
                if math.isfinite(efficiency)
                else f"{'n/a':>14}"
            )

            lines.append(
                f"{row['stage']:<24}"
                f"{row['raw_events']:>14d}"
                f"{row['weighted_yield']:>20.4f}"
                f"{efficiency_text}"
            )

        return "\n".join(lines)


def selection_summary(analyzers, signal_name="TTbar", data_name="Data"):
    """Combine cutflows to calculate MC signal efficiency and purity."""
    if signal_name not in analyzers:
        raise KeyError(
            f"Signal dataset '{signal_name}' is not available."
        )

    stages = analyzers[signal_name].cutflow.stage_names()

    for dataset_name, analyzer in analyzers.items():
        if analyzer.cutflow.stage_names() != stages:
            raise ValueError(
                "All datasets must use identical cutflow stages. "
                f"Mismatch for dataset '{dataset_name}'."
            )

    mc_datasets = OrderedDict(
        (
            name,
            analyzer,
        )
        for name, analyzer in analyzers.items()
        if name != data_name
    )

    background_names = [
        name for name in mc_datasets
        if name != signal_name
    ]

    initial_signal = analyzers[signal_name].cutflow.weighted_yield(
        stages[0]
    )

    rows = []

    for stage in stages:
        signal_yield = analyzers[signal_name].cutflow.weighted_yield(
            stage
        )

        background_yields = {
            name: analyzers[name].cutflow.weighted_yield(stage)
            for name in background_names
        }
        background_yield = sum(background_yields.values())

        total_mc = signal_yield + background_yield

        signal_efficiency = (
            signal_yield / initial_signal
            if initial_signal != 0.0
            else float("nan")
        )

        purity = (
            signal_yield / total_mc
            if total_mc != 0.0
            else float("nan")
        )

        dominant_background = (
            max(background_yields, key=background_yields.get)
            if background_yields
            else ""
        )

        row = {
            "stage": stage,
            "signal_yield": signal_yield,
            "background_yield": background_yield,
            "signal_efficiency": signal_efficiency,
            "purity": purity,
            "dominant_background": dominant_background,
        }

        if data_name in analyzers:
            row["data_yield"] = analyzers[
                data_name
            ].cutflow.weighted_yield(stage)
        else:
            row["data_yield"] = ""

        for dataset_name, analyzer in analyzers.items():
            row[f"yield_{dataset_name}"] = (
                analyzer.cutflow.weighted_yield(stage)
            )

        rows.append(row)

    return rows


def write_selection_summary(
    analyzers,
    output_path="selection_summary.csv",
    signal_name="TTbar",
    data_name="Data",
):
    rows = selection_summary(analyzers, signal_name, data_name)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(rows[0].keys()) if rows else []

    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("\nSelection summary (simulation):")
    print(
        f"{'stage':<24}"
        f"{'signal efficiency':>20}"
        f"{'purity':>14}"
        f"{'largest background':>22}"
    )

    for row in rows:
        efficiency = row["signal_efficiency"]
        purity = row["purity"]

        efficiency_text = (
            f"{efficiency:>19.3%}"
            if math.isfinite(efficiency)
            else f"{'n/a':>20}"
        )
        purity_text = (
            f"{purity:>13.3%}"
            if math.isfinite(purity)
            else f"{'n/a':>14}"
        )

        print(
            f"{row['stage']:<24}"
            f"{efficiency_text}"
            f"{purity_text}"
            f"{row['dominant_background']:>22}"
        )

    print(f"\nWrote selection summary to {output_path}")
